"""Lightweight validators for the frozen Protocol v1 contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[2]
OPERATIVE_FILES = (
    "configs/protocol_v1.yaml",
    "configs/seed_manifest_v1.yaml",
    "configs/tfim_v1.yaml",
    "configs/split_manifest_v1.yaml",
    "configs/qcnn_v1.yaml",
    "docs/protocol_v1.md",
    "docs/statistical_plan_v1.md",
    "docs/p1_execution_gate.md",
    "results/protocol_v1/p1_execution_gate.json",
)
PLACEHOLDERS = ("TO_FREEZE", "TBD", "TBC", "FIXME", "choose later", "best value", "nearby value", "reasonable threshold", "optional primary")


def load_yaml(relative: str) -> dict:
    return yaml.safe_load((ROOT / relative).read_text())


def expand_intervals(intervals: list[list[int]]) -> set[int]:
    return {value for low, high in intervals for value in range(low, high + 1)}


def label_g_milli(g_milli: int) -> int | None:
    if 100 <= g_milli <= 949:
        return 0
    if 1051 <= g_milli <= 1900:
        return 1
    return None


def scientific_verdict(valid_complete: bool, delta: float, lower_ci: float) -> str:
    if not valid_complete:
        return "INVALID"
    return "PASS" if delta >= 0.02 and lower_ci > 0.0 else "FAIL"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze_manifest() -> bool:
    manifest = json.loads((ROOT / "results/protocol_v1/freeze_manifest_v1.json").read_text())
    return all(sha256(ROOT / item["path"]) == item["sha256"] for item in manifest["files"])


def unresolved_placeholders() -> list[str]:
    failures = []
    for relative in OPERATIVE_FILES:
        text = (ROOT / relative).read_text()
        failures.extend(f"{relative}: {token}" for token in PLACEHOLDERS if token.lower() in text.lower())
    return failures
