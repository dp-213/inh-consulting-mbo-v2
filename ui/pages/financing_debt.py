from __future__ import annotations

import streamlit as st

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    st.markdown("# Financing & Debt")
    st.markdown(
        '<div class="subtle">Debt structure, service and bankability (5-year plan)</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Bank View")
    outputs.render_financing_debt(result, assumptions)

    dscr_values = [row.get("dscr") for row in result.debt if row.get("dscr") is not None]
    avg_dscr = sum(dscr_values) / len(dscr_values) if dscr_values else 0.0
    min_dscr = min(dscr_values) if dscr_values else 0.0
    peak_debt = max(
        row.get("opening_debt", row.get("closing_debt", 0.0)) for row in result.debt
    )
    debt_at_close = result.debt[0].get("opening_debt", assumptions.financing.senior_debt_amount_eur)
    ebitda_year0 = result.pnl[0]["ebitda"] if result.pnl else 0.0
    debt_ebitda = debt_at_close / ebitda_year0 if ebitda_year0 else 0.0

    kpi_rows = [
        {"": "0", "KPI": "Average Debt Coverage", "Value": f"{avg_dscr:.2f}x"},
        {"": "1", "KPI": "Minimum Debt Coverage", "Value": f"{min_dscr:.2f}x"},
        {"": "2", "KPI": "Peak Debt", "Value": outputs._format_money(peak_debt)},
        {"": "3", "KPI": "Debt / Operating Profit (at close)", "Value": f"{debt_ebitda:.2f}x"},
    ]
    st.markdown("### KPIs")
    outputs._render_kpi_table_html(kpi_rows, ["", "KPI", "Value"])
