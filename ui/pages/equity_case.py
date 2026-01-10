from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("# Equity Case")
    st.markdown(
        "Management Buy-Out with an external minority investor. "
        "Holding period defined by the investor exit year. Exit mechanism: management buys out the investor."
    )
    outputs.render_equity_case(result, assumptions)
