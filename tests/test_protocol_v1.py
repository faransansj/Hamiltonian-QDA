import json

import yaml

from hamiltonian_qda.protocol import (
    ROOT,
    expand_intervals,
    label_g_milli,
    scientific_verdict,
    unresolved_placeholders,
    verify_freeze_manifest,
)


def load_yaml(path: str) -> dict:
    return yaml.safe_load((ROOT / path).read_text())


def test_no_unresolved_placeholders() -> None:
    assert unresolved_placeholders() == []


def test_tfim_contract_is_complete() -> None:
    tfim = load_yaml("configs/tfim_v1.yaml")
    assert tfim["qubits"] == 4
    assert tfim["boundary"] == "open"
    assert tfim["coupling_J"] == 1.0
    assert tfim["sites"]["indexing"] == "zero_based"
    assert tfim["basis"]["qubit_0_significance"] == "most_significant"
    assert tfim["numerics"]["matrix_dtype"] == "complex128"
    assert tfim["numerics"]["eigensolver"] == "numpy.linalg.eigh"
    assert tfim["global_phase"]["pivot_tie_break"] == "smallest_vector_index"


def test_grid_sets_are_complete_and_disjoint() -> None:
    split = load_yaml("configs/split_manifest_v1.yaml")
    grid = expand_intervals(split["complete_grid"]["valid_intervals_inclusive"])
    train = expand_intervals(split["sets"]["train_intervals_inclusive"])
    val = expand_intervals(split["sets"]["validation_intervals_inclusive"])
    test = expand_intervals(split["sets"]["test_intervals_inclusive"])
    assert not train & val
    assert not train & test
    assert not val & test
    assert train | val | test == grid
    assert (len(grid), len(train), len(val), len(test)) == (1700, 1300, 200, 200)
    assert min(abs(a - b) for a in train for b in test) == 51


def test_critical_exclusion_and_labels() -> None:
    assert label_g_milli(949) == 0
    assert label_g_milli(950) is None
    assert label_g_milli(1000) is None
    assert label_g_milli(1050) is None
    assert label_g_milli(1051) == 1


def test_c2_is_same_label_and_cannot_access_held_out_information() -> None:
    protocol = load_yaml("configs/protocol_v1.yaml")
    c2 = protocol["C2_proposal"]
    assert "target_label_equals_source_label" in c2["acceptance"]
    assert c2["same_label_rejection"] == "mandatory"
    assert c2["runtime_information_allowed"] == [
        "source_state_id",
        "source_g",
        "source_label",
        "train_support_components",
        "protocol_config",
        "seed_manifest",
    ]
    assert {"validation_g_values", "test_g_values", "validation_states", "test_states"} <= set(
        c2["runtime_information_forbidden"]
    )
    assert c2["fallback"] == "none_BLOCKED_after_attempt_127"


def test_c1_c2_pairing_matching_and_budget_are_exact() -> None:
    protocol = load_yaml("configs/protocol_v1.yaml")
    assert protocol["source_assignment"]["C1_C2_pairing"] == "exact_ordered_ID_equality_required"
    assert protocol["C1_generator"]["source_pairing"] == "exact_C2_source_ID_and_order"
    assert protocol["C1_generator"]["epsilon_FS_radians"] == 1e-10
    assert "absolute_FS_matching_error_at_most_1e-10_radians" in protocol["C1_generator"]["acceptance"]
    assert protocol["budget"]["synthetic_ratio_C1_C2"] == 1.0
    assert protocol["budget"]["total_synthetic_count_per_C1_or_C2_realization"] == 100
    assert protocol["arms"]["C1"]["synthetic_per_source"] == protocol["arms"]["C2"]["synthetic_per_source"] == 1


def test_seed_manifest_is_complete() -> None:
    seeds = load_yaml("configs/seed_manifest_v1.yaml")
    expected = {
        "dataset_generation",
        "split_construction",
        "source_assignment",
        "c1_generic_perturbation",
        "c2_target_proposal",
        "bootstrap",
    }
    assert expected == set(seeds["base_seeds"])
    assert len(seeds["qcnn"]["initialization_seeds"]) == 3
    assert len(seeds["qcnn"]["optimizer_seeds"]) == 3
    assert seeds["realizations"]["count"] == 12


def test_qcnn_contract_is_complete() -> None:
    qcnn = load_yaml("configs/qcnn_v1.yaml")
    assert qcnn["architecture"]["parameter_count"] == 42
    assert qcnn["architecture"]["reduction"] == "4 -> 2 -> 1"
    assert qcnn["readout"] == {
        "qubit": 3,
        "operator": "Z",
        "prediction": "class 1 iff expectation_Z3 >= 0; otherwise class 0",
    }
    assert qcnn["training"]["optimizer"] == "SPSA"
    assert qcnn["training"]["parameter_updates"] == 300
    assert qcnn["training"]["early_stopping"] is False
    assert qcnn["training"]["checkpoint"] == "final_after_update_300"
    assert qcnn["training"]["validation_may_select_checkpoint"] is False


def test_primary_estimand_and_verdict_are_fixed() -> None:
    protocol = load_yaml("configs/protocol_v1.yaml")
    assert protocol["endpoints"]["primary_contrast_exact"] == "C2_minus_C1"
    assert protocol["statistics"]["minimum_meaningful_effect"] == 0.02
    assert scientific_verdict(True, 0.019, 0.01) == "FAIL"
    assert scientific_verdict(True, 0.030, -0.010) == "FAIL"
    assert scientific_verdict(True, 0.025, 0.004) == "PASS"
    assert scientific_verdict(False, 0.025, 0.004) == "INVALID"


def test_gate_is_ready_and_consistent() -> None:
    gate = json.loads((ROOT / "results/protocol_v1/p1_execution_gate.json").read_text())
    booleans = [value for key, value in gate.items() if key.endswith(("_frozen", "_ready"))]
    assert all(booleans)
    assert gate["protocol_frozen"] is True
    assert gate["unresolved_scientific_choices"] == 0
    assert gate["freeze_manifest_valid"] is True
    assert gate["p1_execution_authorized"] is True
    assert gate["status"] == "READY"
    assert gate["scientific_experiments_executed"] == 0


def test_freeze_manifest_verifies() -> None:
    assert verify_freeze_manifest()
