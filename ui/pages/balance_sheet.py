from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Balance Sheet")
    st.markdown("Balance Sheet Assumptions")
    st.table(
        [
            {"Parameter": "Opening Equity", "Value": _format_money(assumptions.balance_sheet.opening_equity_eur), "Unit": "EUR", "Notes": "Opening equity value."},
            {"Parameter": "Depreciation Rate", "Value": f"{assumptions.balance_sheet.depreciation_rate_pct*100:.1f}%", "Unit": "%", "Notes": "Fixed asset depreciation rate."},
        ]
    )
    st.markdown("---")
    outputs.render_balance_sheet(result)


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.1f} m€"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} k€"
    return f"{value:,.0f} €"
