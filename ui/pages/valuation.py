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
    market_multiple = updated_assumptions.valuation.market_multiple
    enterprise_value_multiple = transition_ebit * market_multiple
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
    seller_factors = [
        1 / ((1 + discount_rate) ** year_index) for year_index in (1, 2, 3)
    ]
    seller_pv_ebit = [transition_ebit * factor for factor in seller_factors]
    seller_pv_sum = sum(seller_pv_ebit)
    seller_price_expectation = seller_pv_sum + pension_obligation

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

    intrinsic_label = (
        "Discount to intrinsic value"
        if discount_to_intrinsic >= 0
        else "Premium to intrinsic value"
    )
    market_label = (
        "Discount to market reference"
        if discount_to_market >= 0
        else "Premium to market reference"
    )
    intrinsic_amount = abs(discount_to_intrinsic)
    market_amount = abs(discount_to_market)
    intrinsic_percent = outputs._format_percent(intrinsic_amount, dcf_value)
    market_percent = outputs._format_percent(market_amount, enterprise_value_multiple)

    with output_container:
        st.markdown(
            "## Seller Price Expectation (Negotiation Anchor - not valuation)"
        )
        st.markdown(
            '<div class="subtle">Negotiation anchor - seller internal pricing logic.</div>',
            unsafe_allow_html=True,
        )
        seller_rows = [
            ("Reference EBIT (Transition Year)", [transition_ebit]),
            ("Seller discount rate (assumption)", [f"{discount_rate:.2f}%"]),
            ("PV of EBIT Year 1", [seller_pv_ebit[0]]),
            ("PV of EBIT Year 2", [seller_pv_ebit[1]]),
            ("PV of EBIT Year 3", [seller_pv_ebit[2]]),
            ("Sum PV of 3-year EBIT", [seller_pv_sum]),
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
                ("Market multiple assumption", [f"{market_multiple:.2f}x"]),
            ]
            outputs._render_statement_table_html(
                market_rows,
                years=1,
                year_labels=["Value"],
            )
            st.markdown(
                '<div class="subtle">Observed market reference - not seller anchor.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("## Deal Attractiveness (Price vs. Value)")
        st.markdown(
            '<div class="subtle">Positive discounts mean price is below value.</div>',
            unsafe_allow_html=True,
        )
        deal_rows = [
            ("Purchase Price (Enterprise)", [purchase_price]),
            ("Implied Equity Price (after net debt & pensions)", [equity_price]),
            (intrinsic_label, [intrinsic_amount]),
            (f"{intrinsic_label} (%)", [intrinsic_percent]),
            (market_label, [market_amount]),
            (f"{market_label} (%)", [market_percent]),
            (
                "Implied multiple vs. market",
                [f"{implied_multiple:.2f}x vs {market_multiple:.2f}x"],
            ),
        ]
        outputs._render_statement_table_html(
            deal_rows,
            years=1,
            year_labels=["Value"],
        )

    with st.expander("Detailed Mechanics (Transparency for Review)", expanded=False):
        st.markdown("#### Seller PV Mechanics")
        st.markdown(
            '<div class="subtle">What this shows: 3-year PV of transition EBIT plus pensions.</div>',
            unsafe_allow_html=True,
        )
        seller_year_labels = ["Year 1", "Year 2", "Year 3"]
        seller_detail_rows = [
            ("Reference EBIT", [transition_ebit] * 3),
            ("Seller discount rate (assumption)", [f"{discount_rate:.2f}%"] * 3),
            ("PV factor", [f"{factor:.3f}" for factor in seller_factors]),
            ("PV of EBIT", seller_pv_ebit),
            ("Sum PV of 3-year EBIT", ["", "", seller_pv_sum]),
            ("Pension obligations assumed", ["", "", pension_obligation]),
            ("Seller headline price (Total)", ["", "", seller_price_expectation]),
        ]
        outputs._render_statement_table_html(
            seller_detail_rows,
            years=3,
            year_labels=seller_year_labels,
            bold_labels={"Seller headline price (Total)"},
        )

        st.markdown("#### DCF Walkthrough (No Terminal)")
        st.markdown(
            '<div class="subtle">What this shows: discounted business free cashflow only.</div>',
            unsafe_allow_html=True,
        )
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
            ("Business free cashflow", business_free_cf),
            ("Discount factor", discount_factors),
            ("Present value of cashflow", pv_fcf),
            ("PV sum (no terminal)", cumulative_pv),
            ("DCF value (no terminal)", [""] * (len(business_free_cf) - 1) + [dcf_value]),
        ]
        outputs._render_statement_table_html(
            dcf_rows,
        )
        st.markdown(
            '<div class="subtle">No terminal, no financing effects.</div>',
            unsafe_allow_html=True,
        )

        st.markdown("#### Market Multiple Walkthrough")
        st.markdown(
            '<div class="subtle">What this shows: observed market reference (EBIT x multiple).</div>',
            unsafe_allow_html=True,
        )
        market_detail_rows = [
            ("Reference EBIT (Transition Year)", [transition_ebit]),
            ("Market multiple assumption", [f"{market_multiple:.2f}x"]),
            ("Enterprise value (EBIT x multiple)", [enterprise_value_multiple]),
        ]
        outputs._render_statement_table_html(
            market_detail_rows,
            years=1,
            year_labels=["Value"],
        )

        st.markdown("#### Price to Equity Bridge")
        st.markdown(
            '<div class="subtle">What this shows: enterprise price reconciled to equity value.</div>',
            unsafe_allow_html=True,
        )
        bridge_rows = [
            ("Enterprise purchase price", [purchase_price]),
            ("Net debt at close", [net_debt_close]),
            ("Pension obligations assumed", [pension_obligation]),
            ("Implied equity price", [equity_price]),
        ]
        outputs._render_statement_table_html(
            bridge_rows,
            years=1,
            year_labels=["Value"],
        )

        st.markdown("#### Deal Metrics Proof")
        st.markdown(
            '<div class="subtle">What this shows: formulas used for EUR and % discounts.</div>',
            unsafe_allow_html=True,
        )
        proof_rows = [
            ("Formula: intrinsic discount (EUR)", ["DCF value - purchase price"]),
            ("Formula: intrinsic discount (%)", ["Intrinsic discount EUR / DCF value"]),
            ("Formula: market discount (EUR)", ["Market value - purchase price"]),
            ("Formula: market discount (%)", ["Market discount EUR / market value"]),
        ]
        outputs._render_statement_table_html(
            proof_rows,
            years=1,
            year_labels=["Value"],
        )
    return updated_assumptions
