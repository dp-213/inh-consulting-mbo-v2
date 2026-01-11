from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    st.markdown("# Equity Case")
    output_container = st.container()
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_equity_key_assumptions(
            assumptions, "equity.assumptions"
        )
    updated_result = run_model(updated_assumptions)
    with output_container:
        outputs.render_equity_case(updated_result, updated_assumptions)
        pension_obligation = updated_assumptions.balance_sheet.pension_obligations_eur
        exit_value = updated_result.equity.get("exit_value", 0.0)
        adjusted_exit_value = exit_value - pension_obligation
        st.markdown("### Pension Obligation Impact (Informational)")
        adjustment_rows = [
            ("Equity Value at Exit (Model)", [exit_value]),
            ("Pension Obligations Assumed", [pension_obligation]),
            ("Equity Value at Exit (after pensions)", [adjusted_exit_value]),
        ]
        outputs._render_statement_table_html(
            adjustment_rows,
            bold_labels={"Equity Value at Exit (after pensions)"},
            years=1,
            year_labels=["Value"],
        )
        st.markdown(
            '<div class="subtle">Equity value reflects pension obligations assumed at entry.</div>',
            unsafe_allow_html=True,
        )
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "**A. Business Question**\n"
            "This page clarifies who contributes equity, how cash flows are distributed, and how exit value is allocated between management and external investors.\n\n"
            "**B. Financial Mechanics (Step-by-Step)**\n"
            "Equity required at entry = Purchase Price – Debt Amount.\n"
            "Residual Cash to Equity = Operating Cashflows – Debt Service.\n"
            "Exit Equity Value = Enterprise Value – Net Debt at Exit ± Excess Cash.\n"
            "Pension obligations assumed at entry reduce equity value and therefore reduce exit proceeds to equity holders.\n\n"
            "**C. Interpretation & Red Flags**\n"
            "High reliance on external equity or weak residual cash flow indicates limited sponsor control and fragile economics.\n"
            "Exit equity value below invested capital signals permanent capital loss risk.\n\n"
            "**D. Key Model Dependencies**\n"
            "Depends on transaction terms (purchase price and equity contribution), debt schedule, cashflow generation, and valuation outputs including pension obligations."
        )
    return updated_assumptions
