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

YEARS = ["Year 0", "Year 1", "Year 2", "Year 3", "Year 4"]


def render_revenue_inputs(assumptions: Assumptions) -> Assumptions:
    scenario = _scenario_table(assumptions)
    scenarios = dict(assumptions.revenue.scenarios)
    current = scenarios[scenario]

    st.markdown("### Revenue Drivers")
    drivers_table = _year_table(
        [
            ("Workdays per Year", "Days", current.workdays_per_year, ""),
            ("Utilization Rate", "%", current.utilization_rate_pct, ""),
            ("Day Rate Growth", "% p.a.", current.day_rate_growth_pct, ""),
            ("Revenue Growth", "% p.a.", current.revenue_growth_pct, ""),
        ]
    )
    drivers_table = _edit_table(drivers_table, key="revenue.drivers")

    st.markdown("### Capacity Allocation")
    allocation_table = _year_table(
        [
            ("Group Capacity Share", "%", current.group_capacity_share_pct, ""),
            ("External Capacity Share", "%", current.external_capacity_share_pct, ""),
        ]
    )
    allocation_table = _edit_table(allocation_table, key="revenue.allocation")

    st.markdown("### Pricing")
    pricing_table = _year_table(
        [
            ("Group Day Rate", "EUR", current.group_day_rate_eur, ""),
            ("External Day Rate", "EUR", current.external_day_rate_eur, ""),
        ]
    )
    pricing_table = _edit_table(pricing_table, key="revenue.pricing")

    st.markdown("### Guarantees")
    guarantee_table = _year_table(
        [
            ("Guarantee %", "%", current.guarantee_pct_by_year, ""),
        ]
    )
    guarantee_table = _edit_table(guarantee_table, key="revenue.guarantee")

    st.markdown("### Reference Revenue")
    reference_table = _value_table(
        [
            ("Reference Revenue", "EUR", current.reference_revenue_eur, ""),
        ]
    )
    reference_table = _edit_table(reference_table, key="revenue.reference")

    scenarios[scenario] = RevenueScenarioAssumptions(
        workdays_per_year=_row_years_numeric(drivers_table, "Workdays per Year"),
        utilization_rate_pct=_row_years_numeric(drivers_table, "Utilization Rate"),
        group_day_rate_eur=_row_years_numeric(pricing_table, "Group Day Rate"),
        external_day_rate_eur=_row_years_numeric(pricing_table, "External Day Rate"),
        day_rate_growth_pct=_row_years_numeric(drivers_table, "Day Rate Growth"),
        revenue_growth_pct=_row_years_numeric(drivers_table, "Revenue Growth"),
        group_capacity_share_pct=_row_years_numeric(allocation_table, "Group Capacity Share"),
        external_capacity_share_pct=_row_years_numeric(allocation_table, "External Capacity Share"),
        reference_revenue_eur=_to_float(_row_value(reference_table, "Reference Revenue")),
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
    inflation_table = _value_table(
        [
            ("Apply Inflation (Yes/No)", "", "Yes" if cost.inflation_apply else "No", ""),
            ("Inflation Rate", "% p.a.", cost.inflation_rate_pct, ""),
        ]
    )
    inflation_table = _edit_table(inflation_table, key="cost.inflation")

    st.markdown("### Personnel")
    personnel_table = _year_table(
        [
            ("Consultant FTE", "FTE", [row.consultant_fte for row in cost.personnel_by_year], ""),
            (
                "Consultant Loaded Cost",
                "EUR",
                [row.consultant_loaded_cost_eur for row in cost.personnel_by_year],
                "",
            ),
            ("Backoffice FTE", "FTE", [row.backoffice_fte for row in cost.personnel_by_year], ""),
            (
                "Backoffice Loaded Cost",
                "EUR",
                [row.backoffice_loaded_cost_eur for row in cost.personnel_by_year],
                "",
            ),
            ("Management Cost", "EUR", [row.management_cost_eur for row in cost.personnel_by_year], ""),
        ]
    )
    personnel_table = _edit_table(personnel_table, key="cost.personnel")

    st.markdown("### Fixed Overhead")
    fixed_table = _year_table(
        [
            ("Advisory", "EUR", [row.advisory_eur for row in cost.fixed_overhead_by_year], ""),
            ("Legal", "EUR", [row.legal_eur for row in cost.fixed_overhead_by_year], ""),
            ("IT & Software", "EUR", [row.it_software_eur for row in cost.fixed_overhead_by_year], ""),
            ("Office Rent", "EUR", [row.office_rent_eur for row in cost.fixed_overhead_by_year], ""),
            ("Services", "EUR", [row.services_eur for row in cost.fixed_overhead_by_year], ""),
            ("Other Services", "EUR", [row.other_services_eur for row in cost.fixed_overhead_by_year], ""),
        ]
    )
    fixed_table = _edit_table(fixed_table, key="cost.fixed")

    st.markdown("### Variable Costs — Type")
    variable_type_table = _year_table(
        [
            ("Training Type", "EUR/%", [row.training_type for row in cost.variable_costs_by_year], ""),
            ("Travel Type", "EUR/%", [row.travel_type for row in cost.variable_costs_by_year], ""),
            ("Communication Type", "EUR/%", [row.communication_type for row in cost.variable_costs_by_year], ""),
        ]
    )
    variable_type_table = _edit_table(variable_type_table, key="cost.variable.type")

    st.markdown("### Variable Costs — Value")
    variable_value_table = _year_table(
        [
            ("Training Value", "EUR or %", [row.training_value for row in cost.variable_costs_by_year], ""),
            ("Travel Value", "EUR or %", [row.travel_value for row in cost.variable_costs_by_year], ""),
            ("Communication Value", "EUR or %", [row.communication_value for row in cost.variable_costs_by_year], ""),
        ]
    )
    variable_value_table = _edit_table(variable_value_table, key="cost.variable.value")

    personnel_by_year = [
        PersonnelYearAssumptions(
            consultant_fte=_row_years_numeric(personnel_table, "Consultant FTE")[i],
            consultant_loaded_cost_eur=_row_years_numeric(personnel_table, "Consultant Loaded Cost")[i],
            backoffice_fte=_row_years_numeric(personnel_table, "Backoffice FTE")[i],
            backoffice_loaded_cost_eur=_row_years_numeric(personnel_table, "Backoffice Loaded Cost")[i],
            management_cost_eur=_row_years_numeric(personnel_table, "Management Cost")[i],
        )
        for i in range(5)
    ]
    fixed_overhead_by_year = [
        FixedOverheadYearAssumptions(
            advisory_eur=_row_years_numeric(fixed_table, "Advisory")[i],
            legal_eur=_row_years_numeric(fixed_table, "Legal")[i],
            it_software_eur=_row_years_numeric(fixed_table, "IT & Software")[i],
            office_rent_eur=_row_years_numeric(fixed_table, "Office Rent")[i],
            services_eur=_row_years_numeric(fixed_table, "Services")[i],
            other_services_eur=_row_years_numeric(fixed_table, "Other Services")[i],
        )
        for i in range(5)
    ]
    variable_costs_by_year = [
        VariableCostYearAssumptions(
            training_type=_row_years_text(variable_type_table, "Training Type")[i],
            training_value=_row_years_numeric(variable_value_table, "Training Value")[i],
            travel_type=_row_years_text(variable_type_table, "Travel Type")[i],
            travel_value=_row_years_numeric(variable_value_table, "Travel Value")[i],
            communication_type=_row_years_text(variable_type_table, "Communication Type")[i],
            communication_value=_row_years_numeric(variable_value_table, "Communication Value")[i],
        )
        for i in range(5)
    ]

    inflation_apply = (
        str(_row_value(inflation_table, "Apply Inflation (Yes/No)")).strip().lower() == "yes"
    )
    inflation_rate = _to_float(_row_value(inflation_table, "Inflation Rate"))

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

    st.markdown("### Transaction & Financing")
    transaction_table = _value_table(
        [
            ("Purchase Price", "EUR", transaction.purchase_price_eur, ""),
            ("Equity Contribution", "EUR", transaction.equity_contribution_eur, ""),
            ("Senior Term Loan Start", "EUR", transaction.senior_term_loan_start_eur, ""),
        ]
    )
    transaction_table = _edit_table(transaction_table, key="financing.transaction")

    st.markdown("### Debt Terms")
    financing_table = _value_table(
        [
            ("Senior Debt Amount", "EUR", financing.senior_debt_amount_eur, ""),
            ("Initial Debt", "EUR", financing.initial_debt_eur, ""),
            ("Interest Rate", "% p.a.", financing.interest_rate_pct, ""),
            ("Amortization Type", "", financing.amortization_type, ""),
            ("Amortization Period (Years)", "Years", financing.amortization_period_years, ""),
            ("Grace Period (Years)", "Years", financing.grace_period_years, ""),
            ("Special Repayment Year (None/Year X)", "", _format_special_year(financing.special_repayment_year), ""),
            ("Special Repayment Amount", "EUR", financing.special_repayment_amount_eur, ""),
            ("Minimum DSCR", "", financing.minimum_dscr, ""),
        ]
    )
    financing_table = _edit_table(financing_table, key="financing.terms")

    return Assumptions(
        scenario=assumptions.scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=TransactionFinancingAssumptions(
            purchase_price_eur=_to_float(_row_value(transaction_table, "Purchase Price")),
            equity_contribution_eur=_to_float(_row_value(transaction_table, "Equity Contribution")),
            senior_term_loan_start_eur=_to_float(_row_value(transaction_table, "Senior Term Loan Start")),
        ),
        financing=FinancingAssumptions(
            senior_debt_amount_eur=_to_float(_row_value(financing_table, "Senior Debt Amount")),
            initial_debt_eur=_to_float(_row_value(financing_table, "Initial Debt")),
            interest_rate_pct=_to_float(_row_value(financing_table, "Interest Rate")),
            amortization_type=str(_row_value(financing_table, "Amortization Type")).strip() or "Linear",
            amortization_period_years=int(_to_float(_row_value(financing_table, "Amortization Period (Years)") or 0)),
            grace_period_years=int(_to_float(_row_value(financing_table, "Grace Period (Years)") or 0)),
            special_repayment_year=_parse_special_year(
                str(_row_value(financing_table, "Special Repayment Year (None/Year X)")).strip()
            ),
            special_repayment_amount_eur=_to_float(
                _row_value(financing_table, "Special Repayment Amount")
            ),
            minimum_dscr=_to_float(_row_value(financing_table, "Minimum DSCR")),
        ),
        cashflow=assumptions.cashflow,
        balance_sheet=assumptions.balance_sheet,
        tax_and_distributions=assumptions.tax_and_distributions,
        valuation=assumptions.valuation,
    )


def render_other_assumptions(assumptions: Assumptions) -> Assumptions:
    st.markdown("### Scenario")
    scenario_table = _value_table(
        [
            ("Scenario (Base/Best/Worst)", "", assumptions.scenario, ""),
        ]
    )
    scenario_table = _edit_table(scenario_table, key="other.scenario")
    scenario = str(_row_value(scenario_table, "Scenario (Base/Best/Worst)")).strip() or assumptions.scenario

    st.markdown("### Cashflow")
    cashflow = assumptions.cashflow
    cashflow_table = _value_table(
        [
            ("Tax Cash Rate", "%", cashflow.tax_cash_rate_pct, ""),
            ("Tax Payment Lag (Years)", "Years", cashflow.tax_payment_lag_years, ""),
            ("Capex (% of Revenue)", "%", cashflow.capex_pct_revenue, ""),
            ("Working Capital (% of Revenue)", "%", cashflow.working_capital_pct_revenue, ""),
            ("Opening Cash Balance", "EUR", cashflow.opening_cash_balance_eur, ""),
        ]
    )
    cashflow_table = _edit_table(cashflow_table, key="other.cashflow")

    st.markdown("### Balance Sheet")
    balance = assumptions.balance_sheet
    balance_table = _value_table(
        [
            ("Opening Equity", "EUR", balance.opening_equity_eur, ""),
            ("Depreciation Rate", "% p.a.", balance.depreciation_rate_pct, ""),
        ]
    )
    balance_table = _edit_table(balance_table, key="other.balance")

    st.markdown("### Tax & Valuation")
    tax_table = _value_table(
        [
            ("Tax Rate", "%", assumptions.tax_and_distributions.tax_rate_pct, ""),
            ("Seller Multiple (x EBIT)", "x", assumptions.valuation.seller_multiple, ""),
        ]
    )
    tax_table = _edit_table(tax_table, key="other.tax")

    return Assumptions(
        scenario=scenario,
        revenue=assumptions.revenue,
        cost=assumptions.cost,
        transaction_and_financing=assumptions.transaction_and_financing,
        financing=assumptions.financing,
        cashflow=CashflowAssumptions(
            tax_cash_rate_pct=_to_float(_row_value(cashflow_table, "Tax Cash Rate")),
            tax_payment_lag_years=int(
                _to_float(_row_value(cashflow_table, "Tax Payment Lag (Years)") or 0)
            ),
            capex_pct_revenue=_to_float(_row_value(cashflow_table, "Capex (% of Revenue)")),
            working_capital_pct_revenue=_to_float(
                _row_value(cashflow_table, "Working Capital (% of Revenue)")
            ),
            opening_cash_balance_eur=_to_float(
                _row_value(cashflow_table, "Opening Cash Balance")
            ),
        ),
        balance_sheet=BalanceSheetAssumptions(
            opening_equity_eur=_to_float(_row_value(balance_table, "Opening Equity")),
            depreciation_rate_pct=_to_float(_row_value(balance_table, "Depreciation Rate")),
        ),
        tax_and_distributions=TaxAssumptions(
            tax_rate_pct=_to_float(_row_value(tax_table, "Tax Rate"))
        ),
        valuation=ValuationAssumptions(
            seller_multiple=_to_float(_row_value(tax_table, "Seller Multiple (x EBIT)"))
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
    for name, unit, values, notes in rows:
        row = {"Parameter": name, "Unit": unit, "Notes": notes}
        for idx, year in enumerate(YEARS):
            row[year] = values[idx]
        table.append(row)
    return table


def _value_table(rows: List[tuple]) -> List[dict]:
    table = []
    for name, unit, value, notes in rows:
        table.append(
            {
                "Parameter": name,
                "Value": value,
                "Unit": unit,
                "Notes": notes,
            }
        )
    return table


def _edit_table(table: List[dict], key: str) -> List[dict]:
    edited = st.data_editor(table, use_container_width=True, key=key)
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
            return [_to_float(row.get(year, 0.0)) for year in YEARS]
    return [0.0 for _ in YEARS]


def _row_years_text(table: List[dict], name: str) -> List[str]:
    for row in table:
        if row.get("Parameter") == name:
            return [str(row.get(year, "") or "") for year in YEARS]
    return ["" for _ in YEARS]


def _row_value(table: List[dict], name: str):
    for row in table:
        if row.get("Parameter") == name:
            return row.get("Value", row.get(YEARS[0], 0.0))
    return 0.0


def _to_float(value) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return 0.0


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
