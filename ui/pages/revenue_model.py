from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("# Revenue Model")
    st.markdown("### Consultant Capacity (Derived)")
    rows = [
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
    _render_input_table(rows, ["Parameter", "Unit", "Year 0", "Year 1", "Year 2", "Year 3", "Year 4"])
    return inputs.render_revenue_inputs(assumptions)


def _render_input_table(rows: list[dict], columns: list[str]) -> None:
    html = ['<table class="input-table">', "<thead><tr>"]
    for header in columns:
        html.append(f"<th>{header}</th>")
    html.append("</tr></thead><tbody>")
    for row in rows:
        html.append("<tr>")
        for col in columns:
            html.append(f"<td>{row.get(col, '')}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)

