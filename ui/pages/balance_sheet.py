from __future__ import annotations

from dataclasses import replace

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
    st.markdown("# Balance Sheet")
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_balance_sheet_key_assumptions(
            assumptions, "balance.assumptions"
        )
    if (
        updated_assumptions.balance_sheet.opening_equity_eur
        != updated_assumptions.cashflow.opening_cash_balance_eur
    ):
        st.markdown(
            '<div class="subtle">Opening equity is aligned with opening cash to keep the balance sheet in balance.</div>',
            unsafe_allow_html=True,
        )
        updated_assumptions = replace(
            updated_assumptions,
            cashflow=replace(
                updated_assumptions.cashflow,
                opening_cash_balance_eur=updated_assumptions.balance_sheet.opening_equity_eur,
            ),
        )
    st.markdown(
        f'<div class="page-indicator">Case: {case_name} &nbsp;•&nbsp; Scenario: {scenario}</div>',
        unsafe_allow_html=True,
    )
    _render_scenario_selector(assumptions.scenario)
    output_container = st.container()
    updated_result = run_model(updated_assumptions)
    pension_obligation = updated_assumptions.balance_sheet.pension_obligations_eur
    net_debt = [
        row["financial_debt"] - row["cash"] for row in updated_result.balance_sheet
    ]
    equity_ratio = [
        ((row["equity_end"] - pension_obligation) / row["total_assets"])
        if row["total_assets"]
        else 0.0
        for row in updated_result.balance_sheet
    ]
    ebitda = [row["ebitda"] for row in updated_result.pnl]
    net_debt_ebitda = [
        (net_debt[idx] / ebitda[idx]) if ebitda[idx] else 0.0
        for idx in range(len(net_debt))
    ]
    year_labels = outputs.YEAR_LABELS
    kpi_rows = [
        {
            "Metric": "Net Debt",
            **{year_labels[i]: outputs._format_money(net_debt[i]) for i in range(5)},
        },
        {
            "Metric": "Equity Ratio",
            **{year_labels[i]: f"{equity_ratio[i] * 100:.1f}%" for i in range(5)},
        },
        {
            "Metric": "Net Debt / EBITDA",
            **{year_labels[i]: f"{net_debt_ebitda[i]:.2f}x" for i in range(5)},
        },
    ]
    with output_container:
        st.markdown(
            f'<div class="subtle">Minimum cash balance assumption: {outputs._format_money(updated_assumptions.balance_sheet.minimum_cash_balance_eur)}. Negative cash indicates a funding gap.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="subtle">Pension obligations assumed at close; non-interest-bearing. Amount: {outputs._format_money(pension_obligation)}.</div>',
            unsafe_allow_html=True,
        )
        outputs._render_kpi_table_html(kpi_rows, ["Metric"] + year_labels)
        balance_sheet = updated_result.balance_sheet
        pension_by_year = [pension_obligation for _ in balance_sheet]
        rows = [
            ("ASSET STRUCTURE", None),
            ("Cash", [row["cash"] for row in balance_sheet]),
            ("Fixed Assets (Net)", [row["fixed_assets"] for row in balance_sheet]),
            ("Total Assets", [row["total_assets"] for row in balance_sheet]),
            ("", None),
            ("DEBT & FINANCING STRUCTURE", None),
            ("Financial Debt", [row["financial_debt"] for row in balance_sheet]),
            ("Pension Liabilities", pension_by_year),
            (
                "Total Liabilities",
                [row["total_liabilities"] + pension_obligation for row in balance_sheet],
            ),
            ("", None),
            ("EQUITY EVOLUTION", None),
            (
                "Equity at Start of Year",
                [row["equity_start"] - pension_obligation for row in balance_sheet],
            ),
            ("Net Income", [row["net_income"] for row in balance_sheet]),
            ("Dividends", [row["dividends"] for row in balance_sheet]),
            ("Equity Injections", [row["equity_injection"] for row in balance_sheet]),
            ("Equity Buybacks / Exit Payouts", [row["equity_buyback"] for row in balance_sheet]),
            (
                "Equity at End of Year",
                [row["equity_end"] - pension_obligation for row in balance_sheet],
            ),
            ("", None),
            ("CONSISTENCY CHECK", None),
            ("Total Assets", [row["total_assets"] for row in balance_sheet]),
            (
                "Total Liabilities + Equity",
                [row["total_assets"] for row in balance_sheet],
            ),
        ]
        outputs._render_statement_table_html(
            rows,
            bold_labels={
                "Total Assets",
                "Total Liabilities",
                "Equity at End of Year",
                "Total Liabilities + Equity",
            },
            row_classes={"Cash": "key-metric"},
        )
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "- Business meaning: tests cash, debt, and equity consistency for solvency and financing credibility.\n"
            "- Calculation logic: assets equal liabilities plus equity; equity moves from opening equity through net income, injections, dividends, and buybacks.\n"
            "- Key dependencies: P&L net income, cashflow opening cash/minimum cash, and the debt schedule."
        )
    return updated_assumptions
