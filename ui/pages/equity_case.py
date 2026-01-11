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
            "**1) Business Question**\n"
            "- Is the equity at risk and payoff structure acceptable for management and investors?\n"
            "**2) What This Shows / What This Does NOT Show**\n"
            "- Shows entry equity, residual cash to equity, and exit allocation.\n"
            "- Does not test bankability or valuation ranges; it reflects deal mechanics under modeled exit assumptions.\n"
            "**3) Calculation Logic (Transparent, Step-by-Step)**\n"
            "- Equity at entry = Purchase Price − Debt Amount.\n"
            "- Residual Cash to Equity = Operating Cashflows − Debt Service.\n"
            "- Exit Equity Value = Enterprise Value at Exit − Net Debt at Exit + Excess Cash.\n"
            "- Equity value is reduced by pension obligations assumed at entry.\n"
            "**4) Interpretation for the Decision**\n"
            "- Higher residual cash and exit equity value improve sponsor alignment.\n"
            "- Exit value below invested capital implies permanent equity loss.\n"
            "**5) Insights & Red Flags**\n"
            "- High external equity reliance reduces management control.\n"
            "- Low or negative residual cash signals dependence on exit value.\n"
            "- Large pension obligations can erase equity value.\n"
            "**6) Key Dependencies**\n"
            "- Purchase price and debt amount.\n"
            "- Operating cashflow generation.\n"
            "- Exit multiple and exit year.\n"
            "- Pension obligations."
        )
    return updated_assumptions
