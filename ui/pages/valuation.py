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
                {"Parameter": "Purchase Price", "Value": _format_amount(assumptions.transaction_and_financing.purchase_price_eur), "Unit": "EUR", "Notes": "Seller equity value."},
                {"Parameter": "Seller Multiple (x EBITDA)", "Value": f"{assumptions.valuation.seller_multiple:.2f}", "Unit": "x", "Notes": "Exit multiple on EBITDA."},
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
        st.markdown(
            "Buyer view is based on discounted free cashflow and explicitly allows for negative equity values if pricing is too high."
        )
        discount_rate = assumptions.financing.interest_rate_pct
        free_cashflow = [row["free_cashflow"] for row in result.cashflow]
        discount_factors = [
            1 / ((1 + discount_rate) ** year) for year in range(len(free_cashflow))
        ]
        pv_cashflow = [
            free_cashflow[i] * discount_factors[i] for i in range(len(free_cashflow))
        ]
        cumulative_pv = []
        running = 0.0
        for value in pv_cashflow:
            running += value
            cumulative_pv.append(running)

        net_debt_exit = result.equity.get("net_debt_exit", 0.0)

        table = [
            _year_row("Free Cashflow", free_cashflow),
            _year_row("Discount Factor", [f"{value:.2f}" for value in discount_factors], raw=True),
            _year_row("Present Value of FCF", pv_cashflow),
            _year_row("Cumulative PV of FCF", cumulative_pv),
            _year_row("PV of FCF (no terminal)", cumulative_pv),
            _year_row("Net Debt at Close", ["", "", "", "", net_debt_exit], raw=True),
        ]
        st.dataframe(table, use_container_width=True)


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.2f} m EUR"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.2f} k EUR"
    return f"{value:,.0f} EUR"


def _format_amount(value: float) -> str:
    if value is None:
        return ""
    return f"{value:,.0f}"


def _year_row(label: str, values: list, raw: bool = False) -> dict:
    row = {"Line Item": label}
    for idx in range(5):
        value = values[idx] if idx < len(values) else ""
        if raw:
            row[f"Year {idx}"] = value if isinstance(value, str) else _format_money(value)
        else:
            row[f"Year {idx}"] = _format_money(value) if value != "" else ""
    return row
