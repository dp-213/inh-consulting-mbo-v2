from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from ui import outputs


def render(result: ModelResult) -> None:
    st.markdown("## Operating Model (P&L)")
    st.markdown("P&L (GuV)")
    outputs.render_operating_model(result)
