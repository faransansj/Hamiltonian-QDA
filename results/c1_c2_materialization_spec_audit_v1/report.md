# C1/C2 Materialization Contract Audit v1

## Decision

**PROTOCOL_REVISION_REQUIRED** — materialization is forbidden.

Frozen Protocol v1.1.0 and all P1 anchors passed byte-integrity and source-assignment checks. C1/C2 purposes, source binding, seed domains, retry limits, tolerances, duplicate rules, and failure semantics were recovered without executing either arm.

The contract is not operationally complete. Items 4, 5, 9, 17, 18, 19, 20, and 22 are MISSING. Exact cross-class candidate traversal matters because duplicate checks include prior accepted synthetics. Exact NumPy sampling calls and scalar/vector/component draw order are also absent; distributions and PCG64DXSM alone do not fix consumed bits. Canonical synthetic IDs/paths, serialized layout, freeze/checksum schema, replay criterion, and downstream handoff are likewise absent. All 2,400 logical outputs resolve to frozen sources and per-source seed payloads, but not to executable candidates or unique artifact identities without hidden defaults.

## Semantic preservation

The v1.1 amendment is limited to source assignment, canonical source identity, seed serialization/derivation, and provenance. C1, C2, and other scientific semantics are unchanged. Completeness gaps are omissions, not semantic conflicts.

## Independent review

Independent review returned FAIL while agreeing that `PROTOCOL_REVISION_REQUIRED` is the consistent gate. Its RNG draw-mapping, traversal-order, and minimum-revision findings are incorporated here.

## Minimum revision

1. Freeze cross-class/source candidate traversal order.
2. Freeze exact NumPy sampling APIs, arguments, and per-attempt draw/component consumption order.
3. Freeze synthetic IDs, directories/filenames, and serialized array/layout schema.
4. Freeze manifest/checksum/serialization and deterministic replay comparison rules.
5. Freeze downstream dataset ordering/layout/loader contract.

No C1/C2 state, QCNN run, downstream metric, or test metric was produced or accessed.
