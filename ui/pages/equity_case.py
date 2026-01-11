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
            "Is the equity at risk and payoff structure acceptable for management and external investors?\n\n"
            "**2) What This Shows / What This Does NOT Show**\n"
            "Shows entry equity contributions, residual cash to equity during the plan, and the allocation of exit value.\n"
            "Does not test bankability or valuation ranges; it reflects the deal mechanics given the modeled exit assumptions.\n\n"
            "**3) Calculation Logic (Transparent, Step-by-Step)**\n"
            "Equity required at entry is derived from purchase price and debt amount.\n"
            "Residual cash to equity is driven by operating cashflows after debt service each year.\n"
            "Exit equity value is derived from enterprise value at exit, adjusted for net debt and excess cash.\n"
            "Pension obligations assumed at entry reduce equity value and therefore reduce exit proceeds.\n\n"
            "**4) Interpretation for the Decision**\n"
            "Higher residual cash and exit equity value improve sponsor returns and increase management alignment.\n"
            "If exit equity value is below invested capital, the structure destroys equity value even if operations are stable.\n\n"
            "**5) Insights & Red Flags**\n"
            "High reliance on external equity reduces management control and dilutes upside.\n"
            "Low or negative residual cash indicates dependence on exit value rather than operating performance.\n"
            "Large pension obligations can erase equity value even when enterprise value is positive.\n\n"
            "**6) Key Dependencies**\n"
            "Purchase price and debt amount, operating cashflow generation, exit multiple and exit year, pension obligations."
        )
    return updated_assumptions
