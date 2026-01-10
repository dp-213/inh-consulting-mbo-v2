from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Financing & Debt")
    st.markdown("Debt structure, service and bankability (5-year plan)")
    with st.expander("Financing Assumptions", expanded=True):
        st.table(
            [
                {"Parameter": "Senior Debt Amount", "Value": _format_money(assumptions.financing.senior_debt_amount_eur), "Unit": "EUR", "Notes": "Opening senior term loan."},
                {"Parameter": "Interest Rate", "Value": f"{assumptions.financing.interest_rate_pct*100:.1f}%", "Unit": "%", "Notes": "Fixed interest rate."},
                {"Parameter": "Amortisation Years", "Value": assumptions.financing.amortization_period_years, "Unit": "Years", "Notes": "Linear amortisation period."},
            ]
        )
    outputs.render_financing_debt(result, assumptions)


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.1f} m€"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} k€"
    return f"{value:,.0f} €"
