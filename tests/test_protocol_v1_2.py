import copy
import hashlib
import json

import numpy as np
import pytest
import yaml

from hamiltonian_qda.protocol_v1_1 import ROOT
from hamiltonian_qda.protocol_v1_2 import (
    P1_FREEZE_HASH,
    PARENT_HASH,
    REQUIRED_IMPLEMENTATION_SOURCES,
    c1_attempt_vector,
    c2_attempt_vector,
    canonical_json_bytes,
    compare_replay_state,
    dry_resolution,
    output_path,
    provenance_path,
    sha256,
    synthetic_id,
    validate_artifact_files,
    validate_freeze_manifest,
    validate_loader_manifest,
)
from hamiltonian_qda.protocol_v1_2 import PROTOCOL_HASH as MODULE_PROTOCOL_HASH

PROTOCOL_HASH = "b6cd7f0e8f239563244a40149aa1e18eb451e4421b8a6cce7c200eff40471761"
OUT = ROOT / "results/protocol_v1_2"


def test_parent_and_p1_anchors_are_byte_identical() -> None:
    assert hashlib.sha256((ROOT / "configs/protocol_v1_1.yaml").read_bytes()).hexdigest() == PARENT_HASH
    assert hashlib.sha256((ROOT / "results/p1_v1_1/freeze_manifest.json").read_bytes()).hexdigest() == P1_FREEZE_HASH
    assert hashlib.sha256((ROOT / "configs/protocol_v1_2.yaml").read_bytes()).hexdigest() == PROTOCOL_HASH


def test_exact_traversal_vectors_and_dry_resolution() -> None:
    rows = dry_resolution()
    assert len(rows) == 2400
    expected = [
        (0, "C2", "D00", 0, 0),
        (49, "C2", "D00", 0, 49),
        (50, "C2", "D00", 1, 0),
        (1199, "C2", "D11", 1, 49),
        (1200, "C1", "D00", 0, 0),
        (2399, "C1", "D11", 1, 49),
    ]
    assert [(rows[i]["global_row"], rows[i]["arm"], rows[i]["realization"], rows[i]["class"], rows[i]["source_position"]) for i, *_ in expected] == expected
    assert len({row["synthetic_id"] for row in rows}) == 2400
    assert len({row["relative_output_path"] for row in rows}) == 2400
    assert len({row["relative_provenance_path"] for row in rows}) == 2400
    assert not {row["relative_output_path"] for row in rows} & {row["relative_provenance_path"] for row in rows}
    assert all(all(value is not None for value in row.values()) for row in rows)
    frozen = json.loads((OUT / "dry_resolution.json").read_text())
    assert frozen["records"] == rows
    assert frozen["unresolved_fields"] == frozen["unspecified_randomness"] == 0


def test_rng_vectors_are_exact() -> None:
    vectors = json.loads((OUT / "rng_test_vectors.json").read_text())["vectors"]
    for vector in vectors:
        actual = c2_attempt_vector(vector["payload"], vector["attempt"]) if vector["arm"] == "C2" else c1_attempt_vector(vector["payload"], vector["attempt"])
        assert actual == vector["draws"]
    assert vectors[0]["draws"] == {"direction_bit": 1, "direction": 1, "step": 0.017587662403976977}
    assert vectors[1]["draws"] == {"direction_bit": 0, "direction": -1, "step": 0.009290322026019399}
    assert vectors[2]["draws"]["real"][:3] == [1.1113881155793683, 1.431752133939135, -1.1326159571680625]
    assert vectors[2]["draws"]["imag"][:3] == [2.83687156448176, 1.1157814425000616, -1.209741730194571]


def test_synthetic_id_and_path_vectors() -> None:
    assert synthetic_id("C2", 0, 0, 0) == "p1v1_2-C2-D00-Y0-S0000-A00"
    assert synthetic_id("C1", 11, 1, 1699) == "p1v1_2-C1-D11-Y1-S1699-A00"
    assert output_path("C1", 11, 1, 1699) == "results/p1_v1_2/materialized/C1/D11/Y1/p1v1_2-C1-D11-Y1-S1699-A00/state.npy"
    assert provenance_path("C1", 11, 1, 1699).endswith("/provenance.json")
    with pytest.raises(ValueError):
        synthetic_id("C0", 0, 0, 0)


def test_serialization_and_replay_schema_are_exact() -> None:
    schema = yaml.safe_load((ROOT / "configs/serialization_schema_v1_2.yaml").read_text())
    state_file = schema["state_file"]
    assert state_file["format"] == "NumPy NPY 1.0"
    assert state_file["shape"] == [16]
    assert state_file["dtype"] == "<c16"
    assert state_file["allow_pickle"] is False
    replay = schema["replay"]["state_field"]
    assert replay == {
        "mode": "NUMERICAL_TOLERANCE",
        "shape_and_dtype": "exact",
        "atol": 1e-10,
        "rtol": 0.0,
        "nan_semantics": "forbidden_in_either_artifact",
        "complex_semantics": "for each canonicalized complex component require abs(expected[i] - actual[i]) <= atol + rtol*abs(expected[i])",
        "executable_API": "numpy.allclose(expected, actual, atol=1e-10, rtol=0.0, equal_nan=False) after exact shape/dtype/finite checks",
        "canonicalization_precondition": "both artifacts must already pass the inherited TFIM global-phase rule; replay comparison does not recanonicalize",
        "reason": "matches the inherited maximum eigenpair residual tolerance; no looser tolerance is introduced",
    }
    assert schema["replay"]["provenance_fields"]["mode"] == "CANONICAL_EXACT"
    assert schema["replay"]["canonical_provenance_bytes"]["mode"] == "BYTE_IDENTICAL"


def valid_loader_manifest() -> tuple[dict, list[dict]]:
    expected = dry_resolution()
    records = [
        {
            **row,
            "state_sha256": "0" * 64,
            "provenance_sha256": "1" * 64,
            "state_payload_sha256": "2" * 64,
            "validation_status": "PASS",
        }
        for row in expected
    ]
    return {
        "protocol_version": "1.2.0",
        "protocol_hash": MODULE_PROTOCOL_HASH,
        "parent_protocol_hash": PARENT_HASH,
        "p1_freeze_hash": P1_FREEZE_HASH,
        "records": records,
    }, expected


def test_loader_manifest_validation_fails_closed() -> None:
    manifest, expected = valid_loader_manifest()
    validate_loader_manifest(manifest, expected)
    mutations = []
    for key in ("protocol_version", "protocol_hash", "parent_protocol_hash", "p1_freeze_hash"):
        changed = copy.deepcopy(manifest)
        changed[key] = "wrong"
        mutations.append(changed)
    missing = copy.deepcopy(manifest)
    missing["records"].pop()
    mutations.append(missing)
    reordered = copy.deepcopy(manifest)
    reordered["records"][0], reordered["records"][1] = reordered["records"][1], reordered["records"][0]
    mutations.append(reordered)
    duplicate = copy.deepcopy(manifest)
    duplicate["records"][1]["synthetic_id"] = duplicate["records"][0]["synthetic_id"]
    mutations.append(duplicate)
    no_hash = copy.deepcopy(manifest)
    no_hash["records"][0]["state_sha256"] = None
    mutations.append(no_hash)
    no_payload = copy.deepcopy(manifest)
    del no_payload["records"][0]["state_payload_sha256"]
    mutations.append(no_payload)
    failed = copy.deepcopy(manifest)
    failed["records"][0]["validation_status"] = "FAIL"
    mutations.append(failed)
    for key in ("arm_row", "source_position", "seed_payload", "seed_sha256", "derived_seed_uint128"):
        changed = copy.deepcopy(manifest)
        changed["records"][0][key] = "wrong"
        mutations.append(changed)
    for changed in mutations:
        with pytest.raises(ValueError):
            validate_loader_manifest(changed, expected)


def test_freeze_manifest_validation_fails_closed() -> None:
    materialization, expected = valid_loader_manifest()
    manifest_path = "results/p1_v1_2/materialized/materialization_manifest.json"
    virtual_files = {manifest_path: canonical_json_bytes(materialization)}
    for record in materialization["records"]:
        virtual_files[record["relative_output_path"]] = b"state"
        virtual_files[record["relative_provenance_path"]] = b"provenance"
    files = [
        {
            "path": path,
            "role": "scientific" if path.endswith("state.npy") else "metadata",
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        for path, content in sorted(virtual_files.items())
    ]
    source_paths = sorted(REQUIRED_IMPLEMENTATION_SOURCES | {"scripts/materialize_c1_c2_v1_2.py"})
    virtual_sources = {path: f"source:{path}".encode() for path in source_paths}
    freeze = {
        "protocol_version": "1.2.0",
        "protocol_hash": MODULE_PROTOCOL_HASH,
        "parent_protocol_version": "1.1.0",
        "parent_protocol_hash": PARENT_HASH,
        "p1_freeze_hash": P1_FREEZE_HASH,
        "previous_audit_hash": "33ecc0dae26219b38b9a5a11ed59701c22e12792b8b15c82d8a15f9cb4dec1be",
        "implementation_commit": "0" * 40,
        "materializer_entrypoint": "scripts/materialize_c1_c2_v1_2.py",
        "implementation_source_hashes": [
            {"path": path, "sha256": hashlib.sha256(virtual_sources[path]).hexdigest()}
            for path in source_paths
        ],
        "environment": {"python": "3.12.13", "numpy": "2.5.2", "byteorder": "little"},
        "validation_status": "PASS",
        "materialization_complete": True,
        "materialization_gate": "C1_C2_MATERIALIZATION_READY",
        "scientific_experiments_executed": 0,
        "duplicate_validation": {"status": "PASS"},
        "materialization_manifest_path": manifest_path,
        "materialization_manifest_sha256": hashlib.sha256(virtual_files[manifest_path]).hexdigest(),
        "files": files,
    }
    reader = virtual_files.__getitem__
    source_reader = virtual_sources.__getitem__
    validate_freeze_manifest(freeze, materialization, expected, reader, source_reader)
    for key in (
        "protocol_hash",
        "parent_protocol_version",
        "previous_audit_hash",
        "implementation_commit",
        "materializer_entrypoint",
        "implementation_source_hashes",
        "environment",
        "validation_status",
        "materialization_complete",
        "materialization_gate",
        "scientific_experiments_executed",
        "duplicate_validation",
        "materialization_manifest_path",
        "materialization_manifest_sha256",
        "files",
    ):
        changed = copy.deepcopy(freeze)
        changed[key] = None
        with pytest.raises((ValueError, TypeError, KeyError)):
            validate_freeze_manifest(changed, materialization, expected, reader, source_reader)
    changed = copy.deepcopy(freeze)
    changed["files"][0]["sha256"] = "f" * 64
    with pytest.raises(ValueError, match="checksum"):
        validate_freeze_manifest(changed, materialization, expected, reader, source_reader)
    changed = copy.deepcopy(freeze)
    changed["implementation_source_hashes"][0]["sha256"] = "f" * 64
    with pytest.raises(ValueError, match="source hash"):
        validate_freeze_manifest(changed, materialization, expected, reader, source_reader)
    changed = copy.deepcopy(freeze)
    changed["implementation_source_hashes"][1]["path"] = changed["implementation_source_hashes"][0]["path"]
    with pytest.raises(ValueError, match="source"):
        validate_freeze_manifest(changed, materialization, expected, reader, source_reader)


def test_replay_comparison_is_executable_and_strict() -> None:
    expected = np.zeros(16, dtype="<c16")
    compare_replay_state(expected, expected.copy())
    within = expected.copy()
    within[0] = 1e-10
    compare_replay_state(expected, within)
    outside = expected.copy()
    outside[0] = 1.00001e-10
    with pytest.raises(ValueError, match="numerical mismatch"):
        compare_replay_state(expected, outside)
    with pytest.raises(ValueError, match="dtype"):
        compare_replay_state(expected, expected.astype("<c8"))
    nonfinite = expected.copy()
    nonfinite[0] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        compare_replay_state(expected, nonfinite)


def test_artifact_file_validation_fails_closed(tmp_path) -> None:
    identity = synthetic_id("C2", 0, 0, 0)
    state_rel = output_path("C2", 0, 0, 0)
    provenance_rel = provenance_path("C2", 0, 0, 0)
    state_path = tmp_path / state_rel
    provenance_file = tmp_path / provenance_rel
    state_path.parent.mkdir(parents=True)
    np.save(state_path, np.zeros(16, dtype="<c16"), allow_pickle=False)
    state_payload_sha256 = hashlib.sha256(np.zeros(16, dtype="<c16").tobytes()).hexdigest()
    record = {
        "synthetic_id": identity,
        "arm": "C2",
        "realization": "D00",
        "class": 0,
        "source_state_id": "tfim4q-obc-j1-gidx-0000",
        "state_index": 0,
        "source_g": 0.1,
        "source_position": 0,
        "seed_payload": "payload",
        "seed_sha256": "0" * 64,
        "derived_seed_uint128": "0",
        "relative_output_path": state_rel,
        "relative_provenance_path": provenance_rel,
        "state_sha256": sha256(state_path),
        "state_payload_sha256": state_payload_sha256,
    }
    provenance = {
        "synthetic_id": identity,
        "arm": "C2",
        "realization": "D00",
        "class": 0,
        "source_state_id": "tfim4q-obc-j1-gidx-0000",
        "source_state_index": 0,
        "source_g": 0.1,
        "source_label": 0,
        "source_position": 0,
        "proposal_seed_payload": "payload",
        "proposal_seed_sha256": "0" * 64,
        "proposal_seed_uint128_decimal": "0",
        "accepted_attempt": 0,
        "target_g": 0.11,
        "FS_displacement": 0.01,
        "generation_method": "test fixture",
        "protocol_version": "1.2.0",
        "protocol_hash": MODULE_PROTOCOL_HASH,
        "parent_protocol_hash": PARENT_HASH,
        "p1_freeze_hash": P1_FREEZE_HASH,
        "state_hash": state_payload_sha256,
        "state_file_sha256": record["state_sha256"],
        "validation": {"status": "PASS"},
    }
    provenance_file.write_bytes(canonical_json_bytes(provenance))
    record["provenance_sha256"] = sha256(provenance_file)
    validate_artifact_files([record], tmp_path)

    provenance_file.unlink()
    with pytest.raises(ValueError, match="missing artifact"):
        validate_artifact_files([record], tmp_path)
    provenance_file.write_text("{}")
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_artifact_files([record], tmp_path)
    record["provenance_sha256"] = sha256(provenance_file)
    with pytest.raises(ValueError, match="provenance serialization"):
        validate_artifact_files([record], tmp_path)

    provenance_file.write_bytes(canonical_json_bytes(provenance))
    record["provenance_sha256"] = sha256(provenance_file)
    for key in ("protocol_hash", "source_state_id", "proposal_seed_payload"):
        wrong = copy.deepcopy(provenance)
        wrong[key] = "wrong"
        provenance_file.write_bytes(canonical_json_bytes(wrong))
        record["provenance_sha256"] = sha256(provenance_file)
        with pytest.raises(ValueError, match="provenance content mismatch"):
            validate_artifact_files([record], tmp_path)
    wrong = copy.deepcopy(provenance)
    wrong["accepted_attempt"] = 128
    provenance_file.write_bytes(canonical_json_bytes(wrong))
    record["provenance_sha256"] = sha256(provenance_file)
    with pytest.raises(ValueError, match="attempt"):
        validate_artifact_files([record], tmp_path)
    c1_record = {**record, "arm": "C1"}
    c1_provenance = {**provenance, "arm": "C1"}
    provenance_file.write_bytes(canonical_json_bytes(c1_provenance))
    c1_record["provenance_sha256"] = sha256(provenance_file)
    with pytest.raises(ValueError, match="C1 target_g"):
        validate_artifact_files([c1_record], tmp_path)
    provenance_file.write_bytes(canonical_json_bytes(provenance))
    record["provenance_sha256"] = sha256(provenance_file)
    extra = tmp_path / "results/p1_v1_2/materialized/unlisted"
    extra.write_text("unexpected")
    with pytest.raises(ValueError, match="unexpected"):
        validate_artifact_files([record], tmp_path)


def test_protocol_freeze_manifest_is_complete_and_valid() -> None:
    freeze = json.loads((OUT / "freeze_manifest_v1_2.json").read_text())
    assert freeze["protocol_hash"] == PROTOCOL_HASH
    assert freeze["validation_status"] == "PASS"
    assert freeze["scientific_semantics_changed"] is False
    assert freeze["operational_determinism_completed"] is True
    assert all(
        hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]
        and (ROOT / item["path"]).stat().st_size == item["bytes"]
        for item in freeze["files"]
    )
    gate = json.loads((OUT / "gate.json").read_text())
    assert gate["decision"] == ["PROTOCOL_V1_2_FROZEN", "C1_C2_MATERIALIZATION_READY"]
    assert gate["independent_review"] == "PASS"
    assert gate["C1_C2_materialized"] is False
    assert gate["scientific_experiments_executed"] == 0


def test_semantic_diff_guard_and_exact_scope() -> None:
    protocol = yaml.safe_load((ROOT / "configs/protocol_v1_2.yaml").read_text())
    diff = json.loads((OUT / "semantic_diff.json").read_text())
    expected = {
        "cross_class_source_candidate_traversal_order",
        "exact_numpy_rng_api_arguments_and_draw_consumption_order",
        "canonical_synthetic_id_and_output_path",
        "serialized_artifact_layout_and_shape",
        "C1_C2_checksum_and_freeze_schema",
        "deterministic_replay_equality_and_tolerance",
        "downstream_dataset_ordering_layout_and_loader_contract",
    }
    assert protocol["protocol"]["scientific_semantics_changed"] is False
    assert protocol["protocol"]["operational_determinism_completed"] is True
    assert set(protocol["resolved_contracts_exactly"]) == expected
    assert set(diff["changed_exactly"]) == expected
    assert all(diff["unchanged"].values())
    assert diff["scope_violation"] is False
    assert diff["test_or_QCNN_metrics_accessed"] is False
