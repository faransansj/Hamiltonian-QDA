# Protocol v1.2.0 Operational Determinism Amendment

## Scope

Protocol v1.2.0 inherits Protocol v1.1.0 byte-for-byte as its complete scientific contract. It changes no transformation, distribution, source, count, seed domain, numerical acceptance parameter, hypothesis, endpoint, statistic, or decision rule. It resolves exactly seven operational omissions found by the frozen C1/C2 audit.

`scientific_semantics_changed = false`; `operational_determinism_completed = true`. No C1/C2 state, QCNN run, scientific benchmark, or test metric was produced or accessed.

## Recovery and decisions

Repository search recovered the C2-before-C1 dependency, P1 list order, seed payloads, PCG64DXSM, retry limits, state dtype/shape, provenance fields, and fail-closed semantics. None of the seven complete operational rules existed, so each is a `NEW_OPERATIONAL_DECISION`:

| Missing contract | Necessary rule | Alternatives | Scientific neutrality |
|---|---|---|---|
| Total traversal | C2 then C1; D00..D11; class 0 then 1; frozen source positions 0..49; attempts 0..127 | C1 first or interleaved; reversed classes | C2 must precede its dependent C1 radius; remaining order only fixes prior-synthetic processing. |
| Exact RNG calls | Scalar `integers` then `uniform` for C2; 16 `normal` real then 16 `normal` imaginary values for C1 | `choice`, vectorized calls, interleaving components | Preserves every frozen distribution and seed while fixing bit consumption. |
| Synthetic identity/path | Fixed grammar and repository-relative per-output paths | Aggregate or machine-specific paths | Representation only. |
| Serialization | One NPY 1.0 `<c16[16]` plus canonical JSON provenance per output | NPZ or aggregate arrays | Representation only. |
| Checksums/freeze | SHA-256 non-recursive manifest over all state, provenance, and materialization-manifest files | Self-hashing or partial coverage | Integrity only. |
| Replay equality | Exact metadata/bytes; state numerical comparison at inherited `1e-10` residual scale | Loose tolerance or byte-only independent eigensolver comparison | Does not relax any generation acceptance rule. |
| Downstream loader | Manifest-only discovery, canonical order, fail closed on every mismatch | Filesystem globbing or permissive loading | Handoff only; evaluation semantics unchanged. |

The exact normative contracts are the files referenced by `configs/protocol_v1_2.yaml`. If prose conflicts with those machine-readable files, materialization is BLOCKED and a new protocol revision is required.
