# Quadrature rule optimization

## Problem

Numerical integration is the problem of estimating the area accumulated by a
function over an interval. In this result the interval is deliberately simple:
from 0 to 1. The exact quantity is an integral,

$$
I[f] = \int_0^1 f(x)\,dx.
$$

{{visual:exact-integral}}

A quadrature rule approximates that integral by evaluating the function at a
small number of selected points and combining those samples with weights:

$$
Q_r[f] = \sum_{i=1}^{n} w_i f(x_i),
\qquad x_i \in [0,1],
\qquad \sum_i w_i = 1.
$$

{{visual:quadrature-rule}}

The residual error for an integrand is the gap between the analytic integral and
the quadrature estimate:

$$
e_j(r) = \left|Q_r[f_j] - I_j\right|.
$$

{{visual:residual-error}}

This is a useful open result for Göther because the problem is small enough to
inspect, but it still has the properties we care about in larger technical
systems: a bounded search space, a frozen evaluation contract, a replayable
objective, and a final candidate that has to remain legible.

The task is to improve a compact one-dimensional quadrature rule for integrals
on the unit interval against a fixed suite of analytic functions. The target is
not to invent a universal integration method. The target is to show that an
evaluation-driven loop can make a measured, replayable improvement without
changing the problem after seeing candidates.

### Evaluation contract

Every candidate is scored by the same evaluation contract. For each public
integrand \(f_j\), the evaluator compares the candidate estimate against the
analytic integral \(I_j\). The run objective is a lower-is-better aggregate over
those errors:

$$
J(r) = \sum_j \alpha_j \left| Q_r[f_j] - I_j \right|.
$$

This score is the acceptance contract. It is not meant to be the only value a
reader should care about. In the report we therefore show both the contracted
objective and the residual errors for representative integrands. The objective
answers “was the candidate retained under the frozen rule?” The residual errors
answer “what numerical behavior changed?”

## Result

The seed rule started at an objective of 688.676231. The best retained
candidate reached 114.514813, an 83.371749% reduction under the frozen
acceptance contract. That percentage is not the headline scientific claim. The
more interpretable readout is the residual error profile: the largest
representative residual drops from 0.36338 in the seed to 0.001029 in the
accepted five-node rule.

The accepted change keeps the implementation intentionally small. It starts
from Gauss-Legendre nodes, applies a deterministic inward remapping, maps the
nodes back to the unit interval, and renormalizes the rule:

```python
nodes, weights = np.polynomial.legendre.leggauss(n)

alpha = 1.7
nodes = np.sign(nodes) * (np.abs(nodes) ** alpha)

mapped_nodes = 0.5 * (nodes + 1.0)
mapped_weights = 0.5 * weights

rule = QuadratureRule(
    nodes=list(mapped_nodes),
    weights=list(mapped_weights),
)

return _renormalize(rule)
```

The exponent \( \alpha = 1.7 \) compresses the Legendre nodes toward the
midpoint before the rule is mapped from \([-1,1]\) to \([0,1]\). In this
contract, that changed the error distribution enough to improve the retained
objective while preserving a rule an engineer can read, replay, and compare.

### What changed

The final candidate moves away from a degenerate seed toward a smooth,
near-uniform weight distribution with endpoint-aware node placement. The public
trace keeps a curated sequence of retained states so the improvement path can be
inspected without exposing prompts, private run records, or uncurated proposal
dumps.

The most important distinction is that the trace can contain candidates that are
interesting for the run history without being the final best candidate. The
reported best objective is the best-so-far value under the frozen contract.
That is the number that should be compared to the seed.

### Limitations

This is a bounded numerical benchmark, not a universal integration method. The
result should be interpreted against the frozen integrand suite and evaluation
contract included with this bundle. It does not prove superiority on arbitrary
integrands, discontinuous functions, high-dimensional integrals, or production
workloads with different stability requirements.

The score is also intentionally narrow. A lower objective is evidence that the
candidate improved under this contract, not a claim that every downstream
quantity of interest improved. For a real client setting, the contract would
include the operational metrics that matter for that system.

## Reproducibility

The bundle includes the accepted candidate, the evaluation contract, metrics, a
sanitized evolution trace, and provenance. Replaying the result should use the
same contract and objective direction: lower is better.

The public source bundle lives in
[Göther Labs Open Results](https://github.com/Gother-Labs/gother-labs-open-results/tree/main/results/quadrature-rule-optimization).

The public artifact is designed to be reviewable in layers: start with the
problem and contract, inspect the objective curve, inspect the accepted rule, and
then read the candidate implementation. Nothing in the website should be treated
as a substitute for the replayable artifacts.
