"""Protocol v1.1 metadata-only randomization primitives."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
VERSION = "1.1.0"
ROOT_SEEDS = {"SOURCE": 13001, "C1": 21001, "C2": 22001}
PURPOSES = {"C1": "tangent", "C2": "proposal"}


def valid_g_milli() -> list[int]:
    return [*range(100, 950), *range(1051, 1901)]


def state_index(g_milli: int) -> int:
    if 100 <= g_milli <= 949:
        return g_milli - 100
    if 1051 <= g_milli <= 1900:
        return g_milli - 201
    raise ValueError(f"invalid g_milli: {g_milli}")


def source_payload(class_label: int) -> str:
    if class_label not in (0, 1):
        raise ValueError("class_label must be 0 or 1")
    return f"hamiltonian-qda|{VERSION}|SOURCE|source_assignment|{class_label}|13001"


def arm_payload(arm: str, realization: int, class_label: int, index: int) -> str:
    if arm not in PURPOSES or not 0 <= realization < 12 or class_label not in (0, 1):
        raise ValueError("invalid seed identity")
    if index not in range(1700):
        raise ValueError("state_index must be in 0..1699")
    return (
        f"hamiltonian-qda|{VERSION}|{arm}|{PURPOSES[arm]}|{realization}|"
        f"{class_label}|{index}|{ROOT_SEEDS[arm]}"
    )


def derive_seed(payload: str) -> tuple[str, int]:
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return digest.hex(), int.from_bytes(digest[:16], "big", signed=False)


def source_assignments() -> list[dict[int, list[int]]]:
    train = {
        0: [*range(100, 450), *range(650, 950)],
        1: [*range(1051, 1351), *range(1551, 1901)],
    }
    permutations = {}
    for label, values in train.items():
        seed = derive_seed(source_payload(label))[1]
        rng = np.random.Generator(np.random.PCG64DXSM(seed))
        permutations[label] = rng.permutation([state_index(g) for g in values]).tolist()
    return [
        {label: permutations[label][50 * r : 50 * (r + 1)] for label in (0, 1)}
        for r in range(12)
    ]
