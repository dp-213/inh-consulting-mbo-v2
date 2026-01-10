from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs
from ui.pages import planning_wizard


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Revenue Model")
    st.markdown("Start here: the Planning Wizard sets the core case drivers.")
    st.markdown("### Planning Wizard (Recommended Start)")
    assumptions = planning_wizard.render_inputs(assumptions)
    st.markdown("---")
    st.markdown("### Detailed Revenue Sheet")
    st.markdown("Editable revenue input sheet for the selected scenario.")
    return inputs.render_revenue_inputs(assumptions)
