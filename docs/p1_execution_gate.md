# P1 Execution Gate

The authoritative gate is [`results/protocol_v1/p1_execution_gate.json`](../results/protocol_v1/p1_execution_gate.json). READY permits—but does not execute—P1.

## Status Definitions

- **READY:** protocol and execution-integrity prerequisites permit P1 to start.
- **BLOCKED:** a required pre-execution condition is missing or candidate generation cannot satisfy the frozen contract.
- **PASS:** valid completed P1 has `Δ(C2−C1)≥0.02` and lower paired-bootstrap 95% bound greater than zero.
- **FAIL:** valid completed P1 does not satisfy both PASS conditions.
- **INVALID:** execution occurred, but leakage, pairing, provenance, hash, missing-run, or other protocol violations prevent scientific interpretation.

Execution failures are never scientific FAILs. Before launch, rerun the manifest, placeholder, YAML/JSON, split, pairing-contract, leakage-contract, and gate-consistency tests. Runtime materialization must additionally prove 12 disjoint 50-per-class source sets, exact C1/C2 source ordering, 100 accepted synthetics per augmented arm/realization, FS matching, state validity, and frozen hashes. Failure leaves the gate BLOCKED; changing v1 requires v2.

Current gate: **READY**. Scientific experiments executed: **0**.

Verify: `python scripts/validate_protocol_v1.py`.
