from __future__ import annotations

from dataclasses import replace

import streamlit as st

from state.assumptions import Assumptions


def render_case_bar(
    assumptions: Assumptions, current_path: str, case_options: list[str]
) -> tuple[Assumptions, dict]:
    st.markdown("## Case")
    st.table([{"Current Case": _case_name(current_path)}])

    scenario = st.selectbox(
        "Scenario View",
        ["Base", "Best", "Worst"],
        index=["Base", "Best", "Worst"].index(assumptions.scenario),
    )
    updated_assumptions = (
        replace(assumptions, scenario=scenario)
        if scenario != assumptions.scenario
        else assumptions
    )

    new_case_table = st.data_editor(
        [{"Parameter": "New Case Name", "Value": ""}],
        use_container_width=True,
        key="case.new_name",
    )
    if hasattr(new_case_table, "to_dict"):
        records = new_case_table.to_dict(orient="records")
    else:
        records = new_case_table
    new_case_name = str(records[0].get("Value", "") or "").strip()

    load_choice = st.selectbox(
        "Load Case",
        ["Select case..."] + case_options,
        index=0,
    )

    save_pressed = st.button("Save")
    save_as_pressed = st.button("Save As")
    load_pressed = st.button("Load Selected Case")
    reset_pressed = st.button("Reset to Base")

    actions = {
        "save": save_pressed,
        "save_as": save_as_pressed,
        "load": load_pressed,
        "reset": reset_pressed,
        "load_choice": load_choice,
        "new_case_name": new_case_name,
    }
    return updated_assumptions, actions


def _case_name(path: str) -> str:
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"
