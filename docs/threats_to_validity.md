# Threats to Validity

**Reason for existence:** predeclare conditions that can invalidate or narrow P1 before outcomes are known.

## Internal Validity

| Threat | Control |
|---|---|
| Validation/test leakage into augmentation | Construct candidates only from frozen training IDs/support; fail closed on held-out IDs or `g` values. |
| Projective near-duplicates across splits | Audit canonical hashes, fidelity/FS nearest neighbors, and split manifests before training. |
| Unequal arm budgets | Match accepted synthetic count, real subset, updates, and paired RNG domains. |
| Test-driven protocol selection | Freeze grid, split, thresholds, baseline, architecture, and analysis before final-test access. |
| Eigensolver branch/degeneracy errors | Record residual and gap; reject below frozen gap tolerance or failed residual gate. |
| Hidden stochastic differences | Use named RNG domains and record every seed; pair initialization and optimizer seeds. |
| Selective failed-run handling | No retry for scientific failures; incomplete matrix fails the gate. |
| Baseline mismatch | Reimplement only the minimal documented control and validate it independently; record any divergence from predecessor behavior. |

## Construct Validity

- “Physical manifold” means exact ground states of the declared finite TFIM family, not every physically realizable state.
- The `g<1`/`g>1` label is an operational finite-size benchmark label, not proof of thermodynamic phase membership.
- FS locality measures projective proximity, not semantic label preservation.
- Low energy/residual and preserved observables measure physical consistency, not downstream usefulness.
- Exact resampling can be interpreted as additional data acquisition rather than augmentation. P1 must state the assumed access model and include equal-budget acquisition/cost discussion.
- Blocked-parameter accuracy measures interpolation/extrapolation over the selected grid, not universal OOD generalization.

## External Validity

Four qubits, one open-boundary TFIM convention, one QCNN, noiseless pure ground states, and one blocked split cannot support claims about larger systems, other Hamiltonians, mixed/noisy states, hardware, or other models. P5 requires independent protocols.

## Statistical Conclusion Validity

Three repeats and four budgets may give unstable intervals and induce budget multiplicity. Only the aggregated paired endpoint is confirmatory; budget and seed breakdowns are descriptive. A fixed `0.02` minimum effect inherits precedent but still requires scientific justification before freeze. Bootstrap assumptions and the number of independent units must be audited; synthetic samples derived from one source are not independent replicates.

## Theoretical Validity

Quasi-adiabatic arguments require regular, suitably gapped paths. Near the critical region, finite-size gaps can narrow and geometric sensitivity can rise. P1 uses exact endpoint solves and makes no claim of implemented adiabatic evolution. P4 cannot inherit validity from P1 without transport-error comparisons.

## Researcher Degrees of Freedom

Unfrozen choices currently block execution: parameter grid and held-out values, target proposal, generic control, QCNN architecture, validation role, gap/residual thresholds, and the non-inferiority margin for the key control comparison. Resolve them without blocked-test outcomes, hash the protocol, then change status from proposed to frozen in a dedicated review commit.

## Stop Conditions

Any held-out data access during augmentation design, unresolved provenance, split overlap, incomplete paired matrix, or numerical-gate failure invalidates P1. An oracle scientific FAIL stops AGP, learned transport, and QuDDPM work in this sequence.

Verify: `grep -q 'Researcher Degrees of Freedom' docs/threats_to_validity.md`.
