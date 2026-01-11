from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def _case_name(path: str) -> str:
    if not path:
        return "Unnamed Case"
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def _format_first_negative_year(values: list[float]) -> str:
    for idx, value in enumerate(values):
        if value < 0:
            return outputs.YEAR_LABELS[idx]
    return "None"


def _interpret_liquidity(values: list[float]) -> str:
    if not values:
        return "Liquidity view not available."
    min_value = min(values)
    if min_value < 0:
        first_negative = _format_first_negative_year(values)
        return f"Liquidity breaks in {first_negative} without additional funding."
    return "Liquidity remains positive across the plan horizon."


def render(result: ModelResult, assumptions: Assumptions) -> None:
    case_name = _case_name(st.session_state.get("data_path", ""))
    st.markdown("# Overview")
    st.markdown(
        f'<div class="page-indicator">Case: {case_name}</div>',
        unsafe_allow_html=True,
    )

    purchase_price = assumptions.transaction_and_financing.purchase_price_eur
    debt_amount = assumptions.financing.senior_debt_amount_eur
    management_equity = assumptions.transaction_and_financing.equity_contribution_eur
    total_equity_needed = max(purchase_price - debt_amount, 0.0)
    external_equity = max(total_equity_needed - management_equity, 0.0)

    debt_year0 = result.debt[0] if result.debt else {}
    closing_debt = debt_year0.get("closing_debt", debt_amount)
    cash_at_close = result.balance_sheet[0].get("cash", 0.0) if result.balance_sheet else 0.0
    net_debt_close = closing_debt - cash_at_close

    enterprise_value = result.equity.get("enterprise_value", 0.0)
    pension_obligation = assumptions.balance_sheet.pension_obligations_eur
    equity_price = purchase_price - net_debt_close - pension_obligation
    total_equity_invested = management_equity + external_equity
    management_share = management_equity / total_equity_invested if total_equity_invested else 0.0
    external_share = external_equity / total_equity_invested if total_equity_invested else 0.0
    management_equity_value = equity_price * management_share
    external_equity_value = equity_price * external_share
    st.markdown("### Deal Snapshot – Mechanics")
    snapshot_rows = [
        ("Enterprise Value (Headline)", [enterprise_value]),
        ("Purchase Price (Enterprise)", [purchase_price]),
        ("Equity Value (Mgmt / Investor)", [f"{outputs._format_money(management_equity_value)} / {outputs._format_money(external_equity_value)}"]),
        ("Debt Amount", [debt_amount]),
        ("Net Debt at Close", [net_debt_close]),
        ("Pension Obligations Assumed", [pension_obligation]),
        ("Plan Horizon", ["Transition Year (Year 0) → Business Plan Years (1–4)"]),
    ]
    outputs._render_statement_table_html(
        snapshot_rows,
        bold_labels={"Enterprise Value (Headline)", "Purchase Price (Enterprise)"},
        years=1,
        year_labels=["Value"],
    )
    st.markdown("### Price Composition")
    composition_rows = [
        ("Enterprise Price", [purchase_price]),
        ("Net Debt at Close", [net_debt_close]),
        ("Pension Obligations", [pension_obligation]),
        ("Equity Price", [equity_price]),
    ]
    outputs._render_statement_table_html(
        composition_rows,
        bold_labels={"Equity Price"},
        years=1,
        year_labels=["Value"],
    )

    top_left, top_right = st.columns(2)
    bottom_left, bottom_right = st.columns(2)

    with top_left:
        st.markdown("### Business Economics (Steady-State)")
        year_index = 2
        revenue = result.pnl[year_index]["revenue"]
        personnel_costs = result.pnl[year_index]["personnel_costs"]
        ebitda = result.pnl[year_index]["ebitda"]
        consultant_fte = assumptions.cost.personnel_by_year[year_index].consultant_fte
        utilization = assumptions.revenue.scenarios[
            assumptions.scenario
        ].utilization_rate_pct[year_index]
        revenue_per_consultant = (
            revenue / consultant_fte if consultant_fte else 0.0
        )
        operating_rows = [
            ("Revenue per Consultant", [outputs._format_money(revenue_per_consultant)]),
            ("Utilization", [f"{utilization:.1f}%"]),
            (
                "Personnel Cost Ratio",
                [outputs._format_percent(personnel_costs, revenue)],
            ),
            ("EBITDA Margin", [outputs._format_percent(ebitda, revenue)]),
        ]
        outputs._render_statement_table_html(
            operating_rows,
            years=1,
            year_labels=[outputs.YEAR_LABELS[year_index]],
        )

    with top_right:
        st.markdown("### Cash & Liquidity Risk")
        cash_balances = [row["cash_balance"] for row in result.cashflow]
        min_cash = min(cash_balances) if cash_balances else 0.0
        peak_gap = abs(min_cash) if min_cash < 0 else 0.0
        cash_rows = [
            ("Minimum Cash Balance", [outputs._format_money(min_cash)]),
            ("First Year with Negative Cash", [_format_first_negative_year(cash_balances)]),
            ("Peak Funding Gap", [outputs._format_money(peak_gap)]),
        ]
        outputs._render_statement_table_html(
            cash_rows,
            years=1,
            year_labels=["Value"],
        )
        st.markdown(
            f'<div class="subtle">{_interpret_liquidity(cash_balances)}</div>',
            unsafe_allow_html=True,
        )

    with bottom_left:
        st.markdown("### Debt / Bank View")
        coverage = [row.get("dscr") for row in result.debt]
        min_required = assumptions.financing.minimum_dscr
        dscr_values = [value for value in coverage if value is not None]
        min_dscr = min(dscr_values) if dscr_values else 0.0
        years_below = len([value for value in dscr_values if value < min_required])
        covenant_breach = "YES" if years_below > 0 else "NO"
        peak_debt = max(
            row.get("opening_debt", row.get("closing_debt", 0.0)) for row in result.debt
        )
        debt_rows = [
            ("Minimum DSCR", [f"{min_dscr:.2f}x"]),
            ("Years below covenant", [str(years_below)]),
            ("Peak Debt", [outputs._format_money(peak_debt)]),
            ("Covenant Breach", [covenant_breach]),
        ]
        outputs._render_statement_table_html(
            debt_rows,
            years=1,
            year_labels=["Value"],
        )

    with bottom_right:
        st.markdown("### Value vs. Price – Decision Core")
        free_cf = [row["free_cashflow"] for row in result.cashflow]
        discount_rate = assumptions.valuation.discount_rate_pct
        start_year = assumptions.valuation.valuation_start_year
        running = 0.0
        for idx, value in enumerate(free_cf):
            if idx < start_year:
                continue
            factor = 1 / ((1 + discount_rate) ** (idx - start_year + 1))
            running += value * factor
        dcf_value = running
        intrinsic_value = sum(
            value for idx, value in enumerate(free_cf) if idx >= start_year
        )
        multiple_equity = enterprise_value - net_debt_close - pension_obligation
        dcf_equity = dcf_value - net_debt_close - pension_obligation
        intrinsic_equity = intrinsic_value - net_debt_close - pension_obligation
        valuation_min = min(multiple_equity, dcf_equity, intrinsic_equity)
        valuation_max = max(multiple_equity, dcf_equity, intrinsic_equity)
        midpoint = (valuation_min + valuation_max) / 2 if valuation_min or valuation_max else 0.0
        affordability = result.equity.get("exit_value", 0.0) - pension_obligation
        negotiation_gap = equity_price - midpoint

        value_rows = [
            ("Valuation Min (Today)", [valuation_min]),
            ("Valuation Midpoint (Today)", [midpoint]),
            ("Valuation Max (Today)", [valuation_max]),
            ("Buyer Affordability (Ceiling)", [affordability]),
            ("Purchase Price (Enterprise)", [purchase_price]),
            ("Negotiation Gap (EUR)", [negotiation_gap]),
        ]
        outputs._render_statement_table_html(
            value_rows,
            years=1,
            year_labels=["Value"],
        )
        if purchase_price > affordability and purchase_price > valuation_max:
            interpretation = "Purchase price exceeds conservative valuation and affordability."
        elif purchase_price > affordability:
            interpretation = "Purchase price is below intrinsic value but above financing-based affordability."
        else:
            interpretation = "Purchase price is below affordability and within the valuation range."
        st.markdown(f'<div class="subtle">{interpretation}</div>', unsafe_allow_html=True)

    with st.expander("Key Assumptions (View Only)", expanded=False):
        key_rows = [
            ("Purchase Price", [purchase_price]),
            ("Debt Amount", [debt_amount]),
            ("Interest Rate", [f"{assumptions.financing.interest_rate_pct:.2f}%"]),
            ("Seller Multiple", [f"{assumptions.valuation.seller_multiple:.2f}x"]),
            ("Discount Rate", [f"{assumptions.valuation.discount_rate_pct:.2f}%"]),
        ]
        outputs._render_statement_table_html(
            key_rows,
            years=1,
            year_labels=["Value"],
        )
