# Reveal — QRNG reference module, fifth sealed run (r4) on IBM ibm_fez, 2026-11-03 (after the next recalibration)

**Sealed before the run:** `plan_r4.json`, sha256 d430f33f781132ecd6cf7bfab358599a0098c48868cd25bd691d0f3615187468. Every number
comes from `qrng_r4_numbers.py` on the committed r0, r1, r2 and r3 raw samples with the published module's own functions
(`numbers_r4.json`, sha256 6b962434…). Four priors were chosen *before* the run by age, not by fit: `prior_r3CD.json` (one
recalibration back), `prior_r2AB.json` (two), `prior_r0.json` (the same state, five days and four recalibrations back),
`prior_r1.json` (the other state). Module and checker: `tools/qrng` at 70f4f41 — with the compatibility z gate the second arm's
counterexample of 3 November forced — cited by sha256. Clocks: RFC 3161 timestamp on the plan **03:52:19 UTC**; this repository
received the sealed folder at 03:52:22 UTC (commit 4c16679, our clock); the second arm's notary channel received the fingerprint at
03:53:49 UTC (no adversary call for r4 arrived within the five minutes; its reply of 03:53:49 UTC answered the previous item). The
trigger — a vendor calibration newer than the r3 one — was seen live at 03:51:45 UTC. IBM created job E **dbkllt0nceqs73am5s3g at
03:54:28.474 UTC** and job F **dbklltd6p51s73cmtsk0 at 03:54:29.627 UTC** (`receipts/`), both under the vendor calibration stamped
03:27:58 UTC (`calibration_before.json` = `calibration_after.json`; r3 ran under 18:20:09 UTC the day before).

**Run:** the same circuit — 156 qubits each put into |+⟩ with one gate and measured, 4096 shots, no mitigation — submitted twice
back to back (E, F). 6 seconds of processor time (74 → 68 s left). `E/raw.bin` sha256 2961af44…, `F/raw.bin` sha256 054ec3ab…,
79 872 bytes each. Block E ran through the module five ways (`E/module_none`, `E/module_P1_r3CD`, `E/module_P2_r2AB`, `E/module_P3_r0`,
`E/module_P4_r1`), block F once; every receipt is recomputed by the buyer's checker with the same prior file.

| K | sealed prediction | measured | |
|---|---|---|---|
| K1–K6 on E | accept, checker PASS, 0–4 excluded, h_acc ≥ 6.731 | accepted, h_mcv 7.551, ones 0.5030, excluded q72, h_acc 7.254, PASS | ✓ |
| K1–K6 on F | same | accepted, h_mcv 7.580, ones 0.5022, excluded q72, h_acc 7.233, PASS | ✓ |
| K-S1 known state: max over {r0, r1, r2, r3} of r(E, state) ≥ 0.622 | known | r(E, r2) = **0.871**, r(E, r3) = 0.861, r(E, r0) = 0.778, r(E, r1) = 0.483 | ✓ |
| K-S2 the latest state persists: r(E, r3) ≥ 0.622 | persists | 0.861 | ✓ |
| K-S3 stable in itself: r(E, F) ≥ 0.622 | | 0.919 | ✓ |
| K-V1–4 gate decision per prior = prediction (used, used, used, refused) | | r3: used (r 0.861, mean \|z\| 0.93, 154 of 156 channels combined); r2: used (0.871, 0.96, 154); r0: used (0.778, 0.99, 152); r1: **refused** (r 0.483) | ✓ ✓ ✓ ✓ |
| K-V5 every used prior: never worse than none, hold-out coverage ≥ 0.859 | | h_acc 7.455 / 7.452 / 7.384 ≥ 7.254; output 37 024 / 37 024 / 36 512 ≥ 35 968 B; coverage of F 0.910 / 0.885 / 0.917 | ✓ |
| K-V6 the gain does not grow with age: gain(r3) ≥ gain(r2) ≥ gain(r0) | | +0.201 ≥ +0.198 ≥ +0.129 bit/byte | ✓ |

**Verdict: every sealed criterion held.** No third state appeared: after the fourth recalibration we have seen, the per-qubit bias
pattern is still the state of 28 October, 2 November afternoon and 2 November evening (correlations 0.78–0.87 with those, 0.48 with
the 31 October state), and the new blocks agree with each other at 0.92. The same qubit (q72, p(1) = 0.283 and 0.296) is excluded by
the 0.5-bit rule, as in every run of this state. On the buyer's side the picture is graded by age: a prior one or two recalibrations
back buys +0.20 bit per byte of accounting and 1 056 more output bytes; the five-day-old prior of the same state still buys +0.13 and
544 bytes, with two to four channels left out of the combination by the per-channel z filter; the prior from the other state is
refused by the gate. Validation held in every arm: the tighter bounds still cover the hold-out block in 88–92 % of channels (floor 0.859).

**What this does not say.** Four recalibrations on one machine; the bias pattern has so far shown two states, with the 31 October
one seen once. "Never worse" is still not a theorem: the second arm's second counterexample (3 November, after the plan was sealed)
shows that at a channel rule sitting exactly on the entropy threshold a compatible prior can tip channels into exclusion; under the
0.5-bit rule used here no channel sits near that edge, and the fix (exclusion decided by the current block alone, the prior refining
credit only) is applied to the module after this reveal, not to this result. Statistics still cannot certify a quantum source; the
receipts say `statistical`.
