# Provenance

**Reason for existence:** separate prior evidence from new work and make any future adaptation auditable.

## Prior Repository

- Repository: [faransansj/Conditional_QuDDPM](https://github.com/faransansj/Conditional_QuDDPM)
- Status: **closed/archived research track; do not modify or execute new studies there**
- Inspected upstream `main`: `72c536a7d846f623d441f4fa4f0b21452db2487f`
- Authoritative archived result: [`docs/tfim_state_augmentation_final_archive.md` at result-freeze commit `1e3ac703...`](https://github.com/faransansj/Conditional_QuDDPM/blob/1e3ac703ff34444de473b6ecf2e5b8641c73213b/docs/tfim_state_augmentation_final_archive.md)
- Protocol/result details reused as prior evidence: 4-qubit open-chain TFIM, fixed QCNN, q50 local-random-tangent, ratio 1.0, 48/48 runs, paired delta and CI, 300 SPSA updates, `{10,25,50,100}` budgets, three repeats, pairing and bootstrap conventions.

## Code Reuse

No source code, datasets, generated states, result files, or model weights were copied in this bootstrap. Package files are clean scaffolding. The protocol wording adapts high-level controls from the archived report and inspected YAML, not implementation code.

Any future copied or adapted component must append a row before merge:

| Source repository | Commit | Source path | Destination | Adaptation | Validation |
|---|---|---|---|---|---|
| _none_ | — | — | — | — | — |

Candidate minimal adaptations, only after review: TFIM matrix convention, frozen QCNN architecture, generic-control baseline, split audit, and metrics. Prefer clean reimplementation and behavior-level comparison.

## New Repository

- Repository: `Hamiltonian-QDA`
- Remote: `https://github.com/faransansj/Hamiltonian-QDA.git`
- Initial state: empty Git repository on `main`, no commits.
- Bootstrap scope: literature/protocol documents, package directories, config contract, dependency lock, and lightweight checks only.
- Scientific data generated: none.

Verify: `git log --oneline --decorate -1 && git status --short`.
