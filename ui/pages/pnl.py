from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui.pages.quick_adjust import render_quick_adjust_pnl


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


def render(result: ModelResult, assumptions: Assumptions) -> None:
    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown("# Operating Model (P&L)")
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )
    _render_scenario_selector(assumptions.scenario)

    updated_assumptions = render_quick_adjust_pnl(assumptions, "pnl.quick")
    updated_result = run_model(updated_assumptions)
    st.markdown(
        "<div class=\"info-box\"><strong>Interpretation</strong><ul>"
        "<li>Economics are driven by utilization and seniority mix, not pricing power.</li>"
        "<li>Personnel costs dominate the P&amp;L and define downside risk.</li>"
        "<li>Operating leverage only materializes if capacity is filled.</li>"
        "</ul></div>",
        unsafe_allow_html=True,
    )
    st.markdown("### P&L (Summary)")
    outputs.render_operating_model(updated_result, updated_assumptions)
