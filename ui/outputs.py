from __future__ import annotations

from typing import Dict, List

import streamlit as st

from model.run_model import ModelResult


def render_overview(result: ModelResult) -> None:
    st.markdown("### Key KPIs")
    irr = result.equity.get("irr", 0.0)
    initial_equity = result.equity.get("initial_equity", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)
    moic = exit_value / initial_equity if initial_equity else 0.0
    peak_debt = max((row.get("closing_debt", 0.0) for row in result.debt), default=0.0)
    min_dscr = _min_dscr(result.debt)

    st.metric("IRR", f"{irr * 100:.1f}%")
    st.metric("MOIC", f"{moic:.2f}x")
    st.metric("Equity (EUR)", _fmt(initial_equity))
    st.metric("Peak Debt (EUR)", _fmt(peak_debt))
    st.metric("Min DSCR", f"{min_dscr:.2f}" if min_dscr is not None else "n/a")

    st.markdown("### Red Flags")
    breaches = [row for row in result.debt if row.get("covenant_breach")]
    if breaches:
        st.dataframe(
            _year_table(
                {
                    "Covenant Breach": [
                        "Yes" if row.get("covenant_breach") else "No"
                        for row in result.debt
                    ]
                }
            ),
            use_container_width=True,
        )
    else:
        st.table([{"Status": "No covenant breaches in the projection period."}])

    st.markdown("### Narrative")
    st.table(
        [
            {
                "Summary": (
                    "This overview highlights equity returns, leverage pressure, and covenant headroom "
                    "based on the current planning case."
                )
            }
        ]
    )


def render_operating_model(result: ModelResult) -> None:
    st.markdown("### P&L (5-Year View)")
    rows = {
        "Revenue": [row["revenue"] for row in result.pnl],
        "Personnel Costs": [row["personnel_costs"] for row in result.pnl],
        "Overhead + Variable Costs": [row["overhead_and_variable_costs"] for row in result.pnl],
        "EBITDA": [row["ebitda"] for row in result.pnl],
        "Depreciation": [row["depreciation"] for row in result.pnl],
        "EBIT": [row["ebit"] for row in result.pnl],
        "Interest Expense": [row["interest_expense"] for row in result.pnl],
        "EBT": [row["ebt"] for row in result.pnl],
        "Taxes": [row["taxes"] for row in result.pnl],
        "Net Income": [row["net_income"] for row in result.pnl],
    }
    st.dataframe(_year_table(rows), use_container_width=True)


def render_cashflow_liquidity(result: ModelResult) -> None:
    st.markdown("### Cashflow & Liquidity")
    rows = {
        "EBITDA": [row["ebitda"] for row in result.cashflow],
        "Taxes Paid": [row["taxes_paid"] for row in result.cashflow],
        "Working Capital Change": [row["working_capital_change"] for row in result.cashflow],
        "Operating CF": [row["operating_cf"] for row in result.cashflow],
        "Capex": [row["capex"] for row in result.cashflow],
        "Free Cashflow": [row["free_cashflow"] for row in result.cashflow],
        "Financing CF": [row["financing_cf"] for row in result.cashflow],
        "Net Cashflow": [row["net_cashflow"] for row in result.cashflow],
        "Cash Balance": [row["cash_balance"] for row in result.cashflow],
    }
    st.dataframe(_year_table(rows), use_container_width=True)
    st.table(
        [
            {
                "Note": (
                    "Liquidity reflects operating cash generation after tax and working capital, "
                    "then debt service and financing flows."
                )
            }
        ]
    )


def render_balance_sheet(result: ModelResult) -> None:
    st.markdown("### Balance Sheet")
    rows = {
        "Cash": [row["cash"] for row in result.balance_sheet],
        "Fixed Assets": [row["fixed_assets"] for row in result.balance_sheet],
        "Acquisition Intangible": [row["acquisition_intangible"] for row in result.balance_sheet],
        "Working Capital": [row["working_capital"] for row in result.balance_sheet],
        "Total Assets": [row["total_assets"] for row in result.balance_sheet],
        "Financial Debt": [row["financial_debt"] for row in result.balance_sheet],
        "Tax Payable": [row["tax_payable"] for row in result.balance_sheet],
        "Total Liabilities": [row["total_liabilities"] for row in result.balance_sheet],
        "Equity End": [row["equity_end"] for row in result.balance_sheet],
        "Total Liabilities + Equity": [
            row["total_liabilities_equity"] for row in result.balance_sheet
        ],
    }
    st.dataframe(_year_table(rows), use_container_width=True)


def render_financing_debt(result: ModelResult) -> None:
    st.markdown("### Bank View (Debt Schedule)")
    rows = {
        "Opening Debt": [row["opening_debt"] for row in result.debt],
        "Debt Drawdown": [row["debt_drawdown"] for row in result.debt],
        "Interest Expense": [row["interest_expense"] for row in result.debt],
        "Total Repayment": [row["total_repayment"] for row in result.debt],
        "Closing Debt": [row["closing_debt"] for row in result.debt],
        "DSCR": [row.get("dscr", 0.0) for row in result.debt],
        "Covenant Breach": [
            "Yes" if row.get("covenant_breach") else "No" for row in result.debt
        ],
    }
    st.dataframe(_year_table(rows), use_container_width=True)
    st.table(
        [
            {
                "Footnote": (
                    "DSCR uses CFADS (operating CF less capex) divided by debt service. "
                    "Breach flags indicate DSCR below minimum covenant."
                )
            }
        ]
    )


def render_equity_case(result: ModelResult) -> None:
    st.markdown("### Equity Case")
    initial_equity = result.equity.get("initial_equity", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)
    moic = exit_value / initial_equity if initial_equity else 0.0

    st.metric("Initial Equity (EUR)", _fmt(initial_equity))
    st.metric("Exit Value (EUR)", _fmt(exit_value))
    st.metric("IRR", f"{result.equity.get('irr', 0.0) * 100:.1f}%")
    st.metric("MOIC", f"{moic:.2f}x")

    st.dataframe(
        _year_table(
            {"Equity Cashflows": result.equity.get("equity_cashflows", [])},
            years=len(result.equity.get("equity_cashflows", [])),
            start_year=-1,
        ),
        use_container_width=True,
    )


def render_valuation(result: ModelResult) -> None:
    st.markdown("### Valuation & Purchase Price")
    enterprise_value = result.equity.get("enterprise_value", 0.0)
    net_debt_exit = result.equity.get("net_debt_exit", 0.0)
    excess_cash = result.equity.get("excess_cash_exit", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)

    st.dataframe(
        [
            {"Line Item": "Enterprise Value", "Amount (EUR)": enterprise_value},
            {"Line Item": "Net Debt at Exit", "Amount (EUR)": -net_debt_exit},
            {"Line Item": "Excess Cash", "Amount (EUR)": excess_cash},
            {"Line Item": "Equity Value", "Amount (EUR)": exit_value},
        ],
        use_container_width=True,
    )


def _year_table(
    rows: Dict[str, List[float]],
    years: int = 5,
    start_year: int = 0,
) -> List[dict]:
    table = []
    for row_name, values in rows.items():
        row = {"Metric": row_name}
        for year_index in range(years):
            col = f"Year {start_year + year_index}"
            value = values[year_index] if year_index < len(values) else 0.0
            row[col] = round(value, 2) if isinstance(value, (int, float)) else value
        table.append(row)
    return table


def _min_dscr(debt_schedule: List[dict]) -> float | None:
    dscr_values = [row.get("dscr") for row in debt_schedule if row.get("dscr") is not None]
    if not dscr_values:
        return None
    return min(dscr_values)


def _fmt(value: float) -> str:
    return f"{value:,.0f}"
