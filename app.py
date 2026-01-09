from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from model.run_model import run_model
from state.persistence import load_assumptions, save_assumptions
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
    revenue_model,
    valuation,
)

PAGES = [
    "Overview",
    "Operating Model (P&L)",
    "Cashflow & Liquidity",
    "Balance Sheet",
    "Revenue Model",
    "Cost Model",
    "Financing Assumptions",
    "Other Assumptions",
    "Financing & Debt",
    "Equity Case",
    "Valuation & Purchase Price",
    "Model Settings",
]


def main() -> None:
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
    assumptions = load_assumptions(data_path)

    if page == "Revenue Model":
        updated_assumptions = revenue_model.render(assumptions)
    elif page == "Cost Model":
        updated_assumptions = cost_model.render(assumptions)
    elif page == "Financing Assumptions":
        updated_assumptions = financing_assumptions.render(assumptions)
    elif page == "Other Assumptions":
        updated_assumptions = other_assumptions.render(assumptions)
    else:
        updated_assumptions = assumptions

    if asdict(updated_assumptions) != asdict(assumptions):
        save_assumptions(updated_assumptions, data_path)

    result = run_model(updated_assumptions)

    if page == "Overview":
        overview.render(result)
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


if __name__ == "__main__":
    main()
