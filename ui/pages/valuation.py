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
    with output_container:
        outputs.render_valuation_summary(updated_result, updated_assumptions)

    with st.expander("Detailed analysis", expanded=False):
        outputs.render_valuation_detail(updated_result, updated_assumptions)
    with st.expander("Upside / Exit Sensitivity (Optional)", expanded=False):
        outputs.render_valuation_exit(updated_result)
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "- Business meaning: contrasts what the business is worth today with what a buyer can afford to pay today.\n"
            "- Calculation logic: multiple-based value uses the reference year metric and multiple, DCF discounts plan cashflows to today, intrinsic sums plan cashflows, and affordability reflects financing and liquidity constraints.\n"
            "- Key dependencies: P&L (reference year metric), cashflow plan, balance sheet net debt at close, and financing assumptions."
        )
    return updated_assumptions
