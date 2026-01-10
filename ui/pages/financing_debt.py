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
                {"Parameter": "Senior Debt Amount", "Value": _format_amount(assumptions.financing.senior_debt_amount_eur), "Unit": "EUR", "Notes": "Opening senior term loan."},
                {"Parameter": "Interest Rate", "Value": f"{assumptions.financing.interest_rate_pct*100:.1f}", "Unit": "%", "Notes": "Fixed interest rate."},
                {"Parameter": "Amortisation Years", "Value": assumptions.financing.amortization_period_years, "Unit": "Years", "Notes": "Linear amortisation period."},
            ]
        )
    st.markdown("Bank View")
    outputs.render_financing_debt(result, assumptions)
    st.markdown(
        "CFADS = EBITDA - Cash Taxes - Maintenance Capex + Working Capital Change."
    )
    st.markdown(
        "DSCR = CFADS / (Interest Expense + Scheduled Repayment)."
    )
    st.markdown(
        "Peak debt may differ from initial drawdown when repayments occur within Year 0."
    )


def _format_amount(value: float) -> str:
    if value is None:
        return ""
    return f"{value:,.0f}"
