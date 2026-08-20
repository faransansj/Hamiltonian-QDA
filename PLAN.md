# Gated Research Plan

Protocol v1 is frozen and P1 is READY, but this repository contains no scientific P1 execution or result.

## P0 — Complete

Literature, hypothesis, threats, provenance, exact TFIM/grid/splits, C1/C2 generators, QCNN instrument, seeds, statistics, validity gates, and freeze hashes are preregistered. Any material P1 change requires Protocol v2.

## P1 — Exact Hamiltonian-Manifold Oracle

Run only C0 Real-only, C1 Generic displacement-matched control, and C2 Exact Hamiltonian-Manifold Oracle. Use 12 disjoint 50-per-class source realizations, one synthetic per source for C1/C2, three paired QCNN seed streams, and the fixed 300-update instrument. The primary endpoint is blocked-`g` accuracy and the primary contrast is C2−C1.

PASS requires valid complete execution, mean delta at least `0.02`, and paired realization-bootstrap 95% CI lower bound greater than zero. Valid completion that misses either condition is FAIL. Integrity violations are INVALID. Pre-execution infeasibility is BLOCKED.

**FAIL:** freeze the negative result, verify integrity, allow bounded diagnostics, and stop. A new scientific experiment requires a new protocol.

**PASS:** a future P2 may be preregistered; it is not automatically authorized.

## Future Roadmap — Descriptive Only

- **P2:** fixed Hamiltonian displacement vs FS/QGT-adaptive on-manifold displacement.
- **P3:** validated physics/symmetry certificates and ablations.
- **P4:** approximate physical transport/AGP against exact targets.
- **P5:** larger systems, other Hamiltonians/models, noisy or mixed states.
- **P6:** learned physical transport or QuDDPM-like generator.

No phase may use the best P1 examples to set future thresholds.

Verify: `uv run pytest && python scripts/validate_protocol_v1.py`.
