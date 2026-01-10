from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Cashflow & Liquidity")
    st.markdown("Cashflow Assumptions")
    st.table(
        [
            {"Parameter": "Tax Cash Rate", "Value": f"{assumptions.cashflow.tax_cash_rate_pct*100:.1f}%", "Unit": "%", "Notes": "Cash tax rate on EBT."},
            {"Parameter": "Tax Payment Lag", "Value": assumptions.cashflow.tax_payment_lag_years, "Unit": "Years", "Notes": "Timing lag for cash taxes."},
            {"Parameter": "Capex (% of Revenue)", "Value": f"{assumptions.cashflow.capex_pct_revenue*100:.1f}%", "Unit": "%", "Notes": "Capex as % of revenue."},
            {"Parameter": "Working Capital (% of Revenue)", "Value": f"{assumptions.cashflow.working_capital_pct_revenue*100:.1f}%", "Unit": "%", "Notes": "Working capital adjustment."},
            {"Parameter": "Opening Cash Balance", "Value": _format_money(assumptions.cashflow.opening_cash_balance_eur), "Unit": "EUR", "Notes": "Opening cash balance."},
        ]
    )
    st.markdown("---")
    outputs.render_cashflow_liquidity(result)


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.1f} m€"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} k€"
    return f"{value:,.0f} €"
