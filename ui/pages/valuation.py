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
    enterprise_value = updated_result.equity.get("enterprise_value", 0.0)

    free_cf = [row["free_cashflow"] for row in updated_result.cashflow]
    discount_rate = updated_assumptions.valuation.discount_rate_pct
    start_year = updated_assumptions.valuation.valuation_start_year
    if start_year < 0 or start_year >= len(free_cf):
        st.error("Valuation Start Year is out of range for the current plan horizon.")
        st.stop()
    running = 0.0
    for idx, value in enumerate(free_cf):
        if idx < start_year:
            continue
        factor = 1 / ((1 + discount_rate) ** (idx - start_year + 1))
        running += value * factor
    dcf_value = running
    intrinsic_value = sum(
        value for idx, value in enumerate(free_cf) if idx >= start_year
    )

    multiple_equity = enterprise_value - net_debt_close - pension_obligation
    dcf_equity = dcf_value - net_debt_close - pension_obligation
    intrinsic_equity = intrinsic_value - net_debt_close - pension_obligation
    affordability = updated_result.equity.get("exit_value", 0.0) - pension_obligation

    with output_container:
        st.markdown("### Valuation Today – Overview")
        overview_rows = [
            ("Multiple-based Equity Value (Today)", [multiple_equity]),
            ("DCF-based Equity Value (Today, no terminal)", [dcf_equity]),
            ("Intrinsic / Cash-Based Value (Today)", [intrinsic_equity]),
            ("Buyer Affordability (Ceiling)", [affordability]),
        ]
        outputs._render_statement_table_html(
            overview_rows,
            years=1,
            year_labels=["Equity Value"],
        )

        st.markdown("### Purchase Price Logic")
        ebit_years = [updated_result.pnl[idx]["ebit"] for idx in range(1, 4)]
        discounted_ebit = 0.0
        for idx, value in enumerate(ebit_years, start=1):
            discounted_ebit += value / ((1 + discount_rate) ** idx)
        purchase_price = updated_assumptions.transaction_and_financing.purchase_price_eur
        price_rows = [
            ("Seller pricing mechanism (3-year EBIT discounted)", [discounted_ebit]),
            ("Pension obligations assumed", [pension_obligation]),
            ("Purchase Price (Enterprise)", [purchase_price]),
        ]
        outputs._render_statement_table_html(
            price_rows,
            years=1,
            year_labels=["Value"],
        )

    with st.expander("Detailed analysis", expanded=False):
        st.markdown("#### Multiple-Based Valuation (Today)")
        reference_year = updated_assumptions.valuation.reference_year
        if reference_year < 0 or reference_year >= len(updated_result.pnl):
            st.error("Reference Year is out of range for the current plan horizon.")
            st.stop()
        reference_ebit = updated_result.pnl[reference_year]["ebit"]
        multiple_rows = [
            (f"Reference EBIT ({outputs.YEAR_LABELS[reference_year]})", [reference_ebit]),
            ("Applied Multiple (Assumption)", [f"{updated_assumptions.valuation.seller_multiple:.2f}x"]),
            ("Enterprise Value (Model)", [enterprise_value]),
            ("Net Debt at Close (Reference)", [net_debt_close]),
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
        for idx in range(len(free_cf)):
            if idx < start_year:
                discount_factors.append("")
                pv_fcf.append("")
                cumulative_pv.append("")
                continue
            factor = 1 / ((1 + discount_rate) ** (idx - start_year + 1))
            value = free_cf[idx] * factor
            running += value
            discount_factors.append(f"{factor:.2f}")
            pv_fcf.append(value)
            cumulative_pv.append(running)
        dcf_rows = [
            ("Free Cashflow", free_cf),
            ("Discount Factor", discount_factors),
            ("Present Value of FCF", pv_fcf),
            ("PV Sum (no terminal)", cumulative_pv),
            ("Net Debt at Close (Reference)", [net_debt_close] + [""] * 4),
            ("Pension Obligations Assumed", [pension_obligation] + [""] * 4),
            ("Equity Value (DCF, no terminal)", ["", "", "", "", dcf_equity]),
        ]
        outputs._render_statement_table_html(
            dcf_rows,
            bold_labels={"Equity Value (DCF, no terminal)"},
        )

        st.markdown("#### Intrinsic / Cash-Based Value (Undiscounted)")
        intrinsic_rows = [
            ("Free Cashflow", free_cf),
            ("Sum of Plan Cashflows", ["", "", "", "", intrinsic_value]),
            ("Net Debt at Close (Reference)", [net_debt_close] + [""] * 4),
            ("Pension Obligations Assumed", [pension_obligation] + [""] * 4),
            ("Equity Value (Intrinsic / Cash-Based)", ["", "", "", "", intrinsic_equity]),
        ]
        outputs._render_statement_table_html(
            intrinsic_rows,
            bold_labels={"Equity Value (Intrinsic / Cash-Based)"},
        )

        st.markdown("#### Buyer Affordability (Ceiling, not valuation)")
        affordability_rows = [
            ("Minimum Cash Balance (Assumption)", [updated_assumptions.balance_sheet.minimum_cash_balance_eur]),
            ("Covenant Threshold (DSCR)", [f"{updated_assumptions.financing.minimum_dscr:.2f}x"]),
            ("Net Debt at Close (Reference)", [net_debt_close]),
            ("Pension Obligations Assumed", [pension_obligation]),
            ("Equity Value (Buyer Affordability)", [affordability]),
        ]
        outputs._render_statement_table_html(
            affordability_rows,
            bold_labels={"Equity Value (Buyer Affordability)"},
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
            "- Business meaning: contrasts what the business is worth today with what a buyer can afford to pay today, net of assumed pension liabilities.\n"
            "- Calculation logic: equity value is derived as enterprise value minus net debt at close and assumed pension obligations; DCF discounts plan cashflows to today; intrinsic sums plan cashflows; affordability reflects financing and liquidity constraints.\n"
            "- Key dependencies: P&L (reference year metric), cashflow plan, balance sheet net debt at close, pension obligation assumption, and financing assumptions."
        )
    return updated_assumptions
