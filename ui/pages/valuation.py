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

    with output_container:
        st.markdown("## Seller Price Expectation – Transparent Build-Up")
        st.markdown(
            '<div class="subtle">Reference pricing based on historic EBIT, not a standalone valuation.</div>',
            unsafe_allow_html=True,
        )
        discount_factors = [
            1 / ((1 + discount_rate) ** year_index) for year_index in (1, 2, 3)
        ]
        pv_ebit = [transition_ebit * factor for factor in discount_factors]
        pv_sum = sum(pv_ebit)
        seller_price_expectation = pv_sum + pension_obligation
        seller_rows = [
            ("Reference EBIT (Transition Year)", [transition_ebit]),
            ("Discount rate (Seller assumption)", [f"{discount_rate:.2f}%"]),
            ("EBIT Year 1", [transition_ebit]),
            ("Discount factor Year 1", [f"{discount_factors[0]:.4f}"]),
            ("Present Value Year 1", [pv_ebit[0]]),
            ("EBIT Year 2", [transition_ebit]),
            ("Discount factor Year 2", [f"{discount_factors[1]:.4f}"]),
            ("Present Value Year 2", [pv_ebit[1]]),
            ("EBIT Year 3", [transition_ebit]),
            ("Discount factor Year 3", [f"{discount_factors[2]:.4f}"]),
            ("Present Value Year 3", [pv_ebit[2]]),
            ("Sum of Present Values (3-year EBIT)", [pv_sum]),
            ("Pension obligations assumed", [pension_obligation]),
            ("Seller Price Expectation (Total)", [seller_price_expectation]),
        ]
        outputs._render_statement_table_html(
            seller_rows,
            bold_labels={"Seller Price Expectation (Total)"},
            years=1,
            year_labels=["Value"],
            row_classes={
                "Discount factor Year 1": "substep",
                "Present Value Year 1": "substep",
                "Discount factor Year 2": "substep",
                "Present Value Year 2": "substep",
                "Discount factor Year 3": "substep",
                "Present Value Year 3": "substep",
            },
        )

        st.markdown("### Interpretation")
        st.markdown(
            "- Uses only transition-year EBIT, so it is backward-looking and conservative.\n"
            "- Applies a fixed seller discount rate rather than buyer affordability logic.\n"
            "- Ignores growth and financing structure by design; it is a price anchor, not a value claim."
        )

        st.markdown("### Buyer Sanity Checks (Context Only)")
        st.markdown(
            '<div class="subtle">Reference / Plausibility Checks</div>',
            unsafe_allow_html=True,
        )
        buyer_rows = [
            ("Multiple-Based Reference (EBIT × Multiple)", [enterprise_value_multiple]),
            ("Cashflow Coverage Value (DCF, no terminal)", [dcf_value]),
        ]
        outputs._render_statement_table_html(
            buyer_rows,
            years=1,
            year_labels=["Value"],
        )

    with st.expander("Detailed Mechanics (Optional)", expanded=False):
        st.markdown("#### Multiple-Based Reference (EBIT × Multiple)")
        multiple_rows = [
            (f"Reference EBIT ({outputs.YEAR_LABELS[0]})", [transition_ebit]),
            ("Applied Multiple (Assumption)", [f"{seller_multiple:.2f}x"]),
            ("Enterprise Value (EBIT × Multiple)", [enterprise_value_multiple]),
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
            (
                "Cashflow Coverage Value",
                [""] * (len(business_free_cf) - 1) + [dcf_value],
            ),
        ]
        outputs._render_statement_table_html(
            dcf_rows,
        )
    return updated_assumptions
