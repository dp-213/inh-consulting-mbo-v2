from __future__ import annotations

from dataclasses import replace

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Cost Model")
    scenario = st.radio(
        "Scenario",
        ["Worst", "Base", "Best"],
        index=["Worst", "Base", "Best"].index(assumptions.scenario),
        horizontal=True,
    )
    if scenario != assumptions.scenario:
        assumptions = replace(assumptions, scenario=scenario)
    if st.checkbox("Explain cost logic & assumptions", value=False):
        st.markdown("Costs are driven by headcount, loaded costs, and overhead assumptions.")
    return inputs.render_cost_inputs(assumptions)
