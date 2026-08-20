import hashlib
import json
from pathlib import Path

from hamiltonian_qda.protocol_v1_1 import ROOT
from hamiltonian_qda.protocol_v1_2 import (
    P1_FREEZE_HASH,
    PARENT_HASH,
    PROTOCOL_HASH,
    dry_resolution,
    validate_artifact_files,
    validate_freeze_manifest,
    validate_loader_manifest,
)

MATERIALIZED = ROOT / "results/p1_v1_2/materialized"
FREEZE = ROOT / "results/p1_v1_2/freeze"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def test_frozen_materialization_is_complete_and_loader_valid() -> None:
    manifest = load_json(MATERIALIZED / "materialization_manifest.json")
    freeze = load_json(MATERIALIZED / "materialization_freeze_manifest.json")
    expected = dry_resolution()
    validate_loader_manifest(manifest, expected)
    validate_freeze_manifest(
        freeze,
        manifest,
        expected,
        lambda path: (ROOT / path).read_bytes(),
        lambda path: (ROOT / path).read_bytes(),
    )
    validate_artifact_files(manifest["records"], ROOT)
    assert len(manifest["records"]) == 2400
    assert sum(record["arm"] == "C1" for record in manifest["records"]) == 1200
    assert sum(record["arm"] == "C2" for record in manifest["records"]) == 1200


def test_physical_and_pairing_validation_reports_pass() -> None:
    manifest = load_json(MATERIALIZED / "materialization_manifest.json")
    c2_radii = {}
    for record in manifest["records"]:
        provenance = load_json(ROOT / record["relative_provenance_path"])
        validation = provenance["validation"]
        assert validation["status"] == "PASS"
        assert validation["exact_duplicate"] is False
        assert validation["projective_duplicate"] is False
        assert validation["norm_error"] <= 1e-12
        key = (record["realization"], record["class"], record["source_position"])
        if record["arm"] == "C2":
            assert validation["residual"] <= 1e-10
            assert validation["spectral_gap"] > 1e-10
            c2_radii[key] = provenance["FS_displacement"]
        else:
            assert provenance["target_g"] is None
            assert abs(provenance["FS_displacement"] - c2_radii[key]) <= 1e-10
    validation = load_json(FREEZE / "validation_report.json")
    assert validation == {
        "C1_count": 1200,
        "C2_count": 1200,
        "all_sources_TRAIN": True,
        "combined_count": 2400,
        "loader_validation": "PASS",
        "pairwise_realization_source_overlap": 0,
        "source_reassignments": 0,
        "status": "PASS",
        "unexpected_outputs": 0,
        "unique_ids": 2400,
        "unique_provenance_paths": 2400,
        "unique_state_paths": 2400,
        "unspecified_randomness": 0,
    }


def test_replay_and_freeze_gate_pass_without_downstream_execution() -> None:
    replay = load_json(FREEZE / "replay_report.json")
    assert replay == {
        "compared_outputs": 2400,
        "maximum_absolute_difference": 0.0,
        "metadata_mismatch_count": 0,
        "missing_count": 0,
        "state_mismatch_count": 0,
        "status": "PASS",
        "unexpected_count": 0,
    }
    gate = load_json(FREEZE / "freeze_gate.json")
    assert gate["decision"] == [
        "C1_C2_MATERIALIZATION_FROZEN",
        "DOWNSTREAM_EXECUTION_PROHIBITED_PENDING_SEPARATE_AUTHORIZATION",
    ]
    assert gate["scientific_experiments_executed"] == 0
    assert gate["QCNN_or_downstream_runs"] == 0


def test_protocol_p1_and_generated_checksums_are_immutable() -> None:
    assert hashlib.sha256((ROOT / "configs/protocol_v1_2.yaml").read_bytes()).hexdigest() == PROTOCOL_HASH
    assert hashlib.sha256((ROOT / "configs/protocol_v1_1.yaml").read_bytes()).hexdigest() == PARENT_HASH
    assert hashlib.sha256((ROOT / "results/p1_v1_1/freeze_manifest.json").read_bytes()).hexdigest() == P1_FREEZE_HASH
    for line in (FREEZE / "checksums.sha256").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
