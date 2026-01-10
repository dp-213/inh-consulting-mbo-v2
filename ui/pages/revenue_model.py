from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("## Revenue Model")
    st.markdown("Editable revenue input sheet for the selected scenario.")
    if st.checkbox("Explain revenue logic & assumptions", value=False):
        st.markdown("Revenue is driven by capacity, utilization, and day rates across the planning period.")
    st.markdown("### Consultant Capacity (Derived)")
    st.table(
        [
            {
                "Parameter": "Consultant FTE (Derived from Cost Model)",
                "Unit": "FTE",
                "Year 0": assumptions.cost.personnel_by_year[0].consultant_fte,
                "Year 1": assumptions.cost.personnel_by_year[1].consultant_fte,
                "Year 2": assumptions.cost.personnel_by_year[2].consultant_fte,
                "Year 3": assumptions.cost.personnel_by_year[3].consultant_fte,
                "Year 4": assumptions.cost.personnel_by_year[4].consultant_fte,
            }
        ]
    )
    return inputs.render_revenue_inputs(assumptions)
