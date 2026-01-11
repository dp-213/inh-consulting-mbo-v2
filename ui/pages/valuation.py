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
    if not updated_result.pnl:
        st.error("P&L data is missing for the current plan horizon.")
        st.stop()
    transition_ebit = updated_result.pnl[0]["ebit"]
    seller_multiple = updated_assumptions.valuation.seller_multiple
    enterprise_value_multiple = transition_ebit * seller_multiple
    purchase_price = updated_assumptions.transaction_and_financing.purchase_price_eur

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
    seller_price_expectation = enterprise_value_multiple + pension_obligation

    debt_year0 = updated_result.debt[0] if updated_result.debt else {}
    closing_debt = debt_year0.get(
        "closing_debt", updated_assumptions.financing.senior_debt_amount_eur
    )
    cash_at_close = (
        updated_result.balance_sheet[0].get("cash", 0.0)
        if updated_result.balance_sheet
        else 0.0
    )
    net_debt_close = closing_debt - cash_at_close
    equity_price = purchase_price - net_debt_close - pension_obligation
    discount_to_intrinsic = dcf_value - purchase_price
    discount_to_market = enterprise_value_multiple - purchase_price
    implied_multiple = purchase_price / transition_ebit if transition_ebit else 0.0

    with output_container:
        st.markdown(
            "## Seller Price Expectation (Negotiation Anchor - not valuation)"
        )
        st.markdown(
            '<div class="subtle">Reference pricing based on transition-year EBIT, not a standalone valuation.</div>',
            unsafe_allow_html=True,
        )
        seller_rows = [
            ("Reference EBIT (Transition Year)", [transition_ebit]),
            ("Seller reference multiple (anchor)", [f"{seller_multiple:.2f}x"]),
            ("Seller headline price (EBIT x multiple)", [enterprise_value_multiple]),
            ("Pension obligations assumed", [pension_obligation]),
            ("Seller headline price (Total)", [seller_price_expectation]),
        ]
        outputs._render_statement_table_html(
            seller_rows,
            bold_labels={"Seller headline price (Total)"},
            years=1,
            year_labels=["Value"],
        )

        st.markdown(
            "This reflects the seller's internal pricing logic, not intrinsic business value."
        )

        st.markdown("## Buyer Value Perspectives (Standalone, Today)")
        st.markdown(
            '<div class="subtle">Buyer value is shown separately from price; both are enterprise values.</div>',
            unsafe_allow_html=True,
        )
        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown("### Intrinsic Value (Cashflow-Based)")
            intrinsic_rows = [
                ("Conservative intrinsic value (no growth, no terminal)", [dcf_value]),
            ]
            outputs._render_statement_table_html(
                intrinsic_rows,
                years=1,
                year_labels=["Value"],
            )
            st.markdown(
                '<div class="subtle">Based on business free cashflow (no financing).</div>',
                unsafe_allow_html=True,
            )
        with right_col:
            st.markdown("### Market Reference Value")
            market_rows = [
                ("Observed market valuation reference", [enterprise_value_multiple]),
                ("Reference EBIT (Transition Year)", [transition_ebit]),
                ("Market multiple assumption", [f"{seller_multiple:.2f}x"]),
            ]
            outputs._render_statement_table_html(
                market_rows,
                years=1,
                year_labels=["Value"],
            )

        st.markdown("## Deal Attractiveness (Price vs. Value)")
        st.markdown(
            '<div class="subtle">Positive discounts mean price is below value.</div>',
            unsafe_allow_html=True,
        )
        deal_rows = [
            ("Purchase Price (Enterprise)", [purchase_price]),
            ("Implied Equity Price (after net debt & pensions)", [equity_price]),
            ("Discount to intrinsic value", [discount_to_intrinsic]),
            ("Discount to market reference", [discount_to_market]),
            (
                "Implied multiple vs. market",
                [f"{implied_multiple:.2f}x vs {seller_multiple:.2f}x"],
            ),
        ]
        outputs._render_statement_table_html(
            deal_rows,
            years=1,
            year_labels=["Value"],
        )
    return updated_assumptions
