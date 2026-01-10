from __future__ import annotations

from dataclasses import replace

import streamlit as st

from state.assumptions import (
    Assumptions,
    BalanceSheetAssumptions,
    CashflowAssumptions,
    FinancingAssumptions,
    RevenueAssumptions,
    TransactionFinancingAssumptions,
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

    with st.expander("Operational Steering Levers", expanded=False):
        top_cols = st.columns([0.8, 0.2])
        reset_key = f"{key_prefix}.reset.{scenario}"
        if top_cols[1].button("Reset to planning values", key=reset_key):
            _set_state_defaults(
                {
                    f"{key_prefix}.utilization.{scenario}": utilization_default,
                    f"{key_prefix}.day_rate.{scenario}": avg_day_rate_default,
                    f"{key_prefix}.consultant_fte.{scenario}": consultant_fte_default,
                    f"{key_prefix}.overhead_pct.{scenario}": overhead_default,
                }
            )
            st.rerun()

        st.markdown("**Capacity & Utilization**")
        utilization_rate = st.number_input(
            "Utilization rate",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=float(utilization_default),
            key=f"{key_prefix}.utilization.{scenario}",
        )
        st.markdown("**Pricing**")
        avg_day_rate = st.number_input(
            "Average day rate",
            min_value=0.0,
            step=50.0,
            value=float(avg_day_rate_default),
            key=f"{key_prefix}.day_rate.{scenario}",
        )
        st.markdown("**People Costs**")
        consultant_fte = st.number_input(
            "Consultant FTE",
            min_value=0.0,
            step=0.5,
            value=float(consultant_fte_default),
            key=f"{key_prefix}.consultant_fte.{scenario}",
        )
        st.markdown("**Overhead**")
        overhead_pct = st.number_input(
            "Overhead %",
            min_value=0.0,
            step=5.0,
            value=overhead_default,
            key=f"{key_prefix}.overhead_pct.{scenario}",
        )
        st.markdown(
            '<div class="hint-text">What-if sliders for this page only. Nothing is saved. Revenue Model stays the source of truth.</div>',
            unsafe_allow_html=True,
        )

    return _apply_quick_inputs(
        assumptions=assumptions,
        utilization_rate=utilization_rate,
        avg_day_rate=avg_day_rate,
        consultant_fte=consultant_fte,
        overhead_pct=overhead_pct,
    )


def render_quick_adjust_cashflow(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    cashflow = assumptions.cashflow
    defaults = {
        f"{key_prefix}.tax_rate": cashflow.tax_cash_rate_pct,
        f"{key_prefix}.capex_pct": cashflow.capex_pct_revenue,
        f"{key_prefix}.wc_pct": cashflow.working_capital_pct_revenue,
    }
    with st.expander("Key Cashflow Drivers (Quick Adjust)", expanded=False):
        top_cols = st.columns([0.8, 0.2])
        if top_cols[1].button("Reset to planning values", key=f"{key_prefix}.reset"):
            _set_state_defaults(defaults)
            st.rerun()
        cols = st.columns(3)
        tax_rate = cols[0].number_input(
            "Cash tax rate",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=float(cashflow.tax_cash_rate_pct),
            key=f"{key_prefix}.tax_rate",
        )
        capex_pct = cols[1].number_input(
            "Capex % of revenue",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=float(cashflow.capex_pct_revenue),
            key=f"{key_prefix}.capex_pct",
        )
        wc_pct = cols[2].number_input(
            "Working capital % of revenue",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=float(cashflow.working_capital_pct_revenue),
            key=f"{key_prefix}.wc_pct",
        )
        st.markdown(
            '<div class="hint-text">What-if sliders for this page only. Nothing is saved. Revenue Model stays the source of truth.</div>',
            unsafe_allow_html=True,
        )
    updated_cashflow = CashflowAssumptions(
        tax_cash_rate_pct=tax_rate,
        tax_payment_lag_years=cashflow.tax_payment_lag_years,
        capex_pct_revenue=capex_pct,
        working_capital_pct_revenue=wc_pct,
        opening_cash_balance_eur=cashflow.opening_cash_balance_eur,
    )
    return replace(assumptions, cashflow=updated_cashflow)


def render_quick_adjust_balance_sheet(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    balance = assumptions.balance_sheet
    defaults = {
        f"{key_prefix}.opening_equity": balance.opening_equity_eur,
        f"{key_prefix}.depr_rate": balance.depreciation_rate_pct,
    }
    with st.expander("Balance Sheet Assumptions", expanded=False):
        top_cols = st.columns([0.8, 0.2])
        if top_cols[1].button("Reset to planning values", key=f"{key_prefix}.reset"):
            _set_state_defaults(defaults)
            st.rerun()
        cols = st.columns(2)
        opening_equity = cols[0].number_input(
            "Opening equity (EUR)",
            min_value=0.0,
            step=10000.0,
            value=float(balance.opening_equity_eur),
            key=f"{key_prefix}.opening_equity",
        )
        depr_rate = cols[1].number_input(
            "Depreciation rate",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=float(balance.depreciation_rate_pct),
            key=f"{key_prefix}.depr_rate",
        )
        st.markdown(
            '<div class="hint-text">What-if sliders for this page only. Nothing is saved. Revenue Model stays the source of truth.</div>',
            unsafe_allow_html=True,
        )
    updated_balance = BalanceSheetAssumptions(
        opening_equity_eur=opening_equity,
        depreciation_rate_pct=depr_rate,
    )
    return replace(assumptions, balance_sheet=updated_balance)


def render_quick_adjust_valuation(assumptions: Assumptions, key_prefix: str) -> Assumptions:
    transaction = assumptions.transaction_and_financing
    financing = assumptions.financing
    defaults = {
        f"{key_prefix}.purchase_price": transaction.purchase_price_eur,
        f"{key_prefix}.equity_contrib": transaction.equity_contribution_eur,
        f"{key_prefix}.debt_amount": financing.senior_debt_amount_eur,
        f"{key_prefix}.seller_multiple": assumptions.valuation.seller_multiple,
    }
    with st.expander("Key Valuation Drivers (Quick Adjust)", expanded=False):
        top_cols = st.columns([0.8, 0.2])
        if top_cols[1].button("Reset to planning values", key=f"{key_prefix}.reset"):
            _set_state_defaults(defaults)
            st.rerun()
        cols = st.columns(4)
        purchase_price = cols[0].number_input(
            "Purchase price (EUR)",
            min_value=0.0,
            step=100000.0,
            value=float(transaction.purchase_price_eur),
            key=f"{key_prefix}.purchase_price",
        )
        equity_contrib = cols[1].number_input(
            "Equity contribution (EUR)",
            min_value=0.0,
            step=50000.0,
            value=float(transaction.equity_contribution_eur),
            key=f"{key_prefix}.equity_contrib",
        )
        debt_amount = cols[2].number_input(
            "Senior debt amount (EUR)",
            min_value=0.0,
            step=100000.0,
            value=float(financing.senior_debt_amount_eur),
            key=f"{key_prefix}.debt_amount",
        )
        seller_multiple = cols[3].number_input(
            "Seller multiple",
            min_value=0.0,
            step=0.1,
            value=float(assumptions.valuation.seller_multiple),
            key=f"{key_prefix}.seller_multiple",
        )
        st.markdown(
            '<div class="hint-text">What-if sliders for this page only. Nothing is saved. Revenue Model stays the source of truth.</div>',
            unsafe_allow_html=True,
        )
    updated_transaction = TransactionFinancingAssumptions(
        purchase_price_eur=purchase_price,
        equity_contribution_eur=equity_contrib,
        senior_term_loan_start_eur=transaction.senior_term_loan_start_eur,
    )
    updated_financing = FinancingAssumptions(
        senior_debt_amount_eur=debt_amount,
        initial_debt_eur=financing.initial_debt_eur,
        interest_rate_pct=financing.interest_rate_pct,
        amortization_type=financing.amortization_type,
        amortization_period_years=financing.amortization_period_years,
        grace_period_years=financing.grace_period_years,
        special_repayment_year=financing.special_repayment_year,
        special_repayment_amount_eur=financing.special_repayment_amount_eur,
        minimum_dscr=financing.minimum_dscr,
    )
    updated_valuation = replace(
        assumptions.valuation, seller_multiple=seller_multiple
    )
    return replace(
        assumptions,
        transaction_and_financing=updated_transaction,
        financing=updated_financing,
        valuation=updated_valuation,
    )


def _set_state_defaults(defaults: dict) -> None:
    for key, value in defaults.items():
        st.session_state[key] = value


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
