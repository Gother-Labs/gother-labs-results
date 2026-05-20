# 26-circle unit-square packing

## Abstract

This note reports a deterministic packing of 26 circles inside the unit square. The accepted geometry reaches a validated total radius of 2.6359773947541023. The public chain starts from the original domain `program.py` baseline with total radius 0.9597783591318301, then records the first generated candidates before the retained high-quality checkpoints. The governed lower-is-better score improves from -0.9597783591318301 to -2.6359773947541023.

For audit clarity, the public claim is the validated geometry and curated best-so-far chain, not the raw solver artifact. The accepted candidate is deterministic: it reconstructs the accepted packing from the evolved contact graph and then returns the generated centers and radii to the evaluator.

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

The accepted public candidate reconstructs the packing from the contact structure exposed by the run. It starts from a coarse deterministic seed, solves the boundary and pairwise tangency equations with a small damped Newton system, and then validates the resulting geometry before returning it. The replayed centers and radii remain part of the audit bundle, but they are not the implementation surface.

{{visual:implementation-code}}

## 4. Results

The curated chain improved from the original `program.py` total radius of 0.9597783591318301 to an accepted total radius of 2.6359773947541023. The first valid generated candidate reached 1.0642342609737314, and the first generation later produced the retained 2.4389662673796346 checkpoint. In evaluator-score terms, the full public trajectory is a reduction from -0.9597783591318301 to -2.6359773947541023.

{{visual:objective-curve}}

{{visual:objective-summary-table}}

The accepted packing is close to a contact graph: 20 boundary contacts and 58 pairwise contacts are detected at the public tolerance. The smallest boundary and pairwise slacks are near machine precision, which is expected for a tight validated layout.

{{visual:packing-layout}}

{{visual:contact-readout}}

## 5. Limitations

This is a result for the 26-circle unit-square packing contract only. It is not a proof of global optimality, and it does not claim a general packing solver for other circle counts, other containers, or changed objectives.

The accepted candidate is deterministic and reconstructs the validated contact graph. It is not a general-purpose solver for arbitrary circle-packing instances, and changing the circle count, container, objective, or contact graph creates a new evaluation.

## 6. Reproducibility

The bundle includes the accepted candidate, evaluation contract, curated evolution chain, metrics, provenance, replay confirmation, and a public animated run surface. The run page is a presentation layer over the same public artifacts and excludes raw operational material.

The source bundle is available in [Göther Labs results repository](https://github.com/Gother-Labs/gother-labs-results/tree/main/results/circle-packing-26-unit-square).
