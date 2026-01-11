from __future__ import annotations

import streamlit as st

from dataclasses import replace

from model.run_model import run_model
from state.assumptions import Assumptions
from ui import inputs
from ui import outputs


def _render_scenario_selector(current: str) -> str:
    options = ["Worst", "Base", "Best"]
    if "view_scenario" not in st.session_state:
        st.session_state["view_scenario"] = current
    current_value = st.session_state["view_scenario"]
    if current_value not in options:
        current_value = current
    selection = st.radio(
        "Scenario",
        options,
        index=options.index(current_value),
        horizontal=True,
        key="view_scenario",
        label_visibility="collapsed",
    )
    return selection


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("# Revenue Model")
    selected_scenario = _render_scenario_selector(assumptions.scenario)
    st.markdown(
        '<div class="subtle">Szenarien = operative Realitaet (Revenue-Risiko). '
        'Kosten &amp; Kapitalstruktur = strukturelle Fixpunkte. konservativ.</div>',
        unsafe_allow_html=True,
    )
    if selected_scenario != assumptions.scenario:
        assumptions = replace(assumptions, scenario=selected_scenario)
    st.markdown("### Consultant Capacity (Derived)")
    year_columns = inputs.YEARS
    consultant_fte = [
        int(round(assumptions.cost.personnel_by_year[idx].consultant_fte))
        for idx in range(5)
    ]
    rows = [
        (
            "Consultant FTE (Derived from Cost Model)",
            [str(value) for value in consultant_fte],
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
            ("Guaranteed Floor (Reference × %)", [row["guaranteed_floor"] for row in components]),
            ("Effective Group Revenue", [row["guaranteed_group_revenue"] for row in components]),
            ("External Revenue", [row["modeled_external_revenue"] for row in components]),
            ("Total Revenue", [row["final_total"] for row in components]),
        ]
        outputs._render_statement_table_html(
            rows,
            bold_labels={"Total Revenue", "Effective Group Revenue"},
            year_labels=outputs.YEAR_LABELS,
        )
        if any(
            row["modeled_group_revenue"] < row["guaranteed_floor"]
            for row in components
        ):
            st.markdown(
                '<div class="subtle">Group revenue below guaranteed floor – guarantee applied.</div>',
                unsafe_allow_html=True,
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
