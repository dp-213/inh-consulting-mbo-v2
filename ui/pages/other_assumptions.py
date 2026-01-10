from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Other Assumptions")
    st.markdown("Editable model settings for cash flow, balance sheet, and tax and value assumptions.")
    return inputs.render_other_assumptions(assumptions)
