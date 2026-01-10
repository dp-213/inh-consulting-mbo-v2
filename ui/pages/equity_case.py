from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    st.markdown("# Equity Case")
    output_container = st.container()
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_equity_key_assumptions(
            assumptions, "equity.assumptions"
        )
    updated_result = run_model(updated_assumptions)
    with output_container:
        outputs.render_equity_case(updated_result, updated_assumptions)
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "- Business meaning: shows who puts capital at risk and who receives cashflows and exit proceeds.\n"
            "- Calculation logic: equity contributions fund the purchase price gap, residual cash after debt service flows to equity holders, and the exit bridge reconciles enterprise value to equity value.\n"
            "- Key dependencies: transaction and financing assumptions, debt schedule, and valuation exit values."
        )
    return updated_assumptions
