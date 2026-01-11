from __future__ import annotations

import streamlit as st

from model.run_model import run_model
from state.assumptions import Assumptions
from ui import inputs
from ui import outputs


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("# Revenue Model")
    st.markdown("### Consultant Capacity (Derived)")
    year_columns = inputs.YEARS
    rows = [
        (
            "Consultant FTE (Derived from Cost Model)",
            [assumptions.cost.personnel_by_year[idx].consultant_fte for idx in range(5)],
        )
    ]
    outputs._render_statement_table_html(
        rows,
        years=len(year_columns),
        year_labels=year_columns,
    )
    updated_assumptions = inputs.render_revenue_inputs(assumptions)
    updated_result = run_model(updated_assumptions)
    components = updated_result.revenue.get("components_by_year", [])
    if components:
        st.markdown("### Revenue Bridge")
        rows = [
            ("Modeled Group Revenue", [row["modeled_group_revenue"] for row in components]),
            ("Guaranteed Floor", [row["guaranteed_floor"] for row in components]),
            ("Guaranteed Group Revenue", [row["guaranteed_group_revenue"] for row in components]),
            ("Modeled External Revenue", [row["modeled_external_revenue"] for row in components]),
            ("Total Revenue (Final)", [row["final_total"] for row in components]),
        ]
        outputs._render_statement_table_html(
            rows,
            bold_labels={"Total Revenue (Final)", "Guaranteed Group Revenue"},
            year_labels=outputs.YEAR_LABELS,
        )
    return updated_assumptions


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
