from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("# Cost Model")
    return inputs.render_cost_inputs(assumptions)
