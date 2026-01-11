from __future__ import annotations

from pathlib import Path

import streamlit as st

from state.assumptions import Assumptions


def render(assumptions: Assumptions, data_path: str, case_options: list[str]) -> dict:
    st.markdown("# Case Management")
    is_base_case = data_path.endswith("base_case.json")

    # A. Active Case (read-only)
    st.subheader("A. Active Case")
    st.markdown(f"**{_case_name(data_path)}**")
    st.caption(f"Source: {'Base' if is_base_case else 'Custom'}")
    st.caption(f"Active Scenario: {assumptions.scenario}")
    st.caption(f"File path: {data_path}")

    st.markdown("---")

    # B. Switch Case
    st.subheader("B. Switch Case")
    st.caption("Loading a case replaces the current session immediately.")

    library_paths = _discover_case_paths(case_options)
    load_choice = st.selectbox(
        "Available cases",
        ["Select case..."] + library_paths,
        index=0,
        format_func=_case_option_label,
    )
    load_pressed = st.button("Load Case", type="primary")

    st.markdown("---")

    # C. Save / Duplicate
    st.subheader("C. Save / Duplicate")
    if is_base_case:
        st.caption("Base Case is read-only. Use Save As to create a copy.")

    new_case_name = st.text_input(
        "New case name (for Save As)",
        value="",
        placeholder="e.g. downside_case_v2",
        label_visibility="visible",
    ).strip()

    save_cols = st.columns([1, 1, 3])
    with save_cols[0]:
        save_pressed = st.button("Save", disabled=is_base_case, type="primary")
    with save_cols[1]:
        save_as_pressed = st.button("Save As", type="secondary")

    st.markdown("---")

    # D. Reset (Danger Zone)
    st.subheader("D. Reset (Danger Zone)")
    st.caption("This will discard all unsaved changes in the current session.")
    reset_pressed = st.button("Reset to Base Case", type="secondary")

    return {
        "scenario": assumptions.scenario,
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


def _discover_case_paths(case_options: list[str]) -> list[str]:
    paths: list[str] = []

    base_case = Path("data") / "base_case.json"
    if base_case.exists():
        paths.append(str(base_case))

    data_dir = Path("data")
    if data_dir.exists():
        for path in sorted(data_dir.glob("*.json")):
            if path.name == "base_case.json":
                continue
            paths.append(str(path))

    cases_dir = data_dir / "cases"
    if cases_dir.exists():
        for name in case_options:
            candidate = cases_dir / f"{name}.json"
            if candidate.exists():
                paths.append(str(candidate))

    seen: set[str] = set()
    ordered: list[str] = []
    for item in paths:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _case_option_label(value: str) -> str:
    if value == "Select case...":
        return value
    name = value.split("/")[-1].replace(".json", "")
    if value.endswith("base_case.json"):
        return "Base Case (read-only)"
    if "/data/cases/" in value.replace("\\", "/"):
        return f"{name} (saved)"
    return f"{name} (json)"
