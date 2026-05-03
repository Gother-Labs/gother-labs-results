# Quadrature rule optimization

## Abstract

This note reports a compact five-node quadrature rule for one-dimensional
integrals on the unit interval. The rule is evaluated against a frozen suite of
analytic integrands, and every reported improvement is measured under the same
lower-is-better acceptance objective. The accepted candidate reduces the
contracted objective from 688.676231 to 114.514813, while the largest public
representative residual is reduced from 0.36338 to 0.001029.

The result should be read as a bounded optimization artifact, not as a universal
integration method. The purpose of the report is to make the problem, contract,
candidate, metrics, and replay surface inspectable in one place.

## 1. Problem formulation

Let \(f_j\) denote an analytic test integrand on the unit interval. The exact
quantity of interest is the integral

$$
I[f] = \int_0^1 f(x)\,dx.
$$

{{visual:exact-integral}}

A quadrature rule \(r\) approximates this quantity by evaluating the integrand at
a finite set of nodes and combining those evaluations with normalized weights:

$$
Q_r[f] = \sum_{i=1}^{n} w_i f(x_i),
\qquad x_i \in [0,1],
\qquad \sum_i w_i = 1.
$$

{{visual:quadrature-rule}}

For each public integrand, the observable residual is the absolute difference
between the quadrature estimate and the analytic reference value:

$$
e_j(r) = \left|Q_r[f_j] - I_j\right|.
$$

{{visual:residual-error}}

The notation used throughout the report is summarized below.

{{visual:notation-table}}

## 2. Evaluation contract

The evaluation contract is fixed before candidate comparison. Each candidate
rule is scored on the same public analytic integrand suite, with the same
objective direction and the same aggregation rule. The run objective is

$$
J(r) = \sum_j \alpha_j \left| Q_r[f_j] - I_j \right|.
$$

Lower values of \(J(r)\) are preferred. This objective is the acceptance score
used to retain candidates during the run. It is not a general-purpose measure of
integration quality, so the report also exposes residual errors for
representative integrands.

## 3. Accepted candidate

The accepted rule keeps five nodes on \([0,1]\) with near-uniform normalized
weights. The implementation starts from Gauss-Legendre nodes, applies a
deterministic inward remapping with exponent \(\alpha=1.7\), maps the nodes back
to the unit interval, and renormalizes the resulting rule.

{{visual:accepted-rule-figure}}

{{visual:accepted-rule-table}}

## 4. Results

The primary reported improvement is the reduction in the frozen acceptance
objective. The result should be interpreted together with the residual readout,
because the score answers whether the candidate was retained under the contract,
while the residuals show the observable numerical behavior.

{{visual:objective-summary-table}}

{{visual:residual-error-table}}

{{visual:objective-curve}}

{{visual:candidate-trace}}

## 5. Limitations

This is a bounded benchmark on a fixed analytic integrand suite. It does not
establish superiority for arbitrary integrands, discontinuous functions,
high-dimensional integration, or production workloads with different stability
requirements.

The contracted score is intentionally narrow. A lower objective is evidence that
the accepted candidate improved under this contract, not evidence that every
downstream quantity of interest improved.

## 6. Reproducibility

The public bundle includes the accepted candidate, the evaluation contract,
metrics, sanitized evolution trace, and provenance. Replaying the result should
use the same analytic integrand suite, the same objective definition, and the
same lower-is-better direction.

The source bundle is available in
[Göther Labs Open Results](https://github.com/Gother-Labs/gother-labs-open-results/tree/main/results/quadrature-rule-optimization).

{{visual:implementation-code}}
