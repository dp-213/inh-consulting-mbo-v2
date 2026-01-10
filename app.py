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
    equity_case,
    financing_assumptions,
    financing_debt,
    model_settings,
    other_assumptions,
    overview,
    pnl,
    planning_wizard,
    revenue_model,
    valuation,
)

PAGES = [
    "Overview",
    "Operating Model (P&L)",
    "Cashflow & Liquidity",
    "Balance Sheet",
    "Revenue Model",
    "Planning Wizard",
    "Cost Model",
    "Financing Assumptions",
    "Other Assumptions",
    "Financing & Debt",
    "Equity Case",
    "Valuation & Purchase Price",
    "Model Settings",
]


def _render_case_bar(assumptions, current_path, case_options):
    st.markdown("## Case")
    case_col, scenario_col = st.columns([2, 2])
    with case_col:
        st.table([{"Current Case": _case_name(current_path)}])
    with scenario_col:
        scenario = st.selectbox(
            "Scenario View",
            ["Base", "Best", "Worst"],
            index=["Base", "Best", "Worst"].index(assumptions.scenario),
        )
        st.markdown("Applies to input view only.")
        if scenario != assumptions.scenario:
            assumptions = replace(assumptions, scenario=scenario)

    st.markdown("### Case Actions")
    name_col, load_col = st.columns([2, 2])
    with name_col:
        new_case_table = st.data_editor(
            [{"Parameter": "New Case Name", "Value": ""}],
            use_container_width=True,
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
    with button_cols[0]:
        save_pressed = st.button("Save")
    with button_cols[1]:
        save_as_pressed = st.button("Save As")
    with button_cols[2]:
        load_pressed = st.button("Load Selected Case")
    with button_cols[3]:
        reset_pressed = st.button("Reset to Base")

    actions = {
        "save": save_pressed,
        "save_as": save_as_pressed,
        "load": load_pressed,
        "reset": reset_pressed,
        "load_choice": load_choice,
        "new_case_name": new_case_name,
    }
    st.markdown("---")
    return assumptions, actions


def _case_name(path: str) -> str:
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def main() -> None:
    st.set_page_config(page_title="INH Consulting MBO Model", layout="wide")
    if "data_path" not in st.session_state:
        st.session_state["data_path"] = "data/base_case.json"

    st.sidebar.markdown(
        "\n".join(
            [
                "**OVERVIEW**",
                "Overview",
                "",
                "**OPERATING MODEL**",
                "Operating Model (P&L)",
                "Cashflow & Liquidity",
                "Balance Sheet",
                "",
                "**PLANNING (MODEL INPUTS)**",
                "Revenue Model",
                "Planning Wizard",
                "Cost Model",
                "Financing Assumptions",
                "Other Assumptions",
                "",
                "**FINANCING**",
                "Financing & Debt",
                "Equity Case",
                "",
                "**VALUATION**",
                "Valuation & Purchase Price",
                "",
                "**SETTINGS**",
                "Model Settings",
            ]
        )
    )

    page = st.sidebar.selectbox("Navigate", PAGES, index=0, key="page")

    data_path = st.session_state["data_path"]
    original_assumptions = load_assumptions(data_path)
    assumptions = original_assumptions
    base_case = load_assumptions("data/base_case.json")
    case_options = list_cases()
    assumptions, actions = _render_case_bar(assumptions, data_path, case_options)

    if actions["reset"]:
        data_path = "data/base_case.json"
        st.session_state["data_path"] = data_path
        assumptions = load_assumptions(data_path)
    elif actions["load"] and actions["load_choice"] != "Select case...":
        data_path = str(case_path(actions["load_choice"]))
        st.session_state["data_path"] = data_path
        assumptions = load_case(data_path)

    if page == "Revenue Model":
        updated_assumptions = revenue_model.render(assumptions)
    elif page == "Planning Wizard":
        updated_assumptions = planning_wizard.render_inputs(assumptions)
    elif page == "Cost Model":
        updated_assumptions = cost_model.render(assumptions)
    elif page == "Financing Assumptions":
        updated_assumptions = financing_assumptions.render(assumptions)
    elif page == "Other Assumptions":
        updated_assumptions = other_assumptions.render(assumptions)
    else:
        updated_assumptions = assumptions

    if asdict(updated_assumptions) != asdict(original_assumptions):
        save_case(updated_assumptions, data_path)

    if actions["save"]:
        save_case(updated_assumptions, data_path)
    if actions["save_as"] and actions["new_case_name"]:
        new_path = str(case_path(actions["new_case_name"]))
        save_case(updated_assumptions, new_path)
        st.session_state["data_path"] = new_path
        data_path = new_path
    if actions["load_choice"] == "Select case...":
        pass

    result = run_model(updated_assumptions)

    if page == "Overview":
        overview.render(result, updated_assumptions, base_case)
    elif page == "Operating Model (P&L)":
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
    elif page == "Planning Wizard":
        planning_wizard.render_outputs(result)


if __name__ == "__main__":
    main()
