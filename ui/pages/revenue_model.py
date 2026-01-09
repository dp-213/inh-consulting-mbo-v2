from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Revenue Model")
    st.markdown("Editable revenue input sheet for the selected scenario.")
    return inputs.render_revenue_inputs(assumptions)
