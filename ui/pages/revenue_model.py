from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions
from ui import inputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("# Revenue Model")
    st.markdown("### Consultant Capacity (Derived)")
    year_columns = inputs.YEARS
    rows = [
        {
            "Parameter": "Consultant FTE (Derived from Cost Model)",
            "Unit": "FTE",
            **{
                year_columns[idx]: assumptions.cost.personnel_by_year[idx].consultant_fte
                for idx in range(5)
            },
        }
    ]
    _render_input_table(rows, ["Parameter", "Unit"] + year_columns)
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
