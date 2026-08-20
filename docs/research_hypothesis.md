# Research Hypothesis and P1 Oracle Contract

**Reason for existence:** make P1 falsifiable before code or results can influence its decision rule.

## Primary Hypothesis

For frozen 4-qubit open-boundary TFIM ground states, train-only exact same-label states sampled on the Hamiltonian manifold improve fixed-QCNN blocked-parameter accuracy over generic projective-tangent states matched by source, count, and Fubini–Study displacement.

The Protocol v1 primary estimand is:

```text
blocked-g accuracy(C2 Exact Hamiltonian-Manifold Oracle)
- blocked-g accuracy(C1 Generic displacement-matched control)
```

The C2−C0 real-only contrast is key secondary evidence and cannot rescue a failed primary contrast.

## Why an Oracle First

P1 asks whether useful augmentation exists on the true physical manifold. Exact Hermitian eigendecomposition supplies the target `|ψ₀(g')⟩`; it is not presented as efficient or deployable. If this oracle does not pass, approximating it with AGP, learned transport, or QuDDPM has no justification in this research sequence.

## Operational Label Preservation

Using integer `g_milli`, `y=0` for `100≤g_milli≤949`, `y=1` for `1051≤g_milli≤1900`, and all other values are invalid. C2 requires exact label equality and membership in the source's connected train-support component.

This is a finite-task operational definition, not a claim that four qubits exhibit a sharp thermodynamic phase transition. Fidelity, FS distance, magnetization, residual, and symmetry sector are diagnostics and cannot override the label rule.

## P1 Arms and Fairness

1. **C0 Real-only.** Frozen 50-per-class real subset.
2. **C1 Generic displacement-matched control.** One source-keyed isotropic projective-tangent state per C2 source.
3. **C2 Exact Hamiltonian-Manifold Oracle.** `g→g'→H(g')→|ψ₀(g')⟩` with frozen same-label train-support proposal.

Paired runs share real subsets, QCNN initialization, SPSA stream, update count, and source ordering. C1 and C2 each add exactly 100 states per realization.

## Primary Endpoint and Gate

Primary endpoint: final-checkpoint blocked-parameter test accuracy. P1 passes only if:

- every expected paired run completes and provenance/split audits pass;
- mean C2-minus-C1 delta is at least `0.02`; and
- its predeclared paired-bootstrap 95% CI lower bound is greater than zero.

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
