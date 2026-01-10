from __future__ import annotations

from typing import Dict, List, Iterable

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions

YEAR_LABELS = [f"Year {i}" for i in range(5)]


def render_overview(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("### A. Deal Snapshot (What are we buying and how is it funded?)")

    purchase_price = assumptions.transaction_and_financing.purchase_price_eur
    debt_at_close = assumptions.financing.senior_debt_amount_eur
    equity_at_close = assumptions.transaction_and_financing.equity_contribution_eur
    exit_multiple = assumptions.valuation.seller_multiple
    last_year = len(result.pnl) - 1
    ebitda = result.pnl[0]["ebitda"] if result.pnl else 0.0
    debt_ebitda = debt_at_close / ebitda if ebitda else 0.0

    metric_items = [
        ("Purchase Price", _format_money(purchase_price)),
        ("Debt at Close", _format_money(debt_at_close)),
        ("Equity at Close", _format_money(equity_at_close)),
        ("Debt / Operating Profit (EBITDA)", f"{debt_ebitda:.2f}x"),
        ("Exit Year", f"Year {last_year}"),
        ("Exit Multiple", f"{exit_multiple:.2f}x"),
    ]
    metric_html = ['<div class="metric-grid">']
    for label, value in metric_items:
        metric_html.append(
            f'<div><div class="metric-item-label">{label}</div>'
            f'<div class="metric-item-value">{value}</div></div>'
        )
    metric_html.append("</div>")
    st.markdown("".join(metric_html), unsafe_allow_html=True)

    revenue = [row["revenue"] for row in result.pnl]
    total_costs = [
        row["personnel_costs"] + row["overhead_and_variable_costs"]
        for row in result.pnl
    ]
    st.markdown("### Break-even View")
    st.line_chart(
        {"Revenue": revenue, "Total Costs": total_costs},
        use_container_width=True,
    )

    st.markdown("**Interpretation**")
    st.markdown(
        "- Debt at Close shows the initial borrowing that must be serviced from operating cash.\n"
        "- Equity at Close is the cash contributed by management and investors before debt service begins.\n"
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
    _render_kpi_table_html(
        rows,
        columns=["Driver", "Current", "Base", "Delta", "Unit"],
        table_class="kpi-table",
    )


def render_operating_model(result: ModelResult, assumptions: Assumptions) -> None:
    revenue = [row["revenue"] for row in result.pnl]
    personnel_costs = [row["personnel_costs"] for row in result.pnl]
    overhead_costs = [row["overhead_and_variable_costs"] for row in result.pnl]
    ebitda = [row["ebitda"] for row in result.pnl]
    depreciation = [row["depreciation"] for row in result.pnl]
    ebit = [row["ebit"] for row in result.pnl]
    interest = [row["interest_expense"] for row in result.pnl]
    taxes = [row["taxes"] for row in result.pnl]
    net_income = [row["net_income"] for row in result.pnl]
    net_contribution = [
        revenue[idx] - personnel_costs[idx] for idx in range(len(result.pnl))
    ]

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

    revenue_per_consultant = [
        _format_money(
            revenue[idx] / assumptions.cost.personnel_by_year[idx].consultant_fte
        )
        if assumptions.cost.personnel_by_year[idx].consultant_fte
        else _format_money(0.0)
        for idx in range(5)
    ]
    ebitda_margin = [_format_percent(ebitda[idx], revenue[idx]) for idx in range(5)]
    personnel_cost_ratio = [
        _format_percent(personnel_costs[idx], revenue[idx]) for idx in range(5)
    ]
    net_margin = [_format_percent(net_income[idx], revenue[idx]) for idx in range(5)]
    opex_ratio = [_format_percent(overhead_costs[idx], revenue[idx]) for idx in range(5)]

    rows = [
        ("REVENUE ENGINE", None),
        ("Total Revenue", revenue),
        ("Revenue per Consultant", revenue_per_consultant),
        ("", None),
        ("PEOPLE COST ENGINE", None),
        ("Total Personnel Costs", personnel_costs),
        ("Personnel Cost Ratio", personnel_cost_ratio),
        ("Net Contribution after Personnel Costs", net_contribution),
        ("", None),
        ("OPERATING LEVERAGE & SCALE COSTS", None),
        ("Total Operating Expenses", overhead_costs),
        ("Opex Ratio", opex_ratio),
        ("EBITDA (Operating Leverage)", ebitda),
        ("EBITDA Margin", ebitda_margin),
        ("", None),
        ("RESULT", None),
        ("EBITDA", ebitda),
        ("EBIT", ebit),
        ("Net Income", net_income),
        ("Net Margin", net_margin),
    ]
    year_labels = ["Current Operating Reality (Year 0)"] + [
        f"Scaled Operations (Year {idx})" for idx in range(1, 5)
    ]
    _render_statement_table_html(
        rows,
        bold_labels={
            "Total Revenue",
            "Total Personnel Costs",
            "Total Operating Expenses",
            "EBITDA",
            "EBIT",
            "Net Income",
            "Net Contribution after Personnel Costs",
        },
        row_classes={
            "Total Personnel Costs": "people-row",
            "Personnel Cost Ratio": "people-row percent-kpi",
            "Net Contribution after Personnel Costs": "key-metric",
        },
        year_labels=year_labels,
    )
    st.markdown(
        '<div class="hint-text">Primary steering metric for hiring, utilization, and scalable growth.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Detailed analysis", expanded=False):
        st.markdown("#### Full P&L")
        detailed_rows = [
            ("REVENUE", None),
            ("Total Revenue", revenue),
            ("", None),
            ("PERSONNEL COSTS", None),
            ("Consultant Compensation", consultant_costs),
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
            ("PROFITABILITY", None),
            ("EBITDA", ebitda),
            ("Depreciation", depreciation),
            ("EBIT", ebit),
            ("Interest Expense", interest),
            ("Taxes", taxes),
            ("Net Income", net_income),
        ]
        _render_statement_table_html(
            detailed_rows,
            bold_labels={
                "Total Revenue",
                "Total Personnel Costs",
                "Total Operating Expenses",
                "EBITDA",
                "EBIT",
                "Net Income",
            },
            year_labels=year_labels,
        )

        st.markdown("#### Revenue Bridge")
        components = result.revenue.get("components_by_year", [])
        bridge_rows = [
            (
                "Consultant Headcount (FTE)",
                [
                    f"{components[idx].get('consulting_fte', 0.0):,.1f}"
                    if idx < len(components)
                    else "0.0"
                    for idx in range(5)
                ],
            ),
            (
                "Capacity Days",
                [
                    f"{components[idx].get('capacity_days', 0.0):,.0f}"
                    if idx < len(components)
                    else "0"
                    for idx in range(5)
                ],
            ),
            (
                "Adjusted Capacity Days",
                [
                    f"{components[idx].get('adjusted_capacity_days', 0.0):,.0f}"
                    if idx < len(components)
                    else "0"
                    for idx in range(5)
                ],
            ),
            (
                "Modeled Group Revenue",
                [
                    components[idx].get("modeled_group_revenue", 0.0)
                    if idx < len(components)
                    else 0.0
                    for idx in range(5)
                ],
            ),
            (
                "Modeled External Revenue",
                [
                    components[idx].get("modeled_external_revenue", 0.0)
                    if idx < len(components)
                    else 0.0
                    for idx in range(5)
                ],
            ),
            (
                "Guaranteed Revenue Floor",
                [
                    components[idx].get("guaranteed_floor", 0.0)
                    if idx < len(components)
                    else 0.0
                    for idx in range(5)
                ],
            ),
            (
                "Total Revenue",
                [
                    components[idx].get("final_total", 0.0)
                    if idx < len(components)
                    else 0.0
                    for idx in range(5)
                ],
            ),
        ]
        _render_statement_table_html(
            bridge_rows, bold_labels={"Total Revenue"}, year_labels=year_labels
        )

        st.markdown("#### Personnel Cost Logic")
        personnel_rows = [
            ("Consultant Compensation", consultant_costs),
            ("Backoffice Compensation", backoffice_costs),
            ("Management / MD Compensation", management_costs),
            ("Total Personnel Costs", personnel_costs),
        ]
        _render_statement_table_html(
            personnel_rows, bold_labels={"Total Personnel Costs"}, year_labels=year_labels
        )

        st.markdown("#### Operating Expense Logic")
        operating_rows = [
            ("External Consulting / Advisors", external_consulting),
            ("IT", it_costs),
            ("Office", office_costs),
            ("Other Services", other_services),
            ("Total Operating Expenses", overhead_costs),
        ]
        _render_statement_table_html(
            operating_rows, bold_labels={"Total Operating Expenses"}, year_labels=year_labels
        )

        st.markdown("#### Earnings Bridge")
        earnings_rows = [
            ("EBITDA", ebitda),
            ("Depreciation", depreciation),
            ("EBIT", ebit),
            ("Interest Expense", interest),
            ("Taxes", taxes),
            ("Net Income", net_income),
        ]
        _render_statement_table_html(
            earnings_rows, bold_labels={"EBIT", "Net Income"}, year_labels=year_labels
        )

        st.markdown("#### KPI Definitions")
        st.markdown(
            "- Revenue per Consultant: Total Revenue divided by consultant FTE.\n"
            "- EBITDA Margin: EBITDA divided by Total Revenue.\n"
            "- Personnel Cost Ratio: Total Personnel Costs divided by Total Revenue.\n"
            "- Net Margin: Net Income divided by Total Revenue.\n"
        )


def render_cashflow_liquidity(result: ModelResult) -> None:
    rows = [
        ("CASH GENERATION (OPERATING REALITY)", None),
        ("EBITDA", [row["ebitda"] for row in result.cashflow]),
        ("Cash Taxes Paid", [row["taxes_paid"] for row in result.cashflow]),
        (
            "Working Capital Change",
            [row["working_capital_change"] for row in result.cashflow],
        ),
        ("Operating Cashflow", [row["operating_cf"] for row in result.cashflow]),
        ("", None),
        ("INVESTMENT & FREE CASHFLOW", None),
        ("Capex", [row["capex"] for row in result.cashflow]),
        ("Free Cashflow", [row["free_cashflow"] for row in result.cashflow]),
        ("", None),
        ("FINANCING & DEBT BURDEN", None),
        ("Debt Drawdowns", [row["debt_drawdown"] for row in result.cashflow]),
        ("Interest Paid", [row["interest_paid"] for row in result.cashflow]),
        ("Debt Repayment", [row["debt_repayment"] for row in result.cashflow]),
        ("Net Cashflow", [row["net_cashflow"] for row in result.cashflow]),
        ("", None),
        ("LIQUIDITY POSITION", None),
        ("Opening Cash", [row["opening_cash"] for row in result.cashflow]),
        ("Net Cashflow", [row["net_cashflow"] for row in result.cashflow]),
        ("Closing Cash", [row["cash_balance"] for row in result.cashflow]),
    ]
    _render_statement_table_html(
        rows,
        bold_labels={
            "Operating Cashflow",
            "Free Cashflow",
            "Net Cashflow",
            "Closing Cash",
        },
        row_classes={"Closing Cash": "key-metric"},
    )


def render_balance_sheet(result: ModelResult) -> None:
    rows = [
        ("ASSET STRUCTURE", None),
        ("Cash", [row["cash"] for row in result.balance_sheet]),
        ("Fixed Assets (Net)", [row["fixed_assets"] for row in result.balance_sheet]),
        ("Total Assets", [row["total_assets"] for row in result.balance_sheet]),
        ("", None),
        ("DEBT & FINANCING STRUCTURE", None),
        ("Financial Debt", [row["financial_debt"] for row in result.balance_sheet]),
        ("Total Liabilities", [row["total_liabilities"] for row in result.balance_sheet]),
        ("", None),
        ("EQUITY EVOLUTION", None),
        ("Equity at Start of Year", [row["equity_start"] for row in result.balance_sheet]),
        ("Net Income", [row["net_income"] for row in result.balance_sheet]),
        ("Dividends", [row["dividends"] for row in result.balance_sheet]),
        ("Equity Injections", [row["equity_injection"] for row in result.balance_sheet]),
        ("Equity Buybacks / Exit Payouts", [row["equity_buyback"] for row in result.balance_sheet]),
        ("Equity at End of Year", [row["equity_end"] for row in result.balance_sheet]),
        ("", None),
        ("CONSISTENCY CHECK", None),
        ("Total Assets", [row["total_assets"] for row in result.balance_sheet]),
        ("Total Liabilities + Equity", [row["total_liabilities_equity"] for row in result.balance_sheet]),
    ]
    _render_statement_table_html(
        rows,
        bold_labels={
            "Total Assets",
            "Total Liabilities",
            "Equity at End of Year",
            "Total Liabilities + Equity",
        },
        row_classes={"Cash": "key-metric"},
    )


def render_financing_debt(result: ModelResult, assumptions: Assumptions) -> None:
    coverage = [row.get("dscr") for row in result.debt]
    debt_service = [row.get("debt_service", 0.0) for row in result.debt]
    cfads = [row.get("cfads", 0.0) or 0.0 for row in result.debt]
    min_required = assumptions.financing.minimum_dscr
    dscr_headroom = [
        (value - min_required) if value is not None else None for value in coverage
    ]

    st.markdown("### Cash Available for Debt Service")
    cfads_rows = [
        ("EBITDA", [row["ebitda"] for row in result.cashflow]),
        ("Cash Taxes", [row["taxes_paid"] for row in result.cashflow]),
        ("Maintenance Capex", [row["capex"] for row in result.cashflow]),
        ("Working Capital Change", [row["working_capital_change"] for row in result.cashflow]),
        ("CFADS", cfads),
    ]
    _render_statement_table_html(
        cfads_rows,
        bold_labels={"CFADS"},
    )

    st.markdown("### Debt Service Obligation")
    service_rows = [
        ("Interest Expense", [row["interest_expense"] for row in result.debt]),
        ("Scheduled Repayment", [row["total_repayment"] for row in result.debt]),
        ("Total Debt Service", debt_service),
    ]
    _render_statement_table_html(
        service_rows,
        bold_labels={"Total Debt Service"},
    )

    st.markdown("### Coverage & Covenant Test")
    coverage_rows = [
        (
            "DSCR",
            [f"{value:.2f}" if value is not None else "n/a" for value in coverage],
        ),
        (
            "Minimum Required DSCR",
            [f"{min_required:.2f}" for _ in result.debt],
        ),
        ("DSCR Headroom", dscr_headroom),
        ("Covenant Breach", ["YES" if row.get("covenant_breach") else "NO" for row in result.debt]),
    ]
    _render_statement_table_html(
        coverage_rows,
        bold_labels={"DSCR Headroom"},
    )

    st.markdown("### Debt Risk Summary")
    dscr_values = [value for value in coverage if value is not None]
    min_dscr = min(dscr_values) if dscr_values else 0.0
    years_below = len(
        [value for value in dscr_values if value < min_required]
    )
    peak_debt = max(
        row.get("opening_debt", row.get("closing_debt", 0.0)) for row in result.debt
    )
    debt_at_close = result.debt[0].get(
        "opening_debt", assumptions.financing.senior_debt_amount_eur
    )
    cfads_at_close = cfads[0] if cfads else 0.0
    debt_cfads = debt_at_close / cfads_at_close if cfads_at_close else 0.0
    summary_rows = [
        ("Minimum DSCR", [f"{min_dscr:.2f}x"]),
        ("Years below covenant", [str(years_below)]),
        ("Peak Debt Outstanding", [_format_money(peak_debt)]),
        ("Debt / CFADS at Close", [f"{debt_cfads:.2f}x" if debt_cfads else "n/a"]),
    ]
    _render_statement_table_html(
        summary_rows,
        years=1,
        year_labels=["Value"],
    )


def render_equity_case(result: ModelResult, assumptions: Assumptions) -> None:
    exit_value = result.equity.get("exit_value", 0.0)

    purchase_price = assumptions.transaction_and_financing.purchase_price_eur
    debt_at_close = assumptions.financing.senior_debt_amount_eur
    management_equity = assumptions.transaction_and_financing.equity_contribution_eur
    total_equity_needed = max(purchase_price - debt_at_close, 0.0)
    external_equity = max(total_equity_needed - management_equity, 0.0)
    total_equity = max(total_equity_needed, management_equity, 0.0)
    management_share = management_equity / total_equity if total_equity else 0.0
    external_share = external_equity / total_equity if total_equity else 0.0
    ownership_split = f"Management {management_share * 100:.1f}% / External {external_share * 100:.1f}%"

    st.markdown("### Capital at Risk – Entry View")
    equity_rows = [
        ("Management (Sponsor) Equity", [_format_money(management_equity), f"{management_share * 100:.1f}%"]),
        ("External Investor Equity", [_format_money(external_equity), f"{external_share * 100:.1f}%"]),
        ("Total Equity", [_format_money(total_equity), "100.0%"]),
    ]
    _render_statement_table_html(
        equity_rows,
        bold_labels={"Total Equity"},
        years=2,
        year_labels=["Equity (EUR)", "Ownership (%)"],
    )

    st.markdown("### Ownership & Control")
    control_rows = [
        ("Ownership Split", [ownership_split]),
        ("Control Logic", ["Management control with minority investor protection"]),
        ("Exit Mechanism", ["Management buys out investor at exit"]),
    ]
    _render_statement_table_html(control_rows, years=1, year_labels=["Statement"])

    external_exit = exit_value * external_share if total_equity else 0.0
    management_exit = exit_value * management_share if total_equity else 0.0

    st.markdown("### Cash Flow to Equity")
    year_labels = [f"Year {i}" for i in range(5)]
    operating_cf = [row["operating_cf"] for row in result.cashflow]
    debt_service = [row.get("debt_service", 0.0) for row in result.debt]
    equity_cashflows = result.equity.get("equity_cashflows", [])
    cashflow_years = equity_cashflows[1:6] if len(equity_cashflows) >= 6 else equity_cashflows
    residual_equity = [
        cashflow_years[idx] if idx < len(cashflow_years) else 0.0 for idx in range(5)
    ]
    investor_cashflows = [
        (value * external_share) if idx < len(cashflow_years) else 0.0
        for idx, value in enumerate(residual_equity)
    ]
    management_cashflows = [
        (value * management_share) if idx < len(cashflow_years) else 0.0
        for idx, value in enumerate(residual_equity)
    ]
    cashflow_rows = [
        ("Operating Cashflows", operating_cf),
        ("Debt Service", debt_service),
        ("Residual Cash to Equity", residual_equity),
        ("Allocation – External Investor", investor_cashflows),
        ("Allocation – Management", management_cashflows),
    ]
    _render_statement_table_html(cashflow_rows, years=5, year_labels=year_labels)

    st.markdown("### Exit Equity Bridge (Single Source of Truth)")
    enterprise_value = result.equity.get("enterprise_value", 0.0)
    net_debt_exit = result.equity.get("net_debt_exit", 0.0)
    excess_cash = result.equity.get("excess_cash_exit", 0.0)
    equity_bridge_rows = [
        ("Enterprise Value at Exit", [enterprise_value]),
        ("Net Debt at Exit", [-net_debt_exit]),
        ("Excess Cash at Exit", [excess_cash]),
        ("Equity Value at Exit", [exit_value]),
        ("External Investor Allocation", [external_exit]),
        ("Management Allocation", [management_exit]),
    ]
    _render_statement_table_html(
        equity_bridge_rows,
        bold_labels={"Equity Value at Exit"},
        years=1,
        year_labels=["Exit Year"],
    )

    st.markdown("### Returns Summary")
    investor_rows = [
        ("Invested Equity", [_format_money(external_equity)]),
        ("Exit Proceeds", [_format_money(external_exit)]),
        (
            "MOIC",
            [f"{external_exit / external_equity:.2f}x" if external_equity else "n/a"],
        ),
        (
            "IRR",
            [f"{result.equity.get('irr', 0.0) * 100:.1f}%" if external_equity else "n/a"],
        ),
    ]
    st.markdown("#### External Investor")
    _render_statement_table_html(investor_rows, years=1, year_labels=["Value"])

    management_rows = [
        ("Invested Equity", [_format_money(management_equity)]),
        ("Exit Proceeds", [_format_money(management_exit)]),
        (
            "MOIC",
            [f"{management_exit / management_equity:.2f}x" if management_equity else "n/a"],
        ),
        (
            "IRR",
            [f"{result.equity.get('irr', 0.0) * 100:.1f}%" if management_equity else "n/a"],
        ),
    ]
    st.markdown("#### Management")
    _render_statement_table_html(management_rows, years=1, year_labels=["Value"])


def render_valuation_summary(result: ModelResult) -> None:
    enterprise_value = result.equity.get("enterprise_value", 0.0)
    net_debt_exit = result.equity.get("net_debt_exit", 0.0)
    excess_cash_exit = result.equity.get("excess_cash_exit", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)
    last_year_ebit = result.pnl[-1]["ebit"] if result.pnl else 0.0
    implied_multiple = (enterprise_value / last_year_ebit) if last_year_ebit else 0.0

    debt_year0 = result.debt[0] if result.debt else {}
    closing_debt = debt_year0.get("closing_debt", 0.0)
    cash_at_close = (
        result.balance_sheet[0].get("cash", 0.0) if result.balance_sheet else 0.0
    )
    net_debt_close = closing_debt - cash_at_close
    free_cf = [row["free_cashflow"] for row in result.cashflow]
    discount_rate = 0.10
    discount_factors = [(1 / ((1 + discount_rate) ** (idx + 1))) for idx in range(5)]
    pv_fcf = [free_cf[idx] * discount_factors[idx] for idx in range(5)]
    cumulative_pv = []
    running = 0.0
    for value in pv_fcf:
        running += value
        cumulative_pv.append(running)
    dcf_value = cumulative_pv[-1] if cumulative_pv else 0.0

    st.markdown("### Valuation Methods – Detailed Breakdown")
    st.markdown("#### Multiple-Based Valuation")
    multiple_rows = [
        ("Exit Year EBIT", [last_year_ebit]),
        (
            "Implied Multiple (model input)",
            [f"{implied_multiple:.2f}x" if last_year_ebit else "n/a"],
        ),
        ("Equity Value (Multiple-Based)", [enterprise_value]),
    ]
    _render_statement_table_html(
        multiple_rows,
        bold_labels={"Equity Value (Multiple-Based)"},
        years=1,
        year_labels=["Value"],
    )

    st.markdown("#### DCF-Based Valuation (no terminal)")
    dcf_rows = [
        ("Free Cashflow", free_cf),
        ("Discount Factor", [f"{value:.2f}" for value in discount_factors]),
        ("Present Value of FCF", pv_fcf),
        ("Cumulative PV of FCF", cumulative_pv),
        ("Equity Value (DCF, no terminal)", ["", "", "", "", dcf_value]),
    ]
    _render_statement_table_html(
        dcf_rows,
        bold_labels={"Equity Value (DCF, no terminal)"},
    )

    st.markdown("#### Intrinsic / Cash-Based Value")
    intrinsic_rows = [
        ("Enterprise Value (Exit Multiple)", [enterprise_value]),
        ("Net Debt at Exit", [net_debt_exit]),
        ("Excess Cash at Exit", [excess_cash_exit]),
        ("Equity Value (Cash-Based)", [exit_value]),
    ]
    _render_statement_table_html(
        intrinsic_rows,
        bold_labels={"Equity Value (Cash-Based)"},
        years=1,
        year_labels=["Value"],
    )

    st.markdown("### Valuation Summary (Method Comparison)")
    method_rows = [
        ("Multiple-Based Valuation", [enterprise_value, "Optimistic"]),
        ("DCF-Based Valuation (no terminal)", [dcf_value, "Conservative"]),
        ("Intrinsic / Cash-Based Value", [exit_value, "Financing-constrained"]),
    ]
    _render_statement_table_html(
        method_rows,
        years=2,
        year_labels=["Equity Value", "Characterization"],
    )

    valuation_min = min(enterprise_value, dcf_value, exit_value)
    valuation_max = max(enterprise_value, dcf_value, exit_value)
    st.markdown("### Valuation Range & Interpretation")
    range_rows = [
        ("Conservative Floor (Min)", [valuation_min]),
        ("Optimistic Ceiling (Max)", [valuation_max]),
    ]
    _render_statement_table_html(range_rows, years=1, year_labels=["Value"])
    st.markdown(
        "- The range is wide because methods weight risk and growth differently.\n"
        "- Downside is driven by cashflow timing and financing constraints.\n"
        "- Upside remains uncertain without terminal value visibility."
    )

    st.markdown("### Buyer Affordability & Price Ceiling")
    affordability_rows = [
        ("Buyer Affordability (Equity Value after financing)", [exit_value]),
        ("Net Debt at Close (reference)", [net_debt_close]),
    ]
    _render_statement_table_html(
        affordability_rows,
        years=1,
        year_labels=["Value"],
    )
    st.markdown(
        "Affordability is a financing- and liquidity-constrained ceiling, not a valuation."
    )

    midpoint = (valuation_min + valuation_max) / 2 if valuation_min or valuation_max else 0.0
    price_gap = exit_value - midpoint
    st.markdown("### Value vs. Price – Negotiation Logic")
    gap_rows = [
        ("Valuation Midpoint (reference)", [midpoint]),
        ("Buyer Affordability", [exit_value]),
        ("Price Gap (EUR)", [price_gap]),
    ]
    _render_statement_table_html(
        gap_rows,
        bold_labels={"Price Gap (EUR)"},
        years=1,
        year_labels=["Value"],
    )
    st.markdown(
        "Key arguments to justify purchase price below value:\n"
        "- Financing and liquidity risk\n"
        "- Downside-only DCF (no terminal value)\n"
        "- People dependency\n"
        "- Transition and separation risk\n"
        "- Conservative buyer-side risk adjustments"
    )


def render_valuation_detail(result: ModelResult) -> None:
    enterprise_value = result.equity.get("enterprise_value", 0.0)
    net_debt_exit = result.equity.get("net_debt_exit", 0.0)
    excess_cash = result.equity.get("excess_cash_exit", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)

    debt_year0 = result.debt[0] if result.debt else {}
    opening_debt = debt_year0.get("opening_debt", 0.0)
    drawdown = debt_year0.get("debt_drawdown", 0.0)
    repayment = debt_year0.get("total_repayment", 0.0)
    closing_debt = debt_year0.get("closing_debt", 0.0)
    cash_at_close = result.balance_sheet[0].get("cash", 0.0) if result.balance_sheet else 0.0
    net_debt_close = closing_debt - cash_at_close
    net_debt_rows = [
        {"Metric": "Opening Debt (Year 0)", "Value": _format_money(opening_debt)},
        {"Metric": "Drawdown (Year 0)", "Value": _format_money(drawdown)},
        {"Metric": "Repayment (Year 0)", "Value": _format_money(repayment)},
        {"Metric": "Closing Debt (Year 0)", "Value": _format_money(closing_debt)},
        {"Metric": "Net Debt at Close", "Value": _format_money(net_debt_close)},
    ]
    st.markdown("#### Net Debt at Close (Reference)")
    _render_statement_table_html(
        [(row["Metric"], [row["Value"]]) for row in net_debt_rows],
        bold_labels={"Net Debt at Close"},
        years=1,
        year_labels=["Value"],
    )

    st.markdown("#### Seller Valuation (Multiple-Based)")
    seller_rows = [
        ("Enterprise Value", [_format_money(enterprise_value)]),
        ("Net Debt at Exit", [_format_money(net_debt_exit)]),
        ("Excess Cash at Exit", [_format_money(excess_cash)]),
        ("Equity Value (Seller View)", [_format_money(exit_value)]),
    ]
    _render_statement_table_html(
        seller_rows,
        bold_labels={"Equity Value (Seller View)"},
        years=1,
        year_labels=["Value"],
    )


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
    _render_kpi_table_html(
        summary_rows,
        columns=["Metric", "Value", "Unit"],
        table_class="kpi-table",
    )


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


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return _format_compact(value, 1_000_000, "m€", 2)
    if abs_value >= 1_000:
        return _format_compact(value, 1_000, "k€", 1)
    return f"{value:,.0f} €"


def _format_compact(value: float, scale: float, suffix: str, decimals: int) -> str:
    formatted = f"{value / scale:,.{decimals}f}"
    if formatted.endswith(".00"):
        formatted = formatted[:-3]
    if formatted.endswith(".0"):
        formatted = formatted[:-2]
    return f"{formatted} {suffix}"


def _format_percent(value: float, base: float) -> str:
    if base == 0:
        return "0.0%"
    return f"{(value / base) * 100:.1f}%"


def _format_output_value(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return _format_money(value)
    return str(value)


def _render_statement_table_html(
    rows: List[tuple[str, List[float] | List[str] | None]],
    bold_labels: Iterable[str] | None = None,
    years: int = 5,
    row_classes: Dict[str, str] | None = None,
    year_labels: List[str] | None = None,
) -> None:
    bold_set = set(bold_labels or [])
    class_map = dict(row_classes or {})
    if year_labels is not None:
        headers = ["Line Item"] + year_labels
    else:
        headers = ["Line Item"] + [f"Year {i}" for i in range(years)]
    html = ['<table class="fin-table">', "<thead><tr>"]
    for index, header in enumerate(headers):
        if index == 0:
            header_classes = ["label"]
        else:
            header_classes = ["num"]
            if index == 1:
                header_classes.append("section")
        html.append(f'<th class="{" ".join(header_classes)}">{header}</th>')
    html.append("</tr></thead><tbody>")
    for label, values in rows:
        if label == "" and values is None:
            html.append(f'<tr class="spacer"><td colspan="{years + 1}"></td></tr>')
            continue
        if values is None:
            row_class = class_map.get(label, "section")
            html.append(f'<tr class="{row_class}">')
            html.append(f'<td class="label">{label}</td>')
            for year_index in range(years):
                cell_classes = ["num"]
                if year_index == 0:
                    cell_classes.append("section")
                html.append(f'<td class="{" ".join(cell_classes)}"></td>')
            html.append("</tr>")
            continue
        row_classes_list = []
        if label in bold_set:
            row_classes_list.append("total")
        if label in class_map:
            row_classes_list.append(class_map[label])
        class_attr = f' class="{" ".join(row_classes_list)}"' if row_classes_list else ""
        html.append(f'<tr{class_attr}><td class="label">{label}</td>')
        for year_index in range(years):
            value = values[year_index] if year_index < len(values) else ""
            cell_classes = ["num"]
            if year_index == 0 and "total" not in row_classes_list:
                cell_classes.append("section")
            if isinstance(value, (int, float)) and value < 0:
                cell_classes.append("neg")
            class_attr = f' class="{" ".join(cell_classes)}"'
            html.append(f"<td{class_attr}>{_format_output_value(value)}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _render_kpi_table_html(
    rows: List[dict],
    columns: List[str],
    table_class: str = "kpi-table",
    bold_rows: Iterable[str] | None = None,
) -> None:
    if "Year 0" in columns:
        table_class = f"{table_class} year-table"
    html = [f'<table class="{table_class}">', "<thead><tr>"]
    bold_set = set(bold_rows or [])
    for header in columns:
        html.append(f"<th>{header}</th>")
    html.append("</tr></thead><tbody>")
    for row in rows:
        row_label = row.get(columns[0], "")
        row_class = "total" if row_label in bold_set else ""
        class_attr = f' class="{row_class}"' if row_class else ""
        html.append(f"<tr{class_attr}>")
        for col in columns:
            html.append(f"<td>{row.get(col, '')}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)
