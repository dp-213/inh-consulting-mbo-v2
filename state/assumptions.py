from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

PLANNING_YEARS = 5
SCENARIOS = ("Base", "Best", "Worst")


@dataclass(frozen=True)
class RevenueScenarioAssumptions:
    workdays_per_year: List[float]
    utilization_rate_pct: List[float]
    group_day_rate_eur: List[float]
    external_day_rate_eur: List[float]
    day_rate_growth_pct: List[float]
    revenue_growth_pct: List[float]
    group_capacity_share_pct: List[float]
    external_capacity_share_pct: List[float]
    reference_revenue_eur: float
    guarantee_pct_by_year: List[float]


@dataclass(frozen=True)
class RevenueAssumptions:
    scenarios: Dict[str, RevenueScenarioAssumptions]


@dataclass(frozen=True)
class PersonnelYearAssumptions:
    consultant_fte: float
    consultant_loaded_cost_eur: float
    backoffice_fte: float
    backoffice_loaded_cost_eur: float
    management_cost_eur: float


@dataclass(frozen=True)
class FixedOverheadYearAssumptions:
    advisory_eur: float
    legal_eur: float
    it_software_eur: float
    office_rent_eur: float
    services_eur: float
    other_services_eur: float


@dataclass(frozen=True)
class VariableCostYearAssumptions:
    training_type: str
    training_value: float
    travel_type: str
    travel_value: float
    communication_type: str
    communication_value: float


@dataclass(frozen=True)
class CostAssumptions:
    inflation_apply: bool
    inflation_rate_pct: float
    personnel_by_year: List[PersonnelYearAssumptions]
    fixed_overhead_by_year: List[FixedOverheadYearAssumptions]
    variable_costs_by_year: List[VariableCostYearAssumptions]


@dataclass(frozen=True)
class TransactionFinancingAssumptions:
    purchase_price_eur: float
    equity_contribution_eur: float
    senior_term_loan_start_eur: float


@dataclass(frozen=True)
class FinancingAssumptions:
    senior_debt_amount_eur: float
    initial_debt_eur: float
    interest_rate_pct: float
    amortization_type: str
    amortization_period_years: int
    grace_period_years: int
    special_repayment_year: int | None
    special_repayment_amount_eur: float
    minimum_dscr: float


@dataclass(frozen=True)
class CashflowAssumptions:
    tax_cash_rate_pct: float
    tax_payment_lag_years: int
    capex_pct_revenue: float
    working_capital_pct_revenue: float
    opening_cash_balance_eur: float


@dataclass(frozen=True)
class BalanceSheetAssumptions:
    opening_equity_eur: float
    depreciation_rate_pct: float
    minimum_cash_balance_eur: float
    pension_obligations_eur: float


@dataclass(frozen=True)
class TaxAssumptions:
    tax_rate_pct: float


@dataclass(frozen=True)
class ValuationAssumptions:
    seller_multiple: float
    market_multiple: float
    reference_year: int
    discount_rate_pct: float
    valuation_start_year: int
    transaction_costs_pct: float


@dataclass(frozen=True)
class EquityAssumptions:
    exit_year: int
    exit_mechanism: str
    investor_participation: str
    management_participation: str


@dataclass(frozen=True)
class Assumptions:
    scenario: str
    revenue: RevenueAssumptions
    cost: CostAssumptions
    transaction_and_financing: TransactionFinancingAssumptions
    financing: FinancingAssumptions
    cashflow: CashflowAssumptions
    balance_sheet: BalanceSheetAssumptions
    tax_and_distributions: TaxAssumptions
    valuation: ValuationAssumptions
    equity: EquityAssumptions


def _year_list(value: float) -> List[float]:
    return [float(value) for _ in range(PLANNING_YEARS)]


def default_assumptions() -> Assumptions:
    base_revenue = RevenueScenarioAssumptions(
        workdays_per_year=_year_list(220.0),
        utilization_rate_pct=_year_list(0.7),
        group_day_rate_eur=_year_list(900.0),
        external_day_rate_eur=_year_list(1100.0),
        day_rate_growth_pct=_year_list(0.02),
        revenue_growth_pct=_year_list(0.0),
        group_capacity_share_pct=_year_list(0.7),
        external_capacity_share_pct=_year_list(0.3),
        reference_revenue_eur=2_500_000.0,
        guarantee_pct_by_year=_year_list(0.0),
    )
    revenue = RevenueAssumptions(
        scenarios={
            "Base": base_revenue,
            "Best": RevenueScenarioAssumptions(
                workdays_per_year=_year_list(225.0),
                utilization_rate_pct=_year_list(0.75),
                group_day_rate_eur=_year_list(950.0),
                external_day_rate_eur=_year_list(1200.0),
                day_rate_growth_pct=_year_list(0.03),
                revenue_growth_pct=_year_list(0.0),
                group_capacity_share_pct=_year_list(0.65),
                external_capacity_share_pct=_year_list(0.35),
                reference_revenue_eur=2_500_000.0,
                guarantee_pct_by_year=_year_list(0.0),
            ),
            "Worst": RevenueScenarioAssumptions(
                workdays_per_year=_year_list(210.0),
                utilization_rate_pct=_year_list(0.6),
                group_day_rate_eur=_year_list(850.0),
                external_day_rate_eur=_year_list(1000.0),
                day_rate_growth_pct=_year_list(0.01),
                revenue_growth_pct=_year_list(0.0),
                group_capacity_share_pct=_year_list(0.75),
                external_capacity_share_pct=_year_list(0.25),
                reference_revenue_eur=2_500_000.0,
                guarantee_pct_by_year=_year_list(0.0),
            ),
        }
    )

    cost = CostAssumptions(
        inflation_apply=True,
        inflation_rate_pct=0.02,
        personnel_by_year=[
            PersonnelYearAssumptions(
                consultant_fte=8.0,
                consultant_loaded_cost_eur=95_000.0,
                backoffice_fte=1.0,
                backoffice_loaded_cost_eur=65_000.0,
                management_cost_eur=150_000.0,
            )
            for _ in range(PLANNING_YEARS)
        ],
        fixed_overhead_by_year=[
            FixedOverheadYearAssumptions(
                advisory_eur=0.0,
                legal_eur=0.0,
                it_software_eur=12_000.0,
                office_rent_eur=30_000.0,
                services_eur=5_000.0,
                other_services_eur=0.0,
            )
            for _ in range(PLANNING_YEARS)
        ],
        variable_costs_by_year=[
            VariableCostYearAssumptions(
                training_type="EUR",
                training_value=0.0,
                travel_type="EUR",
                travel_value=0.0,
                communication_type="EUR",
                communication_value=0.0,
            )
            for _ in range(PLANNING_YEARS)
        ],
    )

    transaction_and_financing = TransactionFinancingAssumptions(
        purchase_price_eur=5_000_000.0,
        equity_contribution_eur=2_000_000.0,
        senior_term_loan_start_eur=3_000_000.0,
    )

    financing = FinancingAssumptions(
        senior_debt_amount_eur=3_000_000.0,
        initial_debt_eur=3_000_000.0,
        interest_rate_pct=0.06,
        amortization_type="Linear",
        amortization_period_years=5,
        grace_period_years=0,
        special_repayment_year=None,
        special_repayment_amount_eur=0.0,
        minimum_dscr=1.3,
    )

    cashflow = CashflowAssumptions(
        tax_cash_rate_pct=0.25,
        tax_payment_lag_years=0,
        capex_pct_revenue=0.0,
        working_capital_pct_revenue=0.0,
        opening_cash_balance_eur=0.0,
    )

    balance_sheet = BalanceSheetAssumptions(
        opening_equity_eur=0.0,
        depreciation_rate_pct=0.1,
        minimum_cash_balance_eur=0.0,
        pension_obligations_eur=4_000_000.0,
    )

    tax_and_distributions = TaxAssumptions(tax_rate_pct=0.25)

    valuation = ValuationAssumptions(
        seller_multiple=6.0,
        market_multiple=6.0,
        reference_year=4,
        discount_rate_pct=0.10,
        valuation_start_year=0,
        transaction_costs_pct=0.0,
    )

    equity = EquityAssumptions(
        exit_year=4,
        exit_mechanism="Management buys out investor",
        investor_participation="Pro-rata",
        management_participation="Pro-rata",
    )

    return Assumptions(
        scenario="Base",
        revenue=revenue,
        cost=cost,
        transaction_and_financing=transaction_and_financing,
        financing=financing,
        cashflow=cashflow,
        balance_sheet=balance_sheet,
        tax_and_distributions=tax_and_distributions,
        valuation=valuation,
        equity=equity,
    )
