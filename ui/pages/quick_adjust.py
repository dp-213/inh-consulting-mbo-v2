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
        avg_day_rate_default = (
            (group_rate + external_rate) / 2 if group_rate or external_rate else 0.0
        )
    consultant_fte_default = assumptions.cost.personnel_by_year[year_index].consultant_fte
    overhead_default = 100.0
    steering_state = st.session_state.setdefault("operational_steering", {})
    scenario_state = steering_state.setdefault(scenario, {})

    with st.expander("Operational Steering Levers", expanded=False):
        top_cols = st.columns([0.8, 0.2])
        reset_key = f"{key_prefix}.reset.{scenario}"
        if top_cols[1].button("Reset to planning values", key=reset_key):
            scenario_state.update(
                {
                    "utilization_rate": utilization_default,
                    "avg_day_rate": avg_day_rate_default,
                    "consultant_fte": consultant_fte_default,
                    "overhead_pct": overhead_default,
                }
            )
            st.rerun()

        st.markdown("**Capacity & Utilization**")
        utilization_key = f"{key_prefix}.utilization.{scenario}"
        utilization_rate = st.number_input(
            "Utilization rate",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=float(scenario_state.get("utilization_rate", utilization_default)),
            key=utilization_key,
        )
        st.markdown("**Pricing**")
        day_rate_key = f"{key_prefix}.day_rate.{scenario}"
        avg_day_rate = st.number_input(
            "Average day rate",
            min_value=0.0,
            step=50.0,
            value=float(scenario_state.get("avg_day_rate", avg_day_rate_default)),
            key=day_rate_key,
        )
        st.markdown("**People Costs**")
        fte_key = f"{key_prefix}.consultant_fte.{scenario}"
        consultant_fte = st.number_input(
            "Consultant FTE",
            min_value=0.0,
            step=0.5,
            value=float(scenario_state.get("consultant_fte", consultant_fte_default)),
            key=fte_key,
        )
        st.markdown("**Overhead**")
        overhead_key = f"{key_prefix}.overhead_pct.{scenario}"
        overhead_pct = st.number_input(
            "Overhead %",
            min_value=0.0,
            step=5.0,
            value=float(scenario_state.get("overhead_pct", overhead_default)),
            key=overhead_key,
        )
        st.markdown(
            '<div class="hint-text">What-if sliders for this page only. Nothing is saved. Revenue Model stays the source of truth.</div>',
            unsafe_allow_html=True,
        )

    scenario_state.update(
        {
            "utilization_rate": utilization_rate,
            "avg_day_rate": avg_day_rate,
            "consultant_fte": consultant_fte,
            "overhead_pct": overhead_pct,
        }
    )
    for key in (utilization_key, day_rate_key, fte_key, overhead_key):
        if key in st.session_state:
            del st.session_state[key]

    return _apply_quick_inputs(
        assumptions=assumptions,
        utilization_rate=utilization_rate,
        avg_day_rate=avg_day_rate,
        consultant_fte=consultant_fte,
        overhead_pct=overhead_pct,
    )


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
