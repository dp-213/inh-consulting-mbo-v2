from __future__ import annotations

from dataclasses import replace
from typing import List

import streamlit as st

from ui.outputs import build_year_labels
from state.assumptions import (
    Assumptions,
    BalanceSheetAssumptions,
    CashflowAssumptions,
    CostAssumptions,
    EquityAssumptions,
    FinancingAssumptions,
    FixedOverheadYearAssumptions,
    PersonnelYearAssumptions,
    RevenueAssumptions,
    RevenueScenarioAssumptions,
    TransactionFinancingAssumptions,
    ValuationAssumptions,
    VariableCostYearAssumptions,
)

YEARS = build_year_labels(5)
MILLION = 1_000_000.0


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
            ("Reference Revenue", "m€", [_to_meur(current.reference_revenue_eur) for _ in range(5)], ""),
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
        equity=assumptions.equity,
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
        equity=assumptions.equity,
    )


def render_financing_assumptions(assumptions: Assumptions) -> Assumptions:
    transaction = assumptions.transaction_and_financing
    financing = assumptions.financing

    st.markdown("### Quick Inputs")
    repayment_options = _options_with_current(["Linear", "Bullet"], financing.amortization_type)
    repayment_type = st.selectbox(
        "Repayment Type",
        repayment_options,
        index=repayment_options.index(financing.amortization_type)
        if financing.amortization_type in repayment_options
        else 0,
        key="financing.quick.repayment_type",
    )
    quick_table = _value_table(
        [
            ("Purchase Price", "m€", _to_meur(transaction.purchase_price_eur), "Transaction entry price."),
            ("Owner Contribution", "m€", _to_meur(transaction.equity_contribution_eur), "Owner cash at close."),
            ("Senior Loan Amount", "m€", _to_meur(financing.senior_debt_amount_eur), "Starting loan amount."),
            ("Interest Rate", "% p.a.", financing.interest_rate_pct, "Loan interest rate."),
            ("Repayment Period (Years)", "Years", financing.amortization_period_years, "Repayment length."),
        ]
    )
    quick_table = _edit_table(quick_table, key="financing.quick")
    st.markdown("---")

    with st.expander("Advanced Financing Inputs", expanded=False):
        st.markdown("#### Transaction & Financing")
        transaction_table = _value_table(
            [
                ("Senior Loan Start", "m€", _to_meur(transaction.senior_term_loan_start_eur), ""),
            ]
        )
        transaction_table = _edit_table(transaction_table, key="financing.transaction")

        st.markdown("#### Loan Terms")
        special_year_options = ["None"] + YEARS
        special_year_value = (
            YEARS[financing.special_repayment_year]
            if financing.special_repayment_year is not None
            and 0 <= financing.special_repayment_year < len(YEARS)
            else "None"
        )
        special_year = st.selectbox(
            "One-Time Repayment Year",
            special_year_options,
            index=special_year_options.index(special_year_value),
            key="financing.terms.special_year",
        )
        financing_table = _value_table(
            [
                ("Opening Loan Balance", "m€", _to_meur(financing.initial_debt_eur), ""),
                ("Interest-Only Period (Years)", "Years", financing.grace_period_years, ""),
                ("One-Time Repayment Amount", "m€", _to_meur(financing.special_repayment_amount_eur), ""),
                ("Minimum Loan Coverage", "", financing.minimum_dscr, ""),
            ]
        )
        financing_table = _edit_table(financing_table, key="financing.terms")

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=TransactionFinancingAssumptions(
            purchase_price_eur=_from_meur(_row_value(quick_table, "Purchase Price")),
            equity_contribution_eur=_from_meur(
                _row_value(quick_table, "Owner Contribution")
            ),
            senior_term_loan_start_eur=_from_meur(
                _row_value(transaction_table, "Senior Loan Start")
            )
            if "transaction_table" in locals()
            else transaction.senior_term_loan_start_eur,
        ),
        financing=FinancingAssumptions(
            senior_debt_amount_eur=_from_meur(_row_value(quick_table, "Senior Loan Amount")),
            initial_debt_eur=_from_meur(
                _row_value(financing_table, "Opening Loan Balance")
            )
            if "financing_table" in locals()
            else financing.initial_debt_eur,
            interest_rate_pct=_to_float(_row_value(quick_table, "Interest Rate")),
            amortization_type=repayment_type,
            amortization_period_years=int(
                _to_float(_row_value(quick_table, "Repayment Period (Years)") or 0)
            ),
            grace_period_years=int(
                _to_float(_row_value(financing_table, "Interest-Only Period (Years)") or 0)
            )
            if "financing_table" in locals()
            else financing.grace_period_years,
            special_repayment_year=_parse_year_option(special_year)
            if "financing_table" in locals()
            else financing.special_repayment_year,
            special_repayment_amount_eur=_from_meur(
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
        equity=assumptions.equity,
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
        [("Reference Revenue", "m€", _to_meur(current.reference_revenue_eur), "")]
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
        reference_revenue_eur=_from_meur(_row_value(reference_table, "Reference Revenue")),
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
        equity=assumptions.equity,
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
        equity=assumptions.equity,
    )


def render_financing_quick_inputs(assumptions: Assumptions) -> Assumptions:
    finance = assumptions.financing
    repayment_options = _options_with_current(["Linear", "Bullet"], finance.amortization_type)
    repayment_type = st.selectbox(
        "Repayment Type",
        repayment_options,
        index=repayment_options.index(finance.amortization_type)
        if finance.amortization_type in repayment_options
        else 0,
        key="wizard.financing.repayment_type",
    )
    table = _value_table(
        [
            ("Senior Loan Amount", "m€", _to_meur(finance.senior_debt_amount_eur), "Starting loan amount."),
            ("Opening Loan Balance", "m€", _to_meur(finance.initial_debt_eur), "Drawn at close."),
            ("Interest Rate", "% p.a.", finance.interest_rate_pct, "Loan interest rate."),
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
            senior_debt_amount_eur=_from_meur(_row_value(table, "Senior Loan Amount")),
            initial_debt_eur=_from_meur(_row_value(table, "Opening Loan Balance")),
            interest_rate_pct=_to_float(_row_value(table, "Interest Rate")),
            amortization_type=repayment_type,
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
        equity=assumptions.equity,
    )


def render_valuation_quick_inputs(assumptions: Assumptions) -> Assumptions:
    table = _value_table(
        [
            ("Purchase Price", "m€", _to_meur(assumptions.transaction_and_financing.purchase_price_eur), "Entry consideration."),
            ("Seller Multiple (x Operating Profit)", "x", assumptions.valuation.seller_multiple, "Exit multiple assumption."),
        ]
    )
    table = _edit_table(table, key="wizard.valuation")

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=TransactionFinancingAssumptions(
            purchase_price_eur=_from_meur(_row_value(table, "Purchase Price")),
            equity_contribution_eur=assumptions.transaction_and_financing.equity_contribution_eur,
            senior_term_loan_start_eur=assumptions.transaction_and_financing.senior_term_loan_start_eur,
        ),
        financing=assumptions.financing,
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=ValuationAssumptions(
            seller_multiple=_to_float(_row_value(table, "Seller Multiple (x Operating Profit)")),
            reference_year=assumptions.valuation.reference_year,
            discount_rate_pct=assumptions.valuation.discount_rate_pct,
            valuation_start_year=assumptions.valuation.valuation_start_year,
            transaction_costs_pct=assumptions.valuation.transaction_costs_pct,
        ),
        equity=assumptions.equity,
    )


def render_cashflow_key_assumptions(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    cashflow = assumptions.cashflow
    table = _value_table(
        [
            ("Tax Cash Rate", "%", cashflow.tax_cash_rate_pct, ""),
            ("Tax Payment Lag", "Years", cashflow.tax_payment_lag_years, ""),
            ("Capex (% of Revenue)", "%", cashflow.capex_pct_revenue, ""),
            ("Working Capital (% of Revenue)", "%", cashflow.working_capital_pct_revenue, ""),
            ("Opening Cash Balance", "m€", _to_meur(cashflow.opening_cash_balance_eur), ""),
        ]
    )
    table = _edit_table(table, key=f"{key_prefix}.cashflow")
    _require_value(table, "Tax Cash Rate")
    _require_value(table, "Tax Payment Lag")
    _require_value(table, "Capex (% of Revenue)")
    _require_value(table, "Working Capital (% of Revenue)")
    _require_value(table, "Opening Cash Balance")
    updated_cashflow = CashflowAssumptions(
        tax_cash_rate_pct=_to_float(_row_value(table, "Tax Cash Rate")),
        tax_payment_lag_years=int(_to_float(_row_value(table, "Tax Payment Lag"))),
        capex_pct_revenue=_to_float(_row_value(table, "Capex (% of Revenue)")),
        working_capital_pct_revenue=_to_float(_row_value(table, "Working Capital (% of Revenue)")),
        opening_cash_balance_eur=_from_meur(_row_value(table, "Opening Cash Balance")),
    )
    return replace(assumptions, cashflow=updated_cashflow)


def render_balance_sheet_key_assumptions(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    balance_sheet = assumptions.balance_sheet
    table = _value_table(
        [
            ("Opening Equity", "m€", _to_meur(balance_sheet.opening_equity_eur), ""),
            ("Depreciation Rate", "%", balance_sheet.depreciation_rate_pct, ""),
            ("Minimum Cash Balance", "m€", _to_meur(balance_sheet.minimum_cash_balance_eur), ""),
            ("Pension Obligations at Close", "m€", _to_meur(balance_sheet.pension_obligations_eur), ""),
        ]
    )
    table = _edit_table(table, key=f"{key_prefix}.balance_sheet")
    _require_value(table, "Opening Equity")
    _require_value(table, "Depreciation Rate")
    _require_value(table, "Minimum Cash Balance")
    _require_value(table, "Pension Obligations at Close")
    updated_balance_sheet = BalanceSheetAssumptions(
        opening_equity_eur=_from_meur(_row_value(table, "Opening Equity")),
        depreciation_rate_pct=_to_float(_row_value(table, "Depreciation Rate")),
        minimum_cash_balance_eur=_from_meur(_row_value(table, "Minimum Cash Balance")),
        pension_obligations_eur=_from_meur(_row_value(table, "Pension Obligations at Close")),
    )
    return replace(assumptions, balance_sheet=updated_balance_sheet)


def render_financing_key_assumptions(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    financing = assumptions.financing
    amortization_options = _options_with_current(["Linear", "Bullet"], financing.amortization_type)
    repayment_type = st.selectbox(
        "Repayment Type",
        amortization_options,
        index=amortization_options.index(financing.amortization_type)
        if financing.amortization_type in amortization_options
        else 0,
        key=f"{key_prefix}.repayment_type",
    )
    year_options = ["None"] + YEARS
    special_year_value = (
        YEARS[financing.special_repayment_year]
        if financing.special_repayment_year is not None
        and 0 <= financing.special_repayment_year < len(YEARS)
        else "None"
    )
    special_year = st.selectbox(
        "One-Time Repayment Year",
        year_options,
        index=year_options.index(special_year_value),
        key=f"{key_prefix}.special_repayment_year",
    )
    table = _value_table(
        [
            ("Debt Amount", "m€", _to_meur(financing.senior_debt_amount_eur), ""),
            ("Opening Loan Balance", "m€", _to_meur(financing.initial_debt_eur), ""),
            ("Interest Rate", "% p.a.", financing.interest_rate_pct, ""),
            ("Repayment Period (Years)", "Years", financing.amortization_period_years, ""),
            ("Interest-Only Period (Years)", "Years", financing.grace_period_years, ""),
            ("One-Time Repayment Amount", "m€", _to_meur(financing.special_repayment_amount_eur), ""),
            ("Minimum DSCR", "", financing.minimum_dscr, ""),
        ]
    )
    table = _edit_table(table, key=f"{key_prefix}.financing")
    _require_value(table, "Debt Amount")
    _require_value(table, "Opening Loan Balance")
    _require_value(table, "Interest Rate")
    _require_value(table, "Repayment Period (Years)")
    _require_value(table, "Interest-Only Period (Years)")
    _require_value(table, "One-Time Repayment Amount")
    _require_value(table, "Minimum DSCR")
    updated_financing = FinancingAssumptions(
        senior_debt_amount_eur=_from_meur(_row_value(table, "Debt Amount")),
        initial_debt_eur=_from_meur(_row_value(table, "Opening Loan Balance")),
        interest_rate_pct=_to_float(_row_value(table, "Interest Rate")),
        amortization_type=repayment_type,
        amortization_period_years=int(_to_float(_row_value(table, "Repayment Period (Years)"))),
        grace_period_years=int(_to_float(_row_value(table, "Interest-Only Period (Years)"))),
        special_repayment_year=_parse_year_option(special_year),
        special_repayment_amount_eur=_from_meur(_row_value(table, "One-Time Repayment Amount")),
        minimum_dscr=_to_float(_row_value(table, "Minimum DSCR")),
    )
    return replace(assumptions, financing=updated_financing)


def render_valuation_key_assumptions(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    valuation = assumptions.valuation
    table = _value_table(
        [
            ("Seller Multiple", "x", valuation.seller_multiple, ""),
            ("Reference Year", "Year", valuation.reference_year, ""),
            ("Discount Rate", "%", valuation.discount_rate_pct, ""),
            ("Valuation Start Year", "Year", valuation.valuation_start_year, ""),
            ("Transaction Costs (%)", "%", valuation.transaction_costs_pct, ""),
        ]
    )
    table = _edit_table(table, key=f"{key_prefix}.valuation")
    _require_value(table, "Seller Multiple")
    _require_value(table, "Reference Year")
    _require_value(table, "Discount Rate")
    _require_value(table, "Valuation Start Year")
    _require_value(table, "Transaction Costs (%)")
    updated_valuation = ValuationAssumptions(
        seller_multiple=_to_float(_row_value(table, "Seller Multiple")),
        reference_year=int(_to_float(_row_value(table, "Reference Year"))),
        discount_rate_pct=_to_float(_row_value(table, "Discount Rate")),
        valuation_start_year=int(_to_float(_row_value(table, "Valuation Start Year"))),
        transaction_costs_pct=_to_float(_row_value(table, "Transaction Costs (%)")),
    )
    return replace(assumptions, valuation=updated_valuation)


def render_equity_key_assumptions(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    equity = assumptions.equity
    transaction = assumptions.transaction_and_financing
    exit_year_options = YEARS
    exit_year_label = (
        YEARS[equity.exit_year]
        if 0 <= equity.exit_year < len(YEARS)
        else YEARS[0]
    )
    exit_year = st.selectbox(
        "Exit Year",
        exit_year_options,
        index=exit_year_options.index(exit_year_label),
        key=f"{key_prefix}.exit_year",
    )
    exit_mechanism_options = _options_with_current(
        ["Management buys out investor", "Third-party sale", "Investor buyout"],
        equity.exit_mechanism,
    )
    exit_mechanism = st.selectbox(
        "Exit Mechanism",
        exit_mechanism_options,
        index=exit_mechanism_options.index(equity.exit_mechanism)
        if equity.exit_mechanism in exit_mechanism_options
        else 0,
        key=f"{key_prefix}.exit_mechanism",
    )
    participation_options = _options_with_current(
        ["Pro-rata", "Preferred return", "Waterfall"],
        equity.investor_participation,
    )
    investor_participation = st.selectbox(
        "Investor Participation",
        participation_options,
        index=participation_options.index(equity.investor_participation)
        if equity.investor_participation in participation_options
        else 0,
        key=f"{key_prefix}.investor_participation",
    )
    management_participation = st.selectbox(
        "Management Participation",
        participation_options,
        index=participation_options.index(equity.management_participation)
        if equity.management_participation in participation_options
        else 0,
        key=f"{key_prefix}.management_participation",
    )
    table = _value_table(
        [
            ("Purchase Price", "m€", _to_meur(transaction.purchase_price_eur), ""),
            ("Management Equity Contribution", "m€", _to_meur(transaction.equity_contribution_eur), ""),
        ]
    )
    table = _edit_table(table, key=f"{key_prefix}.equity")
    _require_value(table, "Purchase Price")
    _require_value(table, "Management Equity Contribution")
    updated_transaction = TransactionFinancingAssumptions(
        purchase_price_eur=_from_meur(_row_value(table, "Purchase Price")),
        equity_contribution_eur=_from_meur(
            _row_value(table, "Management Equity Contribution")
        ),
        senior_term_loan_start_eur=transaction.senior_term_loan_start_eur,
    )
    updated_equity = EquityAssumptions(
        exit_year=_parse_year_option(exit_year),
        exit_mechanism=exit_mechanism,
        investor_participation=investor_participation,
        management_participation=management_participation,
    )
    return replace(
        assumptions,
        transaction_and_financing=updated_transaction,
        equity=updated_equity,
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
            if unit == "m€":
                return [value * MILLION for value in values]
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


def _require_value(table: List[dict], name: str) -> None:
    for row in table:
        if row.get("Parameter") == name:
            value = row.get("Value", row.get(YEARS[0], None))
            if value is None or str(value).strip() == "":
                st.error(f"Missing required assumption: {name}.")
                st.stop()
            return
    st.error(f"Missing required assumption: {name}.")
    st.stop()


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
    if str(unit).strip() == "m€":
        return f"{float(number):,.2f}" if number is not None else "0.00"
    if _is_currency_unit(str(unit).strip()):
        return _format_currency_display(number)
    return f"{float(number):,.2f}" if number is not None else "0.00"


def _is_percent_unit(unit: str) -> bool:
    return unit in {"%", "% p.a."}


def _is_currency_unit(unit: str) -> bool:
    return "EUR" in unit and "%" not in unit and "m€" not in unit


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


def _to_meur(value: float) -> float:
    return float(value) / MILLION if value is not None else 0.0


def _from_meur(value) -> float:
    return _to_float(value) * MILLION


def _options_with_current(options: List[str], current: str) -> List[str]:
    if current in options:
        return options
    return [current] + options


def _parse_year_option(value: str) -> int | None:
    if value == "None":
        return None
    if value in YEARS:
        return YEARS.index(value)
    return None


def _normalize_variable_value(value: float, cost_type: str) -> float:
    if str(cost_type).strip() == "%":
        return value / 100
    return value
