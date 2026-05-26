# 26-circle unit-square packing

[Published web article](https://www.gotherlabs.com/results/circle-packing-26-unit-square/) · [Animated run surface](https://www.gotherlabs.com/results/circle-packing-26-unit-square/run/) · [Structured metadata](result.json) · [Evaluation contract](artifacts/evaluation_contract.md) · [Accepted candidate](artifacts/accepted_candidate.py)

## Abstract

This result reports a deterministic packing of 26 non-overlapping circles inside
the unit square. The accepted geometry reaches a validated total radius of
2.635983, starting from a sparse public baseline at 0.959778. Because the
evaluator score is the negative total radius, the governed lower-is-better score
moves from -0.959778 to -2.635983.

The claim is deliberately bounded: this is not a proof of global optimality and
not a general circle-packing solver. It is a public, replayable geometry result
with three audit surfaces: the accepted candidate code, the frozen validation
contract, and the scored public trace and seeded continuation that led to the retained packing.

The result is also close to the strongest public AI-discovery references listed
in the comparison artifact. It matches the strongest exact public values in the
tracked papers at six displayed decimals. Some newer benchmark pages report
2.636 at three-decimal precision, so this bundle treats world ranking as
unresolved unless those entries publish replayable full-precision geometries.

## 1. Problem formulation

The task is to place 26 circles in the unit square without overlap. A packing is
defined by centers \((x_i, y_i)\) and radii \(r_i\) for
\(i = 1, \dots, 26\). The geometric objective is the total radius:

$$
R(P) = \sum_{i=1}^{26} r_i
$$

Every circle must remain inside \([0,1]^2\), and every pair of circles must
satisfy the non-overlap constraint:

$$
\sqrt{(x_i-x_j)^2 + (y_i-y_j)^2} \ge r_i + r_j.
$$

![Accepted 26-circle packing](assets/packing-layout.svg)

## 2. Evaluation contract

The evaluator asks the candidate for exactly 26 centers, 26 positive radii, and
a reported sum. It rejects non-finite values, mismatched reported sums,
unit-square boundary violations, pairwise overlaps, and non-deterministic
repeat calls.

See [evaluation_contract.md](artifacts/evaluation_contract.md).

The score is:

$$
J(P) = -R(P).
$$

Lower score is therefore better under the evaluator, while total radius remains
the direct geometric readout.

## 3. Accepted candidate

The accepted public candidate is a deterministic reconstruction program rather
than only a stored coordinate table. It starts from a coarse deterministic seed,
solves boundary and pairwise tangency equations with a damped Newton system,
checks the solve against the retained accepted continuation trace, and validates
the geometry before returning it to the evaluator.

See [accepted_candidate.py](artifacts/accepted_candidate.py).

This distinction matters for review. The replayed centers and radii are retained
as audit evidence, but the implementation surface is the reconstruction code
that regenerates the accepted contact graph.

## 4. Result summary

| Readout | Value |
| --- | ---: |
| Baseline total radius | 0.959778 |
| Accepted total radius | 2.635983 |
| Total-radius gain | 1.676205 |
| Evaluator score change | -0.959778 to -2.635983 |
| Boundary contacts detected | 20 |
| Pairwise contacts detected | 58 |
| Interior circles | 10 |
| Minimum radius | 0.069181 |
| Maximum radius | 0.137010 |

The public trajectory has three visible phases. The original `program.py`
baseline is a sparse packing with total radius 0.959778. Early generated
candidates move quickly into useful geometries: the first valid candidate
reaches 1.064234, and generation 1 later produces the retained 2.438966
checkpoint. Later candidates mostly explore the high-radius plateau until the previous
accepted reconstruction reaches 2.635977. A seeded continuation from that
geometry then reaches the updated accepted total radius 2.635983.

![Best-so-far total radius curve](assets/objective-curve.svg)

See [metrics.json](artifacts/metrics.json) and
[score-trace.json](artifacts/score-trace.json).

The accepted packing is tight in the sense exposed by the public diagnostics:
20 boundary contacts and 58 pairwise contacts are detected at the public
tolerance. The smallest boundary and pairwise slacks are near machine precision,
so the contact readout is a structural check on the geometry rather than a
separate optimization claim.

![Boundary and pairwise contact diagnostics](assets/contact-readout.svg)

## 5. Public standing

The comparison artifact records the strongest public reference values used for
context:

| Reference | Public precision | Status versus this result |
| --- | ---: | --- |
| AlphaEvolve V2 | 2.635983 | Equal at six displayed decimals |
| ThetaEvolve | 2.635983 | Equal at six displayed decimals |
| TTT-Discover | 2.635983 | Equal at six displayed decimals |
| LoongFlow | 2.636 | Rounded third-party benchmark entry; exact rank unresolved |
| SkyDiscover | 2.636 | Rounded third-party benchmark entry; exact rank unresolved |
| ASI-Evolve | 2.636 | Rounded third-party benchmark entry; exact rank unresolved |

The accepted Göther Labs geometry reaches 2.6359830849768984. It is above
2.635983 when compared to six-decimal published values at full precision, but
that does not prove a strict rank above systems whose public entries are rounded
to 2.636 or whose full coordinates are not available here.

See [reference-comparison.json](artifacts/reference-comparison.json). The
six-decimal values are taken from the circle-packing table in
[Learning to Discover at Test Time](https://test-time-training.github.io/discover.pdf);
the rounded 2.636 entries are recorded as unresolved leaderboard context.

## 6. Limitations

This is a result for the 26-circle unit-square packing contract only. It does
not claim a general solver for other circle counts, other containers, changed
objectives, or arbitrary contact graphs. Changing any of those terms creates a
new evaluation.

The external comparison is contextual rather than a leaderboard claim. It uses
the values reported in cited public sources and does not independently rerun
those systems under this repository's evaluator.

The accepted candidate is deterministic and reconstructs this validated contact
graph. Its purpose is auditability of this geometry, not broad instance
generation.

## 7. Reproducibility

The public bundle includes the accepted candidate, evaluation contract, curated original-plus-continuation
evolution chain, scored-candidate trace, metrics, provenance, replay
confirmation, figures, and the public
[animated run surface](https://www.gotherlabs.com/results/circle-packing-26-unit-square/run/).
The run page is a presentation layer over the same public artifacts and excludes
raw operational material.

Useful entry points:

- [accepted_candidate.py](artifacts/accepted_candidate.py): deterministic
  reconstruction code
- [evaluation_contract.md](artifacts/evaluation_contract.md): frozen validator
  behavior
- [replay.json](artifacts/replay.json): accepted replay and geometry trace
- [metrics.json](artifacts/metrics.json): headline numerical readouts
- [score-trace.json](artifacts/score-trace.json): public scored-candidate trace
- [reference-comparison.json](artifacts/reference-comparison.json): external
  comparison values

The source bundle is available in the
[Göther Labs results repository](https://github.com/Gother-Labs/gother-labs-results/tree/main/results/circle-packing-26-unit-square).
