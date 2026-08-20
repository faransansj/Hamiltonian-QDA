from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_protocol_is_proposed_and_execution_is_disabled() -> None:
    protocol = yaml.safe_load((ROOT / "configs/protocol_v0.yaml").read_text())
    assert protocol["protocol"]["status"] == "PROPOSED_FROZEN_FOR_REVIEW"
    assert protocol["protocol"]["execution_authorized"] is False
    assert protocol["augmentation"]["train_only"] is True
    assert protocol["splits"]["final_test_use"] == "once_after_all_protocol_choices"
    assert protocol["stopping"]["p1_stop"].startswith("If the exact manifold oracle does not PASS")


def test_required_research_documents_exist() -> None:
    required = [
        "README.md",
        "PLAN.md",
        "TODO.md",
        "docs/literature_review.md",
        "docs/research_hypothesis.md",
        "docs/threats_to_validity.md",
        "docs/provenance.md",
    ]
    assert all((ROOT / path).is_file() for path in required)
