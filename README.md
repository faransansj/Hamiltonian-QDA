# Hamiltonian-QDA

Protocol-first research on physical-manifold quantum data augmentation.

## Research Question

Does useful quantum-state data augmentation for QML require transformations aligned with the physical Hamiltonian manifold rather than generic perturbations in Hilbert or projective state space?

## Motivation

For a Hamiltonian family, define the ground-state manifold

\[
\mathcal M_H=\{\lvert\psi_0(\theta)\rangle:\theta\in\Theta\}.
\]

This project tests whether moving a training example through a physically allowed parameter path, rather than perturbing its state vector and checking validity afterward, improves out-of-distribution (OOD) generalization.

## Previous Negative Evidence

[Conditional_QuDDPM](https://github.com/faransansj/Conditional_QuDDPM) is **closed and archived**. It will not be reopened or used as an experiment workspace. Under its frozen 4-qubit open-chain TFIM, fixed-QCNN, q50 local-random-tangent, synthetic-ratio-1.0 Protocol v2.3, all 48 runs completed but the blocked-`g` augmentation-minus-real-only delta was `-0.01806` with 95% CI `[-0.04861, 0.00139]`; the confirmatory verdict was FAIL.

That bounded result motivates this project. It does not prove augmentation is generally harmful, nor that physical-manifold augmentation will work. See [provenance](docs/provenance.md).

## Proposed Hypothesis

**H1:** Under a frozen blocked-parameter protocol and equal data/training budgets, exact ground states sampled along the TFIM Hamiltonian manifold improve blocked-parameter QCNN accuracy over real-only training and a generic state-space control.

P1 is an oracle test of whether useful on-manifold augmentation exists. Exact diagonalization is not claimed as a practical augmentation algorithm. Failure of the oracle gate stops the AGP, learned-transport, and generator sequence.

## Scientific Basis and Related Work

- **Gapped paths — theoretical foundation.** Hastings and Wen's [quasi-adiabatic continuation](https://doi.org/10.1103/PhysRevB.72.045141) constructs quasi-local continuation along suitably gapped local-Hamiltonian paths; later [spectral-flow work](https://doi.org/10.1007/s00220-011-1380-0) sharpens the phase-equivalence framework. This motivates treating connected ground states as a physical transformation family. It does not make continuation a data-augmentation algorithm or cover a path whose relevant gap closes.
- **Quantum geometry — methodological foundation.** The [quantum geometric tensor](https://doi.org/10.1007/BF02193559), [ground-state fidelity](https://doi.org/10.1103/PhysRevE.74.031123), and [fidelity susceptibility](https://doi.org/10.1103/PhysRevLett.99.100603) quantify local state sensitivity and critical behavior. They motivate choosing `δg` to meet a Fubini–Study distance band in P2. They do not guarantee label preservation or downstream benefit.
- **Symmetry-aware QML — related work/methodological precedent.** [Group-invariant QML](https://doi.org/10.1103/PRXQuantum.3.030341) and [equivariant QNNs](https://doi.org/10.1103/PRXQuantum.5.020328) show how known data symmetries can be encoded in models. They motivate a later controlled arm only after label invariance is established. Hamiltonian symmetry, state symmetry, dataset symmetry, label invariance, and model equivariance remain separate claims.
- **Adiabatic gauge potentials — later methodological precedent.** Variational [local counterdiabatic driving](https://doi.org/10.1073/pnas.1619826114) and [nested-commutator constructions](https://doi.org/10.1103/PhysRevLett.123.090602) motivate approximating useful exact transport if P1 passes. They do not establish useful augmentation and are out of scope for P1.
- **Quantum augmentation — baselines/related work.** Existing work includes generative, symmetry-based, noisy-channel, and application-specific augmentation. The audit found no verified paper that clearly establishes the full combination of Hamiltonian-manifold transport, geometry-controlled locality, physical and label validation, and blocked-parameter downstream QML evaluation. This is a search result, not a novelty claim.

The evidence map, search log, exclusions, and scoped interpretation of each reference are in [the literature review](docs/literature_review.md).

## Proposed Pipeline

```text
Real training state → Hamiltonian parameter θ → candidate θ'
→ Hamiltonian-path validity → physical-manifold state
→ FS/QGT locality control → physics checks → label check
→ duplicate/diversity check → accepted synthetic state → downstream QML
```

Components enter only through the gates in [PLAN.md](PLAN.md); they are not implemented together.

## Experimental Roadmap

- **P0:** literature, falsifiable protocol, threats, frozen split and implementation choices.
- **P1:** real-only vs generic control vs exact Hamiltonian-manifold oracle.
- **P2:** fixed parameter steps vs geometry-controlled on-manifold steps, only if P1 passes.
- **P3:** validated symmetry ablations, only after task-level label invariance is proved.
- **P4:** approximate physical transport, only if the exact oracle is useful.
- **P5:** other sizes, Hamiltonians, models, and state types, only after a TFIM proof of concept.

## Repository Structure

```text
src/hamiltonian_qda/{datasets,models,augmentation,geometry,physics,metrics}/
configs/protocol_v0.yaml   # proposed P1 contract; execution disabled
experiments/               # future config-driven entry points
tests/                     # bootstrap contract checks
docs/                      # evidence, hypothesis, threats, provenance
```

## Reproducibility

Every future result must bind a frozen config hash, git SHA, dependency lock, environment, named seeds, dataset and split hashes, source-state IDs, synthetic provenance, and evaluation split. Augmentation is train-only. Final blocked test data cannot select directions, neighbors, thresholds, displacements, models, or generators.

Bootstrap check:

```bash
uv sync --dev && uv run pytest && uv run ruff check .
```

## Scope and Non-Claims

P0 produces no scientific result. P1 does not implement QuDDPM, AGP, symmetry augmentation, geometry-adaptive sampling, learned generation, or hyperparameter tuning. FS locality and physical observables do not establish label preservation. Exact resampling is not assumed cheap. A 4-qubit TFIM result cannot establish generality.
