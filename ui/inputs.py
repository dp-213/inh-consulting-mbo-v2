from __future__ import annotations

from typing import List

import streamlit as st

from state.assumptions import (
    Assumptions,
    CostAssumptions,
    FinancingAssumptions,
    FixedOverheadYearAssumptions,
    PersonnelYearAssumptions,
    RevenueAssumptions,
    RevenueScenarioAssumptions,
    TransactionFinancingAssumptions,
    ValuationAssumptions,
    VariableCostYearAssumptions,
)

YEARS = ["Year 0", "Year 1", "Year 2", "Year 3", "Year 4"]


def render_revenue_inputs(assumptions: Assumptions) -> Assumptions:
    scenario = assumptions.scenario
    scenarios = dict(assumptions.revenue.scenarios)
    current = scenarios[scenario]

    st.markdown("### Revenue Drivers")
    drivers_table = _year_table(
        [
            ("Workdays per Year", "Days", current.workdays_per_year, "Billable calendar days."),
            ("Utilization %", "%", current.utilization_rate_pct, "Share of billable time."),
            ("Day Rate Growth (% p.a.)", "% p.a.", current.day_rate_growth_pct, ""),
            ("Revenue Growth (% p.a.)", "% p.a.", current.revenue_growth_pct, ""),
        ]
    )
    drivers_table = _edit_table(drivers_table, key="revenue.drivers")
    st.markdown(
        '<div class="subtle">Revenue Growth (% p.a.) applies to capacity-driven revenue, not a guaranteed top-line uplift.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Capacity Allocation")
    allocation_table = _year_table(
        [
            ("Group Capacity Share %", "%", current.group_capacity_share_pct, ""),
            ("External Capacity Share %", "%", current.external_capacity_share_pct, ""),
        ]
    )
    allocation_table = _edit_table(allocation_table, key="revenue.allocation")

    st.markdown("### Pricing Assumptions")
    rate_table = _year_table(
        [
            ("Group Day Rate", "EUR", current.group_day_rate_eur, "Contracted group pricing."),
            ("External Day Rate", "EUR", current.external_day_rate_eur, "Market upside pricing."),
        ]
    )
    rate_table = _edit_table(rate_table, key="revenue.rates")

    st.markdown("### Group Revenue Floor")
    reference_table = _year_table(
        [
            ("Reference Revenue", "EUR", [current.reference_revenue_eur for _ in range(5)], ""),
        ]
    )
    reference_table = _edit_table(reference_table, key="revenue.reference")
    guarantee_table = _year_table(
        [
            ("Guarantee %", "%", current.guarantee_pct_by_year, ""),
        ]
    )
    guarantee_table = _edit_table(guarantee_table, key="revenue.guarantee")

    scenarios[scenario] = RevenueScenarioAssumptions(
        workdays_per_year=_row_years_numeric(drivers_table, "Workdays per Year"),
        utilization_rate_pct=_row_years_numeric(drivers_table, "Utilization %"),
        group_day_rate_eur=_row_years_numeric(rate_table, "Group Day Rate"),
        external_day_rate_eur=_row_years_numeric(rate_table, "External Day Rate"),
        day_rate_growth_pct=_row_years_numeric(drivers_table, "Day Rate Growth (% p.a.)"),
        revenue_growth_pct=_row_years_numeric(drivers_table, "Revenue Growth (% p.a.)"),
        group_capacity_share_pct=_row_years_numeric(allocation_table, "Group Capacity Share %"),
        external_capacity_share_pct=_row_years_numeric(allocation_table, "External Capacity Share %"),
        reference_revenue_eur=_to_float(_row_years_numeric(reference_table, "Reference Revenue")[0]),
        guarantee_pct_by_year=_row_years_numeric(guarantee_table, "Guarantee %"),
    )

    return Assumptions(
        scenario=scenario,
        revenue=RevenueAssumptions(scenarios=scenarios),
        cost=assumptions.cost,
        transaction_and_financing=assumptions.transaction_and_financing,
        financing=assumptions.financing,
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=assumptions.valuation,
    )


def render_cost_inputs(assumptions: Assumptions) -> Assumptions:
    cost = assumptions.cost

    st.markdown("### Inflation")
    inflation_table = [
        {
            "Parameter": "Apply Inflation",
            "Unit": "",
            "Value": "True" if cost.inflation_apply else "False",
        },
        {
            "Parameter": "Inflation Rate (% p.a.)",
            "Unit": "% p.a.",
            "Value": _display_value(cost.inflation_rate_pct, "% p.a."),
        },
    ]
    inflation_table = _edit_table(inflation_table, key="cost.inflation")

    st.markdown("### Consultant Costs")
    consultant_table = _year_table(
        [
            ("Consultant FTE", "FTE", [row.consultant_fte for row in cost.personnel_by_year], ""),
            ("Consultant Loaded Cost", "EUR", [row.consultant_loaded_cost_eur for row in cost.personnel_by_year], ""),
        ]
    )
    consultant_table = _edit_table(consultant_table, key="cost.consultant")

    st.markdown("### Backoffice Costs")
    backoffice_table = _year_table(
        [
            ("Backoffice FTE", "FTE", [row.backoffice_fte for row in cost.personnel_by_year], ""),
            ("Backoffice Loaded Cost", "EUR", [row.backoffice_loaded_cost_eur for row in cost.personnel_by_year], ""),
        ]
    )
    backoffice_table = _edit_table(backoffice_table, key="cost.backoffice")

    st.markdown("### Management")
    management_table = _year_table(
        [
            ("Management Cost", "EUR", [row.management_cost_eur for row in cost.personnel_by_year], ""),
        ]
    )
    management_table = _edit_table(management_table, key="cost.management")

    st.markdown("### Fixed Overhead")
    fixed_overhead_table = _year_table(
        [
            ("Advisory", "EUR", [row.advisory_eur for row in cost.fixed_overhead_by_year], ""),
            ("Legal", "EUR", [row.legal_eur for row in cost.fixed_overhead_by_year], ""),
            ("IT & Software", "EUR", [row.it_software_eur for row in cost.fixed_overhead_by_year], ""),
            ("Office Rent", "EUR", [row.office_rent_eur for row in cost.fixed_overhead_by_year], ""),
            ("Services", "EUR", [row.services_eur for row in cost.fixed_overhead_by_year], ""),
            ("Other Services", "EUR", [row.other_services_eur for row in cost.fixed_overhead_by_year], ""),
        ]
    )
    fixed_overhead_table = _edit_table(fixed_overhead_table, key="cost.fixed")

    st.markdown("### Variable Costs")
    variable_type_table = _year_table(
        [
            ("Training", "Type", [row.training_type for row in cost.variable_costs_by_year], ""),
            ("Travel", "Type", [row.travel_type for row in cost.variable_costs_by_year], ""),
            ("Communication", "Type", [row.communication_type for row in cost.variable_costs_by_year], ""),
        ]
    )
    variable_type_table = _edit_table(variable_type_table, key="cost.variable.type")
    variable_value_table = _year_table(
        [
            ("Training", "EUR / %", [row.training_value for row in cost.variable_costs_by_year], ""),
            ("Travel", "EUR / %", [row.travel_value for row in cost.variable_costs_by_year], ""),
            ("Communication", "EUR / %", [row.communication_value for row in cost.variable_costs_by_year], ""),
        ]
    )
    variable_value_table = _edit_table(variable_value_table, key="cost.variable.value")

    personnel_by_year = [
        PersonnelYearAssumptions(
            consultant_fte=_row_years_numeric(consultant_table, "Consultant FTE")[i],
            consultant_loaded_cost_eur=_row_years_numeric(consultant_table, "Consultant Loaded Cost")[i],
            backoffice_fte=_row_years_numeric(backoffice_table, "Backoffice FTE")[i],
            backoffice_loaded_cost_eur=_row_years_numeric(backoffice_table, "Backoffice Loaded Cost")[i],
            management_cost_eur=_row_years_numeric(management_table, "Management Cost")[i],
        )
        for i in range(5)
    ]
    fixed_overhead_by_year = [
        FixedOverheadYearAssumptions(
            advisory_eur=_row_years_numeric(fixed_overhead_table, "Advisory")[i],
            legal_eur=_row_years_numeric(fixed_overhead_table, "Legal")[i],
            it_software_eur=_row_years_numeric(fixed_overhead_table, "IT & Software")[i],
            office_rent_eur=_row_years_numeric(fixed_overhead_table, "Office Rent")[i],
            services_eur=_row_years_numeric(fixed_overhead_table, "Services")[i],
            other_services_eur=_row_years_numeric(fixed_overhead_table, "Other Services")[i],
        )
        for i in range(5)
    ]
    training_types = _row_years_text(variable_type_table, "Training")
    travel_types = _row_years_text(variable_type_table, "Travel")
    communication_types = _row_years_text(variable_type_table, "Communication")
    training_values = _row_years_numeric(variable_value_table, "Training")
    travel_values = _row_years_numeric(variable_value_table, "Travel")
    communication_values = _row_years_numeric(variable_value_table, "Communication")
    variable_costs_by_year = [
        VariableCostYearAssumptions(
            training_type=training_types[i],
            training_value=_normalize_variable_value(training_values[i], training_types[i]),
            travel_type=travel_types[i],
            travel_value=_normalize_variable_value(travel_values[i], travel_types[i]),
            communication_type=communication_types[i],
            communication_value=_normalize_variable_value(communication_values[i], communication_types[i]),
        )
        for i in range(5)
    ]
    inflation_apply = (
        str(_row_value(inflation_table, "Apply Inflation")).strip().lower()
        in {"yes", "true"}
    )
    inflation_rate = (
        _to_float(_row_value(inflation_table, "Inflation Rate (% p.a.)"))
        if "inflation_table" in locals()
        else cost.inflation_rate_pct
    )

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=CostAssumptions(
            inflation_apply=inflation_apply,
            inflation_rate_pct=inflation_rate,
            personnel_by_year=personnel_by_year,
            fixed_overhead_by_year=fixed_overhead_by_year,
            variable_costs_by_year=variable_costs_by_year,
        ),
        transaction_and_financing=assumptions.transaction_and_financing,
        financing=assumptions.financing,
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=assumptions.valuation,
    )


def render_financing_assumptions(assumptions: Assumptions) -> Assumptions:
    transaction = assumptions.transaction_and_financing
    financing = assumptions.financing

    st.markdown("### Quick Inputs")
    quick_table = _value_table(
        [
            ("Purchase Price", "EUR", transaction.purchase_price_eur, "Transaction entry price."),
            ("Owner Contribution", "EUR", transaction.equity_contribution_eur, "Owner cash at close."),
            ("Senior Loan Amount", "EUR", financing.senior_debt_amount_eur, "Starting loan amount."),
            ("Interest Rate", "% p.a.", financing.interest_rate_pct, "Loan interest rate."),
            ("Repayment Type", "", financing.amortization_type, "Straight-line or lump-sum."),
            ("Repayment Period (Years)", "Years", financing.amortization_period_years, "Repayment length."),
        ]
    )
    quick_table = _edit_table(quick_table, key="financing.quick")
    st.markdown("---")

    with st.expander("Advanced Financing Inputs", expanded=False):
        st.markdown("#### Transaction & Financing")
        transaction_table = _value_table(
            [
                ("Senior Loan Start", "EUR", transaction.senior_term_loan_start_eur, ""),
            ]
        )
        transaction_table = _edit_table(transaction_table, key="financing.transaction")

        st.markdown("#### Loan Terms")
        financing_table = _value_table(
            [
                ("Opening Loan Balance", "EUR", financing.initial_debt_eur, ""),
                ("Interest-Only Period (Years)", "Years", financing.grace_period_years, ""),
                ("One-Time Repayment Year (None/Year X)", "", _format_special_year(financing.special_repayment_year), ""),
                ("One-Time Repayment Amount", "EUR", financing.special_repayment_amount_eur, ""),
                ("Minimum Loan Coverage", "", financing.minimum_dscr, ""),
            ]
        )
        financing_table = _edit_table(financing_table, key="financing.terms")

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=TransactionFinancingAssumptions(
            purchase_price_eur=_to_float(_row_value(quick_table, "Purchase Price")),
            equity_contribution_eur=_to_float(
                _row_value(quick_table, "Owner Contribution")
            ),
            senior_term_loan_start_eur=_to_float(
                _row_value(transaction_table, "Senior Loan Start")
            )
            if "transaction_table" in locals()
            else transaction.senior_term_loan_start_eur,
        ),
        financing=FinancingAssumptions(
            senior_debt_amount_eur=_to_float(_row_value(quick_table, "Senior Loan Amount")),
            initial_debt_eur=_to_float(
                _row_value(financing_table, "Opening Loan Balance")
            )
            if "financing_table" in locals()
            else financing.initial_debt_eur,
            interest_rate_pct=_to_float(_row_value(quick_table, "Interest Rate")),
            amortization_type=str(_row_value(quick_table, "Repayment Type")).strip() or "Linear",
            amortization_period_years=int(
                _to_float(_row_value(quick_table, "Repayment Period (Years)") or 0)
            ),
            grace_period_years=int(
                _to_float(_row_value(financing_table, "Interest-Only Period (Years)") or 0)
            )
            if "financing_table" in locals()
            else financing.grace_period_years,
            special_repayment_year=_parse_special_year(
                str(_row_value(financing_table, "One-Time Repayment Year (None/Year X)")).strip()
            )
            if "financing_table" in locals()
            else financing.special_repayment_year,
            special_repayment_amount_eur=_to_float(
                _row_value(financing_table, "One-Time Repayment Amount")
            )
            if "financing_table" in locals()
            else financing.special_repayment_amount_eur,
            minimum_dscr=_to_float(_row_value(financing_table, "Minimum Loan Coverage"))
            if "financing_table" in locals()
            else financing.minimum_dscr,
        ),
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=assumptions.valuation,
    )


def render_revenue_quick_inputs(assumptions: Assumptions) -> Assumptions:
    scenario = assumptions.scenario
    scenarios = dict(assumptions.revenue.scenarios)
    current = scenarios[scenario]

    quick_table = _year_table(
        [
            ("Workdays per Year", "Days", current.workdays_per_year, "Billable calendar days."),
            ("Utilization Rate", "%", current.utilization_rate_pct, "Share of billable time."),
            ("Group Day Rate", "EUR", current.group_day_rate_eur, "Contracted group pricing."),
            ("External Day Rate", "EUR", current.external_day_rate_eur, "Market upside pricing."),
            ("Guarantee %", "%", current.guarantee_pct_by_year, "Floor applied to group revenue."),
        ]
    )
    quick_table = _edit_table(quick_table, key="wizard.revenue")

    reference_table = _value_table(
        [("Reference Revenue", "EUR", current.reference_revenue_eur, "")]
    )
    reference_table = _edit_table(reference_table, key="wizard.revenue.reference")

    scenarios[scenario] = RevenueScenarioAssumptions(
        workdays_per_year=_row_years_numeric(quick_table, "Workdays per Year"),
        utilization_rate_pct=_row_years_numeric(quick_table, "Utilization Rate"),
        group_day_rate_eur=_row_years_numeric(quick_table, "Group Day Rate"),
        external_day_rate_eur=_row_years_numeric(quick_table, "External Day Rate"),
        day_rate_growth_pct=current.day_rate_growth_pct,
        revenue_growth_pct=current.revenue_growth_pct,
        group_capacity_share_pct=current.group_capacity_share_pct,
        external_capacity_share_pct=current.external_capacity_share_pct,
        reference_revenue_eur=_to_float(_row_value(reference_table, "Reference Revenue")),
        guarantee_pct_by_year=_row_years_numeric(quick_table, "Guarantee %"),
    )

    return Assumptions(
        scenario=scenario,
        revenue=RevenueAssumptions(scenarios=scenarios),
        cost=assumptions.cost,
        transaction_and_financing=assumptions.transaction_and_financing,
        financing=assumptions.financing,
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=assumptions.valuation,
    )


def render_cost_quick_inputs(assumptions: Assumptions) -> Assumptions:
    cost = assumptions.cost
    quick_table = _year_table(
        [
            ("Consultant Headcount", "People", [row.consultant_fte for row in cost.personnel_by_year], "Delivery capacity."),
            ("Consultant Cost (All-in)", "EUR", [row.consultant_loaded_cost_eur for row in cost.personnel_by_year], "Fully loaded cost per person."),
            ("Backoffice Headcount", "People", [row.backoffice_fte for row in cost.personnel_by_year], "Support capacity."),
            ("Backoffice Cost (All-in)", "EUR", [row.backoffice_loaded_cost_eur for row in cost.personnel_by_year], "Fully loaded cost per person."),
            ("Management Cost", "EUR", [row.management_cost_eur for row in cost.personnel_by_year], "Fixed leadership cost."),
        ]
    )
    quick_table = _edit_table(quick_table, key="wizard.cost")

    personnel_by_year = [
        PersonnelYearAssumptions(
            consultant_fte=_row_years_numeric(quick_table, "Consultant Headcount")[i],
            consultant_loaded_cost_eur=_row_years_numeric(quick_table, "Consultant Cost (All-in)")[i],
            backoffice_fte=_row_years_numeric(quick_table, "Backoffice Headcount")[i],
            backoffice_loaded_cost_eur=_row_years_numeric(quick_table, "Backoffice Cost (All-in)")[i],
            management_cost_eur=_row_years_numeric(quick_table, "Management Cost")[i],
        )
        for i in range(5)
    ]

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=CostAssumptions(
            inflation_apply=cost.inflation_apply,
            inflation_rate_pct=cost.inflation_rate_pct,
            personnel_by_year=personnel_by_year,
            fixed_overhead_by_year=cost.fixed_overhead_by_year,
            variable_costs_by_year=cost.variable_costs_by_year,
        ),
        transaction_and_financing=assumptions.transaction_and_financing,
        financing=assumptions.financing,
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=assumptions.valuation,
    )


def render_financing_quick_inputs(assumptions: Assumptions) -> Assumptions:
    finance = assumptions.financing
    table = _value_table(
        [
            ("Senior Loan Amount", "EUR", finance.senior_debt_amount_eur, "Starting loan amount."),
            ("Opening Loan Balance", "EUR", finance.initial_debt_eur, "Drawn at close."),
            ("Interest Rate", "% p.a.", finance.interest_rate_pct, "Loan interest rate."),
            ("Repayment Type", "", finance.amortization_type, "Straight-line or lump-sum."),
            ("Repayment Period (Years)", "Years", finance.amortization_period_years, "Repayment length."),
            ("Interest-Only Period (Years)", "Years", finance.grace_period_years, "Initial interest-only years."),
            ("Minimum Loan Coverage", "", finance.minimum_dscr, "Coverage threshold."),
        ]
    )
    table = _edit_table(table, key="wizard.financing")

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=assumptions.transaction_and_financing,
        financing=FinancingAssumptions(
            senior_debt_amount_eur=_to_float(_row_value(table, "Senior Loan Amount")),
            initial_debt_eur=_to_float(_row_value(table, "Opening Loan Balance")),
            interest_rate_pct=_to_float(_row_value(table, "Interest Rate")),
            amortization_type=str(_row_value(table, "Repayment Type")).strip() or "Linear",
            amortization_period_years=int(
                _to_float(_row_value(table, "Repayment Period (Years)") or 0)
            ),
            grace_period_years=int(
                _to_float(_row_value(table, "Interest-Only Period (Years)") or 0)
            ),
            special_repayment_year=finance.special_repayment_year,
            special_repayment_amount_eur=finance.special_repayment_amount_eur,
            minimum_dscr=_to_float(_row_value(table, "Minimum Loan Coverage")),
        ),
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=assumptions.valuation,
    )


def render_valuation_quick_inputs(assumptions: Assumptions) -> Assumptions:
    table = _value_table(
        [
            ("Purchase Price", "EUR", assumptions.transaction_and_financing.purchase_price_eur, "Entry consideration."),
            ("Seller Multiple (x Operating Profit)", "x", assumptions.valuation.seller_multiple, "Exit multiple assumption."),
        ]
    )
    table = _edit_table(table, key="wizard.valuation")

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=TransactionFinancingAssumptions(
            purchase_price_eur=_to_float(_row_value(table, "Purchase Price")),
            equity_contribution_eur=assumptions.transaction_and_financing.equity_contribution_eur,
            senior_term_loan_start_eur=assumptions.transaction_and_financing.senior_term_loan_start_eur,
        ),
        financing=assumptions.financing,
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=ValuationAssumptions(
            seller_multiple=_to_float(_row_value(table, "Seller Multiple (x Operating Profit)"))
        ),
    )


def render_other_assumptions(assumptions: Assumptions) -> Assumptions:
    st.markdown("### Financing Assumptions")
    financing_table = _value_table(
        [
            ("Senior Debt Amount", "EUR", assumptions.financing.senior_debt_amount_eur, "Opening senior term loan."),
            ("Interest Rate", "%", assumptions.financing.interest_rate_pct, "Fixed interest rate."),
            ("Amortisation Years", "Years", assumptions.financing.amortization_period_years, "Linear amortisation period."),
            ("Transaction Fees (%)", "%", 0.01, "Fees as % of EV."),
        ]
    )
    financing_table = _edit_table(financing_table, key="other.financing")

    st.markdown("### Equity & Investor Assumptions")
    investor_equity = max(
        assumptions.transaction_and_financing.purchase_price_eur
        - assumptions.financing.senior_debt_amount_eur
        - assumptions.transaction_and_financing.equity_contribution_eur,
        0.0,
    )
    equity_table = _value_table(
        [
            ("Sponsor Equity Contribution", "EUR", assumptions.transaction_and_financing.equity_contribution_eur, "Management equity contribution."),
            ("Investor Equity Contribution", "EUR", investor_equity, "External investor contribution."),
            ("Investor Exit Year", "Year", 4, "Exit year for investor."),
            ("Exit Multiple (x Operating Profit)", "x", assumptions.valuation.seller_multiple, "Exit multiple on operating profit."),
            ("Distribution Rule", "", "Pro-rata", "Fixed distribution rule."),
        ]
    )
    equity_table = _edit_table(equity_table, key="other.equity")
    exit_multiple_value = _to_float(_row_value(equity_table, "Exit Multiple (x Operating Profit)"))

    st.markdown("### Cashflow Assumptions")
    cashflow_table = _value_table(
        [
            ("Tax Cash Rate", "%", assumptions.cashflow.tax_cash_rate_pct, "Cash tax rate on profit before tax."),
            ("Tax Payment Lag", "Years", assumptions.cashflow.tax_payment_lag_years, "Timing lag for cash taxes."),
            ("Capex (% of Revenue)", "%", assumptions.cashflow.capex_pct_revenue, "Capex as % of revenue."),
            (
                "Working Capital (% of Revenue)",
                "%",
                assumptions.cashflow.working_capital_pct_revenue,
                "Working capital adjustment.",
            ),
            ("Opening Cash Balance", "EUR", assumptions.cashflow.opening_cash_balance_eur, "Opening cash balance."),
        ]
    )
    cashflow_table = _edit_table(cashflow_table, key="other.cashflow")

    st.markdown("### Balance Sheet Assumptions")
    balance_sheet_table = _value_table(
        [
            ("Opening Equity", "EUR", assumptions.balance_sheet.opening_equity_eur, "Opening equity value."),
            ("Depreciation Rate", "%", assumptions.balance_sheet.depreciation_rate_pct, "Fixed asset depreciation rate."),
            ("Minimum Cash Balance", "EUR", 250_000.0, "Minimum cash balance."),
        ]
    )
    balance_sheet_table = _edit_table(balance_sheet_table, key="other.balance_sheet")

    st.markdown("### Valuation Assumptions")
    valuation_table = _value_table(
        [
            ("Seller Operating Profit Multiple", "x", exit_multiple_value, "Operating profit multiple for seller view."),
            ("Reference Year", "Year", 1, "Reference year for multiple."),
            ("Discount Rate (Cost of Capital)", "%", 0.10, "DCF discount rate."),
            ("Valuation Start Year", "Year", 0, "DCF start year."),
            ("Transaction Costs (%)", "%", 0.01, "Fees as % of EV."),
        ]
    )
    valuation_table = _edit_table(valuation_table, key="other.valuation")

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=TransactionFinancingAssumptions(
            equity_contribution_eur=_to_float(_row_value(equity_table, "Sponsor Equity Contribution")),
            purchase_price_eur=assumptions.transaction_and_financing.purchase_price_eur,
            senior_term_loan_start_eur=assumptions.transaction_and_financing.senior_term_loan_start_eur,
        ),
        financing=FinancingAssumptions(
            senior_debt_amount_eur=_to_float(_row_value(financing_table, "Senior Debt Amount")),
            initial_debt_eur=assumptions.financing.initial_debt_eur,
            interest_rate_pct=_to_float(_row_value(financing_table, "Interest Rate")),
            amortization_type=assumptions.financing.amortization_type,
            amortization_period_years=int(_to_float(_row_value(financing_table, "Amortisation Years") or 0)),
            grace_period_years=assumptions.financing.grace_period_years,
            special_repayment_year=assumptions.financing.special_repayment_year,
            special_repayment_amount_eur=assumptions.financing.special_repayment_amount_eur,
            minimum_dscr=assumptions.financing.minimum_dscr,
        ),
        cashflow=assumptions.cashflow.__class__(
            tax_cash_rate_pct=_to_float(_row_value(cashflow_table, "Tax Cash Rate")),
            tax_payment_lag_years=int(_to_float(_row_value(cashflow_table, "Tax Payment Lag") or 0)),
            capex_pct_revenue=_to_float(_row_value(cashflow_table, "Capex (% of Revenue)")),
            working_capital_pct_revenue=_to_float(_row_value(cashflow_table, "Working Capital (% of Revenue)")),
            opening_cash_balance_eur=_to_float(_row_value(cashflow_table, "Opening Cash Balance")),
        ),
        balance_sheet=assumptions.balance_sheet.__class__(
            opening_equity_eur=_to_float(_row_value(balance_sheet_table, "Opening Equity")),
            depreciation_rate_pct=_to_float(_row_value(balance_sheet_table, "Depreciation Rate")),
        ),
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=ValuationAssumptions(
            seller_multiple=_to_float(_row_value(valuation_table, "Seller Operating Profit Multiple"))
        ),
    )


def _scenario_table(assumptions: Assumptions) -> str:
    scenario_table = _value_table(
        [("Scenario (Base/Best/Worst)", "", assumptions.scenario, "")]
    )
    scenario_table = _edit_table(scenario_table, key="scenario.table")
    scenario = str(_row_value(scenario_table, "Scenario (Base/Best/Worst)")).strip()
    if scenario not in {"Base", "Best", "Worst"}:
        return assumptions.scenario
    return scenario


def _year_table(rows: List[tuple]) -> List[dict]:
    table = []
    for name, unit, values, _notes in rows:
        row = {"Parameter": name, "Unit": unit}
        for idx, year in enumerate(YEARS):
            row[year] = _display_value(values[idx], unit)
        table.append(row)
    return table


def _value_table(rows: List[tuple]) -> List[dict]:
    table = []
    has_notes = any(note for _, _, _, note in rows)
    for name, unit, value, note in rows:
        row = {
            "Parameter": name,
            "Value": _display_value(value, unit),
            "Unit": unit,
        }
        if has_notes:
            row["Notes"] = note
        table.append(row)
    return table


def _edit_table(table: List[dict], key: str) -> List[dict]:
    edited = st.data_editor(
        table,
        use_container_width=True,
        key=key,
        hide_index=True,
        disabled=["Parameter", "Unit", "Notes"],
    )
    if edited is None:
        return table
    if isinstance(edited, list):
        return edited
    if hasattr(edited, "to_dict"):
        return edited.to_dict(orient="records")
    return table


def _row_years_numeric(table: List[dict], name: str) -> List[float]:
    for row in table:
        if row.get("Parameter") == name:
            unit = str(row.get("Unit", "")).strip()
            values = [_to_float(row.get(year, 0.0)) for year in YEARS]
            if _is_percent_unit(unit):
                return [value / 100 for value in values]
            return values
    return [0.0 for _ in YEARS]


def _row_years_text(table: List[dict], name: str) -> List[str]:
    for row in table:
        if row.get("Parameter") == name:
            return [str(row.get(year, "") or "") for year in YEARS]
    return ["" for _ in YEARS]


def _row_value(table: List[dict], name: str):
    for row in table:
        if row.get("Parameter") == name:
            value = row.get("Value", row.get(YEARS[0], 0.0))
            unit = str(row.get("Unit", "")).strip()
            if isinstance(value, str) and _looks_like_text(value):
                return value
            if _is_percent_unit(unit):
                return _to_float(value) / 100
            return _to_float(value)
    return 0.0


def _to_float(value) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        text = str(value).replace(",", "").strip().lower()
        multiplier = 1.0
        if text.endswith("%"):
            text = text[:-1]
        text = text.replace("eur", "").replace("€", "").strip()
        if text.endswith("k"):
            multiplier = 1_000.0
            text = text[:-1]
        if text.endswith("m"):
            multiplier = 1_000_000.0
            text = text[:-1]
        return float(text) * multiplier
    except ValueError:
        return 0.0


def _display_value(value, unit: str):
    number = value
    if isinstance(value, str):
        return value
    if _is_percent_unit(str(unit).strip()):
        return f"{float(number) * 100:,.1f}" if number is not None else "0.0"
    if str(unit).strip() in {"Year", "Years"}:
        return f"{float(number):,.0f}" if number is not None else "0"
    if _is_currency_unit(str(unit).strip()):
        return _format_currency_display(number)
    return f"{float(number):,.2f}" if number is not None else "0.00"


def _is_percent_unit(unit: str) -> bool:
    return unit in {"%", "% p.a."}


def _is_currency_unit(unit: str) -> bool:
    return "EUR" in unit and "%" not in unit


def _format_currency_display(value: float) -> str:
    if value is None:
        return "0"
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


def _looks_like_text(value: str) -> bool:
    text = value.strip().lower()
    if text in {"yes", "no", "linear", "bullet", "straight-line", "lump-sum", "none"}:
        return True
    if text.startswith("year"):
        return True
    return not any(char.isdigit() for char in text)


def _format_special_year(value: int | None) -> str:
    if value is None:
        return "None"
    return f"Year {value}"


def _parse_special_year(value: str) -> int | None:
    if value.lower() == "none":
        return None
    if value.lower().startswith("year"):
        try:
            return int(value.split(" ")[1])
        except (IndexError, ValueError):
            return None
    return None


def _normalize_variable_value(value: float, cost_type: str) -> float:
    if str(cost_type).strip() == "%":
        return value / 100
    return value
