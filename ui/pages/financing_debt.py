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
            "Is this debt structure bankable, or does it breach covenants under the operating plan?\n\n"
            "**2) What This Shows / What This Does NOT Show**\n"
            "Shows CFADS, debt service, DSCR, and covenant headroom across the plan years.\n"
            "Does not show equity returns or valuation; pension obligations are structural liabilities and are assessed separately.\n\n"
            "**3) Calculation Logic (Transparent, Step-by-Step)**\n"
            "CFADS is built from EBITDA, reduced by cash taxes and maintenance capex, and adjusted for working capital changes.\n"
            "Total debt service is the sum of interest expense and scheduled repayment from the debt schedule.\n"
            "DSCR is derived by comparing CFADS to total debt service for each year, and headroom compares DSCR to the minimum covenant threshold.\n"
            "A covenant breach is flagged in any year where DSCR falls below the minimum requirement.\n\n"
            "**4) Interpretation for the Decision**\n"
            "Comfortable DSCR headroom indicates bankability; thin headroom means the deal is fragile to downside scenarios.\n"
            "Any breach requires either refinancing, structural changes, or additional equity support.\n\n"
            "**5) Insights & Red Flags**\n"
            "Repeated years below covenant indicate a structurally unbankable profile.\n"
            "High peak debt with flat CFADS signals leverage risk even if the first years appear stable.\n"
            "Transition-year stress is common and must be explained with explicit sources of cash support if applicable.\n\n"
            "**6) Key Dependencies**\n"
            "EBITDA trajectory, tax and capex assumptions, working capital settings, interest rate and amortization schedule, minimum DSCR covenant."
        )
    return updated_assumptions
