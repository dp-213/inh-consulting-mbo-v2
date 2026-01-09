from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Financing Assumptions")
    st.markdown("Editable transaction and debt inputs used across the model.")
    return inputs.render_financing_assumptions(assumptions)
