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
    exit_equity_value = (
        updated_result.equity.get("exit_value", 0.0) - pension_obligation
    )

    with output_container:
        st.markdown("### Valuation Today – Overview")
        overview_rows = [
            ("Multiple-based Equity Value (Today)", [multiple_equity]),
            ("DCF-based Equity Value (Today, no terminal)", [dcf_equity]),
            ("Intrinsic / Cash-Based Value (Today)", [intrinsic_equity]),
            ("Illustrative Exit Equity Value (Sensitivity)", [exit_equity_value]),
        ]
        outputs._render_statement_table_html(
            overview_rows,
            years=1,
            year_labels=["Equity Value"],
        )
        st.markdown(
            '<div class="subtle">DCF and intrinsic values exclude acquisition outflows and reflect operating free cashflow only.</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Seller Valuation Logic (Reference)")
        ebit_years = [updated_result.pnl[idx]["ebit"] for idx in range(3)]
        discount_factors = [1 / ((1 + discount_rate) ** idx) for idx in range(3)]
        pv_ebit = [ebit_years[idx] * discount_factors[idx] for idx in range(3)]
        pv_sum = sum(pv_ebit)
        seller_price_expectation = pv_sum + pension_obligation
        seller_rows = [
            ("EBIT", ebit_years),
            (
                "Discount Factor to Today",
                [f"{discount_factors[0]:.2f}", f"{discount_factors[1]:.2f}", f"{discount_factors[2]:.2f}"],
            ),
            ("Present Value of EBIT", pv_ebit),
            ("PV of 3-year EBIT", ["", "", pv_sum]),
            ("Pension Obligations Assumed", ["", "", pension_obligation]),
            ("Seller Price Expectation", ["", "", seller_price_expectation]),
        ]
        outputs._render_statement_table_html(
            seller_rows,
            bold_labels={"Seller Price Expectation"},
            years=3,
            year_labels=outputs.YEAR_LABELS[:3],
        )
        st.markdown(
            '<div class="subtle">This reflects the seller’s internal pricing logic and serves as a negotiation anchor. It is not a valuation of intrinsic business value.</div>',
            unsafe_allow_html=True,
        )

    with st.expander("Detailed analysis", expanded=False):
        st.markdown("#### Multiple-Based Valuation (Today)")
        multiple_rows = [
            (f"Reference EBIT ({outputs.YEAR_LABELS[reference_year]})", [reference_ebit]),
            ("Applied Multiple (Assumption)", [f"{seller_multiple:.2f}x"]),
            ("Enterprise Value (EBIT × Multiple)", [enterprise_value_multiple]),
            ("Net Debt (End of Transition Year)", [net_debt_close]),
            ("Pension Obligations Assumed", [pension_obligation]),
            ("Equity Value (Multiple-Based)", [multiple_equity]),
        ]
        outputs._render_statement_table_html(
            multiple_rows,
            bold_labels={"Equity Value (Multiple-Based)"},
            years=1,
            year_labels=["Value"],
        )

        st.markdown("#### DCF-Based Valuation (no terminal)")
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
            ("Equity Value (DCF, no terminal)", ["", "", "", "", dcf_equity]),
        ]
        outputs._render_statement_table_html(
            dcf_rows,
            bold_labels={"Equity Value (DCF, no terminal)"},
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

        st.markdown("#### Illustrative Exit Equity Value (Sensitivity)")
        exit_rows = [
            ("Minimum Cash Balance (Assumption)", [updated_assumptions.balance_sheet.minimum_cash_balance_eur]),
            ("Covenant Threshold (DSCR)", [f"{updated_assumptions.financing.minimum_dscr:.2f}x"]),
            ("Net Debt (End of Transition Year)", [net_debt_close]),
            ("Pension Obligations Assumed", [pension_obligation]),
            ("Equity Value (Illustrative Exit)", [exit_equity_value]),
        ]
        outputs._render_statement_table_html(
            exit_rows,
            bold_labels={"Equity Value (Illustrative Exit)"},
            years=1,
            year_labels=["Value"],
        )

    with st.expander("Upside / Exit Sensitivity (Optional)", expanded=False):
        st.markdown(
            '<div class="subtle">Exit analysis is shown for sensitivity only and is not part of today’s valuation.</div>',
            unsafe_allow_html=True,
        )
        outputs.render_valuation_exit(updated_result)
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "**1) Business Question**\n"
            "Is the price defensible today versus intrinsic cash value and market reference, and is the downside acceptable without relying on exit upside?\n\n"
            "**2) What This Shows / What This Does NOT Show**\n"
            "Shows three value perspectives today (DCF intrinsic, EBIT multiple reference, and an illustrative exit sensitivity) and the explicit adjustments for net debt and pensions.\n"
            "Does not include a terminal value, a growth case, or a price recommendation; exit value is a sensitivity view, not an affordability ceiling.\n\n"
            "**3) Calculation Logic (Transparent, Step-by-Step)**\n"
            "Market reference value is built from the reference-year EBIT and the seller multiple to derive enterprise value, then adjusted for net debt at the end of the transition year and pension obligations to reach equity value.\n"
            "DCF intrinsic value is built from operating free cashflows from the valuation start year, discounted at the stated rate, then adjusted for net debt at the end of the transition year and pension obligations.\n"
            "Intrinsic cash value is the undiscounted sum of operating free cashflows from the start year, again adjusted for net debt and pensions.\n"
            "Seller pricing logic discounts the first three years of EBIT and adds assumed pension obligations to reflect the seller’s internal anchor.\n\n"
            "**4) Interpretation for the Decision**\n"
            "Higher intrinsic and reference values support a higher price; values below the contemplated price indicate overpayment risk.\n"
            "If intrinsic cash value is materially below market reference, the business relies on multiple expansion rather than cash generation.\n"
            "Exit sensitivity should only be used to assess upside risk, not to justify today’s price.\n\n"
            "**5) Insights & Red Flags**\n"
            "Large dispersion between DCF and multiple-based values signals uncertainty in sustainable cash generation.\n"
            "Negative or weak early‑year free cashflows reduce intrinsic value and increase reliance on exit.\n"
            "High pension obligations materially compress equity value and can make otherwise reasonable enterprise values unattractive.\n\n"
            "**6) Key Dependencies**\n"
            "Reference EBIT and seller multiple, discount rate and valuation start year, operating free cashflow drivers (EBITDA, capex, working capital, cash taxes), net debt at the end of the transition year, pension obligations."
        )
    return updated_assumptions
