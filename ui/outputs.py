from __future__ import annotations

from typing import Dict, List

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions


def render_overview(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("## Deal Summary (IC View)")
    st.markdown(
        "Conservative decision view based on current inputs and selected output scenario."
    )
    st.markdown("---")
    st.markdown("### A. Deal Snapshot (What are we buying and how is it funded?)")

    purchase_price = assumptions.transaction_and_financing.purchase_price_eur
    debt_at_close = assumptions.financing.senior_debt_amount_eur
    equity_at_close = assumptions.transaction_and_financing.equity_contribution_eur
    exit_multiple = assumptions.valuation.seller_multiple
    last_year = len(result.pnl) - 1
    ebitda = result.pnl[0]["ebitda"] if result.pnl else 0.0
    debt_ebitda = debt_at_close / ebitda if ebitda else 0.0

    cols = st.columns(6)
    cols[0].metric("Purchase Price", _format_money(purchase_price))
    cols[1].metric("Debt at Close", _format_money(debt_at_close))
    cols[2].metric("Equity at Close", _format_money(equity_at_close))
    cols[3].metric("Debt/EBITDA", f"{debt_ebitda:.2f}x")
    cols[4].metric("Exit Year", f"Year {last_year}")
    cols[5].metric("Exit Multiple", f"{exit_multiple:.2f}x")

    st.markdown("**Interpretation**")
    st.markdown(
        "- Debt at Close shows the initial borrowing that must be serviced from operating cash.\n"
        "- Equity at Close is the cash contributed by management and investors before debt service begins.\n"
        "- Debt/EBITDA indicates leverage intensity at entry and is monitored against lender limits."
    )


def render_impact_preview(result: ModelResult) -> None:
    last_year = len(result.pnl) - 1
    revenue = result.pnl[last_year]["revenue"]
    ebitda = result.pnl[last_year]["ebitda"]
    fcf = result.cashflow[last_year]["free_cashflow"]
    equity_value = result.equity.get("exit_value", 0.0)
    min_dscr = _min_dscr(result.debt)

    cols = st.columns(5)
    cols[0].metric("Revenue (Year 4)", _format_money(revenue))
    cols[1].metric("Profit Before Depreciation (Year 4)", _format_money(ebitda))
    cols[2].metric("Cash After Investment (Year 4)", _format_money(fcf))
    cols[3].metric("Owner Value", _format_money(equity_value))
    cols[4].metric("Minimum Loan Coverage", f"{min_dscr:.2f}" if min_dscr is not None else "n/a")


def render_driver_summary(current: Assumptions, base: Assumptions) -> None:
    st.markdown("### Key Drivers (This Case vs Base)")
    st.markdown("Comparison uses the Base Case file for the same scenario.")
    scenario = current.scenario
    current_rev = current.revenue.scenarios[scenario]
    base_rev = base.revenue.scenarios[scenario]

    rows = [
        _driver_row("Workdays (Year 0)", current_rev.workdays_per_year[0], base_rev.workdays_per_year[0], "Days"),
        _driver_row("Utilization (Year 0)", current_rev.utilization_rate_pct[0], base_rev.utilization_rate_pct[0], "%"),
        _driver_row("Group Day Rate (Year 0)", current_rev.group_day_rate_eur[0], base_rev.group_day_rate_eur[0], "€"),
        _driver_row("External Day Rate (Year 0)", current_rev.external_day_rate_eur[0], base_rev.external_day_rate_eur[0], "€"),
        _driver_row("Consultant Headcount (Year 0)", current.cost.personnel_by_year[0].consultant_fte, base.cost.personnel_by_year[0].consultant_fte, "People"),
        _driver_row("Consultant Cost (All-in) (Year 0)", current.cost.personnel_by_year[0].consultant_loaded_cost_eur, base.cost.personnel_by_year[0].consultant_loaded_cost_eur, "€"),
        _driver_row("Senior Loan Amount", current.financing.senior_debt_amount_eur, base.financing.senior_debt_amount_eur, "€"),
        _driver_row("Interest Rate", current.financing.interest_rate_pct, base.financing.interest_rate_pct, "%"),
        _driver_row("Purchase Price", current.transaction_and_financing.purchase_price_eur, base.transaction_and_financing.purchase_price_eur, "€"),
        _driver_row("Seller Multiple", current.valuation.seller_multiple, base.valuation.seller_multiple, "x"),
    ]
    st.dataframe(rows, use_container_width=True)


def render_operating_model(result: ModelResult) -> None:
    st.markdown("### Operating Statement (5-Year View)")
    st.markdown("Summary view of operating performance and profitability.")
    last_year = len(result.pnl) - 1
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Revenue (Year 4)", _format_money(result.pnl[last_year]["revenue"]))
    kpi_cols[1].metric("Profit Before Depreciation", _format_money(result.pnl[last_year]["ebitda"]))
    kpi_cols[2].metric("Net Profit", _format_money(result.pnl[last_year]["net_income"]))
    st.markdown("---")
    rows = [
        ("REVENUE", None),
        ("Total Revenue", [row["revenue"] for row in result.pnl]),
        ("", None),
        ("PERSONNEL COSTS", None),
        ("Personnel Costs", [row["personnel_costs"] for row in result.pnl]),
        ("", None),
        ("OPERATING EXPENSES", None),
        ("Operating Expenses", [row["overhead_and_variable_costs"] for row in result.pnl]),
        ("", None),
        ("PROFITABILITY", None),
        ("EBITDA", [row["ebitda"] for row in result.pnl]),
        ("Depreciation", [row["depreciation"] for row in result.pnl]),
        ("EBIT", [row["ebit"] for row in result.pnl]),
        ("Interest Cost", [row["interest_expense"] for row in result.pnl]),
        ("PROFIT BEFORE TAX", [row["ebt"] for row in result.pnl]),
        ("Taxes", [row["taxes"] for row in result.pnl]),
        ("NET INCOME", [row["net_income"] for row in result.pnl]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)


def render_cashflow_liquidity(result: ModelResult) -> None:
    st.markdown("### Cash Flow & Liquidity")
    st.markdown("Cash generation and liquidity profile across the plan.")
    last_year = len(result.cashflow) - 1
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Cash from Operations", _format_money(result.cashflow[last_year]["operating_cf"]))
    kpi_cols[1].metric("Cash After Investment", _format_money(result.cashflow[last_year]["free_cashflow"]))
    kpi_cols[2].metric("Ending Cash", _format_money(result.cashflow[last_year]["cash_balance"]))
    st.markdown("---")
    rows = [
        ("OPERATING CASH FLOW", None),
        ("EBITDA", [row["ebitda"] for row in result.cashflow]),
        ("Taxes Paid", [row["taxes_paid"] for row in result.cashflow]),
        ("Working Capital Change", [row["working_capital_change"] for row in result.cashflow]),
        ("Operating Cashflow", [row["operating_cf"] for row in result.cashflow]),
        ("", None),
        ("INVESTING CASH FLOW", None),
        ("Capex", [row["capex"] for row in result.cashflow]),
        ("Free Cashflow", [row["free_cashflow"] for row in result.cashflow]),
        ("", None),
        ("FINANCING CASH FLOW", None),
        ("Financing Cashflow", [row["financing_cf"] for row in result.cashflow]),
        ("Net Cashflow", [row["net_cashflow"] for row in result.cashflow]),
        ("Closing Cash", [row["cash_balance"] for row in result.cashflow]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)
    st.markdown("---")
    st.table(
        [
            {
                "Note": (
                    "Liquidity reflects operating cash generation after tax and cash tied in operations, "
                    "then loan payments and financing flows."
                )
            }
        ]
    )


def render_balance_sheet(result: ModelResult) -> None:
    st.markdown("### Balance Sheet")
    st.markdown("Year-end asset, liability, and owner capital position.")
    last_year = len(result.balance_sheet) - 1
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Assets", _format_money(result.balance_sheet[last_year]["total_assets"]))
    kpi_cols[1].metric("Loan Balance", _format_money(result.balance_sheet[last_year]["financial_debt"]))
    kpi_cols[2].metric("Owner Capital End", _format_money(result.balance_sheet[last_year]["equity_end"]))
    st.markdown("---")
    rows = [
        ("ASSETS", None),
        ("Cash", [row["cash"] for row in result.balance_sheet]),
        ("Fixed Assets (Net)", [row["fixed_assets"] for row in result.balance_sheet]),
        ("Acquisition Intangible", [row["acquisition_intangible"] for row in result.balance_sheet]),
        ("Working Capital", [row["working_capital"] for row in result.balance_sheet]),
        ("TOTAL ASSETS", [row["total_assets"] for row in result.balance_sheet]),
        ("", None),
        ("LIABILITIES", None),
        ("Financial Debt", [row["financial_debt"] for row in result.balance_sheet]),
        ("Taxes Payable", [row["tax_payable"] for row in result.balance_sheet]),
        ("TOTAL LIABILITIES", [row["total_liabilities"] for row in result.balance_sheet]),
        ("", None),
        ("EQUITY", None),
        ("Equity at Start of Year", [row["equity_end"] for row in result.balance_sheet]),
        ("TOTAL LIABILITIES + EQUITY", [row["total_liabilities_equity"] for row in result.balance_sheet]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)
    st.markdown("---")
    st.markdown("### KPI Summary")
    st.table(
        [
            {"Metric": "Total Assets (Year 4)", "Value": _format_money(result.balance_sheet[last_year]["total_assets"])},
            {"Metric": "Total Liabilities (Year 4)", "Value": _format_money(result.balance_sheet[last_year]["total_liabilities"])},
            {"Metric": "Equity (Year 4)", "Value": _format_money(result.balance_sheet[last_year]["equity_end"])},
        ]
    )


def render_financing_debt(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("### Loan Schedule (5-Year View)")
    st.markdown("Loan evolution, payments, and coverage health by year.")
    st.markdown("Bank View")
    coverage = [row.get("dscr", 0.0) for row in result.debt]
    debt_service = [
        row["interest_expense"] + row["total_repayment"] for row in result.debt
    ]
    cfads = [
        result.cashflow[i]["free_cashflow"]
        if i < len(result.cashflow)
        else 0.0
        for i in range(len(result.debt))
    ]
    rows = [
        ("EBITDA", [row["ebitda"] for row in result.cashflow]),
        ("Cash Taxes", [row["taxes_paid"] for row in result.cashflow]),
        ("Capex (Maintenance)", [row["capex"] for row in result.cashflow]),
        ("Working Capital Change", [row["working_capital_change"] for row in result.cashflow]),
        ("CFADS", cfads),
        ("Interest Expense", [row["interest_expense"] for row in result.debt]),
        ("Scheduled Repayment", [row["total_repayment"] for row in result.debt]),
        ("Debt Service", debt_service),
        ("DSCR", [f"{value:.2f}" for value in coverage]),
        ("Minimum Required DSCR", [f"{assumptions.financing.minimum_dscr:.2f}" for _ in result.debt]),
        ("Covenant Breach", ["YES" if row.get("covenant_breach") else "NO" for row in result.debt]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)
    st.markdown("---")
    st.table(
        [
            {
                "Footnote": (
                    "Loan coverage uses operating cash flow less capital spend divided by loan payments. "
                    "Flags indicate coverage below the minimum threshold."
                )
            }
        ]
    )


def render_equity_case(result: ModelResult) -> None:
    st.markdown("### Capital at Risk (Entry View)")
    initial_equity = result.equity.get("initial_equity", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)
    moic = exit_value / initial_equity if initial_equity else 0.0

    st.table(
        [
            {"Line Item": "Total Equity", "Equity (EUR)": _format_money(initial_equity), "Ownership (%)": "100.0%"}
        ]
    )

    st.markdown("### Headline Outcomes")
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Investor Investment", _format_money(initial_equity))
    kpi_cols[1].metric("Investor Proceeds", _format_money(exit_value))
    kpi_cols[2].metric("Investor Multiple", f"{moic:.2f}x")
    kpi_cols[3].metric("Investor IRR", f"{result.equity.get('irr', 0.0) * 100:.1f}%")

    st.dataframe(
        _year_table(
            {"Equity Cashflows": result.equity.get("equity_cashflows", [])},
            years=len(result.equity.get("equity_cashflows", [])),
            start_year=-1,
        ),
        use_container_width=True,
    )


def render_valuation(result: ModelResult) -> None:
    st.markdown("### Purchase Price & Exit")
    st.markdown("Owner value bridge from business value to exit proceeds.")
    enterprise_value = result.equity.get("enterprise_value", 0.0)
    net_debt_exit = result.equity.get("net_debt_exit", 0.0)
    excess_cash = result.equity.get("excess_cash_exit", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Seller Equity Value", _format_money(enterprise_value))
    kpi_cols[1].metric("Buyer Affordability", _format_money(exit_value))
    gap = exit_value - enterprise_value
    kpi_cols[2].metric("Gap (EUR)", _format_money(gap))

    st.dataframe(
        [
            {"Line Item": "Business Value", "Amount": _format_money(enterprise_value)},
            {"Line Item": "Loan Balance minus Cash at Exit", "Amount": _format_money(-net_debt_exit)},
            {"Line Item": "Excess Cash", "Amount": _format_money(excess_cash)},
            {"Line Item": "Owner Value", "Amount": _format_money(exit_value)},
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
        row = {"Line Item": row_name}
        for year_index in range(years):
            year = start_year + year_index
            if year == 0:
                col = "Year 0 (Entry)"
            else:
                col = f"Year {year}"
            value = values[year_index] if year_index < len(values) else 0.0
            row[col] = _format_table_value(value)
        table.append(row)
    return table


def _statement_table(
    rows: List[tuple[str, List[float] | List[str] | None]],
    years: int = 5,
    start_year: int = 0,
) -> List[dict]:
    table = []
    for label, values in rows:
        row = {"Line Item": label}
        for year_index in range(years):
            year = start_year + year_index
            col = "Year 0 (Entry)" if year == 0 else f"Year {year}"
            if values is None:
                row[col] = ""
            else:
                value = values[year_index] if year_index < len(values) else ""
                row[col] = _format_table_value(value)
        table.append(row)
    return table


def render_input_summary(result: ModelResult) -> None:
    st.markdown("---")
    st.markdown("### Summary (Read-Only)")
    st.markdown("This summary reflects the inputs above for the current case.")
    last_year = len(result.pnl) - 1
    min_dscr = _min_dscr(result.debt)
    summary_rows = [
        {"Metric": "Revenue (Year 4)", "Value": _format_money(result.pnl[last_year]["revenue"]), "Unit": "€"},
        {
            "Metric": "Profit Before Depreciation (Year 4)",
            "Value": _format_money(result.pnl[last_year]["ebitda"]),
            "Unit": "€",
        },
        {"Metric": "Net Profit (Year 4)", "Value": _format_money(result.pnl[last_year]["net_income"]), "Unit": "€"},
        {
            "Metric": "Cash After Investment (Year 4)",
            "Value": _format_money(result.cashflow[last_year]["free_cashflow"]),
            "Unit": "€",
        },
        {
            "Metric": "Minimum Loan Coverage",
            "Value": f"{min_dscr:.2f}" if min_dscr is not None else "n/a",
            "Unit": "x",
        },
    ]
    st.table(summary_rows)


def _min_dscr(debt_schedule: List[dict]) -> float | None:
    dscr_values = [row.get("dscr") for row in debt_schedule if row.get("dscr") is not None]
    if not dscr_values:
        return None
    return min(dscr_values)


def _fmt(value: float) -> str:
    return _format_money(value)


def _driver_row(name: str, current: float, base: float, unit: str) -> dict:
    delta = current - base
    return {
        "Driver": name,
        "Current": _format_driver_value(current, unit),
        "Base": _format_driver_value(base, unit),
        "Delta": _format_delta(delta, unit),
        "Unit": unit,
    }


def _format_driver_value(value: float, unit: str) -> str:
    if unit in {"%", "% p.a."}:
        return f"{value:.1%}"
    if unit == "x":
        return f"{value:.2f}x"
    if unit == "€":
        return _format_money(value)
    return f"{value:,.2f}"


def _format_delta(value: float, unit: str) -> str:
    sign = "+" if value > 0 else ""
    if unit in {"%", "% p.a."}:
        return f"{sign}{value:.1%}"
    if unit == "x":
        return f"{sign}{value:.2f}x"
    if unit == "€":
        return f"{sign}{_format_money(value)}"
    return f"{sign}{value:,.2f}"


def _format_table_value(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return _format_money(value)
    return "0.00"


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.1f} m€"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} k€"
    return f"{value:,.0f} €"
