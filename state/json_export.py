from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone

from state.assumptions import Assumptions


def export_case_snapshot_json(
    assumptions: Assumptions,
    *,
    case_name: str,
) -> bytes:
    payload = asdict(assumptions)
    payload["metadata"] = {
        "case_name": case_name,
        "scenario": assumptions.scenario,
        "export_timestamp": _utc_timestamp(),
    }
    return json.dumps(payload, indent=2, sort_keys=False).encode("utf-8")


def _utc_timestamp() -> str:
    value = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return value.replace("+00:00", "Z")
