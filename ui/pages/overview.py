from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from ui import outputs


def render(result: ModelResult) -> None:
    with st.expander("Key Metrics", expanded=True):
        outputs.render_overview(result)
    with st.expander("Revenue Summary", expanded=True):
        outputs.render_revenue(result)
    with st.expander("Cost Summary", expanded=True):
        outputs.render_costs(result)
