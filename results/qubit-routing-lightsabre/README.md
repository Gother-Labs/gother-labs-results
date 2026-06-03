# Qubit routing LightSABRE benchmark

[Published web article](https://www.gotherlabs.com/results/qubit-routing-lightsabre/) · [Animated run surface](https://www.gotherlabs.com/results/qubit-routing-lightsabre/run/) · [Structured metadata](result.json) · [Evaluation contract](artifacts/evaluation_contract.md) · [Accepted candidate](artifacts/accepted_candidate.rs)

## Abstract

This result reports a deterministic qubit-routing policy, a public scoring
trace, and an exact replay candidate for a frozen swap-reduction benchmark. The
accepted policy reduces aggregate added CNOTs by 12,294 versus LightSABRE while
keeping the routing-policy surface, topology split, and selected case-level
readout public.

The claim is deliberately bounded: it is not a universal quantum compiler
result, not a runtime benchmark, and not a hardware-performance claim.

## 1. Problem formulation

Qubit routing maps a logical circuit onto a physical device topology. When two
logical qubits that need a two-qubit gate are not adjacent on the target
topology, the router inserts SWAP gates. A nearest-neighbor SWAP is normally
decomposed into three CNOTs, so each unnecessary SWAP directly inflates the
added-CNOT readout.

The benchmark focuses on routing quality, not wall-clock speed. The observable
quantity is added CNOT count after routing under the fixed portfolio and fixed
reference comparison.

## 2. Evaluation contract

The public portfolio contains 24 circuits crossed with three topology targets:
Q20, Willow, and Heron-FEZ. That produces 72 deterministic circuit/topology
evaluations.

See [evaluation_contract.md](artifacts/evaluation_contract.md).

For a candidate policy \(p\), the evaluator computes a weighted added-CNOT
reduction against the LightSABRE reference:

$$
\Delta_{\mathrm{wCNOT}}(p)
  = \sum_{(c,\tau)\in P} w_{c,\tau}
    \left(A_{\mathrm{LS}}(c,\tau)-A_p(c,\tau)\right).
$$

The governed score is:

$$
J(p) = -\Delta_{\mathrm{wCNOT}}(p).
$$

Lower score is better because a larger positive weighted CNOT reduction becomes
a more negative evaluator score. The report also shows positive reductions
directly because they are easier to read.

## 3. Accepted candidate

The accepted public candidate is a Rust routing-policy implementation. It keeps
the benchmark scaffold, portfolio assets, topology targets, reference
LightSABRE comparison, and replay validator fixed. The candidate changes the
deterministic routing-policy surface used to choose swaps.

See [accepted_candidate.rs](artifacts/accepted_candidate.rs).

The implementation combines a topology-aware initial layout with a SABRE-style
swap scorer. The exposed candidate keeps front-layer distance, extended-set
lookahead, and decay behavior visible in one deterministic policy surface.

## 4. Result summary

| Readout | Value |
| --- | ---: |
| LightSABRE aggregate added CNOTs | 308,076 |
| Accepted aggregate added CNOTs | 295,782 |
| Aggregate added-CNOT reduction | 12,294 fewer |
| Weighted CNOT reduction | 11,506.2 |
| Valid routing cases | 72 / 72 |
| Case split versus LightSABRE | 31 wins / 6 ties / 35 losses |
| Q20 relative reduction | 17.39% |
| Willow relative reduction | 2.12% |
| Heron-FEZ relative reduction | -0.37% |

![Objective trace](assets/objective-curve.svg)

The result is not uniform across topology families. Q20 carries the strongest
positive readout, Willow is modestly positive, and Heron-FEZ is slightly worse
than LightSABRE on aggregate.

![Per-topology added-CNOT comparison](assets/target-comparison.svg)

The selected case-level table highlights the largest positive exported case
savings. It is not a second aggregate readout.

![Selected case-level replay examples](assets/routing-readout.svg)

See [metrics.json](artifacts/metrics.json),
[replay.json](artifacts/replay.json), and
[score-trace.json](artifacts/score-trace.json).

## 5. Limitations

This report is limited to the frozen 24-circuit LightSABRE portfolio in the
bundle. It does not claim improvement on arbitrary circuits, arbitrary hardware
topologies, all related benchmark assets, or production compiler workloads.

The benchmark measures routing quality through added CNOT count. It does not
make a wall-clock speed claim, does not measure hardware execution fidelity, and
does not evaluate downstream transpiler passes after routing.

## 6. Reproducibility

The public bundle includes the accepted Rust candidate, the evaluation contract,
metrics, a curated evolution chain, replay confirmation, public figures, and
the public [animated run surface](https://www.gotherlabs.com/results/qubit-routing-lightsabre/run/).
The run page is a presentation layer over the same artifacts and excludes
prompts, raw telemetry, local logs, private paths, and operational run state.

Replaying the result should use the same 24-circuit LightSABRE portfolio, the
same Q20, Willow, and Heron-FEZ coupling graphs, the same added-CNOT objective,
the same case weights, and the same lower-is-better governed score. Changing the
topology set, case set, routing objective, or LightSABRE reference creates a new
evaluation, not a replay of this result.

Useful entry points:

- [accepted_candidate.rs](artifacts/accepted_candidate.rs): accepted routing
  policy implementation
- [evaluation_contract.md](artifacts/evaluation_contract.md): frozen validator
  behavior
- [metrics.json](artifacts/metrics.json): headline numerical readouts
- [replay.json](artifacts/replay.json): accepted replay confirmation and
  topology/case summaries
- [score-trace.json](artifacts/score-trace.json): public scored-candidate trace
- [evolution.json](artifacts/evolution.json): curated accepted-chain states

The source bundle is available in the
[Göther Labs results repository](https://github.com/Gother-Labs/gother-labs-results/tree/main/results/qubit-routing-lightsabre).
