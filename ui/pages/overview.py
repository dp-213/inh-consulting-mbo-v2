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


def _build_range_bar(min_value: float, max_value: float, markers: dict[str, float]) -> str:
    if max_value == min_value:
        return "[--------------|--------------]"
    width = 30
    bar = ["-"] * (width + 1)
    bar[0] = "|"
    bar[-1] = "|"
    for label, value in markers.items():
        position = int(round((value - min_value) / (max_value - min_value) * width))
        position = max(0, min(width, position))
        bar[position] = label
    return "[" + "".join(bar) + "]"


def render(result: ModelResult, assumptions: Assumptions) -> None:
    case_name = _case_name(st.session_state.get("data_path", ""))
    st.markdown("# Overview (Decision Screen)")
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

    st.markdown("### Deal Snapshot")
    snapshot_items = [
        ("Purchase Price (Equity)", outputs._format_money(purchase_price)),
        ("Net Debt at Close", outputs._format_money(net_debt_close)),
        (
            "Total Equity Invested (Mgmt / Investor)",
            f"{outputs._format_money(management_equity)} / {outputs._format_money(external_equity)}",
        ),
        ("Debt Amount", outputs._format_money(debt_amount)),
        ("Reference Years", "Transition Year (Year 0) → Business Plan Years 1–4"),
    ]
    snapshot_html = ['<div class="metric-grid">']
    for label, value in snapshot_items:
        snapshot_html.append(
            f'<div><div class="metric-item-label">{label}</div>'
            f'<div class="metric-item-value">{value}</div></div>'
        )
    snapshot_html.append("</div>")
    st.markdown("".join(snapshot_html), unsafe_allow_html=True)

    top_left, top_right = st.columns(2)
    bottom_left, bottom_right = st.columns(2)

    with top_left:
        st.markdown("### Operating Reality")
        year_index = 1
        revenue = result.pnl[year_index]["revenue"]
        personnel_costs = result.pnl[year_index]["personnel_costs"]
        ebitda = result.pnl[year_index]["ebitda"]
        consultant_fte = assumptions.cost.personnel_by_year[year_index].consultant_fte
        revenue_per_consultant = (
            revenue / consultant_fte if consultant_fte else 0.0
        )
        operating_rows = [
            ("Revenue per Consultant", [outputs._format_money(revenue_per_consultant)]),
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
        st.markdown("### Cash & Survival")
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
        st.line_chart(
            {"Cash Balance": cash_balances},
            use_container_width=True,
        )
        st.markdown(f'<div class="subtle">{_interpret_liquidity(cash_balances)}</div>', unsafe_allow_html=True)

    with bottom_left:
        st.markdown("### Debt / Bank View")
        coverage = [row.get("dscr") for row in result.debt]
        min_required = assumptions.financing.minimum_dscr
        dscr_values = [value for value in coverage if value is not None]
        min_dscr = min(dscr_values) if dscr_values else 0.0
        years_below = len([value for value in dscr_values if value < min_required])
        covenant_breach = "YES" if years_below > 0 else "NO"
        debt_rows = [
            ("Minimum DSCR", [f"{min_dscr:.2f}x"]),
            ("Years below covenant", [str(years_below)]),
            ("Covenant Breach", [covenant_breach]),
        ]
        outputs._render_statement_table_html(
            debt_rows,
            years=1,
            year_labels=["Value"],
        )

    with bottom_right:
        st.markdown("### Value vs. Price")
        enterprise_value = result.equity.get("enterprise_value", 0.0)
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
        valuation_min = min(enterprise_value, dcf_value, intrinsic_value)
        valuation_max = max(enterprise_value, dcf_value, intrinsic_value)
        midpoint = (valuation_min + valuation_max) / 2 if valuation_min or valuation_max else 0.0
        affordability = result.equity.get("exit_value", 0.0)

        value_rows = [
            ("Valuation Min (Today)", [valuation_min]),
            ("Valuation Midpoint (Today)", [midpoint]),
            ("Valuation Max (Today)", [valuation_max]),
            ("Buyer Affordability (Ceiling)", [affordability]),
            ("Purchase Price", [purchase_price]),
        ]
        outputs._render_statement_table_html(
            value_rows,
            years=1,
            year_labels=["Value"],
        )
        range_bar = _build_range_bar(
            valuation_min,
            valuation_max,
            {"A": affordability, "P": purchase_price},
        )
        st.markdown(f"`{range_bar}`")
        st.markdown(
            '<div class="subtle">A = buyer affordability, P = purchase price.</div>',
            unsafe_allow_html=True,
        )
        if purchase_price > affordability and purchase_price > valuation_max:
            interpretation = "Purchase price exceeds conservative valuation and affordability."
        elif purchase_price > affordability:
            interpretation = "Purchase price is below intrinsic value but above financing-based affordability."
        else:
            interpretation = "Purchase price is below affordability and within the valuation range."
        st.markdown(f'<div class="subtle">{interpretation}</div>', unsafe_allow_html=True)
