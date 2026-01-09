from __future__ import annotations

from typing import Dict, List

import streamlit as st

from model.run_model import ModelResult


def render_overview(result: ModelResult) -> None:
    last_year = len(result.revenue["revenue_final_by_year"]) - 1
    st.metric(
        "Year 4 Revenue (EUR)",
        _fmt(result.revenue["revenue_final_by_year"][last_year]),
    )
    st.metric("Year 4 EBITDA (EUR)", _fmt(result.pnl[last_year]["ebitda"]))
    st.metric("Year 4 Net Income (EUR)", _fmt(result.pnl[last_year]["net_income"]))
    st.metric("IRR", f"{result.equity['irr'] * 100:.1f}%")


def render_revenue(result: ModelResult) -> None:
    rows = {
        "Modeled Group Revenue": [
            row["modeled_group_revenue"] for row in result.revenue["components_by_year"]
        ],
        "Modeled External Revenue": [
            row["modeled_external_revenue"] for row in result.revenue["components_by_year"]
        ],
        "Modeled Total Revenue": [
            row["modeled_total_revenue"] for row in result.revenue["components_by_year"]
        ],
        "Group Revenue Floor": [
            row["guaranteed_floor"] for row in result.revenue["components_by_year"]
        ],
        "Group Revenue (after Floor Check)": [
            row["guaranteed_group_revenue"] for row in result.revenue["components_by_year"]
        ],
        "Final Revenue": [
            row["final_total"] for row in result.revenue["components_by_year"]
        ],
    }
    st.dataframe(_year_table(rows), use_container_width=True)


def render_costs(result: ModelResult) -> None:
    rows = {
        "Consultant Costs": [row["consultant_costs"] for row in result.cost],
        "Backoffice Costs": [row["backoffice_costs"] for row in result.cost],
        "Management Costs": [row["management_costs"] for row in result.cost],
        "Personnel Costs": [row["personnel_costs"] for row in result.cost],
        "Overhead + Variable": [row["overhead_and_variable_costs"] for row in result.cost],
        "Total Operating Costs": [row["total_operating_costs"] for row in result.cost],
    }
    st.dataframe(_year_table(rows), use_container_width=True)


def render_pnl(result: ModelResult) -> None:
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


def render_cashflow(result: ModelResult) -> None:
    rows = {
        "EBITDA": [row["ebitda"] for row in result.cashflow],
        "Depreciation": [row["depreciation"] for row in result.cashflow],
        "Taxes Paid": [row["taxes_paid"] for row in result.cashflow],
        "Working Capital Change": [row["working_capital_change"] for row in result.cashflow],
        "Operating CF": [row["operating_cf"] for row in result.cashflow],
        "Capex": [row["capex"] for row in result.cashflow],
        "Acquisition Outflow": [row["acquisition_outflow"] for row in result.cashflow],
        "Free Cashflow": [row["free_cashflow"] for row in result.cashflow],
        "Debt Drawdown": [row["debt_drawdown"] for row in result.cashflow],
        "Equity Injection": [row["equity_injection"] for row in result.cashflow],
        "Interest Paid": [row["interest_paid"] for row in result.cashflow],
        "Debt Repayment": [row["debt_repayment"] for row in result.cashflow],
        "Financing CF": [row["financing_cf"] for row in result.cashflow],
        "Net Cashflow": [row["net_cashflow"] for row in result.cashflow],
        "Cash Balance": [row["cash_balance"] for row in result.cashflow],
    }
    st.dataframe(_year_table(rows), use_container_width=True)


def render_balance_sheet(result: ModelResult) -> None:
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


def render_valuation(result: ModelResult) -> None:
    st.metric("Initial Equity (EUR)", _fmt(result.equity["initial_equity"]))
    st.metric("Enterprise Value (EUR)", _fmt(result.equity["enterprise_value"]))
    st.metric("Net Debt Exit (EUR)", _fmt(result.equity["net_debt_exit"]))
    st.metric("Excess Cash Exit (EUR)", _fmt(result.equity["excess_cash_exit"]))
    st.metric("Exit Value (EUR)", _fmt(result.equity["exit_value"]))
    st.metric("IRR", f"{result.equity['irr'] * 100:.1f}%")

    cashflows = result.equity["equity_cashflows"]
    st.dataframe(_year_table({"Equity Cashflows": cashflows}, years=len(cashflows), start_year=-1))


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
            row[col] = round(value, 2)
        table.append(row)
    return table


def _fmt(value: float) -> str:
    return f"{value:,.0f}"
