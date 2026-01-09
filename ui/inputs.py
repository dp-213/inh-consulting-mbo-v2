from __future__ import annotations

from typing import List

import streamlit as st

from state.assumptions import (
    Assumptions,
    BalanceSheetAssumptions,
    CashflowAssumptions,
    CostAssumptions,
    FinancingAssumptions,
    FixedOverheadYearAssumptions,
    PersonnelYearAssumptions,
    RevenueAssumptions,
    RevenueScenarioAssumptions,
    TaxAssumptions,
    TransactionFinancingAssumptions,
    ValuationAssumptions,
    VariableCostYearAssumptions,
)


def render_inputs(assumptions: Assumptions) -> Assumptions:
    scenario = st.selectbox(
        "Scenario",
        ["Base", "Best", "Worst"],
        index=["Base", "Best", "Worst"].index(assumptions.scenario),
    )

    revenue = _render_revenue_inputs(assumptions, scenario)
    cost = _render_cost_inputs(assumptions)
    transaction = _render_transaction_inputs(assumptions)
    financing = _render_financing_inputs(assumptions)
    cashflow = _render_cashflow_inputs(assumptions)
    balance_sheet = _render_balance_sheet_inputs(assumptions)
    tax = _render_tax_inputs(assumptions)
    valuation = _render_valuation_inputs(assumptions)

    return Assumptions(
        scenario=scenario,
        revenue=revenue,
        cost=cost,
        transaction_and_financing=transaction,
        financing=financing,
        cashflow=cashflow,
        balance_sheet=balance_sheet,
        tax_and_distributions=tax,
        valuation=valuation,
    )


def _render_revenue_inputs(
    assumptions: Assumptions, scenario: str
) -> RevenueAssumptions:
    scenarios = dict(assumptions.revenue.scenarios)
    current = scenarios[scenario]

    with st.expander("Revenue Model", expanded=True):
        workdays = _year_number_inputs(
            "Workdays per Year",
            current.workdays_per_year,
            step=1.0,
        )
        utilization = _year_percent_inputs(
            "Utilization (%)",
            current.utilization_rate_pct,
        )
        group_rate = _year_number_inputs(
            "Group Day Rate (EUR)",
            current.group_day_rate_eur,
            step=100.0,
        )
        external_rate = _year_number_inputs(
            "External Day Rate (EUR)",
            current.external_day_rate_eur,
            step=100.0,
        )
        rate_growth = _year_percent_inputs(
            "Day Rate Growth (% p.a.)",
            current.day_rate_growth_pct,
        )
        revenue_growth = _year_percent_inputs(
            "Revenue Growth (% p.a.)",
            current.revenue_growth_pct,
        )
        group_share = _year_percent_inputs(
            "Group Capacity Share (%)",
            current.group_capacity_share_pct,
        )
        external_share = _year_percent_inputs(
            "External Capacity Share (%)",
            current.external_capacity_share_pct,
        )
        reference_revenue = st.number_input(
            "Reference Revenue (EUR)",
            value=current.reference_revenue_eur,
            min_value=0.0,
            step=10_000.0,
        )
        guarantee = _year_percent_inputs(
            "Guarantee (%)",
            current.guarantee_pct_by_year,
        )

    scenarios[scenario] = RevenueScenarioAssumptions(
        workdays_per_year=workdays,
        utilization_rate_pct=utilization,
        group_day_rate_eur=group_rate,
        external_day_rate_eur=external_rate,
        day_rate_growth_pct=rate_growth,
        revenue_growth_pct=revenue_growth,
        group_capacity_share_pct=group_share,
        external_capacity_share_pct=external_share,
        reference_revenue_eur=reference_revenue,
        guarantee_pct_by_year=guarantee,
    )

    return RevenueAssumptions(scenarios=scenarios)


def _render_cost_inputs(assumptions: Assumptions) -> CostAssumptions:
    cost = assumptions.cost

    with st.expander("Cost Model", expanded=True):
        inflation_apply = st.selectbox(
            "Apply Inflation",
            ["No", "Yes"],
            index=1 if cost.inflation_apply else 0,
        )
        inflation_rate = st.number_input(
            "Inflation Rate (% p.a.)",
            value=cost.inflation_rate_pct * 100,
            min_value=0.0,
            step=0.1,
        )

        consultant_fte = _year_number_inputs(
            "Consultant FTE",
            [row.consultant_fte for row in cost.personnel_by_year],
            step=0.5,
        )
        consultant_cost = _year_number_inputs(
            "Consultant Loaded Cost (EUR)",
            [row.consultant_loaded_cost_eur for row in cost.personnel_by_year],
            step=1_000.0,
        )
        backoffice_fte = _year_number_inputs(
            "Backoffice FTE",
            [row.backoffice_fte for row in cost.personnel_by_year],
            step=0.5,
        )
        backoffice_cost = _year_number_inputs(
            "Backoffice Loaded Cost (EUR)",
            [row.backoffice_loaded_cost_eur for row in cost.personnel_by_year],
            step=1_000.0,
        )
        management_cost = _year_number_inputs(
            "Management Cost (EUR)",
            [row.management_cost_eur for row in cost.personnel_by_year],
            step=1_000.0,
        )

        advisory = _year_number_inputs(
            "Advisory (EUR)",
            [row.advisory_eur for row in cost.fixed_overhead_by_year],
            step=1_000.0,
        )
        legal = _year_number_inputs(
            "Legal (EUR)",
            [row.legal_eur for row in cost.fixed_overhead_by_year],
            step=1_000.0,
        )
        it_software = _year_number_inputs(
            "IT & Software (EUR)",
            [row.it_software_eur for row in cost.fixed_overhead_by_year],
            step=1_000.0,
        )
        office_rent = _year_number_inputs(
            "Office Rent (EUR)",
            [row.office_rent_eur for row in cost.fixed_overhead_by_year],
            step=1_000.0,
        )
        services = _year_number_inputs(
            "Services (EUR)",
            [row.services_eur for row in cost.fixed_overhead_by_year],
            step=1_000.0,
        )
        other_services = _year_number_inputs(
            "Other Services (EUR)",
            [row.other_services_eur for row in cost.fixed_overhead_by_year],
            step=1_000.0,
        )

        training = _variable_cost_inputs(
            "Training",
            cost.variable_costs_by_year,
        )
        travel = _variable_cost_inputs(
            "Travel",
            cost.variable_costs_by_year,
        )
        communication = _variable_cost_inputs(
            "Communication",
            cost.variable_costs_by_year,
        )

    personnel_by_year = [
        PersonnelYearAssumptions(
            consultant_fte=consultant_fte[i],
            consultant_loaded_cost_eur=consultant_cost[i],
            backoffice_fte=backoffice_fte[i],
            backoffice_loaded_cost_eur=backoffice_cost[i],
            management_cost_eur=management_cost[i],
        )
        for i in range(5)
    ]
    fixed_overhead_by_year = [
        FixedOverheadYearAssumptions(
            advisory_eur=advisory[i],
            legal_eur=legal[i],
            it_software_eur=it_software[i],
            office_rent_eur=office_rent[i],
            services_eur=services[i],
            other_services_eur=other_services[i],
        )
        for i in range(5)
    ]
    variable_costs_by_year = [
        VariableCostYearAssumptions(
            training_type=training["type"][i],
            training_value=training["value"][i],
            travel_type=travel["type"][i],
            travel_value=travel["value"][i],
            communication_type=communication["type"][i],
            communication_value=communication["value"][i],
        )
        for i in range(5)
    ]

    return CostAssumptions(
        inflation_apply=inflation_apply == "Yes",
        inflation_rate_pct=inflation_rate / 100,
        personnel_by_year=personnel_by_year,
        fixed_overhead_by_year=fixed_overhead_by_year,
        variable_costs_by_year=variable_costs_by_year,
    )


def _render_transaction_inputs(
    assumptions: Assumptions,
) -> TransactionFinancingAssumptions:
    with st.expander("Transaction & Financing", expanded=True):
        purchase_price = st.number_input(
            "Purchase Price (EUR)",
            value=assumptions.transaction_and_financing.purchase_price_eur,
            min_value=0.0,
            step=100_000.0,
        )
        equity_contribution = st.number_input(
            "Equity Contribution (EUR)",
            value=assumptions.transaction_and_financing.equity_contribution_eur,
            min_value=0.0,
            step=100_000.0,
        )
        senior_term_loan = st.number_input(
            "Senior Term Loan Start (EUR)",
            value=assumptions.transaction_and_financing.senior_term_loan_start_eur,
            min_value=0.0,
            step=100_000.0,
        )

    return TransactionFinancingAssumptions(
        purchase_price_eur=purchase_price,
        equity_contribution_eur=equity_contribution,
        senior_term_loan_start_eur=senior_term_loan,
    )


def _render_financing_inputs(
    assumptions: Assumptions,
) -> FinancingAssumptions:
    finance = assumptions.financing

    with st.expander("Financing Terms", expanded=True):
        senior_debt_amount = st.number_input(
            "Senior Debt Amount (EUR)",
            value=finance.senior_debt_amount_eur,
            min_value=0.0,
            step=100_000.0,
        )
        initial_debt = st.number_input(
            "Initial Debt (EUR)",
            value=finance.initial_debt_eur,
            min_value=0.0,
            step=100_000.0,
        )
        interest_rate = st.number_input(
            "Interest Rate (% p.a.)",
            value=finance.interest_rate_pct * 100,
            min_value=0.0,
            step=0.1,
        )
        amortization_type = st.selectbox(
            "Amortization Type",
            ["Linear", "Bullet"],
            index=0 if finance.amortization_type == "Linear" else 1,
        )
        amortization_period = int(
            st.number_input(
                "Amortization Period (Years)",
                value=finance.amortization_period_years,
                min_value=1,
                step=1,
            )
        )
        grace_period = int(
            st.number_input(
                "Grace Period (Years)",
                value=finance.grace_period_years,
                min_value=0,
                step=1,
            )
        )
        special_year_options = ["None"] + [f"Year {i}" for i in range(5)]
        special_index = (
            0
            if finance.special_repayment_year is None
            else finance.special_repayment_year + 1
        )
        special_year_choice = st.selectbox(
            "Special Repayment Year",
            special_year_options,
            index=special_index,
        )
        special_year = (
            None
            if special_year_choice == "None"
            else int(special_year_choice.replace("Year ", ""))
        )
        special_amount = st.number_input(
            "Special Repayment Amount (EUR)",
            value=finance.special_repayment_amount_eur,
            min_value=0.0,
            step=100_000.0,
        )
        minimum_dscr = st.number_input(
            "Minimum DSCR",
            value=finance.minimum_dscr,
            min_value=0.0,
            step=0.1,
        )

    return FinancingAssumptions(
        senior_debt_amount_eur=senior_debt_amount,
        initial_debt_eur=initial_debt,
        interest_rate_pct=interest_rate / 100,
        amortization_type=amortization_type,
        amortization_period_years=amortization_period,
        grace_period_years=grace_period,
        special_repayment_year=special_year,
        special_repayment_amount_eur=special_amount,
        minimum_dscr=minimum_dscr,
    )


def _render_cashflow_inputs(assumptions: Assumptions) -> CashflowAssumptions:
    cashflow = assumptions.cashflow

    with st.expander("Cashflow Assumptions", expanded=True):
        tax_cash_rate = st.number_input(
            "Tax Cash Rate (%)",
            value=cashflow.tax_cash_rate_pct * 100,
            min_value=0.0,
            step=0.1,
        )
        tax_payment_lag = int(
            st.number_input(
                "Tax Payment Lag (Years)",
                value=cashflow.tax_payment_lag_years,
                min_value=0,
                step=1,
            )
        )
        capex_pct = st.number_input(
            "Capex (% of Revenue)",
            value=cashflow.capex_pct_revenue * 100,
            min_value=0.0,
            step=0.1,
        )
        working_capital_pct = st.number_input(
            "Working Capital (% of Revenue)",
            value=cashflow.working_capital_pct_revenue * 100,
            min_value=0.0,
            step=0.1,
        )
        opening_cash = st.number_input(
            "Opening Cash Balance (EUR)",
            value=cashflow.opening_cash_balance_eur,
            min_value=0.0,
            step=10_000.0,
        )

    return CashflowAssumptions(
        tax_cash_rate_pct=tax_cash_rate / 100,
        tax_payment_lag_years=tax_payment_lag,
        capex_pct_revenue=capex_pct / 100,
        working_capital_pct_revenue=working_capital_pct / 100,
        opening_cash_balance_eur=opening_cash,
    )


def _render_balance_sheet_inputs(
    assumptions: Assumptions,
) -> BalanceSheetAssumptions:
    balance = assumptions.balance_sheet

    with st.expander("Balance Sheet Assumptions", expanded=True):
        opening_equity = st.number_input(
            "Opening Equity (EUR)",
            value=balance.opening_equity_eur,
            min_value=0.0,
            step=100_000.0,
        )
        depreciation_rate = st.number_input(
            "Depreciation Rate (% p.a.)",
            value=balance.depreciation_rate_pct * 100,
            min_value=0.0,
            step=0.1,
        )

    return BalanceSheetAssumptions(
        opening_equity_eur=opening_equity,
        depreciation_rate_pct=depreciation_rate / 100,
    )


def _render_tax_inputs(assumptions: Assumptions) -> TaxAssumptions:
    with st.expander("Tax & Distributions", expanded=True):
        tax_rate = st.number_input(
            "Tax Rate (%)",
            value=assumptions.tax_and_distributions.tax_rate_pct * 100,
            min_value=0.0,
            step=0.1,
        )

    return TaxAssumptions(tax_rate_pct=tax_rate / 100)


def _render_valuation_inputs(
    assumptions: Assumptions,
) -> ValuationAssumptions:
    with st.expander("Valuation Assumptions", expanded=True):
        seller_multiple = st.number_input(
            "Seller Multiple (x EBIT)",
            value=assumptions.valuation.seller_multiple,
            min_value=0.0,
            step=0.1,
        )

    return ValuationAssumptions(seller_multiple=seller_multiple)


def _year_number_inputs(label: str, values: List[float], step: float) -> List[float]:
    results = []
    for year_index, value in enumerate(values):
        results.append(
            st.number_input(
                f"{label} — Year {year_index}",
                value=value,
                min_value=0.0,
                step=step,
            )
        )
    return results


def _year_percent_inputs(label: str, values: List[float]) -> List[float]:
    results = []
    for year_index, value in enumerate(values):
        results.append(
            st.number_input(
                f"{label} — Year {year_index}",
                value=value * 100,
                min_value=0.0,
                step=0.1,
            )
            / 100
        )
    return results


def _variable_cost_inputs(
    label: str,
    rows: List[VariableCostYearAssumptions],
) -> dict:
    types = []
    values = []
    for year_index, row in enumerate(rows):
        current_type = getattr(row, f"{label.lower()}_type")
        cost_type = st.selectbox(
            f"{label} Type — Year {year_index}",
            ["EUR", "%"],
            index=0 if current_type == "EUR" else 1,
        )
        if cost_type == "%":
            value = (
                st.number_input(
                    f"{label} Value (% of Revenue) — Year {year_index}",
                    value=getattr(row, f"{label.lower()}_value") * 100,
                    min_value=0.0,
                    step=0.1,
                )
                / 100
            )
        else:
            value = st.number_input(
                f"{label} Value (EUR) — Year {year_index}",
                value=getattr(row, f"{label.lower()}_value"),
                min_value=0.0,
                step=1_000.0,
            )
        types.append(cost_type)
        values.append(value)

    return {"type": types, "value": values}
