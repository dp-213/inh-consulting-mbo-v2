from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    st.markdown("# Financing & Debt")
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_financing_key_assumptions(
            assumptions, "financing.assumptions"
        )
    output_container = st.container()
    updated_result = run_model(updated_assumptions)
    with output_container:
        outputs.render_financing_debt(updated_result, updated_assumptions)
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "- Business meaning: tests whether operational cash covers debt service and where covenants break first.\n"
            "- Calculation logic: CFADS is derived from EBITDA less cash taxes, maintenance capex, and working capital; DSCR compares CFADS to total debt service and headroom versus the minimum covenant.\n"
            "- Key dependencies: cashflow statement, financing assumptions, and the debt schedule (the transition year can be stressed by closing effects)."
        )
    return updated_assumptions
