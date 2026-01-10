from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Cost Model")
    if st.checkbox("Explain cost logic & assumptions", value=False):
        st.markdown("Costs are driven by headcount, loaded costs, and overhead assumptions.")
    return inputs.render_cost_inputs(assumptions)
