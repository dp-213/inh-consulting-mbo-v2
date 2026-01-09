from __future__ import annotations

from pathlib import Path

from state.assumptions import Assumptions
from state.persistence import load_assumptions, save_assumptions

CASES_DIR = Path("data/cases")


def list_cases() -> list[str]:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    return sorted([path.stem for path in CASES_DIR.glob("*.json")])


def case_path(case_name: str) -> Path:
    safe_name = _sanitize_case_name(case_name)
    return CASES_DIR / f"{safe_name}.json"


def load_case(path: str | Path) -> Assumptions:
    return load_assumptions(path)


def save_case(assumptions: Assumptions, path: str | Path) -> None:
    save_assumptions(assumptions, path)


def _sanitize_case_name(name: str) -> str:
    return name.strip().replace(" ", "_").replace("/", "_")
