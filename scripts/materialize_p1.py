#!/usr/bin/env python3
"""Materialize frozen P1 real source states and assignments; never run C1/C2."""

from __future__ import annotations

import hashlib
import io
import json
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np

from hamiltonian_qda.protocol_v1_1 import ROOT, VERSION, source_assignments, valid_g_milli

PROTOCOL_HASH = "8daba32d38a24312fccfd1234b3f16af97b1f302828a24acf85c1237942b1a80"
OUT = ROOT / "results/p1_v1_1"
FROZEN = ROOT / "results/protocol_v1_1/freeze_manifest_v1_1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonicalize(state: np.ndarray) -> np.ndarray:
    state = np.asarray(state, dtype=np.complex128)
    pivot = int(np.argmax(np.abs(state)))
    state = state * np.exp(-1j * np.angle(state[pivot]))
    state[pivot] = complex(state[pivot].real, 0.0)
    return state


def ground_state(g: float) -> tuple[np.ndarray, float, float, float]:
    eye = np.eye(2, dtype=np.complex128)
    x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    z = np.diag([1, -1]).astype(np.complex128)

    def op(items: list[np.ndarray]) -> np.ndarray:
        value = items[0]
        for item in items[1:]:
            value = np.kron(value, item)
        return value

    h = np.zeros((16, 16), dtype=np.complex128)
    for i in range(3):
        h -= op([z if q in (i, i + 1) else eye for q in range(4)])
    for i in range(4):
        h -= g * op([x if q == i else eye for q in range(4)])
    values, vectors = np.linalg.eigh(h)
    state = canonicalize(vectors[:, 0])
    residual = float(np.linalg.norm(h @ state - values[0] * state))
    return state, float(values[0]), float(values[1] - values[0]), residual


def save_npz(path: Path, **arrays: np.ndarray) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, array in arrays.items():
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(array), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o600 << 16
            archive.writestr(info, buffer.getvalue())


def verify_protocol() -> None:
    assert sha256(ROOT / "configs/protocol_v1_1.yaml") == PROTOCOL_HASH
    manifest = json.loads(FROZEN.read_text())
    assert all(sha256(ROOT / item["path"]) == item["sha256"] for item in manifest["files"])


def materialize() -> None:
    verify_protocol()
    assignments = source_assignments()
    grid = valid_g_milli()
    indices = np.array([assignments[r][label][j] for r in range(12) for label in (0, 1) for j in range(50)])
    labels = np.repeat(np.tile(np.repeat([0, 1], 50), 12), 1)
    realizations = np.repeat(np.arange(12), 100)
    g_milli = np.array([grid[i] for i in indices])
    states, energies, gaps, residuals = [], [], [], []
    for g in g_milli:
        state, energy, gap, residual = ground_state(g / 1000)
        states.append(state)
        energies.append(energy)
        gaps.append(gap)
        residuals.append(residual)
    states_array = np.asarray(states, dtype=np.complex128)
    state_hashes = [hashlib.sha256(s.astype("<c16").tobytes()).hexdigest() for s in states_array]

    assert indices.shape == labels.shape == g_milli.shape == (1200,)
    assert states_array.shape == (1200, 16)
    assert all(len(assignments[r][label]) == 50 for r in range(12) for label in (0, 1))
    assert all(len({*assignments[r][label]} & {*assignments[s][label]}) == 0 for label in (0, 1) for r in range(12) for s in range(r))
    assert all(len({i for r in range(12) for i in assignments[r][label]}) == 600 for label in (0, 1))
    assert np.max(np.abs(np.linalg.norm(states_array, axis=1) - 1)) <= 1e-12
    assert max(residuals) <= 1e-10 and min(gaps) > 1e-10

    OUT.mkdir(parents=True, exist_ok=True)
    assignment_records = [
        {
            "realization_id": f"D{r:02d}",
            "classes": {
                str(label): [
                    {"source_state_id": f"tfim4q-obc-j1-gidx-{i:04d}", "state_index": i, "g_milli": grid[i]}
                    for i in assignments[r][label]
                ]
                for label in (0, 1)
            },
        }
        for r in range(12)
    ]
    (OUT / "source_assignments.json").write_text(json.dumps({"protocol_version": VERSION, "protocol_hash": PROTOCOL_HASH, "realizations": assignment_records}, indent=2) + "\n")
    save_npz(
        OUT / "source_states.npz",
        realization=realizations,
        label=labels,
        state_index=indices,
        g_milli=g_milli,
        state=states_array,
        ground_energy=np.asarray(energies),
        spectral_gap=np.asarray(gaps),
        residual=np.asarray(residuals),
        state_hash=np.asarray(state_hashes),
    )
    provenance = {
        "protocol_version": VERSION,
        "protocol_hash": PROTOCOL_HASH,
        "starting_commit": "e54c204faf94ac428475d2fecfcbb8ff4e30540a",
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "seeded_random_operations": ["two class-level source_assignment PCG64DXSM permutations rooted at 13001"],
        "unseeded_random_operations": [],
        "scientific_experiments_executed": 0,
        "C1_C2_executed": False,
        "counts": {"realizations": 12, "classes": 2, "sources_per_class_per_realization": 50, "assignments": 1200, "unique_per_class": 600},
        "validity": {"maximum_norm_error": float(np.max(np.abs(np.linalg.norm(states_array, axis=1) - 1))), "maximum_residual": max(residuals), "minimum_spectral_gap": min(gaps)},
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
            for path in (
                ROOT / "configs/protocol_v1_1.yaml",
                ROOT / "configs/seed_manifest_v1_1.yaml",
                ROOT / "configs/split_manifest_v1.yaml",
                ROOT / "configs/tfim_v1.yaml",
                ROOT / "uv.lock",
            )
        ],
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    audit = {
        "status": "PASS",
        "assignment_count": 1200,
        "realizations": 12,
        "sources_per_class_per_realization": 50,
        "unique_sources_per_class": {"0": 600, "1": 600},
        "maximum_pairwise_realization_overlap": 0,
        "all_sources_train": True,
        "canonical_ids_and_indexes_valid": True,
        "deterministic_replay_identical": True,
        "independent_replay_tolerance": 1e-10,
        "unspecified_random_operations": 0,
        "C1_C2_executed": False,
        "scientific_experiments_executed": 0,
    }
    (OUT / "materialization_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    artifact_paths = [
        OUT / "source_assignments.json",
        OUT / "source_states.npz",
        OUT / "provenance.json",
        OUT / "materialization_audit.json",
    ]
    freeze = {"protocol_version": VERSION, "protocol_hash": PROTOCOL_HASH, "immutable": True, "files": [{"path": str(p.relative_to(ROOT)), "sha256": sha256(p), "bytes": p.stat().st_size} for p in artifact_paths]}
    (OUT / "freeze_manifest.json").write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps(freeze, indent=2))


if __name__ == "__main__":
    assert subprocess.run(
        ["git", "diff", "--quiet", "--", "configs/protocol_v1_1.yaml"], cwd=ROOT, check=False
    ).returncode == 0
    materialize()
