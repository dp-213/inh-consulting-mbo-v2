from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Balance Sheet")
    st.markdown("### Balance Sheet Assumptions")
    st.table(
        [
            {"Parameter": "Opening Equity", "Value": _format_amount(assumptions.balance_sheet.opening_equity_eur), "Unit": "EUR", "Notes": "Opening equity value."},
            {"Parameter": "Depreciation Rate", "Value": f"{assumptions.balance_sheet.depreciation_rate_pct*100:.1f}", "Unit": "%", "Notes": "Fixed asset depreciation rate."},
        ]
    )
    st.markdown("Simplified balance sheet (5-year plan)")
    outputs.render_balance_sheet(result)
    last_year = len(result.balance_sheet) - 1
    st.markdown("### KPI Summary")
    st.table(
        [
            {"Metric": "Total Assets (Year 4)", "Value": _format_output_money(result.balance_sheet[last_year]["total_assets"])},
            {"Metric": "Total Liabilities (Year 4)", "Value": _format_output_money(result.balance_sheet[last_year]["total_liabilities"])},
            {"Metric": "Equity (Year 4)", "Value": _format_output_money(result.balance_sheet[last_year]["equity_end"])},
        ]
    )


def _format_amount(value: float) -> str:
    if value is None:
        return ""
    return f"{value:,.0f}"


def _format_output_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.2f} m EUR"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.2f} k EUR"
    return f"{value:,.0f} EUR"
