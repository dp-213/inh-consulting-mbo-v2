from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    st.markdown("# Financing & Debt")
    output_container = st.container()
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_financing_key_assumptions(
            assumptions, "financing.assumptions"
        )
    updated_result = run_model(updated_assumptions)
    with output_container:
        outputs.render_financing_debt(updated_result, updated_assumptions)
    return updated_assumptions
