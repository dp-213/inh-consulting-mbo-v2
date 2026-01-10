from __future__ import annotations

from dataclasses import asdict, replace

import streamlit as st

from model.run_model import run_model
from state.cases import case_path, list_cases, load_case, save_case
from state.persistence import load_assumptions
from ui.pages import (
    balance_sheet,
    cashflow,
    cost_model,
    case_management,
    equity_case,
    financing_debt,
    model_settings,
    model_export,
    other_assumptions,
    overview,
    pnl,
    revenue_model,
    valuation,
)

SECTIONS = {
    "OVERVIEW": ["Overview"],
    "OPERATING MODEL (OUTPUT / ANALYSIS)": [
        "Operating Model (Profit & Loss)",
        "Cashflow & Liquidity",
        "Balance Sheet",
    ],
    "PLANNING (MODEL INPUTS)": ["Revenue Model", "Cost Model", "Other Assumptions"],
    "FINANCING": ["Financing & Debt", "Equity Case"],
    "VALUATION": ["Valuation & Purchase Price"],
    "SETTINGS": ["Model Settings", "Case Management", "Model Export / Snapshot"],
}

DEFAULT_PAGE = "Revenue Model"


def _render_sidebar(current_page: str) -> str:
    selected_page = current_page
    for title, options in SECTIONS.items():
        st.sidebar.markdown(f"### {title}")
        for option in options:
            is_active = option == current_page
            if st.sidebar.button(
                option,
                key=f"nav_{option}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected_page = option
    return selected_page


def _render_case_badge(current_path: str, scenario: str) -> None:
    st.caption(f"Case: {_case_name(current_path)} | Scenario: {scenario}")
    st.markdown("---")


def _case_name(path: str) -> str:
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def main() -> None:
    st.set_page_config(page_title="INH Consulting MBO Model", layout="wide")
    if "data_path" not in st.session_state:
        st.session_state["data_path"] = "data/base_case.json"

    if "page" not in st.session_state:
        st.session_state["page"] = DEFAULT_PAGE
    page = _render_sidebar(st.session_state["page"])
    st.session_state["page"] = page

    data_path = st.session_state["data_path"]
    original_assumptions = load_assumptions(data_path)
    assumptions = original_assumptions
    base_case = load_assumptions("data/base_case.json")
    case_options = list_cases()

    _render_case_badge(data_path, assumptions.scenario)

    if page in {"Revenue Model", "Cost Model", "Other Assumptions"}:
        st.markdown("Percent inputs use whole numbers (70 = 70%).")

    if page == "Revenue Model":
        updated_assumptions = revenue_model.render(assumptions)
    elif page == "Cost Model":
        updated_assumptions = cost_model.render(assumptions)
    elif page == "Other Assumptions":
        updated_assumptions = other_assumptions.render(assumptions)
    else:
        updated_assumptions = assumptions

    if data_path.endswith("base_case.json") and asdict(updated_assumptions) != asdict(original_assumptions):
        working_path = str(case_path("Working Copy"))
        save_case(updated_assumptions, working_path)
        st.session_state["data_path"] = working_path
        data_path = working_path
        st.markdown("Base Case cloned to Working Copy for edits.")

    if asdict(updated_assumptions) != asdict(original_assumptions):
        save_case(updated_assumptions, data_path)

    result = run_model(updated_assumptions)

    if page == "Overview":
        overview.render(result, updated_assumptions, base_case)
    elif page == "Operating Model (Profit & Loss)":
        pnl.render(result)
    elif page == "Cashflow & Liquidity":
        cashflow.render(result)
    elif page == "Balance Sheet":
        balance_sheet.render(result)
    elif page == "Financing & Debt":
        financing_debt.render(result)
    elif page == "Equity Case":
        equity_case.render(result)
    elif page == "Valuation & Purchase Price":
        valuation.render(result)
    elif page == "Model Settings":
        model_settings.render(data_path)
    elif page == "Case Management":
        case_actions = case_management.render(updated_assumptions, data_path, case_options)
        scenario = case_actions["scenario"]
        if scenario != updated_assumptions.scenario:
            updated_assumptions = replace(updated_assumptions, scenario=scenario)
            save_case(updated_assumptions, data_path)
        if case_actions["reset"]:
            data_path = "data/base_case.json"
            st.session_state["data_path"] = data_path
            updated_assumptions = load_assumptions(data_path)
        elif case_actions["load"] and case_actions["load_choice"] != "Select case...":
            data_path = str(case_path(case_actions["load_choice"]))
            st.session_state["data_path"] = data_path
            updated_assumptions = load_case(data_path)
        if case_actions["save"]:
            save_case(updated_assumptions, data_path)
        if case_actions["save_as"] and case_actions["new_case_name"]:
            new_path = str(case_path(case_actions["new_case_name"]))
            save_case(updated_assumptions, new_path)
            st.session_state["data_path"] = new_path
            data_path = new_path
        if case_actions["save_as"] and not case_actions["new_case_name"]:
            st.markdown("Enter a case name before saving a copy.")
        if case_actions["load"] and case_actions["load_choice"] == "Select case...":
            st.markdown("Select a case to load, then click Load Selected Case.")
    elif page == "Model Export / Snapshot":
        model_export.render(updated_assumptions, result)


if __name__ == "__main__":
    main()
