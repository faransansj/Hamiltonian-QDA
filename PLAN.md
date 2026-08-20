# Gated Research Plan

No phase advances automatically. Each gate requires a reviewed, hashed config and clean repository health checks.

## P0 — Literature and Protocol Formalization

**Goal:** show the question is defensible, sufficiently distinct for a bounded study, and falsifiable.

Outputs: `docs/literature_review.md`, `docs/research_hypothesis.md`, `docs/threats_to_validity.md`, `docs/provenance.md`, and `configs/protocol_v0.yaml`.

Exit gate:

- complete backward/forward citation chaining and terminology search;
- freeze TFIM convention, `g` grid, blocked train/validation/test values, label rule, target proposal, generic control, QCNN, budgets, named seeds, thresholds, and analysis;
- independently audit leakage and state separation;
- set `execution_authorized: true` only in an approved protocol-freeze commit.

No expensive experiment runs in P0.

## P1 — Exact Hamiltonian-Manifold Oracle

**Question:** if extra training states come from the true ground-state manifold, does fixed-QCNN blocked-`g` generalization improve?

```text
g → same-label train-support g' → exact solve H(g') → |ψ₀(g')⟩
```

Run only three arms: real-only, equal-budget generic random state-space control, and exact oracle. Augmentation is train-only. Record state/source IDs, `g/g'`, labels, hashes, seeds, residuals, gaps, config hash, git SHA, environment, and split manifest.

Primary endpoint and PASS rule are frozen in `configs/protocol_v0.yaml`. Exact diagonalization is an oracle, not the proposed scalable method.

**Critical gate:** if P1 does not PASS, stop. Do not proceed to P2–P4, AGP, learned transport, or QuDDPM.

## P2 — Geometry-Adaptive Manifold Augmentation

Run only after P1 PASS. Compare fixed `δg` with FS/QGT-controlled `δg` while both endpoints remain exact states on `M_H`. Geometry selects local displacement; it does not generate arbitrary states. Downstream blocked-parameter accuracy remains the endpoint.

## P3 — Validated Symmetry Augmentation

Run only after proving the frozen task label is invariant under each selected action. Separate Hamiltonian symmetry, state symmetry, dataset closure, label invariance, and model equivariance. Compare manifold-only, symmetry-only, and combined arms.

## P4 — Approximate Physical Transport

Run only after P1 PASS. Approximate `|ψ(g+δg)⟩ ≈ exp(-iδg A_g)|ψ(g)⟩` using one predeclared quasi-adiabatic/AGP family. Compare with exact targets on fidelity, FS distance, residual, observables, downstream utility, and cost. Do not tune against final blocked-test results.

## P5 — Generalization

After a successful TFIM proof of concept, preregister separate studies for larger systems, other Hamiltonians, classifiers, mixed/noisy states, phases, or hardware. No 4-qubit result implies generality.

## Baseline Roadmap

| Arm | First eligible phase |
|---|---|
| Real-only | P1 |
| Generic/random state-space perturbation | P1 |
| Previous physics-aware style | later ablation after P1 |
| Previous geometry-aware style | later ablation after P1 |
| Exact Hamiltonian-manifold oracle | P1 |
| Manifold + geometry control | P2 |
| Manifold + validated symmetry | P3 |
| Approximate physical transport | P4 |

Verify: `uv run pytest && uv run ruff check .`.
