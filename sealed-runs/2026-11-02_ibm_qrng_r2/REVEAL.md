# Reveal — QRNG reference module, third sealed run (r2) on IBM ibm_fez, 2026-11-02

**Sealed before the run:** `plan_r2.json`, sha256 f631d095d5477037ed06df5f6193ecd2fc0166c057f4477a5ddcfa0293edef94. Every number
in it comes from `qrng_r2_numbers.py` run on the committed r0 and r1 raw samples (`numbers_r2.json`, sha256 9e198895…) —
nothing was written by hand. The module and the buyer's checker are the published ones (`tools/qrng`, cited by sha256 in the plan).
Clocks before the jobs: public RFC 3161 timestamp on the plan **18:02:34 UTC** (`provenance/tsa/`, verified); this repository received
the sealed folder at about 18:02:36 UTC (our clock, commit f8a907a); the second arm's notary channel received the fingerprint at
18:03:33 UTC (that message carried the hash fields empty — a shell error on our side — and was corrected at 18:04:35 UTC) and returned
its adversary call at **18:04:48 UTC**; the control it asked for was written into the evaluator and pushed to our own repository at
18:05:23 UTC. IBM created job A **dbkd1qonceqs73alko5g at 18:05:31.376 UTC** and job B **dbkd1r1ffo6c73bb8u90 at 18:05:32.655 UTC**
(`receipts/`, the provider's raw records with sha256) — after all of the above.

**Run:** the r1 circuit — 156 qubits each put into |+⟩ with one gate and measured, 4096 shots, no dynamical decoupling, no twirling,
no readout mitigation — submitted twice back to back (A, B). The vendor's calibration snapshot before A and after B carries the same
`last_update` (17:51:34 UTC, 14 minutes before the jobs). 6 seconds of processor time (86 → 80 s left of the free allowance).
`A/raw.bin` 79 872 bytes sha256 75fe62d1…, `B/raw.bin` 79 872 bytes sha256 c7668976…; `A/module/`, `B/module/` the signed receipts.

**The question, fixed before the data:** r1 (31 October) had refuted the claim that the per-qubit bias pattern is a stable device
property across days (r = 0.36 against a floor of 0.651). Does it repeat within *minutes*, under one calibration (K7)? Does its
correlation fall with the age of the calibration (K8)? Is the vendor's readout-error table as stable as before (K9)?

| K | sealed prediction | measured A | measured B | |
|---|---|---|---|---|
| K1 module accepts the block | accept | accepted, 0 health failures | accepted, 0 health failures | ✓ ✓ |
| K2 min-entropy estimate in [6.5, 8.0] bits/byte | | 7.526 | 7.540 | ✓ ✓ |
| K3 fraction of ones in [0.40, 0.60] | | 0.5039 | 0.5038 | ✓ ✓ |
| K4 buyer's checker PASS (`--expect-rows 1`) | | PASS, rc 0 | PASS, rc 0 | ✓ ✓ |
| K5 excluded channels 0–4 | | 1 (q72) | 1 (q72) | ✓ ✓ |
| K6 per-channel accounting h_acc in [6.731, 8.0] | | 7.251 (output 35 968 B) | 7.233 (output 35 968 B) | ✓ ✓ |
| K7 bias pattern repeats within minutes: r(p1_A, p1_B) ≥ 0.622 (0.872 expected) | | **0.907** | | ✓ |
| K8 correlation falls with calibration age: r(A,B) > r(A,r1) > r(A,r0) | | 0.907 > **0.466 < 0.849** | | **✗** |
| K9 vendor readout-error table r2 vs r1 ≥ 0.9 | | 0.942 | | ✓ |

**Verdict: K1–K6 hold on both jobs, K7 and K9 hold, K8 refuted.** The per-qubit bias *is* a stable property within one
calibration: two blocks 1.3 seconds apart agree at r = 0.91, within the margin of the model that assumes a constant bias plus
independent shot noise (0.87 expected). The second arm's pre-registered negative control confirms the match is tied to the qubit
labels: shuffling B's labels 10 000 times (seed 20261102) never reaches the observed correlation (maximum 0.686; one-sided p = 1/10 001).

**What K8's failure says.** We had assumed the correlation decays with time. It does not: today's pattern matches the run of
28 October (five days old, r = 0.85) far better than the run of 31 October (two days old, r = 0.47). The bias pattern is a property of
the *calibration state*, not of elapsed time. q72 tells the story in one qubit: p(1) = 0.277 on the 28th, 0.514 on the 31st,
0.256 and 0.259 today — excluded by the 0.5-bit rule on the 28th and today, clean on the 31st. The vendor's readout-error table cannot
tell the two states apart (r = 0.94 against both earlier tables); the bias a user measures can. The second arm had named K8 as the
most vulnerable prediction before the reveal — "an older calibration may by chance resemble A more; a single r0–r1 correlation does
not define a decay law" — and it was right.

**Consequence for the module (stated, not re-scored).** The channel test must work from the current block only — it already
does. A per-qubit fingerprint learned from one block is reusable while the vendor's `last_update` is unchanged, and must be dropped
at every recalibration; whether a pattern *returns* after a recalibration (as the 28 October one did today) is the next sealed
question, not a claim.

**What this does not say.** Statistics still cannot certify a quantum source; the receipts say `statistical`. One machine, four
runs, 4096 shots each, a free-tier allowance. Post-hoc diagnostics in `posthoc_k8.json` (nothing re-scored).
