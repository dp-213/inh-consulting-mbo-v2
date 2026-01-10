from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from ui import outputs


def render(result: ModelResult) -> None:
    st.markdown("## Equity Case")
    st.markdown("Owner return profile from entry to exit.")
    outputs.render_equity_case(result)
