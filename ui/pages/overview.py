from __future__ import annotations

from model.run_model import ModelResult
from state.assumptions import Assumptions
from ui import outputs


def render(result: ModelResult, assumptions: Assumptions) -> None:
    outputs.render_overview(result, assumptions)
