# Protocol v1.1.0 Amendment

## Status and scope

Protocol v1.0.0 remains **FROZEN / MATERIALIZATION BLOCKED**. Its parent protocol SHA-256 is `ee1219a2188bcc428dcb5331e7444ab686bb71ac4ae6a86e6d8959affe933945`. It was blocked because randomization semantics were ambiguous before any scientific execution; scientific runs before amendment: **0**.

Protocol v1.1.0 changes only source-assignment RNG semantics, canonical source-state identity, seed serialization and derivation, and version/provenance. All scientific definitions, constants, budgets, QCNN settings, endpoints, estimands, bootstrap settings, and decision rules remain unchanged.

## Resolutions

For each class, eligible TRAIN states are sorted by ascending canonical `state_index`. Exactly one class-level `PCG64DXSM` permutation is generated, then realization `r` receives positions `50*r:50*(r+1)`. No realization-specific source-assignment stream exists. The root remains `13001`; the class payloads are:

```text
hamiltonian-qda|1.1.0|SOURCE|source_assignment|0|13001
hamiltonian-qda|1.1.0|SOURCE|source_assignment|1|13001
```

The valid integer grid is `range(100,950) + range(1051,1901)`. Ascending values map to `state_index=0..1699`; this integer index is the sole source RNG identity. Display IDs such as `tfim4q-obc-j1-gidx-XXXX` are non-authoritative.

C1/C2 payloads are exactly:

```text
hamiltonian-qda|1.1.0|ARM|PURPOSE|REALIZATION|CLASS|STATE_INDEX|ROOT_SEED
```

SHA-256 is applied to UTF-8 bytes. The seed is the first 16 digest bytes interpreted as unsigned big-endian, and initializes `numpy.random.PCG64DXSM`. C1 purpose is `tangent`; C2 purpose is `proposal`. Attempts consume their frozen stream sequentially; attempt index is not part of the payload.

No quantum state was generated and no QCNN was run by this amendment.
