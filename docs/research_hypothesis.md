# Research Hypothesis and P1 Oracle Contract

**Reason for existence:** make P1 falsifiable before code or results can influence its decision rule.

## Primary Hypothesis

For 4-qubit open-boundary TFIM ground states with operational labels `y=0` for `g<1` and `y=1` for `g>1` (`g=1` excluded), train-only exact ground states sampled at nearby, same-label Hamiltonian parameters improve fixed-QCNN blocked-parameter test accuracy under equal real and synthetic budgets.

The primary estimand is the mean paired difference:

```text
blocked-g accuracy(exact manifold oracle) - blocked-g accuracy(real-only)
```

The key control estimand compares the oracle with an equal-budget generic random state-space perturbation arm.

## Why an Oracle First

P1 asks whether useful augmentation exists on the true physical manifold. Exact Hermitian eigendecomposition supplies the target `|ψ₀(g')⟩`; it is not presented as efficient or deployable. If this oracle does not pass, approximating it with AGP, learned transport, or QuDDPM has no justification in this research sequence.

## Operational Label Preservation

A candidate preserves its source label if and only if `g'` remains strictly on the same side of `g=1` as source `g`. Candidates at `g=1`, across the threshold, outside predeclared train support, or at held-out parameter values are rejected.

This is a finite-task operational definition, not a claim that four qubits exhibit a sharp thermodynamic phase transition. Fidelity, FS distance, magnetization, residual, and symmetry sector are diagnostics and cannot override the label rule.

## P1 Arms and Fairness

1. **Real-only.** Frozen real subset.
2. **Generic control.** Minimal predecessor-compatible random state-space perturbation, frozen before execution.
3. **Exact manifold oracle.** `g→g'→H(g')→|ψ₀(g')⟩` with same-label and train-support constraints.

Paired runs share real subsets, QCNN initialization, SPSA seed, update count, and accepted synthetic count. The generic-control implementation, exact `g` grid, blocked values, and QCNN circuit remain explicit P0 freeze items; no execution is authorized while any is unresolved.

## Primary Endpoint and Gate

Primary endpoint: final-checkpoint blocked-parameter test accuracy. P1 passes only if:

- every expected paired run completes and provenance/split audits pass;
- mean oracle-minus-real-only delta is at least `0.02`;
- its predeclared paired-bootstrap 95% CI lower bound is greater than zero; and
- the oracle is not inferior to the generic control under the frozen key comparison.

Otherwise P1 fails or is invalidated by an integrity failure. No outlier removal, failed-run retry, test-driven arm modification, or post-hoc replacement of the primary endpoint is allowed.

## Secondary Endpoints

Macro F1, per-seed delta, descriptive budget dependence, fidelity/FS distance, nearest-training fidelity, duplicate rates, eigensolver residual, energy deviation, magnetization, symmetry-sector consistency, and spectral gap. These explain outcomes; they do not substitute for downstream accuracy.

## Falsifiers

- The oracle gate fails under the frozen complete matrix.
- Gains disappear against equal-budget generic control.
- Gains require crossing the label threshold or using held-out support.
- Split/provenance integrity cannot be demonstrated.
- Results depend on protocol choices selected using final blocked-test outcomes.

## Decision

A P1 PASS permits design of P2; it does not prove the manifold hypothesis generally. A P1 FAIL stops P2–P4 unless a new, independently justified protocol is preregistered as a separate study.

Verify: `uv run pytest tests/test_bootstrap.py`.
