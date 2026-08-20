# Statistical Plan v1

**Status:** FROZEN. This document defines P1 inference; Protocol v2 is required to change it.

## Endpoint and Estimands

The sole primary endpoint is final-update-300 blocked-`g` test accuracy. The primary estimand is

```text
Δprimary = mean_D(mean_Q(accuracy(C2) - accuracy(C1)))
```

where `D` indexes 12 disjoint real-source dataset realizations and `Q` indexes three paired QCNN seed streams. The key secondary estimand replaces C1 with C0. Macro-F1, individual seeds, state metrics, and observables are diagnostic only.

## Experimental Units and Dependence

The outer inferential cluster is the dataset realization. A frozen classwise permutation assigns 50 unique source IDs per class to each realization; source IDs never cross realizations. Within each realization, three QCNN seeds are repeated stochastic measurements, not independent datasets. Arms share source data, initialization, optimizer stream, test set, and schedule within each `(dataset_realization_id, qcnn_seed_index)` pairing key. Synthetic states are derived observations and never inferential replicates.

The 12 source clusters form a disjoint finite-population partition, not 12 draws from an unlimited population. All realizations share one fixed blocked test grid. Inference is therefore conditional on this grid, model, source partition, and seed manifest. Bootstrap replication does not enlarge the evidence base.

Expected matrix: `12 realizations × 3 QCNN seeds × 3 arms = 108` arm runs and 36 complete paired keys.

## Aggregation

For each realization and QCNN seed, calculate the paired C2−C1 accuracy difference. Average the three seed differences within each realization. The point estimate is the unweighted arithmetic mean of the 12 realization means. Use float64 values without intermediate rounding. Apply the same order to C2−C0.

## Confidence Interval

Use `numpy.random.Generator(PCG64DXSM(51001))`. For each of exactly 100,000 replicates, sample 12 realization indices with replacement, carry each selected realization's already seed-averaged paired delta, and compute its unweighted mean. Do not resample arms, QCNN seeds, test examples, source states, or synthetic states independently. The two-sided 95% percentile interval is `numpy.quantile(replicates, [0.025, 0.975], method="linear")`. Use unrounded float64 bounds for decisions.

## Decision Rule

After integrity validation:

```text
PASS iff Δprimary >= 0.02 and lower_95_percent_CI > 0.0
FAIL otherwise
```

Thus `0.019` fails; `0.030` with interval `[-0.010, 0.060]` fails; `0.025` with interval `[0.004, 0.048]` passes. C2−C0 cannot rescue a failed primary contrast.

An incomplete pairing key, nonfinite endpoint, selective retry, replacement seed, outlier removal, hash mismatch, leakage, or protocol violation yields INVALID—not FAIL—and no scientific verdict. A pre-execution feasibility failure yields BLOCKED.

## Minimum Effect Rationale

The `0.02` absolute-accuracy threshold is retained from v0 and the predecessor's confirmatory decision scale. It prevents a precise but negligible positive difference from passing and avoids an outcome-dependent revision. It is not a universal clinical or physical threshold.

Verify: `uv run pytest tests/test_protocol_v1.py`.
