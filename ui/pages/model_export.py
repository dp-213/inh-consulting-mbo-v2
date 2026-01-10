from __future__ import annotations

from datetime import date
import re

import streamlit as st

from model.excel_export import export_ic_excel
from model.run_model import ModelResult
from state.assumptions import Assumptions


def render(assumptions: Assumptions, result: ModelResult) -> None:
    st.markdown("# Model Export")
    st.markdown(
        "Generate an IC-ready Excel model from the current case and scenario. "
        "The export mirrors the tool structure and keeps formulas live."
    )

    case_name = _case_name(st.session_state.get("data_path", ""))
    scenario = assumptions.scenario
    st.markdown(f"Case: {case_name} | Scenario: {scenario}")

    export_key = (case_name, scenario)
    if st.session_state.get("export_key") != export_key:
        st.session_state.pop("export_bytes", None)
        st.session_state.pop("export_filename", None)
        st.session_state["export_key"] = export_key

    if st.button("Export IC-Ready Excel Model", type="primary"):
        try:
            export_bytes = export_ic_excel(assumptions, result, case_name)
        except ImportError:
            st.error("Excel export requires the openpyxl package to be installed.")
            return
        except Exception as exc:  # pragma: no cover - streamlit presentation
            st.error(f"Excel export failed: {exc}")
            return

        st.session_state["export_bytes"] = export_bytes
        st.session_state["export_filename"] = _export_filename(case_name, scenario)
        st.success("Excel model generated. Use the download button below.")

    if "export_bytes" in st.session_state:
        st.download_button(
            "Download Excel Model",
            data=st.session_state["export_bytes"],
            file_name=st.session_state.get("export_filename", "ic_model.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _case_name(path: str) -> str:
    if not path:
        return "Unnamed Case"
    if path.endswith("base_case.json"):
        return "Base Case"
    name = path.split("/")[-1].replace(".json", "")
    return name or "Unnamed Case"


def _export_filename(case_name: str, scenario: str) -> str:
    safe_case = re.sub(r"[^A-Za-z0-9_-]+", "_", case_name.strip()) or "Case"
    safe_scenario = re.sub(r"[^A-Za-z0-9_-]+", "_", str(scenario).strip()) or "Scenario"
    stamp = date.today().isoformat()
    return f"{safe_case}_{safe_scenario}_ic_model_{stamp}.xlsx"
