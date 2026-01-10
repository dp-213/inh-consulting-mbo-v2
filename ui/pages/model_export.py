from __future__ import annotations

import json
from dataclasses import asdict

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions


def render(assumptions: Assumptions, result: ModelResult) -> None:
    st.markdown("## Model Export / Snapshot")
    st.markdown("For internal / AI-assisted analysis only.")
    st.markdown(
        "Structured summaries below are intended for expert review, "
        "scenario discussion, and AI-assisted sparring."
    )

    st.markdown("### A) Model Facts (Human-Readable)")
    st.markdown("Key inputs, outputs, and assumptions for the current case.")
    st.table(_key_inputs(assumptions))
    st.table(_key_outputs(result))
    st.table(
        [
            {
                "Assumptions Summary": (
                    "Scenario-driven planning case with explicit revenue, cost, financing, "
                    "cash flow, balance sheet, and valuation assumptions."
                )
            }
        ]
    )

    st.markdown("---")
    st.markdown("### B) Model Structure (For AI / Review)")
    snapshot = asdict(assumptions)
    st.dataframe(_flatten_snapshot(snapshot), use_container_width=True)

    st.markdown("---")
    st.markdown("### C) Raw JSON (Advanced)")
    with st.expander("Show Raw JSON", expanded=False):
        st.table([{"Snapshot (JSON)": json.dumps(snapshot, indent=2)}])


def _flatten_snapshot(snapshot: dict) -> list[dict]:
    rows: list[dict] = []

    def walk(prefix: str, value):
        if isinstance(value, dict):
            for key, inner in value.items():
                walk(f"{prefix}.{key}" if prefix else key, inner)
        elif isinstance(value, list):
            rows.append(
                {
                    "Section": prefix.split(".")[0] if "." in prefix else prefix,
                    "Field": prefix,
                    "Value": ", ".join(str(item) for item in value),
                }
            )
        else:
            rows.append(
                {
                    "Section": prefix.split(".")[0] if "." in prefix else prefix,
                    "Field": prefix,
                    "Value": value,
                }
            )

    walk("", snapshot)
    return rows


def _key_inputs(assumptions: Assumptions) -> list[dict]:
    scenario = assumptions.scenario
    revenue = assumptions.revenue.scenarios[scenario]
    rows = [
        {"Area": "Revenue", "Driver": "Workdays (Year 0)", "Value": revenue.workdays_per_year[0], "Unit": "Days"},
        {"Area": "Revenue", "Driver": "Utilization (Year 0)", "Value": f"{revenue.utilization_rate_pct[0]*100:.1f}%", "Unit": "%"},
        {"Area": "Revenue", "Driver": "Group Day Rate (Year 0)", "Value": _format_money(revenue.group_day_rate_eur[0]), "Unit": "€"},
        {"Area": "Revenue", "Driver": "External Day Rate (Year 0)", "Value": _format_money(revenue.external_day_rate_eur[0]), "Unit": "€"},
        {"Area": "Revenue", "Driver": "Guarantee (Year 0)", "Value": f"{revenue.guarantee_pct_by_year[0]*100:.1f}%", "Unit": "%"},
        {"Area": "Cost", "Driver": "Consultant Headcount (Year 0)", "Value": assumptions.cost.personnel_by_year[0].consultant_fte, "Unit": "People"},
        {"Area": "Cost", "Driver": "Consultant Cost (All-in)", "Value": _format_money(assumptions.cost.personnel_by_year[0].consultant_loaded_cost_eur), "Unit": "€"},
        {"Area": "Cost", "Driver": "Backoffice Headcount (Year 0)", "Value": assumptions.cost.personnel_by_year[0].backoffice_fte, "Unit": "People"},
        {"Area": "Financing", "Driver": "Purchase Price", "Value": _format_money(assumptions.transaction_and_financing.purchase_price_eur), "Unit": "€"},
        {"Area": "Financing", "Driver": "Owner Contribution", "Value": _format_money(assumptions.transaction_and_financing.equity_contribution_eur), "Unit": "€"},
        {"Area": "Financing", "Driver": "Senior Loan Amount", "Value": _format_money(assumptions.financing.senior_debt_amount_eur), "Unit": "€"},
        {"Area": "Financing", "Driver": "Interest Rate", "Value": f"{assumptions.financing.interest_rate_pct*100:.1f}%", "Unit": "%"},
        {"Area": "Financing", "Driver": "Repayment Type", "Value": assumptions.financing.amortization_type, "Unit": ""},
        {"Area": "Financing", "Driver": "Repayment Period", "Value": assumptions.financing.amortization_period_years, "Unit": "Years"},
        {"Area": "Other", "Driver": "Capital Spend (% of Revenue)", "Value": f"{assumptions.cashflow.capex_pct_revenue*100:.1f}%", "Unit": "%"},
        {"Area": "Other", "Driver": "Cash Tied in Operations", "Value": f"{assumptions.cashflow.working_capital_pct_revenue*100:.1f}%", "Unit": "%"},
        {"Area": "Other", "Driver": "Profit Tax Rate", "Value": f"{assumptions.tax_and_distributions.tax_rate_pct*100:.1f}%", "Unit": "%"},
        {"Area": "Other", "Driver": "Seller Multiple", "Value": f"{assumptions.valuation.seller_multiple:.2f}x", "Unit": "x"},
    ]
    return rows


def _key_outputs(result: ModelResult) -> list[dict]:
    irr = result.equity.get("irr", 0.0)
    initial_equity = result.equity.get("initial_equity", 0.0)
    exit_value = result.equity.get("exit_value", 0.0)
    moic = exit_value / initial_equity if initial_equity else 0.0
    peak_loan = max((row.get("closing_debt", 0.0) for row in result.debt), default=0.0)
    min_coverage = _min_dscr(result.debt)
    last_year = len(result.pnl) - 1
    return [
        {"Metric": "Investor Return (%)", "Value": f"{irr*100:.1f}%"},
        {"Metric": "Owner Multiple", "Value": f"{moic:.2f}x"},
        {"Metric": "Owner Proceeds", "Value": _format_money(exit_value)},
        {"Metric": "Peak Loan Balance", "Value": _format_money(peak_loan)},
        {"Metric": "Minimum Loan Coverage", "Value": f"{min_coverage:.2f}" if min_coverage is not None else "n/a"},
        {"Metric": "Revenue (Year 4)", "Value": _format_money(result.pnl[last_year]["revenue"])},
        {"Metric": "Profit Before Depreciation (Year 4)", "Value": _format_money(result.pnl[last_year]["ebitda"])},
        {"Metric": "Net Profit (Year 4)", "Value": _format_money(result.pnl[last_year]["net_income"])},
        {"Metric": "Cash After Investment (Year 4)", "Value": _format_money(result.cashflow[last_year]["free_cashflow"])},
    ]


def _format_money(value: float) -> str:
    if value is None:
        return ""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.1f} m€"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} k€"
    return f"{value:,.0f} €"


def _min_dscr(debt_schedule: list[dict]) -> float | None:
    values = [row.get("dscr") for row in debt_schedule if row.get("dscr") is not None]
    if not values:
        return None
    return min(values)
