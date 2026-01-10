from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def _case_name(path: str) -> str:
    if not path:
        return "Unnamed Case"
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def _render_scenario_selector(current: str) -> None:
    options = ["Worst", "Base", "Best"]
    if "view_scenario" not in st.session_state:
        st.session_state["view_scenario"] = current
    current_value = st.session_state["view_scenario"]
    if current_value not in options:
        current_value = current
    st.radio(
        "Scenario",
        options,
        index=options.index(current_value),
        horizontal=True,
        key="view_scenario",
        label_visibility="collapsed",
    )


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown("# Balance Sheet")
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_balance_sheet_key_assumptions(
            assumptions, "balance.assumptions"
        )
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )
    _render_scenario_selector(assumptions.scenario)
    output_container = st.container()
    updated_result = run_model(updated_assumptions)
    net_debt = [
        row["financial_debt"] - row["cash"] for row in updated_result.balance_sheet
    ]
    equity_ratio = [
        (row["equity_end"] / row["total_assets"]) if row["total_assets"] else 0.0
        for row in updated_result.balance_sheet
    ]
    ebitda = [row["ebitda"] for row in updated_result.pnl]
    net_debt_ebitda = [
        (net_debt[idx] / ebitda[idx]) if ebitda[idx] else 0.0
        for idx in range(len(net_debt))
    ]
    year_labels = [f"Year {i}" for i in range(5)]
    kpi_rows = [
        {
            "Metric": "Net Debt",
            **{year_labels[i]: outputs._format_money(net_debt[i]) for i in range(5)},
        },
        {
            "Metric": "Equity Ratio",
            **{year_labels[i]: f"{equity_ratio[i] * 100:.1f}%" for i in range(5)},
        },
        {
            "Metric": "Net Debt / EBITDA",
            **{year_labels[i]: f"{net_debt_ebitda[i]:.2f}x" for i in range(5)},
        },
    ]
    with output_container:
        st.markdown(
            f'<div class="subtle">Minimum cash balance assumption: {outputs._format_money(updated_assumptions.balance_sheet.minimum_cash_balance_eur)}. Negative cash indicates a funding gap.</div>',
            unsafe_allow_html=True,
        )
        outputs._render_kpi_table_html(kpi_rows, ["Metric"] + year_labels)
        outputs.render_balance_sheet(updated_result)
    return updated_assumptions
