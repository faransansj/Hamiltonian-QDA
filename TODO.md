# TODO

## P0 blockers — do before P1

- [ ] Complete backward/forward citation chaining and search alternate terms (`parameter interpolation`, `phase-data enrichment`, `Hamiltonian curriculum`, `state preparation`).
- [ ] Resolve and freeze TFIM `g` grid plus train/validation/blocked-test values without final-test model outcomes.
- [ ] Freeze target-`g'` proposal and define whether the access model counts oracle states as augmentation or new data acquisition.
- [ ] Reimplement and verify the minimal generic predecessor-compatible control; record provenance.
- [ ] Reimplement and freeze the QCNN architecture; verify behavior against archived documentation without copying the repository wholesale.
- [ ] Justify `0.02` minimum effect, repeat count, bootstrap unit, and generic-control non-inferiority margin.
- [ ] Freeze residual, gap, duplicate, and near-duplicate thresholds using training-only or analytic evidence.
- [ ] Generate and hash the split manifest; run an independent leakage/projective-separation audit.
- [ ] Add environment capture and config/dataset/provenance manifest utilities only when P1 implementation starts.
- [ ] Review `protocol_v0`; replace every `TO_FREEZE` value, set status `FROZEN`, and authorize execution in a dedicated commit.

## Explicitly deferred

- P1 execution and scientific results
- FS/QGT-adaptive augmentation
- symmetry augmentation
- quasi-adiabatic/AGP transport
- QuDDPM or learned generators
- hyperparameter tuning

Verify: `grep -R 'TO_FREEZE' configs/protocol_v0.yaml` must return no matches before P1 authorization.
