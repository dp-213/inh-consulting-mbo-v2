from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs

YEAR_LABELS = [f"Year {i}" for i in range(5)]


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


def render(result: ModelResult, assumptions: Assumptions) -> None:
    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown("## Cashflow & Liquidity")
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )
    _render_scenario_selector(assumptions.scenario)
    st.markdown(
        '<div class="subtle">Consolidated cashflow statement (5-year plan)</div>',
        unsafe_allow_html=True,
    )
    outputs.render_cashflow_liquidity(result)

    with st.expander("Detailed analysis", expanded=False):
        st.markdown("#### KPI Summary")
        operating_cf = [row["operating_cf"] for row in result.cashflow]
        free_cf = [row["free_cashflow"] for row in result.cashflow]
        ebitda = [row["ebitda"] for row in result.cashflow]
        cash_conversion = [
            outputs._format_percent(free_cf[idx], ebitda[idx])
            for idx in range(len(free_cf))
        ]

        kpi_rows = [
            {
                "KPI": "Operating Cashflow",
                **{YEAR_LABELS[i]: outputs._format_money(operating_cf[i]) for i in range(5)},
            },
            {
                "KPI": "Free Cashflow",
                **{YEAR_LABELS[i]: outputs._format_money(free_cf[i]) for i in range(5)},
            },
            {
                "KPI": "Cash Conversion",
                **{YEAR_LABELS[i]: cash_conversion[i] for i in range(5)},
            },
        ]
        outputs._render_kpi_table_html(kpi_rows, ["KPI"] + YEAR_LABELS)
        st.markdown("#### Cash Volatility")
        cash_balances = [row["cash_balance"] for row in result.cashflow]
        min_cash = min(cash_balances) if cash_balances else 0.0
        max_cash = max(cash_balances) if cash_balances else 0.0
        negative_years = len([value for value in cash_balances if value < 0])
        metric_rows = [
            {"Metric": "Minimum Cash Balance", "Value": outputs._format_money(min_cash)},
            {
                "Metric": "Cash Volatility (Max - Min)",
                "Value": outputs._format_money(max_cash - min_cash),
            },
            {
                "Metric": "Years with Negative Cash",
                "Value": "None" if negative_years == 0 else str(negative_years),
            },
        ]
        outputs._render_kpi_table_html(metric_rows, ["Metric", "Value"])
