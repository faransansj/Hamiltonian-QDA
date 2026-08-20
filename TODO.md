# TODO

## Exact Next Action

- [ ] Independently review the frozen artifacts and commit.
- [ ] Before any P1 process starts, rerun `uv sync --locked`, tests, lint, manifest validation, and the execution gate.
- [ ] Implement v1 materialization strictly from the frozen configs without changing scientific choices.
- [ ] Materialize and hash all source assignments and C1/C2 states before QCNN outcomes are available.
- [ ] Re-evaluate the runtime gate; remain BLOCKED if any source, displacement, budget, validity, provenance, or hash assertion fails.
- [ ] Start the complete 108-run matrix only under a clean READY gate and a separate explicit execution request.

## Deferred Unless P1 Passes

- P2 FS/QGT-adaptive augmentation
- P3 symmetry/physics certificates
- P4 AGP or approximate transport
- P5 scaling/generalization
- P6 learned transport or QuDDPM-like generation

Scientific choices unresolved in Protocol v1: **0**.
