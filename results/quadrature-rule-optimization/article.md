# Quadrature rule optimization

## Abstract

This note reports a compact five-node quadrature rule for one-dimensional
integrals on the unit interval. The run was evaluated under a frozen
lower-is-better acceptance contract, with the public baseline fixed before the
accepted candidate is compared. The accepted candidate reduces the contracted
objective from 688.676231 to 114.514813, while the largest public representative
residual is reduced from 0.363380 to 0.001029.

The result is a bounded optimization artifact. It is not presented as a
universal integration method. The purpose of the report is to make the problem,
evaluation contract, baseline, accepted candidate, residual behavior, and replay
surface inspectable in one place.

## 1. Problem formulation

The conceptual object is an integral of an arbitrary scalar function \(g\) on the
unit interval:

$$
I[g] = \int_{0}^{1} g(x)\,dx.
$$

{{visual:exact-integral}}

A quadrature rule \(r\) replaces the continuous integral with a finite set of
weighted point evaluations. The nodes \(x_i\) determine where the function is
sampled and the normalized weights \(w_i\) determine each sample contribution:

$$
Q_r[g] = \sum_{i=1}^{n} w_i\,g(x_i),
\qquad
x_i \in [0,1],
\qquad
\sum_{i=1}^{n} w_i = 1.
$$

{{visual:quadrature-rule}}

The residual compares the analytic integral with the quadrature estimate. The
visual residual can have regions where the rule overestimates and regions where
it underestimates; the reported scalar residual is the absolute value of the net
difference:

$$
e(r;g) = \left|Q_r[g] - I[g]\right|.
$$

{{visual:residual-error}}

These figures introduce the objects used by the report. The actual acceptance
contract below uses a fixed public suite of three analytic functions, not the
illustrative function \(g\).

## 2. Evaluation contract

The evaluation contract is fixed before candidate comparison. Each candidate
rule is scored on the same public analytic integrand suite:

$$
\begin{aligned}
f_1(x) &= \sin(\pi x),\\
f_2(x) &= \sqrt{x},\\
f_3(x) &= \log(1+x).
\end{aligned}
$$

For each function \(f_j\), the evaluator computes the residual by specializing
Equation (3) to the contract integrand:

$$
e_j(r) =
\left|Q_r[f_j] - I[f_j]\right|.
$$

The run objective \(J(r)\) is a lower-is-better aggregate of the public residual
components:

$$
J(r) = \sum_{j=1}^{3} \alpha_j\,e_j(r).
$$

{{visual:contract-table}}

The public bundle identifies the integrand suite and objective direction, but it
does not expose numeric component weights \(\alpha_j\). Table 1 therefore fixes
the public residual components without inventing unpublished objective weights or
mixing in accepted-candidate outcomes.

### Run baseline

The run baseline \(r_0\) is the first public rule in the curated trace. It fixes
the comparison point before candidate selection.

{{visual:baseline-rule-figure}}

All objective and residual improvements reported below are measured against this
same run baseline, whose contracted objective is \(J(r_0)=688.676231\).

## 3. Accepted candidate

The accepted candidate is the five-node rule shown in Figure 5. The figure is
the primary definition of the node placement and normalized weights; it should be
read against the run baseline in Figure 4 before interpreting the objective
change.

{{visual:accepted-rule-figure}}

### Candidate construction

The implementation maps source nodes \(\xi_i\) on \([-1,1]\) inward with a fixed
remapping exponent \(p=1.7\), maps them back to the unit interval, and
renormalizes the weights:

$$
\tilde{\xi}_i=\operatorname{sign}(\xi_i)\,|\xi_i|^p,
\qquad
x_i=\frac{\tilde{\xi}_i+1}{2},
\qquad
p=1.7.
$$

The accepted implementation is included here because it is part of the candidate
definition, not only a replay appendix.

{{visual:implementation-code}}

### Candidate results

The primary reported improvement is the reduction in the frozen acceptance
objective. The curve shows the scored candidates, the retained best-so-far
objective, the fixed run baseline, and the accepted candidate.

{{visual:objective-curve}}

{{visual:objective-summary-table}}

The residual readout is the scientific check on the objective score. The largest
accepted residual remains on \(f_1(x)=\sin(\pi x)\), but it is also the component
with the largest absolute reduction from the run baseline.

{{visual:residual-location-figure}}

{{visual:residual-error-table}}

## 4. Limitations

This is a bounded benchmark on a fixed one-dimensional analytic suite. It does
not establish superiority for arbitrary integrands, discontinuous functions,
oscillatory functions outside the public suite, endpoint singularities not
represented by the contract, multidimensional integration, or production
workloads with different stability requirements.

The contracted score is intentionally narrow. A lower value of \(J(r)\) is
evidence that the accepted candidate improved under this contract, not evidence
that every downstream quantity of interest improved. Because the public bundle
does not expose numeric component weights \(\alpha_j\), readers should interpret
the residual table as the transparent scientific readout alongside the aggregate
score.

External validity is deliberately left open. A reader should rerun an evaluation
contract that explicitly contains the cases they care about before transferring
the node placement to another integration setting.

## 5. Reproducibility

The replay surface is intentionally small. `evaluation_contract.md` defines the
public contract and objective direction. `accepted_candidate.py` provides Listing
1 and the accepted rule shown in Figure 5. `evolution.json` provides Figure 6.
`metrics.json` provides Table 2 and the retained objective values. The residual
values used in Figure 7 and Table 3 are read from the curated public trace.

Replaying the result should use the same analytic integrand suite, the same
objective definition, the same run baseline, and the same lower-is-better
direction.

The source bundle is available in
[Göther Labs Open Results](https://github.com/Gother-Labs/gother-labs-open-results/tree/main/results/quadrature-rule-optimization).
