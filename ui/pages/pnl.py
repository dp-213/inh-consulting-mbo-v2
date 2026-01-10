from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Operating Model (P&L)")
    st.markdown("P&L (GuV)")
    outputs.render_operating_model(result, assumptions)
