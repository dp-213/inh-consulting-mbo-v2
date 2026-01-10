from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Equity Case")
    with st.expander("Equity Assumptions", expanded=True):
        st.table(
            [
                {
                    "Parameter": "Sponsor Equity Contribution",
                    "Value": _format_money(assumptions.transaction_and_financing.equity_contribution_eur),
                    "Unit": "EUR",
                    "Notes": "Management equity contribution.",
                }
            ]
        )
    outputs.render_equity_case(result)


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.1f} m€"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} k€"
    return f"{value:,.0f} €"
