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
    "ANALYSIS": [
        "Overview",
        "Operating Model (P&L)",
        "Cashflow & Liquidity",
        "Balance Sheet",
        "Valuation & Purchase Price",
    ],
    "PLANNING": ["Revenue Model", "Cost Model", "Other Assumptions"],
    "FINANCING": ["Financing & Debt", "Equity Case"],
    "SETTINGS": ["Case Management", "Model Settings", "Model Export"],
}

DEFAULT_PAGE = "Overview"
NAV_PAGES = [page for pages in SECTIONS.values() for page in pages]
NAV_ICONS = {
    "Overview": "🏠",
    "Operating Model (P&L)": "📊",
    "Cashflow & Liquidity": "💧",
    "Balance Sheet": "🧾",
    "Valuation & Purchase Price": "💼",
    "Revenue Model": "🧮",
    "Cost Model": "🧱",
    "Other Assumptions": "🧩",
    "Financing & Debt": "🏦",
    "Equity Case": "🤝",
    "Case Management": "🗂️",
    "Model Settings": "⚙️",
    "Model Export": "📤",
}


def _render_sidebar(current_page: str) -> str:
    st.sidebar.markdown(
        '<div class="sidebar-title">MBO Financial Model</div>',
        unsafe_allow_html=True,
    )
    if "page" not in st.session_state:
        st.session_state["page"] = current_page
    for section, pages in SECTIONS.items():
        st.sidebar.markdown(
            f'<div class="nav-section">{section}</div>',
            unsafe_allow_html=True,
        )
        for page in pages:
            is_active = st.session_state["page"] == page
            icon = NAV_ICONS.get(page, "•")
            label = f"{icon} {page}"
            if st.sidebar.button(
                label,
                key=f"nav-{page}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["page"] = page
    return st.session_state["page"]


def _inject_base_styles() -> None:
    st.markdown(
        """
        <style>
          [data-testid="stAppViewContainer"] {
            background: #ffffff;
          }
          [data-testid="stSidebar"],
          [data-testid="stSidebarContent"] {
            background: #f6f6f8;
            color: #111827;
          }
          [data-testid="stSidebar"] {
            min-width: 260px;
            max-width: 260px;
          }
          [data-testid="stSidebarContent"] {
            padding: 0.75rem 0.6rem 0.9rem;
          }
          [data-testid="stSidebar"] .sidebar-title {
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            color: #0f172a;
            margin: 0.15rem 0 0.85rem;
            padding-left: 0.4rem;
          }
          [data-testid="stSidebar"] .nav-section {
            font-size: 0.6rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: #6b7280;
            font-weight: 600;
            margin: 0.75rem 0 0.25rem;
            padding-left: 0.45rem;
            }
          [data-testid="stSidebar"] .stButton > button {
            justify-content: flex-start;
            border: none;
            padding: 0.3rem 0.5rem;
            border-radius: 8px;
            margin: 0.1rem 0;
            color: #0f172a;
            background: transparent;
            font-size: 0.82rem;
            line-height: 1.2;
            min-height: 30px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.45rem;
          }
          [data-testid="stSidebar"] .stButton > button:hover {
            background: #e9edf3;
          }
          [data-testid="stSidebar"] [data-testid="baseButton-primary"] > button {
            background: #e4e9f2;
            border-left: 3px solid #1f2937;
            font-weight: 600;
            color: #0b1220;
            padding-left: 0.45rem;
            box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.35);
          }
          [data-testid="stSidebar"] [data-testid="baseButton-primary"] > button:hover {
            background: #dbe2ec;
          }
          [data-testid="stRadio"] {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            padding: 0.25rem 0.6rem;
            border-radius: 8px;
            margin: 0.25rem 0 0.8rem;
          }
          [data-testid="stRadio"] [role="radiogroup"] {
            gap: 0.45rem;
          }
          [data-testid="stRadio"] label {
            font-size: 0.78rem;
            color: #4b5563;
          }
          .statement-table,
          .kpi-table,
          .input-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
          }
          .statement-table th,
          .statement-table td,
          .kpi-table th,
          .kpi-table td,
          .input-table th,
          .input-table td {
            padding: 0.2rem 0.45rem;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: middle;
          }
          .statement-table thead th,
          .kpi-table thead th,
          .input-table thead th {
            text-align: left;
            font-weight: 600;
            color: #374151;
            background: #f6f7f9;
          }
          .statement-table td:not(:first-child),
          .kpi-table td:not(:first-child),
          .input-table td:not(:first-child),
          .statement-table th:not(:first-child),
          .kpi-table th:not(:first-child),
          .input-table th:not(:first-child) {
            text-align: right;
          }
          .statement-table th:nth-child(2),
          .statement-table td:nth-child(2),
          .year-table th:nth-child(2),
          .year-table td:nth-child(2),
          .input-table th:nth-child(3),
          .input-table td:nth-child(3) {
            background: #f3f4f6;
          }
          .statement-table th:first-child,
          .statement-table td:first-child {
            width: 40%;
          }
          .statement-table th:not(:first-child),
          .statement-table td:not(:first-child) {
            width: 12%;
          }
          .statement-table .section td {
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6b7280;
            border-bottom: none;
            padding-top: 0.55rem;
            background: #f8fafc;
          }
          .statement-table .spacer td {
            border-bottom: none;
            padding: 0.25rem 0;
          }
          .input-table .section td {
            font-weight: 600;
            text-transform: uppercase;
            color: #6b7280;
            border-bottom: none;
            padding-top: 0.5rem;
            background: #f8fafc;
          }
          .input-table .spacer td {
            border-bottom: none;
            padding: 0.25rem 0;
          }
          .statement-table .total td {
            font-weight: 600;
            background: #f8fafc;
            border-top: 1px solid #d1d5db;
            padding-top: 0.45rem;
          }
          .statement-table .kpi-divider td {
            border-top: 1px solid #e5e7eb;
            padding: 0.35rem 0;
          }
          .statement-table .kpi-row td {
            color: #6b7280;
            font-size: 0.74rem;
          }
          .statement-table .kpi-section td {
            border-top: 1px solid #e5e7eb;
            color: #9ca3af;
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding-top: 0.35rem;
            padding-bottom: 0.2rem;
            background: transparent;
          }
          .subtle {
            color: #6b7280;
            font-size: 0.9rem;
          }
          .hint-text {
            color: #9ca3af;
            font-size: 0.75rem;
          }
          .metric-grid {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 1.4rem;
            margin: 0.5rem 0 1rem;
          }
          .metric-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1.4rem;
            margin: 0.4rem 0 1.1rem;
          }
          .metric-item-label {
            font-size: 0.8rem;
            color: #6b7280;
            text-transform: none;
          }
          .metric-item-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #111827;
          }
          .assumption-bar {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.45rem 0.75rem;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            color: #374151;
            font-size: 0.85rem;
            margin: 0.3rem 0 1rem;
          }
          .assumption-bar .chevron {
            font-size: 0.9rem;
            color: #6b7280;
          }
          .callout-bar {
            background: #eef2ff;
            color: #1f2937;
            border-radius: 6px;
            padding: 0.55rem 0.8rem;
            font-size: 0.82rem;
            margin: 0.3rem 0 0.8rem;
          }
          .page-indicator {
            color: #6b7280;
            font-size: 0.85rem;
            margin-bottom: 0.9rem;
          }
          .info-box {
            background: #f3f4f6;
            border-radius: 8px;
            padding: 0.9rem 1.1rem;
            color: #111827;
            font-size: 0.85rem;
            margin-bottom: 1rem;
          }
          .info-box h4 {
            margin: 0.6rem 0 0.2rem;
            font-size: 0.85rem;
          }
          .info-box ul {
            margin: 0.2rem 0 0.4rem 1rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _case_name(path: str) -> str:
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def _get_view_scenario(current: str) -> str:
    if "view_scenario" not in st.session_state:
        st.session_state["view_scenario"] = current
    return st.session_state["view_scenario"]


def main() -> None:
    st.set_page_config(page_title="INH Consulting MBO Model", layout="wide")
    _inject_base_styles()
    if "data_path" not in st.session_state:
        st.session_state["data_path"] = "data/base_case.json"

    if "page" not in st.session_state:
        st.session_state["page"] = DEFAULT_PAGE
    page = _render_sidebar(st.session_state["page"])
    st.session_state["page"] = page

    data_path = st.session_state["data_path"]
    original_assumptions = load_assumptions(data_path)
    assumptions = original_assumptions
    case_options = list_cases()

    # Page titles are rendered by each view.

    view_only_scenario_pages = {
        "Overview",
        "Operating Model (P&L)",
        "Cashflow & Liquidity",
        "Balance Sheet",
        "Valuation & Purchase Price",
    }
    analysis_pages = {
        "Overview",
        "Operating Model (P&L)",
        "Cashflow & Liquidity",
        "Balance Sheet",
        "Valuation & Purchase Price",
    }

    view_assumptions = assumptions
    if page in view_only_scenario_pages:
        scenario = _get_view_scenario(assumptions.scenario)
        if scenario not in {"Worst", "Base", "Best"}:
            scenario = assumptions.scenario
        if scenario != assumptions.scenario:
            view_assumptions = replace(assumptions, scenario=scenario)

    if page == "Revenue Model":
        updated_assumptions = revenue_model.render(assumptions)
    elif page == "Cost Model":
        updated_assumptions = cost_model.render(assumptions)
    elif page == "Other Assumptions":
        updated_assumptions = other_assumptions.render(assumptions)
    else:
        updated_assumptions = assumptions

    can_persist = page in {"Revenue Model", "Cost Model", "Other Assumptions", "Case Management"}
    if (
        can_persist
        and data_path.endswith("base_case.json")
        and asdict(updated_assumptions) != asdict(original_assumptions)
    ):
        pass
    elif can_persist and asdict(updated_assumptions) != asdict(original_assumptions):
        save_case(updated_assumptions, data_path)

    result = run_model(
        view_assumptions if page in view_only_scenario_pages else updated_assumptions
    )

    if page == "Overview":
        overview.render(result, assumptions)
    elif page == "Operating Model (P&L)":
        pnl.render(result, view_assumptions)
    elif page == "Cashflow & Liquidity":
        cashflow.render(result, view_assumptions)
    elif page == "Balance Sheet":
        balance_sheet.render(result, view_assumptions)
    elif page == "Financing & Debt":
        financing_debt.render(result, view_assumptions)
    elif page == "Equity Case":
        equity_case.render(result, view_assumptions)
    elif page == "Valuation & Purchase Price":
        valuation.render(result, view_assumptions)
    elif page == "Model Settings":
        model_settings.render(data_path)
    elif page == "Case Management":
        case_actions = case_management.render(updated_assumptions, data_path, case_options)
        scenario = case_actions["scenario"]
        if scenario != updated_assumptions.scenario:
            updated_assumptions = replace(updated_assumptions, scenario=scenario)
            if not data_path.endswith("base_case.json"):
                save_case(updated_assumptions, data_path)
        if case_actions["reset"]:
            data_path = "data/base_case.json"
            st.session_state["data_path"] = data_path
            updated_assumptions = load_assumptions(data_path)
        elif case_actions["load"] and case_actions["load_choice"] != "Select case...":
            load_choice = str(case_actions["load_choice"])
            if load_choice.endswith(".json") and ("/" in load_choice or load_choice.startswith("data")):
                data_path = load_choice
            else:
                data_path = str(case_path(load_choice))
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
    elif page == "Model Export":
        model_export.render(updated_assumptions, result)


if __name__ == "__main__":
    main()
