from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("# Financing Inputs")
    st.markdown(
        "This page has been retired. Financing assumptions now live on the Financing & Debt page.",
    )
    return assumptions
