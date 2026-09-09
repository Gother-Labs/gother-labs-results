# Verified RTL optimization

Three correctness-gated before/after RTL cases show distinct classes of implementation reasoning under fixed public contracts:

| Case | Transformation | Area | Delay | Active power | Composite |
|---|---|---:|---:|---:|---:|
| SHA-1 | Boolean sharing and direct state readout | 0.15% lower | 5.20% lower | 1.38% lower | 2.27% lower |
| INT8 MatVec | Range-correct widths and balanced addition tree | 15.5943% lower | 3.1868% lower | 5.7081% lower | 8.3230% lower |
| ML-KEM CBD | Fixed physical state movement plus byte phase | 15.9083% lower | 6.9920% lower | 5.9621% lower | 9.7338% lower |

These are case-local paired estimates over 64 fixed publication pairs per case. They are not a cross-circuit ranking, average, or expected customer uplift.

## Evidence model

The common sequence is:

1. freeze the RTL contract, correctness semantics, implementation target, metrics, and sampling policy;
2. reject any candidate that fails the declared functional or formal checks;
3. measure correctness-valid RTL on the pinned academic VTR/PTM 45 nm target;
4. freeze the accepted implementation by hash;
5. apply the fixed paired acceptance contract;
6. publish before/after identities, exact patches, evidence, provenance, and limitations.

The machine-readable bundle includes:

- [baseline implementation identities](artifacts/baseline-implementations.json)
- [accepted implementation identities](artifacts/accepted-implementations.json)
- [SHA-1 patch](artifacts/patches/sha1.patch)
- [INT8 MatVec patch](artifacts/patches/int8-matvec.patch)
- [ML-KEM CBD patch](artifacts/patches/mlkem-cbd.patch)
- [correctness summary](artifacts/correctness.json)
- [paired evaluation summary](artifacts/evaluation.json)
- [metrics](artifacts/metrics.json)
- [provenance](artifacts/provenance.json)
- [evaluation contract](artifacts/evaluation_contract.md)

The quantitative authority is `juan-fernandez-gotherlabs/rtl-optimization-case-study` release `v2.2.2`, commit `8cd8b479488f0693d76c2fab39eabf4bd6f9279c`.

## Claim boundary

The current cases are academic VTR/PTM 45 nm implementation-model comparisons on a homogeneous LUT6 target. They are not ASIC signoff, commercial-FPGA characterization, board or silicon measurements, measured energy, accredited certification, or signed independent third-party assurance. ML-KEM CBD is not side-channel analysis or certification of a complete cryptographic implementation.

The full public evidence, reports, verifiers, raw-archive links, methodology, and audit protocol remain in the [canonical evidence repository](https://github.com/juan-fernandez-gotherlabs/rtl-optimization-case-study/tree/v2.2.2).
