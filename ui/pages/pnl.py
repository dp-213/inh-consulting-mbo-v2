from __future__ import annotations

from dataclasses import replace

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions, RevenueAssumptions
from ui import outputs


def _case_name(path: str) -> str:
    if not path:
        return "Unnamed Case"
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def _apply_quick_inputs(
    assumptions: Assumptions,
    utilization_rate: float,
    avg_day_rate: float,
    consultant_fte: float,
    overhead_pct: float,
) -> Assumptions:
    scenario = assumptions.scenario
    scenarios = dict(assumptions.revenue.scenarios)
    current = scenarios[scenario]
    updated_revenue = replace(
        current,
        utilization_rate_pct=[utilization_rate for _ in range(5)],
        group_day_rate_eur=[avg_day_rate for _ in range(5)],
        external_day_rate_eur=[avg_day_rate for _ in range(5)],
    )
    scenarios[scenario] = updated_revenue

    updated_personnel = [
        replace(row, consultant_fte=consultant_fte)
        for row in assumptions.cost.personnel_by_year
    ]
    overhead_factor = max(overhead_pct, 0.0) / 100.0
    updated_fixed_overhead = [
        replace(
            row,
            advisory_eur=row.advisory_eur * overhead_factor,
            legal_eur=row.legal_eur * overhead_factor,
            it_software_eur=row.it_software_eur * overhead_factor,
            office_rent_eur=row.office_rent_eur * overhead_factor,
            services_eur=row.services_eur * overhead_factor,
            other_services_eur=row.other_services_eur * overhead_factor,
        )
        for row in assumptions.cost.fixed_overhead_by_year
    ]
    updated_cost = replace(
        assumptions.cost,
        personnel_by_year=updated_personnel,
        fixed_overhead_by_year=updated_fixed_overhead,
    )

    return replace(
        assumptions,
        revenue=RevenueAssumptions(scenarios=scenarios),
        cost=updated_cost,
    )


def render(result: ModelResult, assumptions: Assumptions) -> None:
    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown("# Operating Model (P&L)")
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )

    scenario_assumptions = assumptions.revenue.scenarios[scenario]
    year_index = 0
    utilization_default = scenario_assumptions.utilization_rate_pct[year_index]
    group_rate = scenario_assumptions.group_day_rate_eur[year_index]
    external_rate = scenario_assumptions.external_day_rate_eur[year_index]
    group_share = scenario_assumptions.group_capacity_share_pct[year_index]
    external_share = scenario_assumptions.external_capacity_share_pct[year_index]
    total_share = group_share + external_share
    if total_share > 0:
        avg_day_rate_default = (
            (group_rate * group_share) + (external_rate * external_share)
        ) / total_share
    else:
        avg_day_rate_default = (group_rate + external_rate) / 2 if group_rate or external_rate else 0.0
    consultant_fte_default = assumptions.cost.personnel_by_year[year_index].consultant_fte

    with st.expander("Key P&L Drivers (Quick Adjust)", expanded=False):
        cols = st.columns(4)
        utilization_rate = cols[0].number_input(
            "Utilization rate",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=float(utilization_default),
            key=f"pnl.quick.utilization.{scenario}",
        )
        avg_day_rate = cols[1].number_input(
            "Average day rate",
            min_value=0.0,
            step=50.0,
            value=float(avg_day_rate_default),
            key=f"pnl.quick.day_rate.{scenario}",
        )
        consultant_fte = cols[2].number_input(
            "Consultant FTE",
            min_value=0.0,
            step=0.5,
            value=float(consultant_fte_default),
            key=f"pnl.quick.consultant_fte.{scenario}",
        )
        overhead_pct = cols[3].number_input(
            "Overhead %",
            min_value=0.0,
            step=5.0,
            value=100.0,
            key=f"pnl.quick.overhead_pct.{scenario}",
        )

    updated_assumptions = _apply_quick_inputs(
        assumptions=assumptions,
        utilization_rate=utilization_rate,
        avg_day_rate=avg_day_rate,
        consultant_fte=consultant_fte,
        overhead_pct=overhead_pct,
    )
    updated_result = run_model(updated_assumptions)
    outputs.render_operating_model(updated_result, updated_assumptions)
