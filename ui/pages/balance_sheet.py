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


def render(result: ModelResult, assumptions: Assumptions) -> None:
    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown("## Balance Sheet")
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtle">Simplified balance sheet (5-year plan)</div>',
        unsafe_allow_html=True,
    )
    outputs.render_balance_sheet(result)

    with st.expander("Detailed analysis", expanded=False):
        st.markdown("#### KPI Summary")
        net_debt = [
            row["financial_debt"] - row["cash"] for row in result.balance_sheet
        ]
        equity_ratio = [
            (row["equity_end"] / row["total_assets"]) if row["total_assets"] else 0.0
            for row in result.balance_sheet
        ]
        ebitda = [row["ebitda"] for row in result.pnl]
        net_debt_ebitda = [
            (net_debt[idx] / ebitda[idx]) if ebitda[idx] else 0.0
            for idx in range(len(net_debt))
        ]
        cash_headroom = [row["cash_balance"] for row in result.cashflow]

        kpi_rows = [
            {
                "KPI": "Net Debt",
                **{YEAR_LABELS[i]: outputs._format_money(net_debt[i]) for i in range(5)},
            },
            {
                "KPI": "Equity Ratio",
                **{YEAR_LABELS[i]: f"{equity_ratio[i] * 100:.1f}%" for i in range(5)},
            },
            {
                "KPI": "Net Debt / Operating Profit",
                **{YEAR_LABELS[i]: f"{net_debt_ebitda[i]:.2f}x" for i in range(5)},
            },
            {
                "KPI": "Minimum Cash Headroom",
                **{YEAR_LABELS[i]: outputs._format_money(cash_headroom[i]) for i in range(5)},
            },
        ]
        outputs._render_kpi_table_html(kpi_rows, ["KPI"] + YEAR_LABELS)
