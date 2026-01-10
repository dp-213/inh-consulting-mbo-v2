from __future__ import annotations

import streamlit as st

from state.assumptions import Assumptions


def render(assumptions: Assumptions) -> Assumptions:
    st.markdown("# Other Assumptions")
    st.markdown(
        "This page has been retired. Assumptions now live on their respective pages.",
    )
    return assumptions
