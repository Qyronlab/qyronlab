# Reveal — QRNG reference module, second sealed run (r1) on IBM ibm_fez, 2026-10-31

**Sealed before the run:** `plan_r1.json`, sha256 ffef322b403580b41b2d209ff3bf6b59e74fb439d9fdc0d99d9c97812a7cf5a9. Every number
in it comes from `qrng_r1_numbers.py` run on the committed r0 raw samples (`numbers_r1.json`, sha256 aac6cc79…) — nothing
was written by hand. Three clocks before the job: public RFC 3161 timestamp on the plan **09:06:08 UTC** (`provenance/tsa/`,
verified), the second arm's notary channel received the fingerprint at **09:07:57 UTC** and returned its adversary call at
**09:09:27 UTC**, GitHub received the push at about 09:10:12 UTC (our clock; the server-side event was not fetched). IBM created the
job **dbir1401h92s738426qg at 09:10:40.93 UTC** (`receipts/`, the provider's raw record with sha256) — after all three.

**Run:** same circuit as r0 — 156 qubits each put into |+⟩ with one gate and measured, 4096 shots, no dynamical decoupling, no
twirling, no readout mitigation. 3 seconds of processor time (89 → 86 s left of the free allowance). `raw.bin` 79 872 bytes,
sha256 bf4cd604…; `meta.json`, `calibration.json` (the vendor's calibration at the run), `ledger.jsonl` the signed receipt (audit block).

**The rule that was new, fixed before the data (the r0 lesson):** every qubit is a channel; a channel is *broken* when the 99 %
upper bound of max(p0, p1) leaves less than 0.5 bit of min-entropy per bit (max probability above 0.707). A broken channel is
named in the receipt and its bits count zero in the entropy accounting — the block is not refused (policy *exclude*). The output
is sized by h_eff = min(MCV estimate, per-channel accounting). On r0 this rule excludes exactly q72 and nothing else; the r0 default
(0.9 bit/bit) had failed 40 of 156 qubits — a false red from the margin alone.

| K | sealed prediction | measured | |
|---|---|---|---|
| K1 module accepts the block | accept | accepted, 0 health failures, lag-1 0.0039 (bound 0.0177) | ✓ |
| K2 min-entropy estimate in [6.5, 8.0] bits/byte | | 7.569 | ✓ |
| K3 fraction of ones in [0.40, 0.60] | | 0.5057 | ✓ |
| K4 buyer's checker PASS (exclusion + accounting recomputed) | | PASS | ✓ |
| K5 excluded channels 0–4 (r0 under the same rule: 1) | | **0** — no qubit below 0.5 bit/bit | ✓ |
| K6 per-channel accounting h_acc in [6.731, 8.0] (r0: 7.231) | | 7.300 (= h_eff; output 35 968 bytes) | ✓ |
| K7 per-qubit bias pattern repeats: Pearson r(p1_r0, p1_r1) ≥ 0.651 (expected 0.90) | | **0.356** | **✗** |

**Verdict: K1–K6 hold, K7 refuted.** The per-channel rule runs end to end on a real quantum source without the r0 false red, the
buyer recomputes exclusion and accounting from the raw bytes, and a broken channel would cost output rather than the block. The
physics-side claim — that the per-qubit bias measured on 28 October is a stable property of the device — is **not supported**: the
correlation between the two runs is 0.36, not the 0.90 the variance decomposition predicted under "bias unchanged, noise independent".

**What the post-hoc look says** (`posthoc_k7.json`, diagnostics only, nothing re-scored): the vendor recalibrated between the runs
(28 Oct 18:28 → 31 Oct 09:35 local). q72, the one channel the rule excluded on r0 (p1 = 0.277), came back at 0.514 — while the
vendor's readout-error figure for it barely moved (0.33 → 0.31). The r0 explanation "the vendor's readout error accounts for q72" is
therefore refuted too: the bias went away, the readout-error number did not. q45 (0.595 on r0, flagged then as unexplained) is 0.486
now — a one-off. The vendor's readout-error table itself is very stable across the two days (r = 0.95) while the measured biases are
not (r = 0.36; 72 % of qubits keep the sign of their bias) — the published calibration does not predict the bias a user actually
sees, which is the point of measuring it. The remaining spread of p1 on r1 (sd 0.018 vs binomial 0.008) says there *is* bias beyond
sampling noise on any given day; it just moves between days.

**Second arm (adversary call before the reveal, #665 at 09:09:27 UTC):** conditional point prediction r = 0.90 under the same model,
and K7 named as the most vulnerable prediction — "calibration drift or a different physical qubit assignment can break the r0↔r1
correlation even while the block-level tests pass". That is what happened. Its suggested negative control (every channel excluded
must yield no positive-entropy output) was added to the break test before the reveal: 43/43 pass, the planted accounting mutant fails
in two places.

**What this does not say.** Statistics still cannot certify a quantum source; the receipt says `statistical`. One machine, two runs
three days apart, 4096 shots each, a free-tier allowance. The next sealed plan takes K7's lesson: predict the bias from a calibration
taken minutes before the run, not days — and state the age of the calibration as a parameter, as the entangled-pair tests already do.
