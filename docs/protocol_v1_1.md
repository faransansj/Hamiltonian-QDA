# Hamiltonian-QDA P1 Protocol v1.1.0

**Status: FROZEN. Scientific experiments executed: 0.**

This protocol incorporates only the randomization amendment in [protocol_amendment_v1_1.md](protocol_amendment_v1_1.md). The complete machine-readable contract is [`configs/protocol_v1_1.yaml`](../configs/protocol_v1_1.yaml), with seeds in [`configs/seed_manifest_v1_1.yaml`](../configs/seed_manifest_v1_1.yaml).

The scientific contract remains Protocol v1.0.0: four-qubit open-boundary TFIM with `J=1`; the frozen integer-grid TRAIN/VALIDATION/TEST splits and labels; C0 real-only, C1 isotropic complex projective-tangent displacement matched to C2, and C2 exact same-label Hamiltonian-manifold states; 50 real states per class, ratio 1.0, 12 disjoint realizations, three QCNN seeds, 108 future runs; the frozen QCNN; and the primary estimand `mean_D(mean_Q(Accuracy(C2)-Accuracy(C1)))`.

C2 still uses at most 128 attempts, uniform sign and uniform float64 step in `[0.005,0.020)`, first valid same-label TRAIN-support candidate, and no fallback. C1 still targets the corresponding C2 FS radius with isotropic complex projective-tangent sampling, `1e-10` rad tolerance, at most 128 attempts, no relaxation, and no fallback.

PASS still requires `Delta_primary >= 0.02` and a strictly positive lower bound of the two-sided 95% realization bootstrap CI. Failure and invalidity rules are unchanged.

Metadata audits and the execution gate are under `results/protocol_v1_1/`. Authorization means only that later P1 materialization may begin; this amendment performs none.
