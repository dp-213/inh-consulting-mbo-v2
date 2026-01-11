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
    default_assumptions,
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
    defaults = default_assumptions()

    scenario_data = data.get("revenue", {}).get("scenarios", {})
    base_default = defaults.revenue.scenarios.get("Base")
    revenue_scenarios: dict[str, RevenueScenarioAssumptions] = {}
    for name, default_scenario in defaults.revenue.scenarios.items():
        merged = _merge_revenue_scenario(
            scenario_data.get(name, {}),
            default_scenario,
        )
        revenue_scenarios[name] = merged
    for name, payload in scenario_data.items():
        if name in revenue_scenarios:
            continue
        reference_default = base_default or next(iter(defaults.revenue.scenarios.values()))
        revenue_scenarios[name] = _merge_revenue_scenario(payload, reference_default)
    revenue = RevenueAssumptions(scenarios=revenue_scenarios)

    cost_data = data.get("cost", {})
    cost = CostAssumptions(
        inflation_apply=cost_data.get(
            "inflation_apply", defaults.cost.inflation_apply
        ),
        inflation_rate_pct=cost_data.get(
            "inflation_rate_pct", defaults.cost.inflation_rate_pct
        ),
        personnel_by_year=[
            PersonnelYearAssumptions(**row)
            for row in _merge_yearly_items(
                defaults.cost.personnel_by_year,
                cost_data.get("personnel_by_year", []),
            )
        ],
        fixed_overhead_by_year=[
            FixedOverheadYearAssumptions(**row)
            for row in _merge_yearly_items(
                defaults.cost.fixed_overhead_by_year,
                cost_data.get("fixed_overhead_by_year", []),
            )
        ],
        variable_costs_by_year=[
            VariableCostYearAssumptions(**row)
            for row in _merge_yearly_items(
                defaults.cost.variable_costs_by_year,
                cost_data.get("variable_costs_by_year", []),
            )
        ],
    )

    transaction_and_financing = TransactionFinancingAssumptions(
        **_merge_dict(
            asdict(defaults.transaction_and_financing),
            data.get("transaction_and_financing", {}),
        )
    )
    financing = FinancingAssumptions(
        **_merge_dict(
            asdict(defaults.financing),
            data.get("financing", {}),
        )
    )
    cashflow = CashflowAssumptions(
        **_merge_dict(
            asdict(defaults.cashflow),
            data.get("cashflow", {}),
        )
    )
    balance_sheet = BalanceSheetAssumptions(
        **_merge_dict(
            asdict(defaults.balance_sheet),
            data.get("balance_sheet", {}),
        )
    )
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
    tax_and_distributions = TaxAssumptions(
        **_merge_dict(
            asdict(defaults.tax_and_distributions),
            data.get("tax_and_distributions", {}),
        )
    )
    valuation_data = _merge_dict(
        asdict(defaults.valuation),
        data.get("valuation", {}),
    )
    if "market_multiple" not in valuation_data:
        valuation_data["market_multiple"] = valuation_data.get("seller_multiple", 0.0)
    valuation = ValuationAssumptions(**valuation_data)
    equity = EquityAssumptions(
        **_merge_dict(
            asdict(defaults.equity),
            data.get("equity", {}),
        )
    )

    scenario_value = data.get("scenario", defaults.scenario)
    if scenario_value not in revenue_scenarios:
        scenario_value = defaults.scenario

    return Assumptions(
        scenario=scenario_value,
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


def _merge_dict(defaults: dict, overrides: dict | None) -> dict:
    merged = dict(defaults)
    if overrides:
        merged.update(overrides)
    return merged


def _merge_year_list(defaults: list[float], overrides: list[float] | None) -> list[float]:
    if not isinstance(overrides, list):
        return list(defaults)
    merged: list[float] = []
    for idx, value in enumerate(defaults):
        merged.append(overrides[idx] if idx < len(overrides) else value)
    return merged


def _merge_yearly_items(defaults: list, overrides: list[dict]) -> list[dict]:
    merged: list[dict] = []
    for idx, default_item in enumerate(defaults):
        override = overrides[idx] if idx < len(overrides) else {}
        merged.append(_merge_dict(asdict(default_item), override))
    return merged


def _merge_revenue_scenario(
    data: dict, defaults: RevenueScenarioAssumptions
) -> RevenueScenarioAssumptions:
    return RevenueScenarioAssumptions(
        workdays_per_year=_merge_year_list(
            defaults.workdays_per_year, data.get("workdays_per_year")
        ),
        utilization_rate_pct=_merge_year_list(
            defaults.utilization_rate_pct, data.get("utilization_rate_pct")
        ),
        group_day_rate_eur=_merge_year_list(
            defaults.group_day_rate_eur, data.get("group_day_rate_eur")
        ),
        external_day_rate_eur=_merge_year_list(
            defaults.external_day_rate_eur, data.get("external_day_rate_eur")
        ),
        day_rate_growth_pct=_merge_year_list(
            defaults.day_rate_growth_pct, data.get("day_rate_growth_pct")
        ),
        revenue_growth_pct=_merge_year_list(
            defaults.revenue_growth_pct, data.get("revenue_growth_pct")
        ),
        group_capacity_share_pct=_merge_year_list(
            defaults.group_capacity_share_pct, data.get("group_capacity_share_pct")
        ),
        external_capacity_share_pct=_merge_year_list(
            defaults.external_capacity_share_pct, data.get("external_capacity_share_pct")
        ),
        reference_revenue_eur=data.get(
            "reference_revenue_eur", defaults.reference_revenue_eur
        ),
        guarantee_pct_by_year=_merge_year_list(
            defaults.guarantee_pct_by_year, data.get("guarantee_pct_by_year")
        ),
    )
