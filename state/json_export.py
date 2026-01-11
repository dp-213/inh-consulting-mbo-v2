from __future__ import annotations

import json
from dataclasses import asdict

from state.assumptions import Assumptions


def export_case_snapshot_json(
    assumptions: Assumptions,
    *,
    case_name: str,
) -> bytes:
    payload = asdict(assumptions)
    return json.dumps(payload, indent=2, sort_keys=False).encode("utf-8")
