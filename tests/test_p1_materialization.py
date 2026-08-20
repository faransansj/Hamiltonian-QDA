import hashlib
import json

import numpy as np

from hamiltonian_qda.protocol_v1_1 import ROOT, derive_seed, source_payload

OUT = ROOT / "results/p1_v1_1"
TRAIN = {0: {*range(100, 450), *range(650, 950)}, 1: {*range(1051, 1351), *range(1551, 1901)}}


def independent_state(g: float) -> np.ndarray:
    h = np.zeros((16, 16), dtype=np.float64)
    for basis in range(16):
        bits = [(basis >> (3 - q)) & 1 for q in range(4)]
        h[basis, basis] = -sum((1 - 2 * bits[q]) * (1 - 2 * bits[q + 1]) for q in range(3))
        for q in range(4):
            h[basis, basis ^ (1 << (3 - q))] -= g
    _, vectors = np.linalg.eigh(h)
    state = vectors[:, 0].astype(np.complex128)
    pivot = int(np.argmax(np.abs(state)))
    state *= np.exp(-1j * np.angle(state[pivot]))
    state[pivot] = complex(state[pivot].real, 0)
    return state


def test_p1_frozen_artifacts_and_independent_replay() -> None:
    freeze = json.loads((OUT / "freeze_manifest.json").read_text())
    assert freeze["protocol_hash"] == "8daba32d38a24312fccfd1234b3f16af97b1f302828a24acf85c1237942b1a80"
    assert all(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in freeze["files"])

    records = json.loads((OUT / "source_assignments.json").read_text())["realizations"]
    assert len(records) == 12
    for label in (0, 1):
        eligible = sorted(TRAIN[label])
        seed = derive_seed(source_payload(label))[1]
        expected_g = np.random.Generator(np.random.PCG64DXSM(seed)).permutation(eligible)[:600]
        actual_g = [item["g_milli"] for record in records for item in record["classes"][str(label)]]
        assert actual_g == expected_g.tolist()
        assert len(actual_g) == len(set(actual_g)) == 600
    assert all(len(record["classes"][str(label)]) == 50 for record in records for label in (0, 1))

    with np.load(OUT / "source_states.npz") as data:
        assert data["state"].shape == (1200, 16)
        assert data["state_index"].shape == data["g_milli"].shape == (1200,)
        assert np.array_equal(data["label"], (data["g_milli"] > 1000).astype(int))
        assert all(int(g) in TRAIN[int(label)] for g, label in zip(data["g_milli"], data["label"], strict=True))
        replay = np.asarray([independent_state(g / 1000) for g in data["g_milli"]])
        assert np.max(np.abs(replay - data["state"])) <= 1e-10
        assert np.array_equal(
            data["state_hash"],
            np.asarray([hashlib.sha256(s.astype("<c16").tobytes()).hexdigest() for s in data["state"]]),
        )
