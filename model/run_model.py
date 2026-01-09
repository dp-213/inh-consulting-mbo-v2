from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from state.assumptions import Assumptions


@dataclass(frozen=True)
class ModelResult:
    revenue: Dict[str, List[float] | List[dict]]
    cost: List[dict]
    pnl: List[dict]
    debt: List[dict]
    cashflow: List[dict]
    balance_sheet: List[dict]
    equity: dict


def run_model(assumptions: Assumptions) -> ModelResult:
    assumptions_state = _build_assumptions_state(assumptions)
    input_model = _InputModelAdapter(assumptions)
    scenario = assumptions.scenario
    if scenario not in assumptions_state["revenue_model"]["workdays_per_year"]:
        raise ValueError(f"Unknown scenario '{scenario}'.")

    revenue_final_by_year, revenue_components = _build_revenue_model_outputs(
        assumptions_state, scenario
    )
    cost_totals_by_year = _build_cost_model_outputs(
        assumptions_state, revenue_final_by_year
    )
    debt_schedule_pre = calculate_debt_schedule(input_model)
    pnl_pre = calculate_pnl(
        input_model,
        depreciation_by_year=None,
        revenue_final_by_year=revenue_final_by_year,
        cost_totals_by_year=cost_totals_by_year,
        debt_schedule=debt_schedule_pre,
    )
    cashflow = calculate_cashflow(input_model, pnl_pre, debt_schedule_pre)
    depreciation_by_year = {
        row["year"]: row.get("depreciation", 0.0) for row in cashflow
    }
    pnl = calculate_pnl(
        input_model,
        depreciation_by_year=depreciation_by_year,
        revenue_final_by_year=revenue_final_by_year,
        cost_totals_by_year=cost_totals_by_year,
        debt_schedule=debt_schedule_pre,
    )
    debt_schedule = calculate_debt_schedule(input_model, cashflow)
    balance_sheet = calculate_balance_sheet(
        input_model, cashflow, debt_schedule, pnl
    )
    equity = calculate_investment(input_model, cashflow, pnl, balance_sheet)

    return ModelResult(
        revenue={
            "revenue_final_by_year": revenue_final_by_year,
            "components_by_year": revenue_components,
        },
        cost=cost_totals_by_year,
        pnl=pnl,
        debt=debt_schedule,
        cashflow=cashflow,
        balance_sheet=balance_sheet,
        equity=equity,
    )


def _build_assumptions_state(assumptions: Assumptions) -> dict:
    revenue_model = {
        "reference_revenue_eur": {},
        "workdays_per_year": {},
        "utilization_rate": {},
        "group_day_rate_eur": {},
        "external_day_rate_eur": {},
        "day_rate_growth_pct": {},
        "revenue_growth_pct": {},
        "group_capacity_share_pct": {},
        "external_capacity_share_pct": {},
        "guarantee_pct_by_year": {},
    }
    for scenario_key, scenario_values in assumptions.revenue.scenarios.items():
        revenue_model["reference_revenue_eur"][scenario_key] = scenario_values.reference_revenue_eur
        revenue_model["workdays_per_year"][scenario_key] = list(
            scenario_values.workdays_per_year
        )
        revenue_model["utilization_rate"][scenario_key] = list(
            scenario_values.utilization_rate_pct
        )
        revenue_model["group_day_rate_eur"][scenario_key] = list(
            scenario_values.group_day_rate_eur
        )
        revenue_model["external_day_rate_eur"][scenario_key] = list(
            scenario_values.external_day_rate_eur
        )
        revenue_model["day_rate_growth_pct"][scenario_key] = list(
            scenario_values.day_rate_growth_pct
        )
        revenue_model["revenue_growth_pct"][scenario_key] = list(
            scenario_values.revenue_growth_pct
        )
        revenue_model["group_capacity_share_pct"][scenario_key] = list(
            scenario_values.group_capacity_share_pct
        )
        revenue_model["external_capacity_share_pct"][scenario_key] = list(
            scenario_values.external_capacity_share_pct
        )
        revenue_model["guarantee_pct_by_year"][scenario_key] = list(
            scenario_values.guarantee_pct_by_year
        )

    cost_state = assumptions.cost
    cost_model = {
        "inflation": {
            "apply": bool(cost_state.inflation_apply),
            "rate_pct": cost_state.inflation_rate_pct,
        },
        "personnel": [
            {
                "Consultant FTE": row.consultant_fte,
                "Consultant Loaded Cost (EUR)": row.consultant_loaded_cost_eur,
                "Backoffice FTE": row.backoffice_fte,
                "Backoffice Loaded Cost (EUR)": row.backoffice_loaded_cost_eur,
                "Management Cost (EUR)": row.management_cost_eur,
            }
            for row in cost_state.personnel_by_year
        ],
        "fixed_overhead": [
            {
                "Advisory": row.advisory_eur,
                "Legal": row.legal_eur,
                "IT & Software": row.it_software_eur,
                "Office Rent": row.office_rent_eur,
                "Services": row.services_eur,
                "Other Services": row.other_services_eur,
            }
            for row in cost_state.fixed_overhead_by_year
        ],
        "variable_costs": [
            {
                "Training Type": row.training_type,
                "Training Value": row.training_value,
                "Travel Type": row.travel_type,
                "Travel Value": row.travel_value,
                "Communication Type": row.communication_type,
                "Communication Value": row.communication_value,
            }
            for row in cost_state.variable_costs_by_year
        ],
    }
    return {"revenue_model": revenue_model, "cost_model": cost_model}


class _Value:
    def __init__(self, value: float):
        self.value = value


class _InputModelAdapter:
    def __init__(self, assumptions: Assumptions) -> None:
        self.transaction_and_financing = {
            "purchase_price_eur": _Value(
                assumptions.transaction_and_financing.purchase_price_eur
            ),
            "equity_contribution_eur": _Value(
                assumptions.transaction_and_financing.equity_contribution_eur
            ),
            "senior_term_loan_start_eur": _Value(
                assumptions.transaction_and_financing.senior_term_loan_start_eur
            ),
        }
        self.tax_and_distributions = {
            "tax_rate_pct": _Value(assumptions.tax_and_distributions.tax_rate_pct)
        }
        self.valuation_assumptions = {
            "multiple_valuation": {
                "seller_multiple": _Value(assumptions.valuation.seller_multiple)
            }
        }
        self.cashflow_assumptions = {
            "tax_cash_rate_pct": assumptions.cashflow.tax_cash_rate_pct,
            "tax_payment_lag_years": assumptions.cashflow.tax_payment_lag_years,
            "capex_pct_revenue": assumptions.cashflow.capex_pct_revenue,
            "working_capital_pct_revenue": assumptions.cashflow.working_capital_pct_revenue,
            "opening_cash_balance_eur": assumptions.cashflow.opening_cash_balance_eur,
        }
        self.balance_sheet_assumptions = {
            "opening_equity_eur": assumptions.balance_sheet.opening_equity_eur,
            "depreciation_rate_pct": assumptions.balance_sheet.depreciation_rate_pct,
        }
        self.financing_assumptions = {
            "senior_debt_amount": assumptions.financing.senior_debt_amount_eur,
            "initial_debt_eur": assumptions.financing.initial_debt_eur,
            "interest_rate_pct": assumptions.financing.interest_rate_pct,
            "amortization_type": assumptions.financing.amortization_type,
            "amortization_period_years": assumptions.financing.amortization_period_years,
            "grace_period_years": assumptions.financing.grace_period_years,
            "special_repayment_year": assumptions.financing.special_repayment_year,
            "special_repayment_amount_eur": assumptions.financing.special_repayment_amount_eur,
            "minimum_dscr": assumptions.financing.minimum_dscr,
        }


def _clamp_pct(value: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(float(value), 1.0))


def _non_negative(value: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, float(value))


def _build_revenue_model_outputs(assumptions_state, scenario):
    revenue_state = assumptions_state["revenue_model"]
    cost_state = assumptions_state["cost_model"]
    revenue_final_by_year = []
    components_by_year = []
    reference_value = _non_negative(
        revenue_state["reference_revenue_eur"].get(scenario, 0.0)
    )

    for year_index in range(5):
        fte = _non_negative(
            cost_state["personnel"][year_index]["Consultant FTE"]
        )
        workdays = revenue_state["workdays_per_year"][scenario][year_index]
        utilization = revenue_state["utilization_rate"][scenario][year_index]
        group_rate = revenue_state["group_day_rate_eur"][scenario][year_index]
        external_rate = revenue_state["external_day_rate_eur"][scenario][year_index]
        rate_growth = revenue_state["day_rate_growth_pct"][scenario][year_index]
        revenue_growth = revenue_state["revenue_growth_pct"][scenario][year_index]
        group_share = revenue_state["group_capacity_share_pct"][scenario][year_index]
        external_share = revenue_state["external_capacity_share_pct"][scenario][
            year_index
        ]
        total_share = group_share + external_share
        if total_share > 0:
            group_share = group_share / total_share
            external_share = external_share / total_share

        group_rate = group_rate * ((1 + rate_growth) ** year_index)
        external_rate = external_rate * ((1 + rate_growth) ** year_index)
        capacity_days = fte * workdays * utilization
        adjusted_capacity_days = capacity_days * (1 + revenue_growth)
        modeled_group_revenue = (
            adjusted_capacity_days * group_share * group_rate
        )
        modeled_external_revenue = (
            adjusted_capacity_days * external_share * external_rate
        )
        modeled_total_revenue = modeled_group_revenue + modeled_external_revenue

        guarantee_pct = _clamp_pct(
            revenue_state["guarantee_pct_by_year"][scenario][year_index]
        )
        guaranteed_floor = reference_value * guarantee_pct
        guaranteed_group_revenue = max(
            modeled_group_revenue, guaranteed_floor
        )
        final_total = guaranteed_group_revenue + modeled_external_revenue
        reconciliation_gap = final_total - (
            guaranteed_group_revenue + modeled_external_revenue
        )
        if abs(reconciliation_gap) > 1e-6:
            raise ValueError(
                f"Revenue reconciliation failed in year {year_index}: {reconciliation_gap}"
            )
        share_guaranteed = (
            guaranteed_group_revenue / final_total if final_total else 0.0
        )

        revenue_final_by_year.append(final_total)
        components_by_year.append(
            {
                "consulting_fte": fte,
                "capacity_days": capacity_days,
                "adjusted_capacity_days": adjusted_capacity_days,
                "group_share_pct": group_share,
                "external_share_pct": external_share,
                "modeled_group_revenue": modeled_group_revenue,
                "modeled_external_revenue": modeled_external_revenue,
                "modeled_total_revenue": modeled_total_revenue,
                "guaranteed_floor": guaranteed_floor,
                "guaranteed_group_revenue": guaranteed_group_revenue,
                "final_total": final_total,
                "share_guaranteed": share_guaranteed,
            }
        )

    return revenue_final_by_year, components_by_year


def _build_cost_model_outputs(assumptions_state, revenue_final_by_year):
    cost_state = assumptions_state["cost_model"]
    apply_inflation = bool(cost_state["inflation"].get("apply", False))
    inflation_rate = cost_state["inflation"].get("rate_pct", 0.0)
    cost_totals_by_year = []
    for year_index in range(5):
        personnel_row = cost_state["personnel"][year_index]
        fixed_row = cost_state["fixed_overhead"][year_index]
        variable_row = cost_state["variable_costs"][year_index]
        inflation_factor = (1 + inflation_rate) ** year_index if apply_inflation else 1.0

        consultant_total = (
            _non_negative(personnel_row["Consultant FTE"])
            * _non_negative(personnel_row["Consultant Loaded Cost (EUR)"])
            * inflation_factor
        )
        backoffice_total = (
            _non_negative(personnel_row["Backoffice FTE"])
            * _non_negative(personnel_row["Backoffice Loaded Cost (EUR)"])
            * inflation_factor
        )
        management_total = _non_negative(
            personnel_row["Management Cost (EUR)"]
        ) * inflation_factor
        personnel_total = consultant_total + backoffice_total + management_total

        fixed_total = sum(
            _non_negative(fixed_row[col])
            for col in [
                "Advisory",
                "Legal",
                "IT & Software",
                "Office Rent",
                "Services",
                "Other Services",
            ]
        ) * inflation_factor

        revenue = revenue_final_by_year[year_index]
        variable_total = 0.0
        for prefix in ["Training", "Travel", "Communication"]:
            cost_type = variable_row[f"{prefix} Type"]
            value = _non_negative(variable_row[f"{prefix} Value"])
            if cost_type == "%":
                variable_total += revenue * value
            else:
                variable_total += value * inflation_factor

        overhead_total = fixed_total + variable_total
        cost_totals_by_year.append(
            {
                "consultant_costs": consultant_total,
                "backoffice_costs": backoffice_total,
                "management_costs": management_total,
                "personnel_costs": personnel_total,
                "overhead_and_variable_costs": overhead_total,
                "total_operating_costs": personnel_total + overhead_total,
            }
        )
    return cost_totals_by_year


def calculate_pnl(
    input_model,
    depreciation_by_year=None,
    revenue_final_by_year=None,
    cost_totals_by_year=None,
    debt_schedule=None,
):
    planning_horizon_years = 5

    cashflow_assumptions = getattr(input_model, "cashflow_assumptions", {})
    tax_rate_pct = cashflow_assumptions.get(
        "tax_cash_rate_pct",
        input_model.tax_and_distributions["tax_rate_pct"].value,
    )

    pnl_by_year = []

    if not isinstance(revenue_final_by_year, list) or len(revenue_final_by_year) != planning_horizon_years:
        raise ValueError("revenue_final_by_year must be a 5-year list.")
    if not isinstance(cost_totals_by_year, list) or len(cost_totals_by_year) != planning_horizon_years:
        raise ValueError("cost_totals_by_year must be a 5-year list.")

    interest_by_year = {}
    if isinstance(debt_schedule, list):
        for row in debt_schedule:
            if "year" in row:
                interest_by_year[row["year"]] = row.get(
                    "interest_expense", 0.0
                )

    for year_index in range(planning_horizon_years):
        revenue = revenue_final_by_year[year_index]
        year_costs = cost_totals_by_year[year_index]
        total_personnel_costs = year_costs.get("personnel_costs", 0.0)
        overhead_and_variable_costs = year_costs.get("overhead_and_variable_costs", 0.0)

        ebitda = revenue - total_personnel_costs - overhead_and_variable_costs
        if isinstance(depreciation_by_year, dict):
            depreciation = depreciation_by_year.get(year_index, 0.0)
        elif (
            isinstance(depreciation_by_year, list)
            and len(depreciation_by_year) > year_index
        ):
            depreciation = depreciation_by_year[year_index]
        else:
            depreciation = 0.0
        ebit = ebitda - depreciation

        interest_expense = interest_by_year.get(year_index, 0.0)
        ebt = ebit - interest_expense

        taxable_income = ebt if ebt > 0 else 0
        taxes = taxable_income * tax_rate_pct
        net_income = ebt - taxes

        pnl_by_year.append(
            {
                "year": year_index,
                "revenue": revenue,
                "personnel_costs": total_personnel_costs,
                "overhead_and_variable_costs": overhead_and_variable_costs,
                "ebitda": ebitda,
                "depreciation": depreciation,
                "ebit": ebit,
                "interest_expense": interest_expense,
                "ebt": ebt,
                "taxes": taxes,
                "net_income": net_income,
            }
        )

    return pnl_by_year


def calculate_cashflow(input_model, pnl_result, debt_schedule):
    financing_assumptions = getattr(input_model, "financing_assumptions", {})

    debt_amount = financing_assumptions.get(
        "initial_debt_eur",
        input_model.transaction_and_financing[
            "senior_term_loan_start_eur"
        ].value,
    )

    cashflow_assumptions = getattr(input_model, "cashflow_assumptions", {})
    tax_cash_rate_pct = cashflow_assumptions.get(
        "tax_cash_rate_pct",
        input_model.tax_and_distributions["tax_rate_pct"].value,
    )
    tax_payment_lag_years = cashflow_assumptions.get(
        "tax_payment_lag_years", 0
    )
    capex_pct_revenue = cashflow_assumptions.get(
        "capex_pct_revenue", 0.0
    )
    working_capital_pct_revenue = cashflow_assumptions.get(
        "working_capital_pct_revenue", 0.0
    )
    opening_cash_balance = cashflow_assumptions.get(
        "opening_cash_balance_eur", 0.0
    )

    equity_injection_amount = input_model.transaction_and_financing[
        "equity_contribution_eur"
    ].value
    purchase_price = input_model.transaction_and_financing[
        "purchase_price_eur"
    ].value

    cashflow = []
    cash_balance = opening_cash_balance
    taxes_due_by_year = []
    debt_by_year = {row["year"]: row for row in debt_schedule}
    depreciation_rate = getattr(
        input_model, "balance_sheet_assumptions", {}
    ).get("depreciation_rate_pct", 0.0)
    fixed_assets = 0.0
    working_capital_balance = 0.0
    for i, year_data in enumerate(pnl_result):
        year = year_data["year"]
        revenue = year_data.get("revenue", 0)
        ebitda = year_data.get("ebitda", 0)

        debt_row = debt_by_year.get(year, {})
        interest = debt_row.get("interest_expense", 0.0)
        principal_repayment = debt_row.get("total_repayment", 0.0)
        debt_drawdown = debt_row.get("debt_drawdown", 0.0)

        working_capital_current = revenue * working_capital_pct_revenue
        working_capital_change = (
            working_capital_current - working_capital_balance
        )
        working_capital_balance = working_capital_current
        capex = revenue * capex_pct_revenue

        depreciation = (fixed_assets + capex) * depreciation_rate
        fixed_assets = max(fixed_assets + capex - depreciation, 0.0)

        ebit = ebitda - depreciation

        ebt = ebit - interest
        taxes_due = max(ebt, 0) * tax_cash_rate_pct
        taxes_due_by_year.append(taxes_due)
        if tax_payment_lag_years == 0:
            taxes_paid = taxes_due
        elif tax_payment_lag_years == 1:
            taxes_paid = taxes_due_by_year[i - 1] if i > 0 else 0.0
        else:
            taxes_paid = 0.0

        operating_cf = ebitda - taxes_paid - working_capital_change

        equity_injection = equity_injection_amount if year == 0 else 0.0
        acquisition_outflow = -purchase_price if year == 0 else 0.0
        if year == 0:
            if equity_injection != equity_injection_amount:
                raise ValueError(
                    "Year 0 equity injection does not match equity contribution."
                )
            if acquisition_outflow != -purchase_price:
                raise ValueError(
                    "Year 0 acquisition outflow does not match purchase price."
                )
            if debt_drawdown != debt_amount:
                raise ValueError(
                    "Year 0 debt drawdown does not match initial debt amount."
                )

        investing_cf = -capex + acquisition_outflow
        free_cashflow = operating_cf + investing_cf

        if i == 0:
            financing_cf = (
                debt_drawdown
                + equity_injection
                - interest
                - principal_repayment
            )
        else:
            financing_cf = -(interest + principal_repayment)

        net_cashflow = free_cashflow + financing_cf
        opening_cash = cash_balance
        cash_balance += net_cashflow
        reconciliation_gap = opening_cash + net_cashflow - cash_balance
        if abs(reconciliation_gap) > 1e-6:
            raise ValueError(
                f"Cash reconciliation failed in year {year}: {reconciliation_gap}"
            )

        cashflow.append(
            {
                "year": year,
                "ebitda": ebitda,
                "depreciation": depreciation,
                "taxes_paid": taxes_paid,
                "working_capital_change": working_capital_change,
                "working_capital_balance": working_capital_balance,
                "operating_cf": operating_cf,
                "capex": capex,
                "acquisition_outflow": acquisition_outflow,
                "free_cashflow": free_cashflow,
                "debt_drawdown": debt_drawdown,
                "equity_injection": equity_injection,
                "interest_paid": interest,
                "debt_repayment": principal_repayment,
                "investing_cf": investing_cf,
                "financing_cf": financing_cf,
                "net_cashflow": net_cashflow,
                "opening_cash": opening_cash,
                "cash_balance": cash_balance,
            }
        )

    return cashflow


def calculate_debt_schedule(input_model, cashflow_result=None):
    financing_assumptions = getattr(input_model, "financing_assumptions", {})
    if "senior_debt_amount" not in financing_assumptions:
        raise ValueError("Senior debt amount missing from financing assumptions.")
    initial_debt = financing_assumptions["senior_debt_amount"]
    interest_rate = financing_assumptions.get("interest_rate_pct")
    if interest_rate is None:
        raise ValueError("Interest rate missing from financing assumptions.")
    amort_type = financing_assumptions.get("amortization_type", "Linear")
    amort_period = financing_assumptions.get("amortization_period_years", 5)
    grace_period = financing_assumptions.get("grace_period_years", 0)
    special_year = financing_assumptions.get("special_repayment_year", None)
    special_amount = financing_assumptions.get("special_repayment_amount_eur", 0.0)
    min_dscr = financing_assumptions.get("minimum_dscr", 1.3)

    schedule = []
    outstanding_principal = 0.0

    for i in range(5):
        year = i
        debt_drawdown = initial_debt if i == 0 else 0.0
        opening_debt = outstanding_principal + debt_drawdown

        interest_expense = opening_debt * interest_rate
        if amort_type == "Bullet":
            scheduled_repayment = (
                opening_debt if i == max(amort_period - 1, 0) else 0.0
            )
        else:
            scheduled_repayment = (
                0.0
                if i < grace_period
                else (
                    opening_debt / amort_period
                    if i < amort_period
                    else 0.0
                )
            )
        if (
            amort_type != "Bullet"
            and i >= grace_period
            and opening_debt > 0
            and amort_period
        ):
            expected_repayment = opening_debt / amort_period
            if abs(scheduled_repayment - expected_repayment) > 1e-6:
                raise ValueError(
                    "Scheduled repayment does not scale with senior debt amount."
                )
        special_repayment = (
            special_amount if special_year == i else 0.0
        )
        pre_repayment_balance = opening_debt
        total_repayment = min(
            pre_repayment_balance, scheduled_repayment + special_repayment
        )
        debt_service = interest_expense + total_repayment
        if initial_debt > 0 and opening_debt > 0:
            if interest_expense == 0:
                raise ValueError(
                    "Interest expense is zero with positive debt balance."
                )
            if scheduled_repayment == 0:
                raise ValueError(
                    "Scheduled repayment is zero with positive debt balance."
                )
            if debt_service == 0:
                raise ValueError(
                    "Debt service is zero with positive debt balance."
                )

        cfads = None
        dscr = None
        covenant_breach = None

        outstanding_principal = max(
            pre_repayment_balance - total_repayment, 0.0
        )

        reconciliation_gap = (
            opening_debt - total_repayment - outstanding_principal
        )
        if abs(reconciliation_gap) > 1e-6:
            raise ValueError(
                f"Debt reconciliation failed in year {year}: {reconciliation_gap}"
            )

        schedule.append(
            {
                "year": year,
                "opening_debt": opening_debt,
                "debt_drawdown": debt_drawdown,
                "scheduled_repayment": scheduled_repayment,
                "special_repayment": special_repayment,
                "total_repayment": total_repayment,
                "closing_debt": outstanding_principal,
                "interest_expense": interest_expense,
                "principal_payment": total_repayment,
                "debt_service": debt_service,
                "outstanding_principal": outstanding_principal,
                "dscr": dscr,
                "cfads": cfads,
                "minimum_dscr": min_dscr,
                "covenant_breach": covenant_breach,
            }
        )

    if cashflow_result is not None:
        cashflow_by_year = {row["year"]: row for row in cashflow_result}
        for row in schedule:
            year = row["year"]
            year_data = cashflow_by_year.get(year, {})
            operating_cf = year_data.get("operating_cf", 0.0)
            cfads = operating_cf - year_data.get("capex", 0.0)
            debt_service = row["debt_service"]
            dscr = cfads / debt_service if debt_service != 0 else 0
            row["cfads"] = cfads
            row["dscr"] = dscr
            row["covenant_breach"] = dscr < min_dscr

    return schedule


def calculate_balance_sheet(
    input_model, cashflow_result, debt_schedule, pnl_result=None
):
    balance_sheet = []

    balance_assumptions = getattr(input_model, "balance_sheet_assumptions", {})
    opening_equity = balance_assumptions.get("opening_equity_eur", 0.0)
    equity_contribution = input_model.transaction_and_financing[
        "equity_contribution_eur"
    ].value
    purchase_price = input_model.transaction_and_financing[
        "purchase_price_eur"
    ].value

    net_income_by_year = {}
    taxes_by_year = {}
    depreciation_by_year = {}
    if pnl_result is not None:
        for year_data in pnl_result:
            net_income_by_year[year_data.get("year")] = year_data.get(
                "net_income", 0
            )
            taxes_by_year[year_data.get("year")] = year_data.get("taxes", 0.0)
            depreciation_by_year[year_data.get("year")] = year_data.get(
                "depreciation", 0.0
            )

    debt_by_year = {
        debt_data["year"]: debt_data["closing_debt"]
        for debt_data in debt_schedule
    }

    equity_start = opening_equity
    fixed_assets = 0.0
    acquisition_intangible = purchase_price
    working_capital_balance = 0.0
    tax_payable_balance = 0.0

    for year_data in cashflow_result:
        year = year_data["year"]
        cash_balance = year_data["cash_balance"]
        capex = year_data.get("capex", 0.0)
        depreciation = depreciation_by_year.get(
            year, year_data.get("depreciation", 0.0)
        )
        working_capital_balance = year_data.get(
            "working_capital_balance", working_capital_balance
        )

        fixed_assets = max(fixed_assets + capex - depreciation, 0.0)

        financial_debt = debt_by_year.get(year, 0.0)
        net_income = net_income_by_year.get(year, 0.0)
        dividends = 0.0
        equity_injection = equity_contribution if year == 0 else 0.0
        equity_buyback = 0.0
        equity_end = (
            equity_start
            + net_income
            - dividends
            + equity_injection
            - equity_buyback
        )

        taxes_due = taxes_by_year.get(year, 0.0)
        taxes_paid = year_data.get("taxes_paid", 0.0)
        tax_payable_balance += taxes_due - taxes_paid

        total_assets = (
            cash_balance
            + fixed_assets
            + working_capital_balance
            + acquisition_intangible
        )
        total_liabilities = financial_debt + tax_payable_balance
        total_liabilities_equity = total_liabilities + equity_end
        balance_check = total_assets - total_liabilities_equity
        if abs(balance_check) > 1.0:
            raise ValueError(
                f"Balance sheet out of balance in year {year}: {balance_check}"
            )

        balance_sheet.append(
            {
                "year": year,
                "cash": cash_balance,
                "fixed_assets": fixed_assets,
                "acquisition_intangible": acquisition_intangible,
                "working_capital": working_capital_balance,
                "total_assets": total_assets,
                "financial_debt": financial_debt,
                "tax_payable": tax_payable_balance,
                "total_liabilities": total_liabilities,
                "equity_start": equity_start,
                "net_income": net_income,
                "dividends": dividends,
                "equity_injection": equity_injection,
                "equity_buyback": equity_buyback,
                "equity_end": equity_end,
                "total_liabilities_equity": total_liabilities_equity,
                "balance_check": balance_check,
            }
        )

        equity_start = equity_end

    return balance_sheet


def calculate_investment(
    input_model, cashflow_result, pnl_result=None, balance_sheet=None
):
    equity_amount = input_model.transaction_and_financing[
        "equity_contribution_eur"
    ].value
    exit_multiple = input_model.valuation_assumptions["multiple_valuation"][
        "seller_multiple"
    ].value
    exit_multiple = 0 if exit_multiple is None else exit_multiple

    final_year_ebit = 0
    if pnl_result:
        final_year_ebit = pnl_result[-1].get("ebit", 0)

    enterprise_value = final_year_ebit * exit_multiple
    net_debt_exit = 0.0
    excess_cash = 0.0
    if balance_sheet:
        last_year = balance_sheet[-1]
        net_debt_exit = last_year.get("financial_debt", 0.0)
        excess_cash = last_year.get("cash", 0.0)
    exit_value = enterprise_value - net_debt_exit + excess_cash

    equity_cashflows = [-equity_amount]
    for i in range(len(cashflow_result)):
        dividend = 0.0
        if i == len(cashflow_result) - 1:
            equity_cashflows.append(dividend + exit_value)
        else:
            equity_cashflows.append(dividend)

    irr = _calculate_irr(equity_cashflows)

    return {
        "initial_equity": equity_amount,
        "equity_cashflows": equity_cashflows,
        "exit_value": exit_value,
        "enterprise_value": enterprise_value,
        "net_debt_exit": net_debt_exit,
        "excess_cash_exit": excess_cash,
        "irr": irr,
    }


def _calculate_irr(cashflows, max_iterations=100):
    def npv(rate):
        return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))

    low = -0.9
    high = 1.0
    npv_low = npv(low)
    npv_high = npv(high)

    while npv_low * npv_high > 0 and high < 10:
        high *= 2
        npv_high = npv(high)

    if npv_low * npv_high > 0:
        return 0.0

    for _ in range(max_iterations):
        mid = (low + high) / 2
        npv_mid = npv(mid)

        if abs(npv_mid) < 1e-8:
            return mid

        if npv_low * npv_mid < 0:
            high = mid
            npv_high = npv_mid
        else:
            low = mid
            npv_low = npv_mid

    return (low + high) / 2
