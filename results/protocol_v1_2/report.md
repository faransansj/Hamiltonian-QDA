# Protocol v1.2.0 Freeze Report

## Gate

**PROTOCOL_V1_2_FROZEN**

**C1_C2_MATERIALIZATION_READY**

Protocol hash: `b6cd7f0e8f239563244a40149aa1e18eb451e4421b8a6cce7c200eff40471761`
Freeze manifest hash: `ffbdd650fca459003ff07043d73fd82b0b3bcb3d7c25313f289183fa0dd936ab`

Protocol v1.2.0 inherits all v1.1 scientific semantics and resolves exactly seven operational determinism omissions. All seven complete contracts are `NEW_OPERATIONAL_DECISION`; recovered v1.1 rules were preserved as constraints. The decisions fix traversal, exact NumPy draw consumption, synthetic identity/path, serialization, checksum/freeze, replay equality, and downstream loading only.

Dry resolution contains exactly 1,200 C2 and 1,200 C1 outputs. IDs, state paths, provenance paths, rows, P1 references, payloads, and seeds are unique and complete. Unresolved fields and unspecified randomness are zero.

Independent review passed after all freeze, loader, provenance, source-attestation, and seed-binding bypasses were closed. No C1/C2 state was materialized. No QCNN, benchmark, downstream metric, or test metric was executed or accessed.
