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

Let \(f_j\) denote one analytic test integrand on the unit interval and let
\(I_j\) denote its analytic reference integral. The exact quantity of interest
for any one integrand \(f\) is

$$
I[f] = \int_0^1 f(x)\,dx.
$$

{{visual:exact-integral}}

A quadrature rule \(r\) approximates this quantity by evaluating the integrand at
a finite set of nodes \(x_i\) and combining those evaluations with normalized
weights \(w_i\):

$$
Q_r[f] = \sum_{i=1}^{n} w_i f(x_i),
\qquad x_i \in [0,1],
\qquad \sum_i w_i = 1.
$$

{{visual:quadrature-rule}}

For each public integrand \(f_j\), the observable residual \(e_j(r)\) is the
absolute difference between the quadrature estimate \(Q_r[f_j]\) and the
analytic reference value \(I_j\):

$$
e_j(r) = \left|Q_r[f_j] - I_j\right|.
$$

{{visual:residual-error}}

## 2. Evaluation contract

The evaluation contract is fixed before candidate comparison. Each candidate
rule is scored on the same public analytic integrand suite:

$$
f_1(x)=\sin(\pi x),\qquad f_2(x)=\sqrt{x},\qquad f_3(x)=\log(1+x).
$$

For each function, the evaluator computes the residual in Equation (3). The run
objective \(J(r)\) is a weighted aggregate of those residuals, with the same
objective direction and aggregation rule used for every candidate:

$$
J(r) = \sum_j \alpha_j \left| Q_r[f_j] - I_j \right|.
$$

Lower values of \(J(r)\) are preferred. The three functions are not three
separate objectives; they are the public residual components inside one frozen
acceptance score. That score is used to retain candidates during the run. It is
not a general-purpose measure of integration quality, so the report also exposes
the per-integrand residuals directly.

The run baseline \(r_0\) is the first public rule in the curated trace. It fixes
the comparison point before candidate selection; the numerical change relative to
that baseline is reported in the results section.

## 3. Accepted candidate

{{visual:objective-curve}}

The accepted rule keeps five nodes on \([0,1]\) with near-uniform normalized
weights. The implementation starts from Gauss-Legendre nodes, applies a
deterministic inward remapping with exponent \(\alpha=1.7\), maps the nodes back
to the unit interval, and renormalizes the resulting rule.

The accepted implementation is included here because it is part of the candidate
definition, not just a replay appendix. It is the code path that produces the
rule analyzed in this section.

{{visual:implementation-code}}

Gauss-Legendre appears in this section only as a construction reference for
interpreting how the accepted rule is formed from a familiar five-node rule. The
reported improvement is still measured against the run baseline fixed in the
evaluation contract.

If \(\xi_i\) are the original Gauss-Legendre nodes on \([-1,1]\), the accepted
candidate uses the deterministic transformation

$$
\tilde{\xi}_i=\operatorname{sign}(\xi_i)|\xi_i|^{1.7},
\qquad
x_i=\frac{\tilde{\xi}_i+1}{2}.
$$

The transformation moves the interior support inward before the rule is expressed
on \([0,1]\). The figure below shows the accepted nodes against the original
Gauss-Legendre locations, so the remapping can be inspected geometrically.

{{visual:accepted-rule-figure}}

## 4. Results

The primary reported improvement is the reduction in the frozen acceptance
objective. The result should be interpreted together with the residual readout,
because the score answers whether the candidate was retained under the contract,
while the residuals show the observable numerical behavior.

Table 1 is therefore the acceptance readout: it states what changed relative to
the fixed run baseline. Table 2 and Figure 6 are the scientific readout: they
show where the accepted rule still differs from the analytic references on the
public functions.

{{visual:objective-summary-table}}

{{visual:residual-error-table}}

{{visual:residual-location-figure}}

## 5. Limitations

This is a bounded benchmark on a fixed analytic integrand suite. It does not
establish superiority for arbitrary integrands, discontinuous functions,
high-dimensional integration, or production workloads with different stability
requirements.

The contracted score is intentionally narrow. A lower objective is evidence that
the accepted candidate improved under this contract, not evidence that every
downstream quantity of interest improved.

External validity is deliberately left open. A reader should not assume the same
node placement improves oscillatory functions, endpoint singularities not
represented by the public suite, discontinuities, or multidimensional integrals
without rerunning an evaluation contract that explicitly contains those cases.

## 6. Reproducibility

The public bundle includes the accepted candidate, the evaluation contract,
metrics, sanitized evolution trace, and provenance. Replaying the result should
use the same analytic integrand suite, the same objective definition, and the
same lower-is-better direction.

The replay surface is intentionally small: `accepted_candidate.py` defines the
candidate, `evaluation_contract.md` defines the scoring rule, `metrics.json`
records the retained values, and `evolution.json` contains the sanitized public
trace used for the figures above.

The source bundle is available in
[Göther Labs Open Results](https://github.com/Gother-Labs/gother-labs-open-results/tree/main/results/quadrature-rule-optimization).
