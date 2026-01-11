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
            "**A. Business Question**\n"
            "This page answers whether the debt structure is bankable by testing CFADS coverage and covenant compliance under the plan.\n\n"
            "**B. Financial Mechanics (Step-by-Step)**\n"
            "CFADS = EBITDA – Cash Taxes – Maintenance Capex ± Working Capital Change.\n"
            "Total Debt Service = Interest Expense + Scheduled Repayment.\n"
            "DSCR = CFADS / Total Debt Service.\n"
            "DSCR Headroom = DSCR – Minimum Required DSCR.\n"
            "A covenant breach is flagged when DSCR < Minimum Required DSCR for a given year.\n"
            "The transition year can be stressed by closing effects and initial drawdown timing.\n\n"
            "**C. Interpretation & Red Flags**\n"
            "DSCR below covenant in any year signals a potential breach and may require refinancing or equity support.\n"
            "Low headroom across multiple years indicates limited resilience to downside scenarios.\n\n"
            "**D. Key Model Dependencies**\n"
            "Depends on cashflow drivers (EBITDA, taxes, capex, working capital), the debt schedule (interest and repayment), and financing assumptions (interest rate, amortization type, covenant threshold).\n"
            "Pension obligations are structural liabilities and are not covered by CFADS; they must be assessed separately in the balance sheet and valuation views."
        )
    return updated_assumptions
