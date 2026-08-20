import hashlib
import json

import yaml

from hamiltonian_qda.protocol_v1_1 import (
    ROOT,
    arm_payload,
    derive_seed,
    source_assignments,
    state_index,
    valid_g_milli,
)

PARENT_HASH = "ee1219a2188bcc428dcb5331e7444ab686bb71ac4ae6a86e6d8959affe933945"


def test_v1_freeze_is_byte_identical() -> None:
    manifest = json.loads((ROOT / "results/protocol_v1/freeze_manifest_v1.json").read_text())
    for item in manifest["files"]:
        assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert next(x["sha256"] for x in manifest["files"] if x["path"] == "configs/protocol_v1.yaml") == PARENT_HASH


def test_integer_state_identity() -> None:
    grid = valid_g_milli()
    assert len(grid) == 1700
    assert [state_index(g) for g in grid] == list(range(1700))
    assert {100: 0, 949: 849, 1051: 850, 1900: 1699} == {
        g: state_index(g) for g in (100, 949, 1051, 1900)
    }


def test_one_permutation_per_class_is_disjoint_and_train_only() -> None:
    assignments = source_assignments()
    assert assignments == source_assignments()
    assert len(assignments) == 12
    assert all(len(a[0]) == len(a[1]) == 50 for a in assignments)
    realization_sets = [set(a[0] + a[1]) for a in assignments]
    assert all(not realization_sets[i] & realization_sets[j] for i in range(12) for j in range(i))
    assert len(set().union(*(set(a[0]) for a in assignments))) == 600
    assert len(set().union(*(set(a[1]) for a in assignments))) == 600
    train_g = {*range(100, 450), *range(650, 950), *range(1051, 1351), *range(1551, 1901)}
    grid = valid_g_milli()
    assert all(grid[i] in train_g for a in assignments for label in (0, 1) for i in a[label])


def test_seed_vectors_are_exact_and_identity_is_canonical() -> None:
    vectors = json.loads((ROOT / "results/protocol_v1_1/seed_test_vectors.json").read_text())["vectors"]
    expected = [
        ("198b1c08602856f0e9479de4f2c1a17c18c8f3cf805c7b7e47168e71f77aa81f", 33952997729012768767026880753340359036),
        ("98856a636a172c244de5ea8c6d6461fa4e76c7be5e4cc566ab841aff2885ef67", 202735388653331845533942486417103151610),
        ("d96cd68f6259cef28c2dcfd9546bd837a9a4c9b1c815861f1511c62b901cd399", 289007594941769029443424440060746651703),
        ("21f2919a3d34c8af3655332128ac506a955497dc11a889f022f44aeda95ae230", 45124012870139606227963363264215928938),
        ("8c1ac467f565733c1864860fd19c97cd06b15c75548224021c06c9b482890611", 186230902716939655516223118113156929485),
        ("5e528597bae638f8463ce4d0dd05586a6b873a012eb88e89a2dffaa0cb35ee0b", 125375909527954307042237016114968483946),
    ]
    assert [derive_seed(v["payload"]) for v in vectors] == expected
    assert arm_payload("C1", 0, 0, 0) != arm_payload("C2", 0, 0, 0)
    assert arm_payload("C2", 0, 0, 0) != arm_payload("C2", 0, 0, 1)
    assert "tfim4q-obc-j1-gidx" not in arm_payload("C2", 0, 0, 0)


def test_scientific_semantic_diff_is_empty() -> None:
    old = yaml.safe_load((ROOT / "configs/protocol_v1.yaml").read_text())
    new = yaml.safe_load((ROOT / "configs/protocol_v1_1.yaml").read_text())
    for key in ("arms", "budget", "novelty", "validity", "qcnn", "endpoints", "statistics", "leakage", "statuses", "oracle_policy", "stop_go"):
        assert new[key] == old[key]
    for section, allowed in (
        ("source_assignment", {"method", "rng_identity", "canonical_source_identity", "pairwise_realization_disjointness"}),
        ("C1_generator", {"candidate_tangent_sampling"}),
        ("C2_proposal", {"candidate_enumeration", "runtime_information_allowed"}),
        ("provenance_schema", {"required_fields"}),
    ):
        assert {k: v for k, v in new[section].items() if k not in allowed} == {
            k: v for k, v in old[section].items() if k not in allowed
        }


def test_audits_pass_and_configs_have_no_placeholders() -> None:
    semantic = json.loads((ROOT / "results/protocol_v1_1/semantic_diff_audit.json").read_text())
    source = json.loads((ROOT / "results/protocol_v1_1/source_assignment_audit.json").read_text())
    assert semantic["semantic_diff_gate"] == source["status"] == "PASS"
    assert semantic["scientific_semantics_unchanged"] is True
    assert source["maximum_pairwise_realization_overlap"] == 0
    manifest = json.loads((ROOT / "results/protocol_v1_1/freeze_manifest_v1_1.json").read_text())
    assert all(
        hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]
        for item in manifest["files"]
    )
    gate = json.loads((ROOT / "results/protocol_v1_1/execution_gate.json").read_text())
    assert gate["p1_materialization_authorized"] is True
    assert gate["materialization_started"] is False
    assert gate["scientific_experiments_executed"] == 0
    for path in [ROOT / "configs/protocol_v1_1.yaml", ROOT / "configs/seed_manifest_v1_1.yaml"]:
        assert isinstance(yaml.safe_load(path.read_text()), dict)
        assert not any(token in path.read_text() for token in ("TODO", "TBD", "PLACEHOLDER", "???"))
