from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def _case_name(path: str) -> str:
    if not path:
        return "Unnamed Case"
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def _render_scenario_selector(current: str) -> None:
    options = ["Worst", "Base", "Best"]
    if "view_scenario" not in st.session_state:
        st.session_state["view_scenario"] = current
    current_value = st.session_state["view_scenario"]
    if current_value not in options:
        current_value = current
    st.radio(
        "Scenario",
        options,
        index=options.index(current_value),
        horizontal=True,
        key="view_scenario",
        label_visibility="collapsed",
    )


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown("# Cashflow & Liquidity")
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_cashflow_key_assumptions(
            assumptions, "cashflow.assumptions"
        )
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )
    _render_scenario_selector(assumptions.scenario)
    output_container = st.container()
    updated_result = run_model(updated_assumptions)
    cash_balances = [row["cash_balance"] for row in updated_result.cashflow]
    min_cash = min(cash_balances) if cash_balances else 0.0
    negative_years = len([value for value in cash_balances if value < 0])
    peak_funding = abs(min_cash) if min_cash < 0 else 0.0
    kpi_rows = [
        {"Metric": "Minimum Cash Balance", "Value": outputs._format_money(min_cash)},
        {"Metric": "Years with Negative Cash", "Value": str(negative_years)},
        {
            "Metric": "Peak Cash Requirement (Max funding gap)",
            "Value": outputs._format_money(peak_funding),
        },
    ]
    with output_container:
        outputs._render_kpi_table_html(kpi_rows, ["Metric", "Value"])
        outputs.render_cashflow_liquidity(updated_result)
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "**1) Business Question**\n"
            "Does the business run out of cash at any point, and is the resulting funding gap acceptable?\n\n"
            "**2) What This Shows / What This Does NOT Show**\n"
            "Shows operating cash generation, investment needs, financing flows, and the resulting closing cash position each year.\n"
            "Does not show profitability quality, valuation, or the source of any additional funding beyond the modeled debt.\n\n"
            "**3) Calculation Logic (Transparent, Step-by-Step)**\n"
            "Operating cashflow is built from EBITDA, reduced by cash taxes, and adjusted for working capital changes.\n"
            "Free cashflow then subtracts capex from operating cashflow.\n"
            "Net cashflow adds financing flows (debt drawdown) and subtracts interest and debt repayment.\n"
            "Closing cash is the opening cash balance plus net cashflow; the transition year includes closing and financing effects.\n\n"
            "**4) Interpretation for the Decision**\n"
            "Negative closing cash indicates a funding gap that must be filled by additional equity or debt.\n"
            "Earlier and deeper gaps increase deal fragility and reduce financing flexibility.\n\n"
            "**5) Insights & Red Flags**\n"
            "Consecutive negative years signal structural underfunding, not just timing noise.\n"
            "Large peak funding gaps in the transition year are a common deal-breaker without committed liquidity support.\n"
            "Improving cash after Year 1 only matters if the initial funding is credible.\n\n"
            "**6) Key Dependencies**\n"
            "EBITDA path, tax rate and payment lag, capex as a percentage of revenue, working capital percentage of revenue, opening cash balance, debt drawdown and repayment schedule."
        )
    return updated_assumptions
