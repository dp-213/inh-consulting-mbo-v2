from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions, base_case: Assumptions) -> None:
    st.markdown("## Overview")
    outputs.render_overview(result, assumptions)
