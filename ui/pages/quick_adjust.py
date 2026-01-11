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
        "Operational Stress Overlay (What-if · temporary)", expanded=False
    ):
        top_cols = st.columns([0.8, 0.2])
        reset_key = f"{key_prefix}.reset.{scenario}"
        if top_cols[1].button("Reset to planning values", key=reset_key):
            scenario_state.update(
                {
                    "utilization_factor": 1.0,
                    "pricing_factor": 1.0,
                    "cost_inflation_factor": 1.0,
                }
            )
            st.rerun()

        st.markdown("**Utilization factor**")
        utilization_key = f"{key_prefix}.utilization_factor.{scenario}"
        utilization_factor = st.slider(
            "Utilization factor",
            min_value=0.85,
            max_value=1.10,
            value=float(scenario_state.get("utilization_factor", 1.0)),
            step=0.01,
            key=utilization_key,
            label_visibility="collapsed",
        )
        st.markdown("**Pricing factor**")
        pricing_key = f"{key_prefix}.pricing_factor.{scenario}"
        pricing_factor = st.slider(
            "Pricing factor",
            min_value=0.90,
            max_value=1.05,
            value=float(scenario_state.get("pricing_factor", 1.0)),
            step=0.01,
            key=pricing_key,
            label_visibility="collapsed",
        )
        st.markdown("**Cost inflation factor**")
        cost_key = f"{key_prefix}.cost_inflation_factor.{scenario}"
        cost_inflation_factor = st.slider(
            "Cost inflation factor",
            min_value=1.00,
            max_value=1.20,
            value=float(scenario_state.get("cost_inflation_factor", 1.0)),
            step=0.01,
            key=cost_key,
            label_visibility="collapsed",
        )
        st.markdown(
            '<div class="hint-text">Temporary overlay for this page only. No planning inputs are changed.</div>',
            unsafe_allow_html=True,
        )

    scenario_state.update(
        {
            "utilization_factor": utilization_factor,
            "pricing_factor": pricing_factor,
            "cost_inflation_factor": cost_inflation_factor,
        }
    )
    for key in (utilization_key, pricing_key, cost_key):
        if key in st.session_state:
            del st.session_state[key]

    return _apply_quick_inputs(
        assumptions=assumptions,
        utilization_factor=utilization_factor,
        pricing_factor=pricing_factor,
        cost_inflation_factor=cost_inflation_factor,
    )


def _apply_quick_inputs(
    assumptions: Assumptions,
    utilization_factor: float,
    pricing_factor: float,
    cost_inflation_factor: float,
) -> Assumptions:
    scenario = assumptions.scenario
    scenarios = dict(assumptions.revenue.scenarios)
    current = scenarios[scenario]
    updated_revenue = replace(
        current,
        utilization_rate_pct=[
            value * utilization_factor for value in current.utilization_rate_pct
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
