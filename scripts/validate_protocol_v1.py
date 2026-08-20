#!/usr/bin/env python3
"""Validate immutable Protocol v1 without running scientific computation."""

from __future__ import annotations

import json

import yaml

from hamiltonian_qda.protocol import ROOT, unresolved_placeholders, verify_freeze_manifest


def main() -> None:
    for path in sorted((ROOT / "configs").glob("*_v1.yaml")):
        assert isinstance(yaml.safe_load(path.read_text()), dict), path
    gate = json.loads((ROOT / "results/protocol_v1/p1_execution_gate.json").read_text())
    assert gate["status"] == "READY"
    assert gate["unresolved_scientific_choices"] == 0
    assert gate["scientific_experiments_executed"] == 0
    assert gate["p1_execution_authorized"] is True
    assert not unresolved_placeholders()
    assert verify_freeze_manifest()
    print("Protocol v1 validation: OK (READY; experiments executed: 0)")


if __name__ == "__main__":
    main()
