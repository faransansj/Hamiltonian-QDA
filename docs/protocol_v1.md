# Protocol v1: Frozen P1 Oracle Test

**Status:** FROZEN. **Scientific experiments executed:** 0. The machine-readable authority is [`configs/protocol_v1.yaml`](../configs/protocol_v1.yaml); this document is its human review surface.

## Frozen Question

Under an equal real-data and synthetic-data budget and a frozen QCNN protocol, do exact same-label TFIM ground states sampled along the physical Hamiltonian manifold improve blocked-`g` QCNN generalization relative to a projective-displacement-matched generic tangent perturbation?

## System, Grid, and Labels

The 4-qubit open TFIM is `H(g)=-Σᵢ₌₀² ZᵢZᵢ₊₁-gΣᵢ₌₀³Xᵢ`, with `J=1`, zero-based sites, `q0` as the most-significant tensor factor, `complex128`, and `numpy.linalg.eigh`. The lowest state is accepted only when `E1-E0>1e-10`, normalization error is at most `1e-12`, and residual is at most `1e-10`; its largest-magnitude amplitude (lowest index on ties) is made real and nonnegative.

`g_milli` is the exact config representation. The valid grid is `{100..949}∪{1051..1900}` divided by 1000: 1,700 values at spacing 0.001. Labels are `0` on `[0.100,0.949]`, `1` on `[1.051,1.900]`, and invalid on `[0.950,1.050]` or outside the range.

- Train: `[.100,.449]∪[.650,.949]∪[1.051,1.350]∪[1.551,1.900]` (1,300).
- Validation: `[.450,.499]∪[.600,.649]∪[1.351,1.400]∪[1.501,1.550]` (200).
- Test: `[.500,.599]∪[1.401,1.500]` (200).

Validation buffers give minimum train-to-test separation 0.051. Augmentation runtime receives only the source record, train-support components, label rule, protocol, and seeds—not held-out locations or states.

## Arms and Budget

- **C0 Real-only:** 50 real states per class; no synthetic states.
- **C1 Generic displacement-matched control:** the same 100 sources as C2, one isotropic complex projective-tangent state per source, with source displacement matched to C2 within `1e-10` FS radians.
- **C2 Exact Hamiltonian-Manifold Oracle:** one exact ground state at a continuous same-label train-support target per source.

C1 and C2 each add 100 states (`ratio=1.0`). Twelve disjoint source realizations use 600 of 650 train IDs per class; the 50-ID reserve cannot replace failures. No budget sweep is part of P1.

## C2 Proposal

For each source, attempts 0–127 draw a symmetric sign and a float64 step uniformly from `[0.005,0.020)`, using the source-keyed C2 seed. Accept the first target in the same connected train-support component with unchanged deterministic label, at least `5e-7` from every real grid point and earlier C2 target, and passing exact-solve and duplicate gates. No held-out point is consulted. There is no fallback; exhaustion leaves P1 BLOCKED before training.

Rejected alternatives were nearest-grid resampling (duplicate/acquisition ambiguity), direction toward the blocked interval (leakage/task shaping), FS/QGT-adaptive step selection (P2), and observable/QCNN-ranked selection (post-selection).

## C1 Matching

Measure C2 radius `r=arccos(|⟨ψ|φC2⟩|)`. Draw iid complex Gaussian `z`, project `v=z-ψ⟨ψ|z⟩`, normalize, and construct `φC1=cos(r)ψ+sin(r)v`. Normalize and canonicalize phase. Require `|dFS(C1)-r|≤1e-10`. Attempts 0–127 are source-keyed; no tolerance relaxation or fallback is allowed. C1 is not required to solve the TFIM ground-state equation.

## Novelty and Validity

Canonical hash equality and projective infidelity `≤1e-12` are rejected against real training states and prior same-arm synthetics. Infidelity `≤1e-8` is a reported near-duplicate, not a rejection, because local augmentation would otherwise be selectively censored. Both arms report source and nearest-training distances.

## QCNN and Statistics

The inherited 42-parameter `4→2→1` QCNN, full-batch MSE, SPSA schedules, three paired initialization/optimizer streams, exactly 300 updates, no early stopping, record-only validation, final checkpoint, and `Z3≥0` threshold are frozen in [`configs/qcnn_v1.yaml`](../configs/qcnn_v1.yaml).

The primary contrast is C2−C1. Average three paired seed deltas inside each of 12 realizations, then average realizations. A paired 100,000-draw realization bootstrap with seed 51001 produces the percentile 95% CI. PASS requires `Δ≥0.02` and lower CI `>0`; a valid complete study otherwise FAILS. Integrity violations yield INVALID.

## Oracle Interpretation and STOP/GO

Exact Hamiltonian resampling in P1 is an oracle existence test, not yet a practical scalable augmentation algorithm. If it lacks downstream utility, there is no immediate justification for AGP, QuDDPM, or learned approximations. If it succeeds, a separately preregistered P2 may test geometry-adaptive and approximate physical transport. Neither outcome automatically authorizes another experiment.

Verify: `uv run pytest && python scripts/validate_protocol_v1.py`.
