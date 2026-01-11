from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def _case_name(path: str) -> str:
    if not path:
        return "Unnamed Case"
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def _render_scenario_selector(current: str) -> None:
    options = ["Worst", "Base", "Best"]
    if "view_scenario" not in st.session_state:
        st.session_state["view_scenario"] = current
    current_value = st.session_state["view_scenario"]
    if current_value not in options:
        current_value = current
    st.radio(
        "Scenario",
        options,
        index=options.index(current_value),
        horizontal=True,
        key="view_scenario",
        label_visibility="collapsed",
    )


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown("# Valuation & Purchase Price")
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_valuation_key_assumptions(
            assumptions, "valuation.assumptions"
        )
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )
    _render_scenario_selector(assumptions.scenario)
    output_container = st.container()
    updated_result = run_model(updated_assumptions)
    pension_obligation = updated_assumptions.balance_sheet.pension_obligations_eur
    debt_year0 = updated_result.debt[0] if updated_result.debt else {}
    closing_debt = debt_year0.get("closing_debt", 0.0)
    cash_at_close = (
        updated_result.balance_sheet[0].get("cash", 0.0)
        if updated_result.balance_sheet
        else 0.0
    )
    net_debt_close = closing_debt - cash_at_close
    reference_year = updated_assumptions.valuation.reference_year
    if reference_year < 0 or reference_year >= len(updated_result.pnl):
        st.error("Reference Year is out of range for the current plan horizon.")
        st.stop()
    reference_ebit = updated_result.pnl[reference_year]["ebit"]
    seller_multiple = updated_assumptions.valuation.seller_multiple
    enterprise_value_multiple = reference_ebit * seller_multiple

    business_free_cf = [
        row["free_cashflow"] - row.get("acquisition_outflow", 0.0)
        for row in updated_result.cashflow
    ]
    discount_rate = updated_assumptions.valuation.discount_rate_pct
    start_year = updated_assumptions.valuation.valuation_start_year
    if start_year < 0 or start_year >= len(business_free_cf):
        st.error("Valuation Start Year is out of range for the current plan horizon.")
        st.stop()
    running = 0.0
    for idx, value in enumerate(business_free_cf):
        if idx < start_year:
            continue
        factor = 1 / ((1 + discount_rate) ** (idx - start_year + 1))
        running += value * factor
    dcf_value = running
    intrinsic_value = sum(
        value for idx, value in enumerate(business_free_cf) if idx >= start_year
    )

    multiple_equity = enterprise_value_multiple - net_debt_close - pension_obligation
    dcf_equity = dcf_value - net_debt_close - pension_obligation
    intrinsic_equity = intrinsic_value - net_debt_close - pension_obligation

    with output_container:
        st.markdown("### Seller Price Expectation")
        ebit_years = [updated_result.pnl[idx]["ebit"] for idx in range(3)]
        discount_factors = [1 / ((1 + discount_rate) ** idx) for idx in range(3)]
        pv_ebit = [ebit_years[idx] * discount_factors[idx] for idx in range(3)]
        pv_sum = sum(pv_ebit)
        seller_price_expectation = pv_sum + pension_obligation
        seller_rows = [
            ("Reference EBIT (Transition Year)", [reference_ebit]),
            ("PV of 3-year EBIT", [pv_sum]),
            ("Pension Obligations Assumed", [pension_obligation]),
            ("Seller Price Expectation", [seller_price_expectation]),
        ]
        outputs._render_statement_table_html(
            seller_rows,
            years=1,
            year_labels=["Value"],
        )
        st.markdown(
            '<div class="subtle">Seller logic reflects a negotiation anchor, not intrinsic value.</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Buyer Sanity Checks")
        buyer_rows = [
            ("Multiple-Based Reference (Negotiation Anchor)", [multiple_equity]),
            ("Cashflow Coverage Value (DCF, no terminal)", [dcf_equity]),
        ]
        outputs._render_statement_table_html(
            buyer_rows,
            years=1,
            year_labels=["Value"],
        )
        st.markdown(
            '<div class="subtle">DCF excludes acquisition outflows and reflects operating free cashflow only.</div>',
            unsafe_allow_html=True,
        )

    with st.expander("Detailed analysis", expanded=False):
        st.markdown("#### Multiple-Based Reference (Negotiation Anchor)")
        multiple_rows = [
            (f"Reference EBIT ({outputs.YEAR_LABELS[reference_year]})", [reference_ebit]),
            ("Applied Multiple (Assumption)", [f"{seller_multiple:.2f}x"]),
            ("Enterprise Value (EBIT × Multiple)", [enterprise_value_multiple]),
            ("Net Debt (End of Transition Year)", [net_debt_close]),
            ("Pension Obligations Assumed", [pension_obligation]),
            ("Reference Equity Value", [multiple_equity]),
        ]
        outputs._render_statement_table_html(
            multiple_rows,
            years=1,
            year_labels=["Value"],
        )

        st.markdown("#### Cashflow Coverage Value (DCF, no terminal)")
        discount_factors = []
        pv_fcf = []
        cumulative_pv = []
        running = 0.0
        for idx in range(len(business_free_cf)):
            if idx < start_year:
                discount_factors.append("")
                pv_fcf.append("")
                cumulative_pv.append("")
                continue
            factor = 1 / ((1 + discount_rate) ** (idx - start_year + 1))
            value = business_free_cf[idx] * factor
            running += value
            discount_factors.append(f"{factor:.2f}")
            pv_fcf.append(value)
            cumulative_pv.append(running)
        dcf_rows = [
            ("Free Cashflow (Business)", business_free_cf),
            ("Discount Factor", discount_factors),
            ("Present Value of FCF", pv_fcf),
            ("PV Sum (no terminal)", cumulative_pv),
            ("Net Debt (End of Transition Year)", [net_debt_close] + [""] * 4),
            ("Pension Obligations Assumed", [pension_obligation] + [""] * 4),
            ("Cashflow Coverage Value", ["", "", "", "", dcf_equity]),
        ]
        outputs._render_statement_table_html(
            dcf_rows,
        )

        st.markdown("#### Intrinsic / Cash-Based Value (Undiscounted)")
        intrinsic_rows = [
            ("Free Cashflow (Business)", business_free_cf),
            ("Sum of Plan Cashflows", ["", "", "", "", intrinsic_value]),
            ("Net Debt (End of Transition Year)", [net_debt_close] + [""] * 4),
            ("Pension Obligations Assumed", [pension_obligation] + [""] * 4),
            ("Equity Value (Intrinsic / Cash-Based)", ["", "", "", "", intrinsic_equity]),
        ]
        outputs._render_statement_table_html(
            intrinsic_rows,
            bold_labels={"Equity Value (Intrinsic / Cash-Based)"},
        )

    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "**1) Business Question**\n"
            "- Is the price defensible today versus intrinsic cash value and the EBIT‑multiple reference?\n"
            "\n**2) What This Shows / What This Does NOT Show**\n"
            "- Shows DCF cash coverage, EBIT‑multiple reference, and seller pricing anchor, all adjusted for net debt and pensions.\n"
            "- Does not include terminal value, growth case, or a price recommendation.\n"
            "\n**3) Calculation Logic (Transparent, Step-by-Step)**\n"
            "- Enterprise Value (Multiple) = Reference EBIT × Seller Multiple.\n"
            "- Equity Value (Multiple) = Enterprise Value − Net Debt (End of Transition Year) − Pension Obligations.\n"
            "- DCF PV = Σ (Operating Free Cashflowᵗ / (1 + discount rate)ᵗ) from valuation start year.\n"
            "- Equity Value (DCF) = DCF PV − Net Debt (End of Transition Year) − Pension Obligations.\n"
            "- Intrinsic Cash Value = Σ Operating Free Cashflow from start year − Net Debt − Pension Obligations.\n"
            "- Seller Price Expectation = Σ PV(EBIT Year 0–2) + Pension Obligations.\n"
            "\n**4) Interpretation for the Decision**\n"
            "- If purchase price exceeds both DCF and multiple reference, downside protection is weak.\n"
            "- If DCF is materially below multiple reference, value depends on multiple expansion, not cash.\n"
            "- Use exit sensitivity only to size upside, not to justify price.\n"
            "\n**5) Insights & Red Flags**\n"
            "- Large dispersion between DCF and multiple values signals fragile cash generation.\n"
            "- Negative or weak early cashflows materially reduce intrinsic value.\n"
            "- Pension obligations can compress equity value to unattractive levels.\n"
            "\n**6) Key Dependencies**\n"
            "- Reference EBIT and seller multiple.\n"
            "- Discount rate and valuation start year.\n"
            "- Operating free cashflow drivers (EBITDA, capex, working capital, cash taxes).\n"
            "- Net debt at end of transition year and pension obligations."
        )
    return updated_assumptions
