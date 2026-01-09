from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from model.run_model import run_model
from state.persistence import load_assumptions, save_assumptions
from ui import inputs
from ui.pages import balance_sheet, cashflow, overview, pnl, valuation


def main() -> None:
    if "data_path" not in st.session_state:
        st.session_state["data_path"] = "data/base_case.json"

    page = st.selectbox(
        "Page",
        ["Overview", "P&L", "Cashflow", "Balance Sheet", "Valuation"],
        index=0,
        key="page",
    )

    data_path = st.session_state["data_path"]
    assumptions = load_assumptions(data_path)
    updated_assumptions = inputs.render_inputs(assumptions)

    if asdict(updated_assumptions) != asdict(assumptions):
        save_assumptions(updated_assumptions, data_path)

    result = run_model(updated_assumptions)

    if page == "Overview":
        overview.render(result)
    elif page == "P&L":
        pnl.render(result)
    elif page == "Cashflow":
        cashflow.render(result)
    elif page == "Balance Sheet":
        balance_sheet.render(result)
    else:
        valuation.render(result)


if __name__ == "__main__":
    main()
