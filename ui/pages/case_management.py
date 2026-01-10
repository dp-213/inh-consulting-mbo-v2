from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions


def render(assumptions: Assumptions, data_path: str, case_options: list[str]) -> dict:
    st.markdown("# Case Management")
    st.markdown("Save, duplicate, and load cases from the case library below.")
    st.table([{"Current Case": _case_name(data_path), "Current JSON Path": data_path}])

    st.markdown("### Case View")
    scenario = st.selectbox(
        "Case View (Base / Best / Worst)",
        ["Base", "Best", "Worst"],
        index=["Base", "Best", "Worst"].index(assumptions.scenario),
    )
    st.markdown("Case view changes affect the planning view for this case.")
    st.markdown("---")

    st.markdown("### Save & Load")
    st.markdown("Base Case is locked. Use Save As to create a new case.")
    name_col, load_col = st.columns([2, 2])
    with name_col:
        new_case_table = st.data_editor(
            [{"Parameter": "New Case Name", "Value": ""}],
            use_container_width=True,
            hide_index=True,
            disabled=["Parameter"],
        )
        if hasattr(new_case_table, "to_dict"):
            records = new_case_table.to_dict(orient="records")
        else:
            records = new_case_table
        new_case_name = str(records[0].get("Value", "") or "").strip()
    with load_col:
        load_choice = st.selectbox(
            "Load Case",
            ["Select case..."] + case_options,
            index=0,
        )

    button_cols = st.columns([1, 1, 1, 1])
    is_base_case = data_path.endswith("base_case.json")
    with button_cols[0]:
        save_pressed = st.button("Save", disabled=is_base_case)
    with button_cols[1]:
        save_as_pressed = st.button("Save As")
    with button_cols[2]:
        load_pressed = st.button("Load Selected Case")
    with button_cols[3]:
        reset_pressed = st.button("Reset to Base")

    return {
        "scenario": scenario,
        "save": save_pressed,
        "save_as": save_as_pressed,
        "load": load_pressed,
        "reset": reset_pressed,
        "load_choice": load_choice,
        "new_case_name": new_case_name,
    }


def _case_name(path: str) -> str:
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"
