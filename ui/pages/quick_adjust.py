from __future__ import annotations

from dataclasses import replace

import streamlit as st

from state.assumptions import (
    Assumptions,
    RevenueAssumptions,
)


def render_quick_adjust_pnl(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    scenario = assumptions.scenario
    scenario_assumptions = assumptions.revenue.scenarios[scenario]
    year_index = 0
    steering_state = st.session_state.setdefault("operational_steering", {})
    scenario_state = steering_state.setdefault(scenario, {})

    with st.expander(
        "Operational Stress Overlay (What-if, non-persistent)", expanded=False
    ):
        top_cols = st.columns([0.8, 0.2])
        reset_key = f"{key_prefix}.reset.{scenario}"
        if top_cols[1].button("Reset to planning values", key=reset_key):
            scenario_state.update(
                {
                    "utilization_delta_pp": 0,
                    "pricing_stress_pct": 0,
                    "cost_inflation_pct": 0,
                }
            )
            st.rerun()

        st.markdown("**Utilization stress (delta vs. plan, percentage points)**")
        utilization_key = f"{key_prefix}.utilization_delta_pp.{scenario}"
        planned_utilization = scenario_assumptions.utilization_rate_pct[year_index]
        max_utilization_delta = int(round((1 - planned_utilization) * 100))
        if max_utilization_delta < 10:
            max_utilization_delta = 10
        utilization_delta_pp = st.slider(
            "Utilization stress (delta vs. plan, percentage points)",
            min_value=-30,
            max_value=max_utilization_delta,
            value=int(scenario_state.get("utilization_delta_pp", 0)),
            step=1,
            key=utilization_key,
            label_visibility="collapsed",
        )
        effective_utilization = max(
            0.0, min(1.0, planned_utilization + (utilization_delta_pp / 100))
        )
        st.markdown(
            f'<div class="subtle">Effective utilization: {effective_utilization * 100:.0f}%</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Pricing stress (day-rate change vs. plan, %)**")
        pricing_key = f"{key_prefix}.pricing_stress_pct.{scenario}"
        pricing_stress_pct = st.slider(
            "Pricing stress (day-rate change vs. plan, %)",
            min_value=-20,
            max_value=5,
            value=int(scenario_state.get("pricing_stress_pct", 0)),
            step=1,
            key=pricing_key,
            label_visibility="collapsed",
        )
        st.markdown(
            '<div class="subtle">Represents blended day-rate pressure (discounting / repricing).</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Cost inflation stress (people + opex, %)**")
        cost_key = f"{key_prefix}.cost_inflation_pct.{scenario}"
        cost_inflation_pct = st.slider(
            "Cost inflation stress (people + opex, %)",
            min_value=0,
            max_value=150,
            value=int(scenario_state.get("cost_inflation_pct", 0)),
            step=1,
            key=cost_key,
            label_visibility="collapsed",
        )
        st.markdown(
            '<div class="subtle">Represents wage inflation, overhead creep, and cost rigidity under stress.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="hint-text">This overlay applies temporary stress deltas only. Planning assumptions remain unchanged.</div>',
            unsafe_allow_html=True,
        )

    scenario_state.update(
        {
            "utilization_delta_pp": utilization_delta_pp,
            "pricing_stress_pct": pricing_stress_pct,
            "cost_inflation_pct": cost_inflation_pct,
        }
    )
    for key in (utilization_key, pricing_key, cost_key):
        if key in st.session_state:
            del st.session_state[key]

    return _apply_quick_inputs(
        assumptions=assumptions,
        utilization_delta_pp=utilization_delta_pp,
        pricing_stress_pct=pricing_stress_pct,
        cost_inflation_pct=cost_inflation_pct,
    )


def _apply_quick_inputs(
    assumptions: Assumptions,
    utilization_delta_pp: int,
    pricing_stress_pct: int,
    cost_inflation_pct: int,
) -> Assumptions:
    scenario = assumptions.scenario
    scenarios = dict(assumptions.revenue.scenarios)
    current = scenarios[scenario]
    utilization_delta = utilization_delta_pp / 100
    pricing_factor = 1 + (pricing_stress_pct / 100)
    cost_inflation_factor = 1 + (cost_inflation_pct / 100)
    updated_revenue = replace(
        current,
        utilization_rate_pct=[
            max(0.0, min(1.0, value + utilization_delta))
            for value in current.utilization_rate_pct
        ],
        group_day_rate_eur=[
            value * pricing_factor for value in current.group_day_rate_eur
        ],
        external_day_rate_eur=[
            value * pricing_factor for value in current.external_day_rate_eur
        ],
    )
    scenarios[scenario] = updated_revenue

    updated_personnel = [
        replace(
            row,
            consultant_loaded_cost_eur=row.consultant_loaded_cost_eur
            * cost_inflation_factor,
            backoffice_loaded_cost_eur=row.backoffice_loaded_cost_eur
            * cost_inflation_factor,
            management_cost_eur=row.management_cost_eur * cost_inflation_factor,
        )
        for row in assumptions.cost.personnel_by_year
    ]
    updated_fixed_overhead = [
        replace(
            row,
            advisory_eur=row.advisory_eur * cost_inflation_factor,
            legal_eur=row.legal_eur * cost_inflation_factor,
            it_software_eur=row.it_software_eur * cost_inflation_factor,
            office_rent_eur=row.office_rent_eur * cost_inflation_factor,
            services_eur=row.services_eur * cost_inflation_factor,
            other_services_eur=row.other_services_eur * cost_inflation_factor,
        )
        for row in assumptions.cost.fixed_overhead_by_year
    ]
    updated_variable_costs = [
        replace(
            row,
            training_value=row.training_value * cost_inflation_factor,
            travel_value=row.travel_value * cost_inflation_factor,
            communication_value=row.communication_value * cost_inflation_factor,
        )
        for row in assumptions.cost.variable_costs_by_year
    ]
    updated_cost = replace(
        assumptions.cost,
        personnel_by_year=updated_personnel,
        fixed_overhead_by_year=updated_fixed_overhead,
        variable_costs_by_year=updated_variable_costs,
    )

    return replace(
        assumptions,
        revenue=RevenueAssumptions(scenarios=scenarios),
        cost=updated_cost,
    )
