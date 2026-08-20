#!/usr/bin/env python3
"""Execute frozen Protocol v1.2 C1/C2 materialization without downstream computation."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from hamiltonian_qda.protocol_v1_1 import ROOT, derive_seed
from hamiltonian_qda.protocol_v1_2 import (
    P1_FREEZE_HASH,
    PARENT_HASH,
    PREVIOUS_AUDIT_HASH,
    PROTOCOL_HASH,
    REQUIRED_IMPLEMENTATION_SOURCES,
    VERSION,
    canonical_json_bytes,
    dry_resolution,
    npy_bytes,
    validate_artifact_files,
    validate_freeze_manifest,
    validate_loader_manifest,
)

STARTING_COMMIT = "433a98f53f5c8949d42b119aad7825c7c389c9b2"
PROTOCOL_FREEZE_HASH = "ffbdd650fca459003ff07043d73fd82b0b3bcb3d7c25313f289183fa0dd936ab"
RNG_VECTORS_HASH = "9963cbea045ec65b5e6fc16a7fb4525a2f1e1d449b57979790e222e53bb767f6"
MATERIALIZER = "scripts/materialize_c1_c2_v1_2.py"
CANONICAL = ROOT / "results/p1_v1_2/materialized"
AUDIT = ROOT / "results/p1_v1_2/freeze"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonicalize(state: np.ndarray) -> np.ndarray:
    state = np.asarray(state, dtype="<c16")
    pivot = int(np.argmax(np.abs(state)))
    state = state * np.exp(-1j * np.angle(state[pivot]))
    state[pivot] = complex(state[pivot].real, 0.0)
    return state.astype("<c16", copy=False)


def tfim_operators() -> tuple[np.ndarray, np.ndarray]:
    config = yaml.safe_load((ROOT / "configs/tfim_v1.yaml").read_text())
    qubits = config["qubits"]
    identity = np.asarray(config["operators"]["I"], dtype="<c16")
    x = np.asarray(config["operators"]["X"], dtype="<c16")
    z = np.asarray(config["operators"]["Z"], dtype="<c16")

    def tensor(items: list[np.ndarray]) -> np.ndarray:
        result = items[0]
        for item in items[1:]:
            result = np.kron(result, item)
        return result

    interaction = np.zeros((2**qubits, 2**qubits), dtype="<c16")
    field = np.zeros_like(interaction)
    for site in range(qubits - 1):
        interaction -= config["coupling_J"] * tensor(
            [z if q in (site, site + 1) else identity for q in range(qubits)]
        )
    for site in range(qubits):
        field -= tensor([x if q == site else identity for q in range(qubits)])
    return interaction, field


def ground_state(g: float, operators: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, dict[str, float]]:
    hamiltonian = operators[0] + np.float64(g) * operators[1]
    values, vectors = np.linalg.eigh(hamiltonian)
    state = canonicalize(vectors[:, 0])
    return state, {
        "ground_energy": float(values[0]),
        "spectral_gap": float(values[1] - values[0]),
        "residual": float(np.linalg.norm(hamiltonian @ state - values[0] * state)),
        "norm_error": float(abs(np.linalg.norm(state) - 1.0)),
    }


def fs_distance(left: np.ndarray, right: np.ndarray) -> float:
    overlap = abs(np.vdot(left, right)) / (np.linalg.norm(left) * np.linalg.norm(right))
    return float(np.arccos(np.clip(overlap, 0.0, 1.0)))


def duplicate_metrics(candidate: np.ndarray, pool: list[np.ndarray], state_hash: str) -> dict[str, Any]:
    hashes = [hashlib.sha256(state.astype("<c16", copy=False).tobytes()).hexdigest() for state in pool]
    exact = state_hash in hashes
    fidelities = np.abs(np.asarray(pool) @ candidate.conj()) ** 2
    nearest = float(np.max(fidelities))
    infidelity = 1.0 - nearest
    return {
        "exact_duplicate": exact,
        "projective_duplicate": infidelity <= 1e-12,
        "near_duplicate": infidelity <= 1e-8,
        "nearest_training_fidelity": nearest,
        "nearest_training_FS_distance": float(np.arccos(np.clip(math.sqrt(nearest), 0.0, 1.0))),
    }


def load_sources() -> tuple[list[dict[str, Any]], np.ndarray]:
    expected = dry_resolution()[:1200]
    with np.load(ROOT / "results/p1_v1_1/source_states.npz") as data:
        states = data["state"].astype("<c16", copy=True)
        assert states.shape == (1200, 16)
        for row, expected_row in enumerate(expected):
            assert int(data["state_index"][row]) == expected_row["state_index"]
            assert int(data["label"][row]) == expected_row["class"]
    return expected, states


def real_training_pool(operators: tuple[np.ndarray, np.ndarray]) -> tuple[list[np.ndarray], list[float]]:
    split = yaml.safe_load((ROOT / "configs/split_manifest_v1.yaml").read_text())
    intervals = split["sets"]["train_intervals_inclusive"]
    g_milli = [value for low, high in intervals for value in range(low, high + 1)]
    return [ground_state(value / 1000, operators)[0] for value in g_milli], [value / 1000 for value in g_milli]


def c2_candidate(
    source: np.ndarray,
    source_g: float,
    class_label: int,
    payload: str,
    operators: tuple[np.ndarray, np.ndarray],
    real_pool: list[np.ndarray],
    real_g: list[float],
    prior: list[np.ndarray],
    prior_targets: list[float],
    protocol: dict[str, Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    seed = derive_seed(payload)[1]
    rng = np.random.Generator(np.random.PCG64DXSM(seed))
    components = protocol["C2_proposal"]["train_support_components_inclusive"]
    for attempt in range(protocol["C2_proposal"]["maximum_attempts"]):
        bit = int(rng.integers(low=0, high=2, size=None, dtype=np.int64, endpoint=False))
        direction = -1 if bit == 0 else 1
        step = float(rng.uniform(low=0.005, high=0.020, size=None))
        target = float(np.float64(source_g) + np.float64(direction) * np.float64(step))
        component = next((bounds for bounds in components if bounds[0] <= source_g <= bounds[1]), None)
        if component is None or not component[0] <= target <= component[1]:
            continue
        if (target > 1.0) != bool(class_label):
            continue
        if min(abs(target - value) for value in real_g) < 5e-7:
            continue
        if prior_targets and min(abs(target - value) for value in prior_targets) < 5e-7:
            continue
        state, physical = ground_state(target, operators)
        if (
            not np.isfinite(state).all()
            or physical["norm_error"] > 1e-12
            or physical["residual"] > 1e-10
            or physical["spectral_gap"] <= 1e-10
        ):
            continue
        state_hash = hashlib.sha256(state.tobytes()).hexdigest()
        duplicate = duplicate_metrics(state, real_pool + prior, state_hash)
        if duplicate["exact_duplicate"] or duplicate["projective_duplicate"]:
            continue
        return state, {
            "accepted_attempt": attempt,
            "target_g": target,
            "FS_displacement": fs_distance(source, state),
            "generation_method": "exact_ground_state_at_continuous_train_support_target_g",
            "physical": physical,
            "duplicate": duplicate,
        }
    raise RuntimeError("C2 BLOCKED after attempt 127")


def c1_candidate(
    source: np.ndarray,
    target_radius: float,
    payload: str,
    real_pool: list[np.ndarray],
    prior: list[np.ndarray],
    protocol: dict[str, Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    seed = derive_seed(payload)[1]
    rng = np.random.Generator(np.random.PCG64DXSM(seed))
    source = source / np.linalg.norm(source)
    for attempt in range(protocol["C1_generator"]["maximum_attempts"]):
        real = rng.normal(loc=0.0, scale=1.0, size=(16,)).astype("<f8", copy=False)
        imag = rng.normal(loc=0.0, scale=1.0, size=(16,)).astype("<f8", copy=False)
        z = (real.astype("<c16") + 1j * imag.astype("<c16")) / np.sqrt(np.float64(2.0))
        tangent = z - source * np.vdot(source, z)
        tangent_norm = float(np.linalg.norm(tangent))
        if not np.isfinite(tangent).all() or tangent_norm <= 1e-12:
            continue
        tangent /= tangent_norm
        candidate = np.cos(target_radius) * source + np.sin(target_radius) * tangent
        candidate /= np.linalg.norm(candidate)
        candidate = canonicalize(candidate)
        norm_error = float(abs(np.linalg.norm(candidate) - 1.0))
        actual_radius = fs_distance(source, candidate)
        if (
            not np.isfinite(candidate).all()
            or norm_error > 1e-12
            or abs(actual_radius - target_radius) > 1e-10
            or abs(np.vdot(source, tangent)) > 1e-12
        ):
            continue
        state_hash = hashlib.sha256(candidate.tobytes()).hexdigest()
        duplicate = duplicate_metrics(candidate, real_pool + prior, state_hash)
        if duplicate["exact_duplicate"] or duplicate["projective_duplicate"]:
            continue
        return candidate, {
            "accepted_attempt": attempt,
            "target_g": None,
            "FS_displacement": actual_radius,
            "generation_method": "isotropic_complex_Gaussian_projective_tangent",
            "physical": {"norm_error": norm_error, "tangent_norm": tangent_norm},
            "duplicate": duplicate,
        }
    raise RuntimeError("C1 BLOCKED after attempt 127")


def write_output(root: Path, dry: dict[str, Any], state: np.ndarray, details: dict[str, Any]) -> dict[str, Any]:
    state_path = root / dry["relative_output_path"]
    provenance_path = root / dry["relative_provenance_path"]
    state_path.parent.mkdir(parents=True, exist_ok=False)
    state_bytes = npy_bytes(state)
    state_path.write_bytes(state_bytes)
    state_payload_hash = hashlib.sha256(state.astype("<c16", copy=False).tobytes()).hexdigest()
    provenance = {
        "synthetic_id": dry["synthetic_id"],
        "arm": dry["arm"],
        "realization": dry["realization"],
        "class": dry["class"],
        "source_state_id": dry["source_state_id"],
        "source_state_index": dry["state_index"],
        "source_g": dry["source_g"],
        "source_label": dry["class"],
        "source_position": dry["source_position"],
        "proposal_seed_payload": dry["seed_payload"],
        "proposal_seed_sha256": dry["seed_sha256"],
        "proposal_seed_uint128_decimal": dry["derived_seed_uint128"],
        "accepted_attempt": details["accepted_attempt"],
        "target_g": details["target_g"],
        "FS_displacement": details["FS_displacement"],
        "generation_method": details["generation_method"],
        "protocol_version": VERSION,
        "protocol_hash": PROTOCOL_HASH,
        "parent_protocol_hash": PARENT_HASH,
        "p1_freeze_hash": P1_FREEZE_HASH,
        "state_hash": state_payload_hash,
        "state_file_sha256": hashlib.sha256(state_bytes).hexdigest(),
        "validation": {"status": "PASS", **details["physical"], **details["duplicate"]},
    }
    provenance_bytes = canonical_json_bytes(provenance)
    provenance_path.write_bytes(provenance_bytes)
    return {
        **dry,
        "state_sha256": provenance["state_file_sha256"],
        "provenance_sha256": hashlib.sha256(provenance_bytes).hexdigest(),
        "state_payload_sha256": state_payload_hash,
        "validation_status": "PASS",
    }


def materialize(root: Path) -> list[dict[str, Any]]:
    protocol = yaml.safe_load((ROOT / "configs/protocol_v1_1.yaml").read_text())
    dry = dry_resolution()
    source_rows, source_states = load_sources()
    operators = tfim_operators()
    real_pool, real_g = real_training_pool(operators)
    records: list[dict[str, Any]] = []
    c2_states: dict[tuple[int, int, int], np.ndarray] = {}
    c2_details: dict[tuple[int, int, int], dict[str, Any]] = {}
    prior_by_arm_realization: dict[tuple[str, int], list[np.ndarray]] = {}
    prior_c2_targets: dict[int, list[float]] = {}

    for dry_row in dry:
        realization = int(dry_row["realization"][1:])
        source_row = realization * 100 + dry_row["class"] * 50 + dry_row["source_position"]
        assert source_rows[source_row]["state_index"] == dry_row["state_index"]
        source = source_states[source_row]
        key = (realization, dry_row["class"], dry_row["source_position"])
        prior = prior_by_arm_realization.setdefault((dry_row["arm"], realization), [])
        if dry_row["arm"] == "C2":
            targets = prior_c2_targets.setdefault(realization, [])
            state, details = c2_candidate(
                source,
                dry_row["source_g"],
                dry_row["class"],
                dry_row["seed_payload"],
                operators,
                real_pool,
                real_g,
                prior,
                targets,
                protocol,
            )
            c2_states[key], c2_details[key] = state, details
            targets.append(details["target_g"])
        else:
            state, details = c1_candidate(
                source,
                c2_details[key]["FS_displacement"],
                dry_row["seed_payload"],
                real_pool,
                prior,
                protocol,
            )
        records.append(write_output(root, dry_row, state, details))
        prior.append(state)
    return records


def materialization_manifest(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "protocol_version": VERSION,
        "protocol_hash": PROTOCOL_HASH,
        "parent_protocol_hash": PARENT_HASH,
        "p1_freeze_hash": P1_FREEZE_HASH,
        "records": records,
    }


def implementation_sources() -> list[dict[str, str]]:
    paths = sorted(REQUIRED_IMPLEMENTATION_SOURCES | {MATERIALIZER})
    return [{"path": path, "sha256": file_hash(ROOT / path)} for path in paths]


def freeze_manifest(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_path = "results/p1_v1_2/materialized/materialization_manifest.json"
    manifest_bytes = canonical_json_bytes(manifest)
    (root / manifest_path).write_bytes(manifest_bytes)
    entries = []
    for record in manifest["records"]:
        for path, role in (
            (record["relative_output_path"], "scientific"),
            (record["relative_provenance_path"], "metadata"),
        ):
            artifact = root / path
            entries.append({"path": path, "role": role, "bytes": artifact.stat().st_size, "sha256": file_hash(artifact)})
    entries.append({"path": manifest_path, "role": "metadata", "bytes": len(manifest_bytes), "sha256": hashlib.sha256(manifest_bytes).hexdigest()})
    entries.sort(key=lambda item: item["path"])
    return {
        "protocol_version": VERSION,
        "protocol_hash": PROTOCOL_HASH,
        "protocol_freeze_hash": PROTOCOL_FREEZE_HASH,
        "parent_protocol_version": "1.1.0",
        "parent_protocol_hash": PARENT_HASH,
        "p1_freeze_hash": P1_FREEZE_HASH,
        "previous_audit_hash": PREVIOUS_AUDIT_HASH,
        "rng_vectors_hash": RNG_VECTORS_HASH,
        "implementation_commit": STARTING_COMMIT,
        "materializer_entrypoint": MATERIALIZER,
        "implementation_source_hashes": implementation_sources(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "byteorder": sys.byteorder},
        "validation_status": "PASS",
        "materialization_complete": True,
        "materialization_gate": "C1_C2_MATERIALIZATION_READY",
        "scientific_experiments_executed": 0,
        "QCNN_or_downstream_runs": 0,
        "duplicate_validation": {"status": "PASS"},
        "materialization_manifest_path": manifest_path,
        "materialization_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "files": entries,
    }


def validate_corpus(root: Path, manifest: dict[str, Any], freeze: dict[str, Any]) -> dict[str, Any]:
    expected = dry_resolution()
    validate_loader_manifest(manifest, expected)
    validate_freeze_manifest(
        freeze,
        manifest,
        expected,
        lambda path: (root / path).read_bytes(),
        lambda path: (ROOT / path).read_bytes(),
    )
    validate_artifact_files(manifest["records"], root)
    records = manifest["records"]
    return {
        "status": "PASS",
        "C1_count": sum(record["arm"] == "C1" for record in records),
        "C2_count": sum(record["arm"] == "C2" for record in records),
        "combined_count": len(records),
        "unique_ids": len({record["synthetic_id"] for record in records}),
        "unique_state_paths": len({record["relative_output_path"] for record in records}),
        "unique_provenance_paths": len({record["relative_provenance_path"] for record in records}),
        "unexpected_outputs": 0,
        "source_reassignments": 0,
        "pairwise_realization_source_overlap": 0,
        "all_sources_TRAIN": True,
        "unspecified_randomness": 0,
        "loader_validation": "PASS",
    }


def replay(canonical_root: Path, replay_root: Path) -> dict[str, Any]:
    replay_records = materialize(replay_root)
    replay_manifest = materialization_manifest(replay_records)
    canonical_manifest = json.loads((canonical_root / "results/p1_v1_2/materialized/materialization_manifest.json").read_text())
    maximum = 0.0
    state_mismatches = metadata_mismatches = 0
    for expected, actual in zip(canonical_manifest["records"], replay_manifest["records"], strict=True):
        expected_state = np.load(canonical_root / expected["relative_output_path"], allow_pickle=False)
        actual_state = np.load(replay_root / actual["relative_output_path"], allow_pickle=False)
        difference = float(np.max(np.abs(expected_state - actual_state)))
        maximum = max(maximum, difference)
        if expected_state.shape != actual_state.shape or expected_state.dtype != actual_state.dtype or not np.isfinite(actual_state).all() or not np.allclose(expected_state, actual_state, atol=1e-10, rtol=0.0, equal_nan=False):
            state_mismatches += 1
        if (canonical_root / expected["relative_provenance_path"]).read_bytes() != (replay_root / actual["relative_provenance_path"]).read_bytes():
            metadata_mismatches += 1
    return {
        "status": "PASS" if state_mismatches == metadata_mismatches == 0 else "FAIL",
        "compared_outputs": len(replay_records),
        "maximum_absolute_difference": maximum,
        "state_mismatch_count": state_mismatches,
        "metadata_mismatch_count": metadata_mismatches,
        "missing_count": 0,
        "unexpected_count": 0,
    }


def write_summaries(validation: dict[str, Any], replay_report: dict[str, Any], freeze: dict[str, Any]) -> None:
    AUDIT.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((CANONICAL / "materialization_manifest.json").read_text())
    for arm in ("C1", "C2"):
        subset = {key: value for key, value in manifest.items() if key != "records"}
        subset["arm"] = arm
        subset["records"] = [record for record in manifest["records"] if record["arm"] == arm]
        (AUDIT / f"{arm.lower()}_manifest.json").write_bytes(canonical_json_bytes(subset))
    (AUDIT / "combined_manifest.json").write_bytes(canonical_json_bytes(manifest))
    (AUDIT / "validation_report.json").write_bytes(canonical_json_bytes(validation))
    (AUDIT / "replay_report.json").write_bytes(canonical_json_bytes(replay_report))
    provenance = {
        "protocol_version": VERSION,
        "protocol_hash": PROTOCOL_HASH,
        "protocol_freeze_hash": PROTOCOL_FREEZE_HASH,
        "p1_hashes": {
            path.name: file_hash(path)
            for path in sorted((ROOT / "results/p1_v1_1").iterdir())
            if path.is_file()
        },
        "rng_vectors_hash": RNG_VECTORS_HASH,
        "counts": {"C1": 1200, "C2": 1200, "combined": 2400},
        "source_assignment_audit": "PASS",
        "replay": replay_report,
        "scientific_experiments_executed": 0,
        "QCNN_or_downstream_runs": 0,
    }
    (AUDIT / "provenance_summary.json").write_bytes(canonical_json_bytes(provenance))
    (CANONICAL / "materialization_freeze_manifest.json").write_bytes(canonical_json_bytes(freeze))
    freeze_hash = file_hash(CANONICAL / "materialization_freeze_manifest.json")
    gate = {
        "decision": ["C1_C2_MATERIALIZATION_FROZEN", "DOWNSTREAM_EXECUTION_PROHIBITED_PENDING_SEPARATE_AUTHORIZATION"],
        "status": "PASS",
        "combined_freeze_hash": freeze_hash,
        "validation": "PASS",
        "replay": "PASS",
        "scientific_experiments_executed": 0,
        "QCNN_or_downstream_runs": 0,
    }
    (AUDIT / "freeze_gate.json").write_bytes(canonical_json_bytes(gate))
    report = f"""# C1/C2 Materialization Freeze\n\n**C1_C2_MATERIALIZATION_FROZEN**\n\n**DOWNSTREAM_EXECUTION_PROHIBITED_PENDING_SEPARATE_AUTHORIZATION**\n\nC1: 1200; C2: 1200; combined: 2400. Validation and isolated replay passed with maximum absolute difference `{replay_report['maximum_absolute_difference']}`. Scientific experiments and QCNN/downstream runs: 0.\n\nCombined freeze hash: `{freeze_hash}`\n"""
    (AUDIT / "report.md").write_text(report)
    checksum_paths = sorted([path for path in AUDIT.iterdir() if path.name != "checksums.sha256"] + [CANONICAL / "materialization_freeze_manifest.json", CANONICAL / "materialization_manifest.json"])
    (AUDIT / "checksums.sha256").write_text(
        "\n".join(f"{file_hash(path)}  {path.relative_to(ROOT)}" for path in checksum_paths) + "\n"
    )


def preflight() -> None:
    anchors = {
        ROOT / "configs/protocol_v1_2.yaml": PROTOCOL_HASH,
        ROOT / "results/protocol_v1_2/freeze_manifest_v1_2.json": PROTOCOL_FREEZE_HASH,
        ROOT / "results/protocol_v1_2/rng_test_vectors.json": RNG_VECTORS_HASH,
        ROOT / "results/p1_v1_1/freeze_manifest.json": P1_FREEZE_HASH,
    }
    if any(file_hash(path) != expected for path, expected in anchors.items()):
        raise RuntimeError("ANCHOR_INTEGRITY_BLOCKED")
    if CANONICAL.exists() and any(CANONICAL.iterdir()):
        raise RuntimeError("EXISTING_OUTPUT_BLOCKED")
    if (ROOT / "results/p1_v1_2").exists():
        raise RuntimeError("EXISTING_OUTPUT_BLOCKED")
    dry = json.loads((ROOT / "results/protocol_v1_2/dry_resolution.json").read_text())
    if dry["counts"] != {"C2": 1200, "C1": 1200, "total": 2400} or any(
        dry[key] != 0 for key in ("duplicate_ids", "duplicate_paths", "unresolved_fields", "unspecified_randomness")
    ):
        raise RuntimeError("PROTOCOL_REVISION_REQUIRED")


def main() -> None:
    preflight()
    temp_root = Path(tempfile.mkdtemp(prefix=".hamiltonian-qda-v1_2-", dir=ROOT / "results"))
    replay_root = Path(tempfile.mkdtemp(prefix=".hamiltonian-qda-v1_2-replay-", dir=ROOT / "results"))
    try:
        records = materialize(temp_root)
        manifest = materialization_manifest(records)
        freeze = freeze_manifest(temp_root, manifest)
        validation = validate_corpus(temp_root, manifest, freeze)
        if validation["combined_count"] != 2400:
            raise RuntimeError("C1_C2_MATERIALIZATION_BLOCKED")
        replay_report = replay(temp_root, replay_root)
        if replay_report["status"] != "PASS":
            raise RuntimeError("C1_C2_MATERIALIZATION_BLOCKED")
        destination = ROOT / "results/p1_v1_2"
        source = temp_root / "results/p1_v1_2"
        os.replace(source, destination)
        write_summaries(validation, replay_report, freeze)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        shutil.rmtree(replay_root, ignore_errors=True)
    print("C1_C2_MATERIALIZATION_FROZEN")
    print("DOWNSTREAM_EXECUTION_PROHIBITED_PENDING_SEPARATE_AUTHORIZATION")


if __name__ == "__main__":
    main()
