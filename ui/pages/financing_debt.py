from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult, run_model
from state.assumptions import Assumptions
from ui import outputs
from ui import inputs


def render(result: ModelResult, assumptions: Assumptions) -> Assumptions:
    st.markdown("# Financing & Debt")
    with st.expander("Key Assumptions", expanded=False):
        updated_assumptions = inputs.render_financing_key_assumptions(
            assumptions, "financing.assumptions"
        )
    output_container = st.container()
    updated_result = run_model(updated_assumptions)
    with output_container:
        outputs.render_financing_debt(updated_result, updated_assumptions)
        st.markdown(
            '<div class="subtle">Repayment profile is fixed to linear amortization for this model version to maintain comparability across cases; changes to repayment structure should be evaluated as a separate financing scenario.</div>',
            unsafe_allow_html=True,
        )
        pension_obligation = updated_assumptions.balance_sheet.pension_obligations_eur
        info_rows = [
            (
                "Structural obligations not covered by CFADS: Pension liabilities",
                [outputs._format_money(pension_obligation)],
            )
        ]
        outputs._render_statement_table_html(
            info_rows,
            years=1,
            year_labels=["Value"],
        )
    with st.expander("Explain business & calculation logic", expanded=False):
        st.markdown(
            "**1) Business Question**\n"
            "- Is the debt structure bankable, or does it breach covenants under the plan?\n"
            "**2) What This Shows / What This Does NOT Show**\n"
            "- Shows CFADS, total debt service, DSCR, and covenant headroom across years.\n"
            "- Does not show valuation or equity returns; pension obligations are assessed separately.\n"
            "**3) Calculation Logic (Transparent, Step-by-Step)**\n"
            "- CFADS = EBITDA − Cash Taxes − Maintenance Capex ± Working Capital Change.\n"
            "- Total Debt Service = Interest Expense + Scheduled Repayment.\n"
            "- DSCR = CFADS / Total Debt Service.\n"
            "- DSCR Headroom = DSCR − Minimum Required DSCR.\n"
            "- Covenant Breach = YES when DSCR < Minimum Required DSCR.\n"
            "**4) Interpretation for the Decision**\n"
            "- DSCR comfortably above covenant indicates bankability.\n"
            "- Any year below covenant implies refinancing or equity support.\n"
            "**5) Insights & Red Flags**\n"
            "- Repeated breaches indicate a structurally unbankable profile.\n"
            "- High peak debt with flat CFADS signals leverage risk.\n"
            "- Transition-year stress must be covered by committed liquidity.\n"
            "**6) Key Dependencies**\n"
            "- EBITDA path, taxes, capex, working capital.\n"
            "- Interest rate, amortization schedule, minimum DSCR covenant."
        )
    return updated_assumptions
