# Reveal — Bell pair at zero wait on a second vendor (Quafu Shenglian), 2026-10-26

**Sealed before the run:** `plan_r0s.json` (the plan with the predictions F = 0.993 and 0.972 from the vendor's table and the
acceptance K1–K4), sha256 15a9f289… — committed 2026-10-26 15:44:17Z, submitted 15:46:54Z (job u1d84a540-261026-234655, done 15:48:16Z).
A second run of the byte-identical plan: 15:52Z (job u1d84a540-261026-235221). Raw counts of both runs: `r0s_counts.json`.

**What came out.** Two qubit pairs, (34,40) and (61,68), prepared as a Bell pair and measured in X, Y and Z, with a |+0⟩ control.
- Without any correction the pair fidelity is 0.786 / 0.825 (run 1) and 0.793 / 0.832 (run 2): both pairs are entangled (bound 0.5).
- The sealed evaluator corrected readout per qubit, as planned. On pair (34,40) this gave XX = 1.09 and ZZ = 1.10–1.14, which is
  impossible (|correlation| ≤ 1). The sealed K1–K4 still passed in run 1 — so the sealed test was **not accepted**: a rule the plan
  lacked (every corrected correlation within [−1−3σ, 1+3σ]) was added before run 2 and both runs fail it. Lesson recorded.
- Why: the readout of qubit 34 depends on the state of its partner — it reads 0 with probability 0.958 when the partner is in 0 and
  0.810 when the partner is in 1 (difference 0.148 ± 0.005, both runs). A per-qubit correction cannot represent that.
- A pairwise correction (the 4×4 assignment matrix of the pair, inverted and also fitted non-negatively; bootstrap of 500) gives
  F = 0.962 / 0.977 (run 1) and 0.971 / 0.991 (run 2), all physical, all within the vendor-table band of the plan — but this is
  post hoc and is reported as such, not as a passed sealed test. The independent arm recomputed the raw correlators and the
  per-qubit correction from the same counts and found the same numbers.
- During run 1 (81 s) the vendor's calibration id changed between circuits; the second run had a single id. The over-correction
  was present in both, so the calibration change was not its cause.

**Limits.** One machine, two runs, two pairs, zero wait (this cloud has no idle instruction). The corrected fidelities are not
a passed prediction; the entanglement without correction is.
