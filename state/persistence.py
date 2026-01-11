from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

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
    EquityAssumptions,
)


def save_assumptions(assumptions: Assumptions, path: str | Path) -> None:
    data = asdict(assumptions)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")


def load_assumptions(path: str | Path) -> Assumptions:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _assumptions_from_dict(data)


def _assumptions_from_dict(data: dict) -> Assumptions:
    revenue = RevenueAssumptions(
        scenarios={
            key: _revenue_scenario_from_dict(value)
            for key, value in data["revenue"]["scenarios"].items()
        }
    )
    cost = CostAssumptions(
        inflation_apply=data["cost"]["inflation_apply"],
        inflation_rate_pct=data["cost"]["inflation_rate_pct"],
        personnel_by_year=[
            PersonnelYearAssumptions(**row)
            for row in data["cost"]["personnel_by_year"]
        ],
        fixed_overhead_by_year=[
            FixedOverheadYearAssumptions(**row)
            for row in data["cost"]["fixed_overhead_by_year"]
        ],
        variable_costs_by_year=[
            VariableCostYearAssumptions(**row)
            for row in data["cost"]["variable_costs_by_year"]
        ],
    )
    transaction_and_financing = TransactionFinancingAssumptions(
        **data["transaction_and_financing"]
    )
    financing = FinancingAssumptions(**data["financing"])
    cashflow = CashflowAssumptions(**data["cashflow"])
    balance_sheet = BalanceSheetAssumptions(**data["balance_sheet"])
    if (
        balance_sheet.opening_equity_eur
        != cashflow.opening_cash_balance_eur
    ):
        cashflow = CashflowAssumptions(
            tax_cash_rate_pct=cashflow.tax_cash_rate_pct,
            tax_payment_lag_years=cashflow.tax_payment_lag_years,
            capex_pct_revenue=cashflow.capex_pct_revenue,
            working_capital_pct_revenue=cashflow.working_capital_pct_revenue,
            opening_cash_balance_eur=balance_sheet.opening_equity_eur,
        )
    tax_and_distributions = TaxAssumptions(**data["tax_and_distributions"])
    valuation = ValuationAssumptions(**data["valuation"])
    equity = EquityAssumptions(**data["equity"])

    return Assumptions(
        scenario=data["scenario"],
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


def _revenue_scenario_from_dict(data: dict) -> RevenueScenarioAssumptions:
    return RevenueScenarioAssumptions(**data)
