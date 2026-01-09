from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from ui import outputs


def render(result: ModelResult) -> None:
    with st.expander("Valuation & Equity Returns", expanded=True):
        outputs.render_valuation(result)
