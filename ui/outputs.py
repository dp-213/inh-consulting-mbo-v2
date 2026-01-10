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
    st.markdown(f"Scenario being viewed: {assumptions.scenario}")
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
        _driver_row("Group Day Rate (Year 0)", current_rev.group_day_rate_eur[0], base_rev.group_day_rate_eur[0], "EUR"),
        _driver_row("External Day Rate (Year 0)", current_rev.external_day_rate_eur[0], base_rev.external_day_rate_eur[0], "EUR"),
        _driver_row("Consultant Headcount (Year 0)", current.cost.personnel_by_year[0].consultant_fte, base.cost.personnel_by_year[0].consultant_fte, "People"),
        _driver_row("Consultant Cost (All-in) (Year 0)", current.cost.personnel_by_year[0].consultant_loaded_cost_eur, base.cost.personnel_by_year[0].consultant_loaded_cost_eur, "EUR"),
        _driver_row("Senior Loan Amount", current.financing.senior_debt_amount_eur, base.financing.senior_debt_amount_eur, "EUR"),
        _driver_row("Interest Rate", current.financing.interest_rate_pct, base.financing.interest_rate_pct, "%"),
        _driver_row("Purchase Price", current.transaction_and_financing.purchase_price_eur, base.transaction_and_financing.purchase_price_eur, "EUR"),
        _driver_row("Seller Multiple", current.valuation.seller_multiple, base.valuation.seller_multiple, "x"),
    ]
    st.dataframe(rows, use_container_width=True)


def render_operating_model(result: ModelResult, assumptions: Assumptions) -> None:
    scenario = assumptions.scenario
    revenue = [row["revenue"] for row in result.pnl]
    personnel_costs = [row["personnel_costs"] for row in result.pnl]
    overhead_costs = [row["overhead_and_variable_costs"] for row in result.pnl]
    ebitda = [row["ebitda"] for row in result.pnl]
    depreciation = [row["depreciation"] for row in result.pnl]
    ebit = [row["ebit"] for row in result.pnl]
    interest = [row["interest_expense"] for row in result.pnl]
    ebt = [row["ebt"] for row in result.pnl]
    taxes = [row["taxes"] for row in result.pnl]
    net_income = [row["net_income"] for row in result.pnl]

    consultant_costs = [row.get("consultant_costs", 0.0) for row in result.cost]
    backoffice_costs = [row.get("backoffice_costs", 0.0) for row in result.cost]
    management_costs = [row.get("management_costs", 0.0) for row in result.cost]

    external_consulting = []
    it_costs = []
    office_costs = []
    other_services = []
    for year_index in range(5):
        fixed = assumptions.cost.fixed_overhead_by_year[year_index]
        inflation_factor = (
            (1 + assumptions.cost.inflation_rate_pct) ** year_index
            if assumptions.cost.inflation_apply
            else 1.0
        )
        external_value = fixed.advisory_eur * inflation_factor
        it_value = fixed.it_software_eur * inflation_factor
        office_value = fixed.office_rent_eur * inflation_factor
        remainder = overhead_costs[year_index] - external_value - it_value - office_value
        if remainder < 0:
            remainder = (
                fixed.legal_eur + fixed.services_eur + fixed.other_services_eur
            ) * inflation_factor
        external_consulting.append(external_value)
        it_costs.append(it_value)
        office_costs.append(office_value)
        other_services.append(remainder)

    consultant_fte = [
        row.consultant_fte for row in assumptions.cost.personnel_by_year
    ]
    revenue_per_consultant = [
        _format_money(rev / fte) if fte else "n/a"
        for rev, fte in zip(revenue, consultant_fte)
    ]
    ebitda_margin = [
        _format_percent(value, revenue[idx]) for idx, value in enumerate(ebitda)
    ]
    ebit_margin = [
        _format_percent(value, revenue[idx]) for idx, value in enumerate(ebit)
    ]
    personnel_ratio = [
        _format_percent(value, revenue[idx])
        for idx, value in enumerate(personnel_costs)
    ]
    guarantee_pct = assumptions.revenue.scenarios[scenario].guarantee_pct_by_year
    guarantee_values = [f"{value * 100:,.1f}%" for value in guarantee_pct]
    net_margin = [
        _format_percent(value, revenue[idx]) for idx, value in enumerate(net_income)
    ]
    opex_ratio = [
        _format_percent(value, revenue[idx])
        for idx, value in enumerate(overhead_costs)
    ]

    rows = [
        ("REVENUE", None),
        ("Total Revenue", revenue),
        ("", None),
        ("PERSONNEL COSTS", None),
        ("Consultant Costs", consultant_costs),
        ("Backoffice Compensation", backoffice_costs),
        ("Management / MD Compensation", management_costs),
        ("Total Personnel Costs", personnel_costs),
        ("", None),
        ("OPERATING EXPENSES", None),
        ("External Consulting / Advisors", external_consulting),
        ("IT", it_costs),
        ("Office", office_costs),
        ("Other Services", other_services),
        ("Total Operating Expenses", overhead_costs),
        ("", None),
        ("EBITDA", ebitda),
        ("Depreciation", depreciation),
        ("EBIT", ebit),
        ("Interest Expense", interest),
        ("EBT", ebt),
        ("Taxes", taxes),
        ("Net Income (Jahresueberschuss)", net_income),
        ("", None),
        ("KPI", None),
        ("Revenue per Consultant", revenue_per_consultant),
        ("EBITDA Margin", ebitda_margin),
        ("EBIT Margin", ebit_margin),
        ("Personnel Cost Ratio", personnel_ratio),
        ("Guaranteed Revenue %", guarantee_values),
        ("Net Margin", net_margin),
        ("Opex Ratio", opex_ratio),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)


def render_cashflow_liquidity(result: ModelResult) -> None:
    rows = [
        ("OPERATING CASHFLOW", None),
        ("EBITDA", [row["ebitda"] for row in result.cashflow]),
        ("Cash Taxes", [row["taxes_paid"] for row in result.cashflow]),
        ("Working Capital Change", [row["working_capital_change"] for row in result.cashflow]),
        ("Operating Cashflow", [row["operating_cf"] for row in result.cashflow]),
        ("", None),
        ("INVESTING CASHFLOW", None),
        ("Capex", [row["capex"] for row in result.cashflow]),
        ("Free Cashflow", [row["free_cashflow"] for row in result.cashflow]),
        ("", None),
        ("FINANCING CASHFLOW", None),
        ("Debt Drawdown", [row["debt_drawdown"] for row in result.cashflow]),
        ("Interest Paid", [row["interest_paid"] for row in result.cashflow]),
        ("Debt Repayment", [row["debt_repayment"] for row in result.cashflow]),
        ("Net Cashflow", [row["net_cashflow"] for row in result.cashflow]),
        ("", None),
        ("LIQUIDITY", None),
        ("Opening Cash", [row["opening_cash"] for row in result.cashflow]),
        ("Net Cashflow", [row["net_cashflow"] for row in result.cashflow]),
        ("Closing Cash", [row["cash_balance"] for row in result.cashflow]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)


def render_balance_sheet(result: ModelResult) -> None:
    rows = [
        ("ASSETS", None),
        ("Cash", [row["cash"] for row in result.balance_sheet]),
        ("Fixed Assets (Net)", [row["fixed_assets"] for row in result.balance_sheet]),
        ("Total Assets", [row["total_assets"] for row in result.balance_sheet]),
        ("", None),
        ("LIABILITIES", None),
        ("Financial Debt", [row["financial_debt"] for row in result.balance_sheet]),
        ("Total Liabilities", [row["total_liabilities"] for row in result.balance_sheet]),
        ("", None),
        ("EQUITY", None),
        ("Equity at Start of Year", [row["equity_start"] for row in result.balance_sheet]),
        ("Net Income", [row["net_income"] for row in result.balance_sheet]),
        ("Dividends", [row["dividends"] for row in result.balance_sheet]),
        ("Equity Injections", [row["equity_injection"] for row in result.balance_sheet]),
        ("Equity Buybacks / Exit Payouts", [row["equity_buyback"] for row in result.balance_sheet]),
        ("Equity at End of Year", [row["equity_end"] for row in result.balance_sheet]),
        ("", None),
        ("Total Assets", [row["total_assets"] for row in result.balance_sheet]),
        ("Total Liabilities + Equity", [row["total_liabilities_equity"] for row in result.balance_sheet]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)


def render_financing_debt(result: ModelResult, assumptions: Assumptions) -> None:
    coverage = [row.get("dscr") for row in result.debt]
    debt_service = [row.get("debt_service", 0.0) for row in result.debt]
    cfads = [row.get("cfads", 0.0) or 0.0 for row in result.debt]
    rows = [
        ("EBITDA", [row["ebitda"] for row in result.cashflow]),
        ("Cash Taxes", [row["taxes_paid"] for row in result.cashflow]),
        ("Capex (Maintenance)", [row["capex"] for row in result.cashflow]),
        ("Working Capital Change", [row["working_capital_change"] for row in result.cashflow]),
        ("CFADS", cfads),
        ("Interest Expense", [row["interest_expense"] for row in result.debt]),
        ("Scheduled Repayment", [row["total_repayment"] for row in result.debt]),
        ("Debt Service", debt_service),
        ("DSCR", [f"{value:.2f}" if value is not None else "n/a" for value in coverage]),
        ("Minimum Required DSCR", [f"{assumptions.financing.minimum_dscr:.2f}" for _ in result.debt]),
        ("Covenant Breach", ["YES" if row.get("covenant_breach") else "NO" for row in result.debt]),
    ]
    st.dataframe(_statement_table(rows), use_container_width=True)


def render_equity_case(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("### Capital at Risk (Entry View)")
    exit_value = result.equity.get("exit_value", 0.0)

    purchase_price = assumptions.transaction_and_financing.purchase_price_eur
    debt_at_close = assumptions.financing.senior_debt_amount_eur
    management_equity = assumptions.transaction_and_financing.equity_contribution_eur
    total_equity_needed = max(purchase_price - debt_at_close, 0.0)
    external_equity = max(total_equity_needed - management_equity, 0.0)
    total_equity = max(total_equity_needed, management_equity, 0.0)
    management_share = management_equity / total_equity if total_equity else 0.0
    external_share = external_equity / total_equity if total_equity else 0.0

    st.table(
        [
            {
                "Line Item": "Management (Sponsor) Equity",
                "Equity (EUR)": _format_money(management_equity),
                "Ownership (%)": f"{management_share * 100:.1f}%",
            },
            {
                "Line Item": "External Investor Equity",
                "Equity (EUR)": _format_money(external_equity),
                "Ownership (%)": f"{external_share * 100:.1f}%",
            },
            {
                "Line Item": "Total Equity",
                "Equity (EUR)": _format_money(total_equity),
                "Ownership (%)": "100.0%",
            },
        ]
    )

    st.markdown("### Headline Outcomes")
    external_exit = exit_value * external_share if total_equity else 0.0
    management_exit = exit_value * management_share if total_equity else 0.0

    cols = st.columns(4)
    cols[0].metric("External Investor - Investment", _format_money(external_equity))
    cols[1].metric("External Investor - Exit Value", _format_money(external_exit))
    cols[2].metric(
        "External Investor - Multiple",
        f"{external_exit / external_equity:.2f}x" if external_equity else "n/a",
    )
    cols[3].metric(
        "External Investor - IRR",
        f"{result.equity.get('irr', 0.0) * 100:.1f}%" if external_equity else "n/a",
    )

    cols = st.columns(4)
    cols[0].metric("Management - Investment", _format_money(management_equity))
    cols[1].metric("Management - Exit Value", _format_money(management_exit))
    cols[2].metric(
        "Management - Multiple",
        f"{management_exit / management_equity:.2f}x" if management_equity else "n/a",
    )
    cols[3].metric(
        "Management - IRR",
        f"{result.equity.get('irr', 0.0) * 100:.1f}%" if management_equity else "n/a",
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
    gap_pct = (gap / enterprise_value * 100) if enterprise_value else 0.0
    kpi_cols[2].metric("Gap (EUR / %)", f"{_format_money(gap)} | {gap_pct:.1f}%")

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
            col = "Year 0" if year == 0 else f"Year {year}"
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
            col = "Year 0" if year == 0 else f"Year {year}"
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
        {"Metric": "Revenue (Year 4)", "Value": _format_money(result.pnl[last_year]["revenue"]), "Unit": "EUR"},
        {
            "Metric": "Profit Before Depreciation (Year 4)",
            "Value": _format_money(result.pnl[last_year]["ebitda"]),
            "Unit": "EUR",
        },
        {"Metric": "Net Profit (Year 4)", "Value": _format_money(result.pnl[last_year]["net_income"]), "Unit": "EUR"},
        {
            "Metric": "Cash After Investment (Year 4)",
            "Value": _format_money(result.cashflow[last_year]["free_cashflow"]),
            "Unit": "EUR",
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
    if unit == "EUR":
        return _format_money(value)
    return f"{value:,.2f}"


def _format_delta(value: float, unit: str) -> str:
    sign = "+" if value > 0 else ""
    if unit in {"%", "% p.a."}:
        return f"{sign}{value:.1%}"
    if unit == "x":
        return f"{sign}{value:.2f}x"
    if unit == "EUR":
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
        return f"{value / 1_000_000:,.2f} m EUR"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.2f} k EUR"
    return f"{value:,.0f} EUR"


def _format_percent(value: float, base: float) -> str:
    if base == 0:
        return "0.0%"
    return f"{(value / base) * 100:.1f}%"
