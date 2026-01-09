from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import inputs, outputs


def render_inputs(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Planning Wizard")
    st.markdown("Guided planning flow with only the most impactful drivers.")

    step = st.selectbox(
        "Step",
        [
            "Step 1: Revenue Drivers",
            "Step 2: Cost Drivers",
            "Step 3: Financing",
            "Step 4: Valuation",
        ],
        index=0,
    )

    if step == "Step 1: Revenue Drivers":
        return inputs.render_revenue_quick_inputs(assumptions)
    if step == "Step 2: Cost Drivers":
        return inputs.render_cost_quick_inputs(assumptions)
    if step == "Step 3: Financing":
        return inputs.render_financing_quick_inputs(assumptions)
    return inputs.render_valuation_quick_inputs(assumptions)


def render_outputs(result: ModelResult) -> None:
    st.markdown("### Impact Preview")
    outputs.render_impact_preview(result)
