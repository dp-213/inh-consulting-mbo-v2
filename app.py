from __future__ import annotations

from dataclasses import asdict, replace
import re

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
        "Operating Model (P&L)",
        "Cashflow & Liquidity",
        "Balance Sheet",
    ],
    "PLANNING (MODEL INPUTS)": ["Revenue Model", "Cost Model", "Other Assumptions"],
    "FINANCING": ["Financing & Debt", "Equity Case"],
    "VALUATION": ["Valuation & Purchase Price"],
    "SETTINGS": ["Model Settings", "Case Management", "Model Export / Snapshot"],
}

DEFAULT_PAGE = "Overview"


def _render_sidebar(current_page: str) -> str:
    selected_page = current_page
    st.sidebar.markdown("**MBO Financial Model**")
    for title, options in SECTIONS.items():
        st.sidebar.markdown(f"### {title}")
        for option in options:
            if option == current_page:
                label = f"**▌ {option}**"
            else:
                label = option
            st.sidebar.markdown(f"[{label}](?page={_slug(option)})")
    return selected_page


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _unslug(text: str) -> str:
    return text.replace("-", " ").title()


def _page_from_query() -> str | None:
    params = st.query_params
    raw = params.get("page")
    if not raw:
        return None
    slug = raw if isinstance(raw, str) else raw[0]
    for options in SECTIONS.values():
        for option in options:
            if _slug(option) == slug:
                return option
    return None


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
    query_page = _page_from_query()
    if query_page:
        st.session_state["page"] = query_page
    page = _render_sidebar(st.session_state["page"])
    st.session_state["page"] = page

    data_path = st.session_state["data_path"]
    original_assumptions = load_assumptions(data_path)
    assumptions = original_assumptions
    base_case = load_assumptions("data/base_case.json")
    case_options = list_cases()

    st.markdown("# Financial Model")

    output_pages = {
        "Overview",
        "Operating Model (P&L)",
        "Cashflow & Liquidity",
        "Balance Sheet",
        "Financing & Debt",
        "Equity Case",
        "Valuation & Purchase Price",
    }

    if page in {"Revenue Model", "Cost Model", "Other Assumptions"}:
        st.markdown("Percent inputs use whole numbers (70 = 70%).")
        scenario = st.radio(
            "Scenario",
            ["Worst", "Base", "Best"],
            index=["Worst", "Base", "Best"].index(assumptions.scenario),
            horizontal=True,
        )
        if scenario != assumptions.scenario:
            assumptions = replace(assumptions, scenario=scenario)
        st.markdown("---")
    elif page in output_pages:
        st.markdown(f"Scenario being viewed: {assumptions.scenario}")
        st.markdown("---")

    if page == "Revenue Model":
        updated_assumptions = revenue_model.render(assumptions)
    elif page == "Cost Model":
        updated_assumptions = cost_model.render(assumptions)
    elif page == "Other Assumptions":
        updated_assumptions = other_assumptions.render(assumptions)
    else:
        updated_assumptions = assumptions

    if data_path.endswith("base_case.json") and asdict(updated_assumptions) != asdict(original_assumptions):
        st.markdown("Base Case is read-only. Use Case Management to create a copy.")
    elif asdict(updated_assumptions) != asdict(original_assumptions):
        save_case(updated_assumptions, data_path)

    result = run_model(updated_assumptions)

    if page == "Overview":
        overview.render(result, updated_assumptions, base_case)
    elif page == "Operating Model (P&L)":
        pnl.render(result)
    elif page == "Cashflow & Liquidity":
        cashflow.render(result, updated_assumptions)
    elif page == "Balance Sheet":
        balance_sheet.render(result, updated_assumptions)
    elif page == "Financing & Debt":
        financing_debt.render(result, updated_assumptions)
    elif page == "Equity Case":
        equity_case.render(result, updated_assumptions)
    elif page == "Valuation & Purchase Price":
        valuation.render(result, updated_assumptions)
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
