from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Equity Case")
    st.markdown(
        "Management Buy-Out with an external minority investor. Holding period defined by the investor exit year. "
        "Exit mechanism: management buys out the investor."
    )
    with st.expander("Equity Assumptions", expanded=True):
        st.table(
            [
                {
                    "Parameter": "Sponsor Equity Contribution",
                    "Value": _format_amount(assumptions.transaction_and_financing.equity_contribution_eur),
                    "Unit": "EUR",
                    "Notes": "Management equity contribution.",
                }
            ]
        )
    outputs.render_equity_case(result, assumptions)


def _format_amount(value: float) -> str:
    if value is None:
        return ""
    return f"{value:,.0f}"
