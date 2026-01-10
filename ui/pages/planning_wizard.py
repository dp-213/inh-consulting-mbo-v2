from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render_inputs(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Planning Wizard")
    st.markdown(
        "Guided planning flow with only the most impactful drivers. "
        "Use this to set the core case before diving into detailed sheets."
    )

    step = st.selectbox(
        "Step",
        [
            "Step 1: Revenue Drivers",
            "Step 2: Cost Drivers",
            "Step 3: Loans & Funding",
            "Step 4: Purchase Price & Exit",
        ],
        index=0,
    )

    if step == "Step 1: Revenue Drivers":
        st.markdown("Focus: capacity, pricing, and guarantee floor.")
        return inputs.render_revenue_quick_inputs(assumptions)
    if step == "Step 2: Cost Drivers":
        st.markdown("Focus: consultant costs, backoffice, and management.")
        return inputs.render_cost_quick_inputs(assumptions)
    if step == "Step 3: Loans & Funding":
        st.markdown("Focus: loan size, pricing, and repayment.")
        return inputs.render_financing_quick_inputs(assumptions)
    st.markdown("Focus: purchase price and exit multiple.")
    return inputs.render_valuation_quick_inputs(assumptions)
