from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Valuation & Purchase Price")
    st.markdown(
        "This page compares seller expectations with a conservative buyer view. "
        "The buyer view focuses on cash generation, financing constraints, and downside risk."
    )
    with st.expander("Valuation Assumptions", expanded=True):
        st.table(
            [
                {"Parameter": "Purchase Price", "Value": _format_money(assumptions.transaction_and_financing.purchase_price_eur), "Unit": "EUR", "Notes": "Seller equity value."},
                {"Parameter": "Seller Multiple (x EBITDA)", "Value": f"{assumptions.valuation.seller_multiple:.2f}x", "Unit": "x", "Notes": "Exit multiple on EBITDA."},
            ]
        )
    st.markdown(
        "Net Debt at Close is taken from the Debt Schedule (Year 0: Closing Debt)."
    )
    outputs.render_valuation(result)

    with st.expander("Seller Valuation (Multiple-Based)", expanded=False):
        st.table(
            [
                {"Metric": "Seller Equity Value", "Value": _format_money(assumptions.transaction_and_financing.purchase_price_eur)},
                {"Metric": "Seller Multiple", "Value": f"{assumptions.valuation.seller_multiple:.2f}x"},
            ]
        )

    with st.expander("Buyer Valuation (Cash-Based)", expanded=False):
        st.table(
            [
                {
                    "Line Item": "Free Cashflow",
                    "Year 0": _format_money(result.cashflow[0]["free_cashflow"]),
                    "Year 1": _format_money(result.cashflow[1]["free_cashflow"]),
                    "Year 2": _format_money(result.cashflow[2]["free_cashflow"]),
                    "Year 3": _format_money(result.cashflow[3]["free_cashflow"]),
                    "Year 4": _format_money(result.cashflow[4]["free_cashflow"]),
                }
            ]
        )


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.1f} m€"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} k€"
    return f"{value:,.0f} €"
