"""Protocol v1.2 operational determinism helpers; performs no state materialization."""

from __future__ import annotations

import hashlib
import io
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from hamiltonian_qda.protocol_v1_1 import ROOT, arm_payload, derive_seed

VERSION = "1.2.0"
PARENT_VERSION = "1.1.0"
PARENT_HASH = "8daba32d38a24312fccfd1234b3f16af97b1f302828a24acf85c1237942b1a80"
P1_FREEZE_HASH = "1f8b28ec08f0686ea4b1162fbf62430dd118c34e13d50533e5f9572e541197e0"
PROTOCOL_HASH = "b6cd7f0e8f239563244a40149aa1e18eb451e4421b8a6cce7c200eff40471761"
PREVIOUS_AUDIT_HASH = "33ecc0dae26219b38b9a5a11ed59701c22e12792b8b15c82d8a15f9cb4dec1be"
REQUIRED_IMPLEMENTATION_SOURCES = {
    "configs/materialization_contract_v1_2.yaml",
    "configs/protocol_v1_1.yaml",
    "configs/protocol_v1_2.yaml",
    "configs/rng_contract_v1_2.yaml",
    "configs/serialization_schema_v1_2.yaml",
    "configs/seed_manifest_v1_1.yaml",
    "configs/split_manifest_v1.yaml",
    "configs/freeze_schema_v1_2.yaml",
    "configs/downstream_loader_schema_v1_2.yaml",
    "configs/tfim_v1.yaml",
    "pyproject.toml",
    "results/p1_v1_1/freeze_manifest.json",
    "results/p1_v1_1/source_assignments.json",
    "results/p1_v1_1/source_states.npz",
    "src/hamiltonian_qda/protocol_v1_1.py",
    "src/hamiltonian_qda/protocol_v1_2.py",
    "uv.lock",
}
ARM_ORDER = ("C2", "C1")


def synthetic_id(arm: str, realization: int, class_label: int, state_index: int) -> str:
    if arm not in ARM_ORDER or not 0 <= realization < 12 or class_label not in (0, 1):
        raise ValueError("invalid synthetic identity")
    if not 0 <= state_index < 1700:
        raise ValueError("invalid state_index")
    return f"p1v1_2-{arm}-D{realization:02d}-Y{class_label}-S{state_index:04d}-A00"


def output_path(arm: str, realization: int, class_label: int, state_index: int) -> str:
    identity = synthetic_id(arm, realization, class_label, state_index)
    return f"results/p1_v1_2/materialized/{arm}/D{realization:02d}/Y{class_label}/{identity}/state.npy"


def provenance_path(arm: str, realization: int, class_label: int, state_index: int) -> str:
    return output_path(arm, realization, class_label, state_index).removesuffix("state.npy") + "provenance.json"


def c2_attempt_vector(payload: str, attempt: int = 0) -> dict[str, int | float]:
    if not 0 <= attempt < 128:
        raise ValueError("attempt must be in 0..127")
    rng = np.random.Generator(np.random.PCG64DXSM(derive_seed(payload)[1]))
    direction_bit = step = None
    for _ in range(attempt + 1):
        direction_bit = int(rng.integers(low=0, high=2, size=None, dtype=np.int64, endpoint=False))
        step = float(rng.uniform(low=0.005, high=0.020, size=None))
    return {"direction_bit": direction_bit, "direction": -1 if direction_bit == 0 else 1, "step": step}


def c1_attempt_vector(payload: str, attempt: int = 0) -> dict[str, list[float]]:
    if not 0 <= attempt < 128:
        raise ValueError("attempt must be in 0..127")
    rng = np.random.Generator(np.random.PCG64DXSM(derive_seed(payload)[1]))
    real = imag = None
    for _ in range(attempt + 1):
        real = rng.normal(loc=0.0, scale=1.0, size=(16,)).astype("<f8", copy=False)
        imag = rng.normal(loc=0.0, scale=1.0, size=(16,)).astype("<f8", copy=False)
    return {"real": real.tolist(), "imag": imag.tolist()}


def dry_resolution() -> list[dict[str, Any]]:
    assignments = json.loads((ROOT / "results/p1_v1_1/source_assignments.json").read_text())["realizations"]
    rows = []
    row = 0
    for arm in ARM_ORDER:
        for realization, record in enumerate(assignments):
            for class_label in (0, 1):
                for source_position, source in enumerate(record["classes"][str(class_label)]):
                    index = source["state_index"]
                    payload = arm_payload(arm, realization, class_label, index)
                    digest, seed = derive_seed(payload)
                    identity = synthetic_id(arm, realization, class_label, index)
                    rows.append(
                        {
                            "global_row": row,
                            "arm_row": row if arm == "C2" else row - 1200,
                            "arm": arm,
                            "realization": record["realization_id"],
                            "class": class_label,
                            "source_position": source_position,
                            "source_state_id": source["source_state_id"],
                            "state_index": index,
                            "source_g": source["g_milli"] / 1000,
                            "p1_assignment_reference": f"results/p1_v1_1/source_assignments.json#/realizations/{realization}/classes/{class_label}/{source_position}",
                            "seed_payload": payload,
                            "seed_sha256": digest,
                            "derived_seed_uint128": str(seed),
                            "synthetic_id": identity,
                            "relative_output_path": output_path(arm, realization, class_label, index),
                            "relative_provenance_path": provenance_path(arm, realization, class_label, index),
                            "serialized_row_index": 0,
                            "replay_comparison_mode": "NUMERICAL_TOLERANCE",
                        }
                    )
                    row += 1
    return rows


def validate_freeze_manifest(
    freeze: dict[str, Any],
    materialization: dict[str, Any],
    expected: list[dict[str, Any]],
    read_artifact: Callable[[str], bytes],
    read_source: Callable[[str], bytes],
) -> None:
    if (
        freeze.get("protocol_version") != VERSION
        or freeze.get("protocol_hash") != PROTOCOL_HASH
        or freeze.get("parent_protocol_version") != PARENT_VERSION
        or freeze.get("parent_protocol_hash") != PARENT_HASH
    ):
        raise ValueError("freeze protocol mismatch")
    if freeze.get("p1_freeze_hash") != P1_FREEZE_HASH or freeze.get("previous_audit_hash") != PREVIOUS_AUDIT_HASH:
        raise ValueError("freeze anchor mismatch")
    if not isinstance(freeze.get("implementation_commit"), str) or len(freeze["implementation_commit"]) != 40:
        raise ValueError("implementation commit missing")
    source_hashes = freeze.get("implementation_source_hashes")
    if not isinstance(source_hashes, list) or not source_hashes or source_hashes != sorted(source_hashes, key=lambda item: item["path"]):
        raise ValueError("implementation source hashes invalid")
    source_paths = [item.get("path") for item in source_hashes]
    materializer_entrypoint = freeze.get("materializer_entrypoint")
    if (
        len(source_paths) != len(set(source_paths))
        or not isinstance(materializer_entrypoint, str)
        or not REQUIRED_IMPLEMENTATION_SOURCES | {materializer_entrypoint} <= set(source_paths)
    ):
        raise ValueError("implementation source coverage invalid")
    for item in source_hashes:
        if set(item) != {"path", "sha256"} or item["sha256"] != hashlib.sha256(read_source(item["path"])).hexdigest():
            raise ValueError("implementation source hash invalid")
    environment = freeze.get("environment")
    if environment != {"python": "3.12.13", "numpy": "2.5.2", "byteorder": "little"}:
        raise ValueError("environment mismatch")
    if freeze.get("validation_status") != "PASS" or freeze.get("materialization_complete") is not True:
        raise ValueError("materialization incomplete")
    if freeze.get("materialization_gate") != "C1_C2_MATERIALIZATION_READY":
        raise ValueError("materialization gate mismatch")
    if freeze.get("scientific_experiments_executed") != 0:
        raise ValueError("unexpected scientific execution")
    duplicate_validation = freeze.get("duplicate_validation")
    if not isinstance(duplicate_validation, dict) or duplicate_validation.get("status") != "PASS":
        raise ValueError("duplicate validation missing")
    if freeze.get("materialization_manifest_path") != "results/p1_v1_2/materialized/materialization_manifest.json":
        raise ValueError("materialization manifest path mismatch")
    materialization_bytes = canonical_json_bytes(materialization)
    if hashlib.sha256(materialization_bytes).hexdigest() != freeze.get("materialization_manifest_sha256"):
        raise ValueError("materialization manifest hash mismatch")
    validate_loader_manifest(materialization, expected)
    required_paths = {
        record["relative_output_path"]: "scientific"
        for record in materialization["records"]
    } | {
        record["relative_provenance_path"]: "metadata"
        for record in materialization["records"]
    } | {freeze["materialization_manifest_path"]: "metadata"}
    files = freeze.get("files")
    if not isinstance(files, list) or [item.get("path") for item in files] != sorted(required_paths):
        raise ValueError("freeze file coverage or ordering mismatch")
    for item in files:
        if set(item) != {"path", "role", "bytes", "sha256"} or item["role"] != required_paths[item["path"]]:
            raise ValueError("freeze file entry schema mismatch")
        content = read_artifact(item["path"])
        if item["bytes"] != len(content) or item["sha256"] != hashlib.sha256(content).hexdigest():
            raise ValueError("freeze file checksum mismatch")
    manifest_entry = next(item for item in files if item["path"] == freeze["materialization_manifest_path"])
    if read_artifact(manifest_entry["path"]) != materialization_bytes:
        raise ValueError("materialization manifest bytes mismatch")


def validate_loader_manifest(manifest: dict[str, Any], expected: list[dict[str, Any]]) -> None:
    if (
        manifest.get("protocol_version") != VERSION
        or manifest.get("protocol_hash") != PROTOCOL_HASH
        or manifest.get("parent_protocol_hash") != PARENT_HASH
    ):
        raise ValueError("protocol mismatch")
    if manifest.get("p1_freeze_hash") != P1_FREEZE_HASH:
        raise ValueError("P1 mismatch")
    records = manifest.get("records")
    if not isinstance(records, list) or len(records) != 2400:
        raise ValueError("record count mismatch")
    required_record_fields = {
        "global_row",
        "arm_row",
        "arm",
        "realization",
        "class",
        "source_position",
        "source_state_id",
        "state_index",
        "source_g",
        "seed_payload",
        "seed_sha256",
        "derived_seed_uint128",
        "synthetic_id",
        "relative_output_path",
        "relative_provenance_path",
        "state_sha256",
        "provenance_sha256",
        "state_payload_sha256",
        "validation_status",
    }
    if any(not required_record_fields <= set(record) for record in records):
        raise ValueError("materialization record schema mismatch")
    if any(record["validation_status"] != "PASS" or len(record["state_payload_sha256"]) != 64 for record in records):
        raise ValueError("materialization record validation failed")
    keys = (
        "global_row",
        "arm_row",
        "arm",
        "realization",
        "class",
        "source_position",
        "source_state_id",
        "state_index",
        "source_g",
        "seed_payload",
        "seed_sha256",
        "derived_seed_uint128",
        "synthetic_id",
        "relative_output_path",
        "relative_provenance_path",
    )
    if any({key: actual.get(key) for key in keys} != {key: wanted[key] for key in keys} for actual, wanted in zip(records, expected, strict=True)):
        raise ValueError("unexpected row or ordering")
    ids = [record["synthetic_id"] for record in records]
    paths = [path for record in records for path in (record["relative_output_path"], record["relative_provenance_path"])]
    if len(set(ids)) != 2400 or len(set(paths)) != 4800:
        raise ValueError("duplicate or collision")
    for record in records:
        if any(not isinstance(record.get(key), str) or len(record[key]) != 64 for key in ("state_sha256", "provenance_sha256")):
            raise ValueError("missing or invalid artifact hash")


def npy_bytes(state: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.lib.format.write_array(buffer, np.asarray(state, dtype="<c16"), version=(1, 0), allow_pickle=False)
    return buffer.getvalue()


def compare_replay_state(expected: np.ndarray, actual: np.ndarray) -> None:
    if expected.shape != (16,) or actual.shape != (16,):
        raise ValueError("replay shape mismatch")
    if expected.dtype != np.dtype("<c16") or actual.dtype != np.dtype("<c16"):
        raise ValueError("replay dtype mismatch")
    if not np.isfinite(expected).all() or not np.isfinite(actual).all():
        raise ValueError("replay non-finite value")
    if not np.allclose(expected, actual, atol=1e-10, rtol=0.0, equal_nan=False):
        raise ValueError("replay numerical mismatch")


def validate_artifact_files(records: list[dict[str, Any]], root: Path) -> None:
    expected_paths = set()
    for record in records:
        state_path = root / record["relative_output_path"]
        provenance_path = root / record["relative_provenance_path"]
        expected_paths.update((state_path.resolve(), provenance_path.resolve()))
        if not state_path.is_file() or not provenance_path.is_file():
            raise ValueError("missing artifact")
        if sha256(state_path) != record["state_sha256"] or sha256(provenance_path) != record["provenance_sha256"]:
            raise ValueError("artifact hash mismatch")
        state = np.load(state_path, allow_pickle=False)
        if state.shape != (16,) or state.dtype != np.dtype("<c16") or not np.isfinite(state).all():
            raise ValueError("state schema mismatch")
        if state_path.read_bytes() != npy_bytes(state):
            raise ValueError("noncanonical NPY serialization")
        raw_provenance = provenance_path.read_bytes()
        provenance = json.loads(raw_provenance)
        if raw_provenance != canonical_json_bytes(provenance):
            raise ValueError("noncanonical provenance serialization")
        required = {
            "synthetic_id",
            "arm",
            "realization",
            "class",
            "source_state_id",
            "source_state_index",
            "source_g",
            "source_label",
            "source_position",
            "proposal_seed_payload",
            "proposal_seed_sha256",
            "proposal_seed_uint128_decimal",
            "accepted_attempt",
            "target_g",
            "FS_displacement",
            "generation_method",
            "protocol_version",
            "protocol_hash",
            "parent_protocol_hash",
            "p1_freeze_hash",
            "state_hash",
            "state_file_sha256",
            "validation",
        }
        if set(provenance) != required:
            raise ValueError("provenance schema mismatch")
        payload_hash = hashlib.sha256(state.astype("<c16", copy=False).tobytes()).hexdigest()
        accepted_attempt = provenance["accepted_attempt"]
        if not isinstance(accepted_attempt, int) or isinstance(accepted_attempt, bool) or not 0 <= accepted_attempt < 128:
            raise ValueError("accepted attempt invalid")
        if record["arm"] == "C1" and provenance["target_g"] is not None:
            raise ValueError("C1 target_g must be null")
        if record["arm"] == "C2" and (not isinstance(provenance["target_g"], float) or not np.isfinite(provenance["target_g"])):
            raise ValueError("C2 target_g invalid")
        if not isinstance(provenance["FS_displacement"], float) or not np.isfinite(provenance["FS_displacement"]):
            raise ValueError("FS displacement invalid")
        if (
            provenance["synthetic_id"] != record["synthetic_id"]
            or provenance["arm"] != record["arm"]
            or provenance["realization"] != record["realization"]
            or provenance["class"] != record["class"]
            or provenance["source_state_id"] != record["source_state_id"]
            or provenance["source_state_index"] != record["state_index"]
            or provenance["source_g"] != record["source_g"]
            or provenance["source_label"] != record["class"]
            or provenance["source_position"] != record["source_position"]
            or provenance["proposal_seed_payload"] != record["seed_payload"]
            or provenance["proposal_seed_sha256"] != record["seed_sha256"]
            or provenance["proposal_seed_uint128_decimal"] != record["derived_seed_uint128"]
            or provenance["protocol_hash"] != PROTOCOL_HASH
            or provenance["state_file_sha256"] != record["state_sha256"]
            or provenance["state_hash"] != payload_hash
            or record.get("state_payload_sha256") != payload_hash
            or provenance["protocol_version"] != VERSION
            or provenance["parent_protocol_hash"] != PARENT_HASH
            or provenance["p1_freeze_hash"] != P1_FREEZE_HASH
            or provenance.get("validation", {}).get("status") != "PASS"
        ):
            raise ValueError("provenance content mismatch")
    namespace = root / "results/p1_v1_2/materialized"
    allowed_metadata = {namespace / "materialization_manifest.json", namespace / "materialization_freeze_manifest.json"}
    actual_paths = {path.resolve() for path in namespace.rglob("*") if path.is_file()} - {path.resolve() for path in allowed_metadata}
    if actual_paths != expected_paths:
        raise ValueError("unexpected or unlisted artifact")


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
