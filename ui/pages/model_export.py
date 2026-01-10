from __future__ import annotations

import json
from dataclasses import asdict

import streamlit as st

from state.assumptions import Assumptions


def render(assumptions: Assumptions) -> None:
    st.markdown("## Model Export / Snapshot")
    st.markdown("For internal / AI-assisted analysis only.")
    st.markdown(
        "This snapshot is a structured view of the current model inputs. "
        "It is intended for offline analysis or AI-assisted review."
    )

    snapshot = asdict(assumptions)
    rows = _flatten_snapshot(snapshot)
    st.dataframe(rows, use_container_width=True)

    with st.expander("Raw JSON (Advanced)", expanded=False):
        st.table([{"Snapshot (JSON)": json.dumps(snapshot, indent=2)}])


def _flatten_snapshot(snapshot: dict) -> list[dict]:
    rows: list[dict] = []

    def walk(prefix: str, value):
        if isinstance(value, dict):
            for key, inner in value.items():
                walk(f"{prefix}.{key}" if prefix else key, inner)
        elif isinstance(value, list):
            rows.append({"Field": prefix, "Value": ", ".join(str(item) for item in value)})
        else:
            rows.append({"Field": prefix, "Value": value})

    walk("", snapshot)
    return rows
