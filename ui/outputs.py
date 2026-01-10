from __future__ import annotations

from typing import Dict, List

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions


def render_overview(result: ModelResult) -> None:
    st.markdown("Use the Planning Wizard to update assumptions.")
    st.markdown("### Key KPIs")
    irr = result.equity.get("irr", 0.0)
    initial_equity = result.equity.get("initial_equity", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)
    moic = exit_value / initial_equity if initial_equity else 0.0
    peak_debt = max((row.get("closing_debt", 0.0) for row in result.debt), default=0.0)
    min_dscr = _min_dscr(result.debt)

    kpi_cols = st.columns(5)
    kpi_cols[0].metric("Investor Return (%)", f"{irr * 100:.1f}%")
    kpi_cols[1].metric("Owner Multiple", f"{moic:.2f}x")
    kpi_cols[2].metric("Owner Investment", _format_money(initial_equity))
    kpi_cols[3].metric("Peak Loan Balance", _format_money(peak_debt))
    kpi_cols[4].metric("Minimum Loan Coverage", f"{min_dscr:.2f}" if min_dscr is not None else "n/a")

    st.markdown("---")
    st.markdown("### Red Flags")
    breaches = [row for row in result.debt if row.get("covenant_breach")]
    if breaches:
        st.dataframe(
            _year_table(
                {
                    "Coverage Below Minimum": [
                        "Yes" if row.get("covenant_breach") else "No"
                        for row in result.debt
                    ]
                }
            ),
            use_container_width=True,
        )
    else:
        st.table([{"Status": "No lender limit breaches in the projection period."}])

    st.markdown("---")
    st.markdown("### Narrative")
    st.table(
        [
            {
                "Summary": (
                    "This overview highlights owner returns, debt pressure, and lender limits "
                    "based on the current planning case."
                )
            }
        ]
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
    st.markdown("Use the Planning Wizard to update assumptions.")
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
        ("Revenue", [row["revenue"] for row in result.pnl]),
        ("", None),
        ("PERSONNEL COSTS", None),
        ("Personnel Costs", [row["personnel_costs"] for row in result.pnl]),
        ("", None),
        ("OPERATING COSTS", None),
        ("Overhead + Variable Costs", [row["overhead_and_variable_costs"] for row in result.pnl]),
        ("", None),
        ("PROFITABILITY", None),
        ("PROFIT BEFORE DEPRECIATION", [row["ebitda"] for row in result.pnl]),
        ("Depreciation", [row["depreciation"] for row in result.pnl]),
        ("PROFIT AFTER DEPRECIATION", [row["ebit"] for row in result.pnl]),
        ("Interest Cost", [row["interest_expense"] for row in result.pnl]),
        ("PROFIT BEFORE TAX", [row["ebt"] for row in result.pnl]),
        ("Taxes", [row["taxes"] for row in result.pnl]),
        ("NET PROFIT", [row["net_income"] for row in result.pnl]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)


def render_cashflow_liquidity(result: ModelResult) -> None:
    st.markdown("Use the Planning Wizard to update assumptions.")
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
        ("Profit Before Depreciation", [row["ebitda"] for row in result.cashflow]),
        ("Taxes Paid", [row["taxes_paid"] for row in result.cashflow]),
        ("Cash Tied in Operations", [row["working_capital_change"] for row in result.cashflow]),
        ("Cash from Operations", [row["operating_cf"] for row in result.cashflow]),
        ("", None),
        ("INVESTMENT", None),
        ("Capital Spend", [row["capex"] for row in result.cashflow]),
        ("CASH AFTER INVESTMENT", [row["free_cashflow"] for row in result.cashflow]),
        ("", None),
        ("FINANCING", None),
        ("Cash from Financing", [row["financing_cf"] for row in result.cashflow]),
        ("NET CASH MOVEMENT", [row["net_cashflow"] for row in result.cashflow]),
        ("Cash Balance", [row["cash_balance"] for row in result.cashflow]),
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
    st.markdown("Use the Planning Wizard to update assumptions.")
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
        ("Fixed Assets", [row["fixed_assets"] for row in result.balance_sheet]),
        ("Purchase Intangible", [row["acquisition_intangible"] for row in result.balance_sheet]),
        ("Cash Tied in Operations", [row["working_capital"] for row in result.balance_sheet]),
        ("TOTAL ASSETS", [row["total_assets"] for row in result.balance_sheet]),
        ("", None),
        ("LIABILITIES", None),
        ("Loan Balance", [row["financial_debt"] for row in result.balance_sheet]),
        ("Taxes Payable", [row["tax_payable"] for row in result.balance_sheet]),
        ("TOTAL LIABILITIES", [row["total_liabilities"] for row in result.balance_sheet]),
        ("", None),
        ("OWNER CAPITAL", None),
        ("Owner Capital End", [row["equity_end"] for row in result.balance_sheet]),
        ("TOTAL LIABILITIES + OWNER CAPITAL", [row["total_liabilities_equity"] for row in result.balance_sheet]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)


def render_financing_debt(result: ModelResult) -> None:
    st.markdown("Use the Planning Wizard to update assumptions.")
    st.markdown("### Loan Schedule (5-Year View)")
    st.markdown("Loan evolution, payments, and coverage health by year.")
    last_year = len(result.debt) - 1
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Opening Loan Balance", _format_money(result.debt[0]["opening_debt"]))
    kpi_cols[1].metric("Closing Loan Balance", _format_money(result.debt[last_year]["closing_debt"]))
    min_coverage = _min_dscr(result.debt)
    kpi_cols[2].metric("Minimum Loan Coverage", f"{min_coverage:.2f}" if min_coverage is not None else "n/a")
    st.markdown("---")
    coverage = [f"{row.get('dscr', 0.0):.2f}x" for row in result.debt]
    rows = [
        ("LOAN BALANCE", None),
        ("Opening Loan Balance", [row["opening_debt"] for row in result.debt]),
        ("New Loan", [row["debt_drawdown"] for row in result.debt]),
        ("CLOSING LOAN BALANCE", [row["closing_debt"] for row in result.debt]),
        ("", None),
        ("COSTS & PAYMENTS", None),
        ("Interest Cost", [row["interest_expense"] for row in result.debt]),
        ("TOTAL REPAYMENT", [row["total_repayment"] for row in result.debt]),
        ("", None),
        ("COVERAGE", None),
        ("Loan Coverage", coverage),
        ("Coverage Below Minimum", ["Yes" if row.get("covenant_breach") else "No" for row in result.debt]),
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
    st.markdown("Use the Planning Wizard to update assumptions.")
    st.markdown("### Owner Returns")
    initial_equity = result.equity.get("initial_equity", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)
    moic = exit_value / initial_equity if initial_equity else 0.0

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Owner Investment", _format_money(initial_equity))
    kpi_cols[1].metric("Owner Proceeds", _format_money(exit_value))
    kpi_cols[2].metric("Investor Return (%)", f"{result.equity.get('irr', 0.0) * 100:.1f}%")
    kpi_cols[3].metric("Owner Multiple", f"{moic:.2f}x")

    st.dataframe(
        _year_table(
            {"Owner Cash Flows": result.equity.get("equity_cashflows", [])},
            years=len(result.equity.get("equity_cashflows", [])),
            start_year=-1,
        ),
        use_container_width=True,
    )


def render_valuation(result: ModelResult) -> None:
    st.markdown("Use the Planning Wizard to update assumptions.")
    st.markdown("### Purchase Price & Exit")
    st.markdown("Owner value bridge from business value to exit proceeds.")
    enterprise_value = result.equity.get("enterprise_value", 0.0)
    net_debt_exit = result.equity.get("net_debt_exit", 0.0)
    excess_cash = result.equity.get("excess_cash_exit", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)

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
        row = {"Metric": row_name}
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
        row = {"Metric": label}
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
