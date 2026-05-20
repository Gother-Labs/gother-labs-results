# 26-circle unit-square packing

## Abstract

This note reports a deterministic 26-circle packing inside the unit square as a validated geometry, a public scoring trace, and a reproducible reconstruction candidate. The accepted geometry reaches total radius 2.635977. The public trace starts from the original domain `program.py` baseline at total radius 0.959778, records all valid scored candidates, and marks the retained implementation states that lead to the accepted packing. The governed lower-is-better score improves from -0.959778 to -2.635977.

For audit clarity, the public claim is not a raw solver artifact. It is the combination of the accepted code surface, the replayed scoring evidence, and the evaluator-validated geometry. The accepted candidate reconstructs the packing from the evolved contact graph and returns the generated centers and radii only after the deterministic reconstruction has passed validation.

## 1. Problem formulation

The task is to place 26 circles in the unit square without overlap. A packing is defined by centers \((x_i, y_i)\) and radii \(r_i\) for \(i = 1, \dots, 26\). The objective is the total radius:

$$
R(P) = \sum_{i=1}^{26} r_i
$$

{{visual:packing-primer}}

Every circle must remain inside \([0,1]^2\), and every pair of circles must satisfy the non-overlap constraint:

$$
\sqrt{(x_i-x_j)^2 + (y_i-y_j)^2} \ge r_i + r_j.
$$

## 2. Evaluation contract

The evaluator asks the candidate for exactly 26 centers, 26 positive radii, and a reported sum. It verifies finite values, checks that the reported sum matches the radii, rejects boundary violations, rejects pairwise overlap, and calls the entrypoint twice to enforce determinism.

{{visual:contract-table}}

The score is defined as:

$$
J(P) = -R(P).
$$

Lower score is therefore better, but the report also shows \(R(P)\) directly because total radius is the geometric quantity of interest.

## 3. Accepted candidate

The accepted public candidate is a deterministic reconstruction program, not a stored list of final coordinates. It starts from a coarse deterministic seed, solves the boundary and pairwise tangency equations with a small damped Newton system, and then validates the resulting geometry before returning it. The replayed centers and radii remain part of the audit bundle as evidence of the accepted run, but the implementation surface is the reconstruction code.

{{visual:implementation-code}}

## 4. Results

The public trajectory has three visible phases. First, the original `program.py` baseline is a sparse packing with total radius 0.959778. Second, early generated candidates move quickly into useful geometries: the first valid candidate reaches 1.064234, and generation 1 later produces the retained 2.438966 checkpoint. Third, most later candidates explore the high-radius plateau until the accepted reconstruction reaches total radius 2.635977. In evaluator-score terms, the full public trajectory is a reduction from -0.959778 to -2.635977.

{{visual:objective-curve}}

{{visual:objective-summary-table}}

The accepted packing is tight in the sense exposed by the public diagnostics: 20 boundary contacts and 58 pairwise contacts are detected at the public tolerance. The smallest boundary and pairwise slacks are near machine precision, so the contact readout acts as a structural check on the geometry rather than a separate optimization claim.

{{visual:packing-layout}}

{{visual:contact-readout}}

## 5. Limitations

This is a result for the 26-circle unit-square packing contract only. It is not a proof of global optimality, and it does not claim a general packing solver for other circle counts, other containers, or changed objectives.

Relative to public AI-discovery references, this validated total radius exceeds the original AlphaEvolve value later reported as 2.635862 for \(n = 26\), but it does not match newer 2.635983 reports from AlphaEvolve V2, ThetaEvolve, and TTT-Discover, or the 2.635982 ShinkaEvolve report. The gap from this result to 2.635983 is about 0.000006 in total radius, or 0.000213%; equivalently, this result reaches 99.999787% of that reference value. These comparison values are stored in `artifacts/reference-comparison.json` and are taken from the circle-packing table in [Learning to Discover at Test Time](https://test-time-training.github.io/discover.pdf).

The accepted candidate is deterministic and reconstructs this validated contact graph. It is not a general-purpose solver for arbitrary circle-packing instances; changing the circle count, container, objective, or contact graph creates a new evaluation.

## 6. Reproducibility

The bundle includes the accepted candidate, evaluation contract, curated evolution chain, scored-candidate trace, metrics, provenance, replay confirmation, and a public [animated run surface](./run/). The run page is a presentation layer over the same public artifacts and excludes raw operational material.

The source bundle is available in [Göther Labs results repository](https://github.com/Gother-Labs/gother-labs-results/tree/main/results/circle-packing-26-unit-square).
