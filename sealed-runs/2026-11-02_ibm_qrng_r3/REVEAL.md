# Reveal — QRNG reference module, fourth sealed run (r3) on IBM ibm_fez, 2026-11-02 (after the vendor's recalibration)

**Sealed before the run:** `plan_r3.json`, sha256 72e659f9dc1afcdb280c2070eb887e15454c73bfe8124bd8bae08b910234380f. Every number in it
comes from `qrng_r3_numbers.py` run on the committed r0, r1 and r2 raw samples with the published module's own functions
(`numbers_r3.json`, sha256 3f166332…). The prior was chosen *before* the run: the most recent run's two blocks, r2 A+B
(`prior_r2AB.json`, sha256 1496d3e8…, 8192 bits per channel). The module and checker with the prior option are `tools/qrng` at
commit 288d1ca (cited by sha256). Clocks: public RFC 3161 timestamp on the plan **18:33:08 UTC** (`provenance/tsa/`, verified); this
repository received the sealed folder at 18:34:52 UTC (commit c982b91, our clock); the second arm's notary channel received the
fingerprint at 18:35:27 UTC (no adversary call arrived within the five minutes the plan allowed); the trigger — a vendor calibration
newer than the r2 one — was first seen live at 18:33:15 UTC. IBM created job C **dbkdiohffo6c73bb9q20 at 18:41:38.710 UTC** and job D
**dbkdiot6p51s73cmdsfg at 18:41:39.841 UTC** (`receipts/`, the provider's raw records with sha256). Both ran under the vendor
calibration stamped 18:20:09 UTC (`calibration_before.json` = `calibration_after.json`), the r2 jobs under 17:51:34 UTC.

**Run:** the r1 circuit — 156 qubits each put into |+⟩ with one gate and measured, 4096 shots, no dynamical decoupling, no twirling,
no readout mitigation — submitted twice back to back (C, D). 6 seconds of processor time (80 → 74 s left of the free allowance).
`C/raw.bin` 79 872 bytes sha256 052cf5bd…, `D/raw.bin` 79 872 bytes sha256 37ce4a8e…. Block C was run through the module three ways
(`C/module_none`, `C/module_validated`, `C/module_blind`), block D once (`D/module_none`); every receipt is recomputed by the buyer's
checker with the same prior file.

**The two questions, separated before the data.** Q1, physics: after a recalibration, does the per-qubit bias pattern *return* to a
state already seen? Q2, the buyer: does an old pattern chosen before the run improve the buyer's result — and does validation
prevent the harm of a stale one?

| K | sealed prediction | measured | |
|---|---|---|---|
| K1–K6 on C | module accepts, checker PASS, 0–4 excluded, h_acc ≥ 6.731 | accepted, 0 health failures, h_mcv 7.618, ones 0.5032, excluded q72, h_acc 7.258, PASS | ✓ |
| K1–K6 on D | same | accepted, h_mcv 7.584, ones 0.5033, excluded q72, h_acc 7.253, PASS | ✓ |
| K-R1 the pattern returns: max over {r0, r1, r2} of r(C, state) ≥ 0.622 | returns | r(C, r2) = **0.913**, r(C, r0) = 0.793, r(C, r1) = 0.465 | ✓ |
| K-R2 the new state is stable in itself: r(C, D) ≥ 0.622 | | 0.919 | ✓ |
| K-P1 validated arm never worse than none; its bound covers D in ≥ 0.865 of channels | | h_acc 7.468 ≥ 7.258, output 37 024 ≥ 35 968 B, coverage 0.923 | ✓ |
| K-P2 (branch "return", r(prior, C) = 0.913 ≥ 0.622): prior used; predicted exclusion = C's; RMSE(prior, C) < RMSE(0.5, C); gain in [0.06, 0.26] | | used; [72] = [72]; 0.0109 < 0.0267; gain **+0.210** bit/byte | ✓ |
| K-P3 (branch "no return") | not scored — the other branch occurred | | — |

**Verdict: everything sealed held.** The bias pattern returned: after the vendor's recalibration the new state correlates 0.91 with
the r2 pattern (and 0.79 with r0, 0.46 with r1 — the same two-state picture as before; q72 read 0.246 and 0.266, excluded again). A
prior chosen before the run, validated on the current block, gave the buyer a tighter per-channel bound: +0.21 bit per byte of
accounting and 1 056 more output bytes (+2.9 %) from the same raw block, with the bound still covering the hold-out block in 92 % of
channels (floor 0.865; the no-prior bound covers 99 % — a tighter bound covers less, by design). The blind arm gave the same numbers
here because the state had returned; the harm it would do on a stale pattern was shown in the sealed dry run on the 31 October block
(`numbers_r3.json`, "other_state": accounting 7.49 instead of 7.30 without any evidence) and is the case the validated mode refuses.

**What this does not say.** One machine, two recalibrations observed, 4096 shots per block, a free-tier allowance. The second arm's
adversary call for r3 did not arrive before the jobs; any objection it raises afterwards is answered in the thread, not re-scored
here. Statistics still cannot certify a quantum source; the receipts say `statistical`. Whether a *third* state ever appears, and how
long a validated prior stays valid across recalibrations, are the next sealed questions.
