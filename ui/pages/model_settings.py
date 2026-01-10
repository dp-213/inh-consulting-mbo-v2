from __future__ import annotations

import streamlit as st


def render(data_path: str) -> None:
    st.markdown("## Model Settings")
    st.markdown("Model inputs are sourced from the JSON file below.")
    st.table([{"Current JSON Path": data_path}])
    st.markdown("---")
    st.markdown("Changes are saved automatically after each edit.")
