---
title: "What it does today"
slug: what-it-does-today
order: 4
---

# What it does today

**Tests so far (short overview).** Every test is sealed before the run: the prediction and its tolerance are written
down and fingerprinted first, the raw data are revealed after. Our calculations and plans stay with us; where and with
whom we test does not.
- **IBM Quantum** (ibm_kingston processor), 21–22 and 25 October 2026: nine sealed tests on entangled pairs while they
  wait — pair decay with and without an echo pulse, echo sequences (evenly spaced and in Fibonacci order), entanglement
  swapping and teleportation. Some predictions
  were confirmed, some refuted; both are shown below with their limits.
- **Quafu cloud** (Beijing Academy of Quantum Information Sciences), from 25 October 2026: a second, independent
  manufacturer. We read the published calibration of its processors every hour, and ran the first sealed test there on
  26 October (an entangled pair at zero wait on the Shenglian processor). Its result is below — the sealed evaluation was
  **not accepted**, and we say why.
- **IBM Quantum** (ibm_fez processor), 28 and 31 October 2026: two sealed runs of our random-number reference module on
  raw samples of all 156 qubits. Results below, with what they do and do not certify — the second run refuted one of its
  own predictions, and we say which.

The first step runs, on three small programs: a state transfer between two machines, a server-side program that
needs no pair, and an entanglement swap at a middle machine.
- The acceptance criteria were written down **before** the code.
- From the programs alone, the choreographer reproduces our earlier hand derivation exactly.
- The independent checker agrees with it, and all books balance.
- Four deliberately broken versions — a copied state, a pair with no ending, a quality lowered by one percent, a
  forgotten message delay — are each caught, for their own reason.
- Two runs produce byte-identical output.

What it already shows: for the entanglement swap, with memory figures published for today's hardware, only about one
run in four has the second pair arrive while the first is still good enough — yet a request format that cannot tie
the two pairs together would count both requests as served.

**21 October 2026 — first hardware check.** A prediction of how an entangled pair loses quality while it waits was
written down, sealed by its fingerprint, and then tested on an IBM quantum processor (two physical qubits, eleven
waiting times up to 800 µs, with and without one echo pulse). The sealed prediction matched the measurement at 9 of 11
points without the echo and at 11 of 11 with it, within the tolerance fixed in advance; a simpler model that ignores the
pair's phase rotation matched only 2 of 11. Most of the loss within the first 200 µs is recoverable by the echo — the two
accounts of our ledger, measured. Raw data, the sealed prediction and the evaluation are published in this repository
(`sealed-runs/2026-10-21_ibm_bell_v1/`). Limits: one device, one qubit pair, one day; waiting inside a chip, not a network
memory.

**21–22 October 2026 — six more sealed tests on the same processor.** Each followed the same rule: prediction written
and fingerprinted before the run, raw data revealed after (all under `sealed-runs/`). What they measured, with limits:
- *One echo is enough.* With 300 µs of waiting, one echo pulse recovers what can be recovered; two to sixteen pulses add
  nothing (energy decay sets the bound). The sealed prediction matched 6 of 6.
- *The pair must be calibrated, not the qubits.* Teleportation of six input states over a waiting pair, and an
  entanglement swap at a middle node, were both predicted to within 0.03 at 6 of 6 waiting times — but only when the pair's
  own decay was measured minutes before the run. A model built from the processor's daily per-qubit table missed the same
  points; the pair decayed faster than the table said in one test and slower in another.
- *A fresh calibration has a short life.* The same sealed teleportation prediction that matched 6 of 6 with a
  2.5-minute-old pair calibration matched 0 of 6 with a 96-minute-old one — while the processor's daily table stayed
  byte-identical between the two runs. Teleportation itself still worked (average fidelity 0.90 at zero wait, above the
  classical limit); only the prediction failed. Our network requests therefore carry the age of the pair calibration they
  rest on, and refuse ages beyond the measured ceiling (40 minutes good, 96 minutes bad; the band between is unmeasured).
- *Feed-forward costs nothing measurable here.* The live correction in the teleportation circuit scored the same as
  post-selecting the uncorrected branch (0.943 vs 0.943 at zero wait), so the classical feedback time is not a cost on this
  device at this scale.
Limits as before: one processor, one qubit pair or triple, two days; waiting inside a chip, not in a network memory;
the classical bound of 2/3 for teleportation is cleared, but nothing here is a network.

**26 October 2026 — a second manufacturer, and a correction that over-corrected.** The same sealed rule on the Quafu
Shenglian processor: two qubit pairs prepared as an entangled pair and measured in three bases, the prediction (0.993 and
0.972, from the vendor's calibration table) fingerprinted before the run, two runs of the byte-identical plan. What came out
(`sealed-runs/2026-10-25_quafu_r0s/`):
- *Both pairs are entangled without any correction:* raw fidelity 0.786 and 0.825 in the first run, 0.793 and 0.832 in the
  second — well above the 0.5 bound.
- *The sealed readout correction was wrong, and the sealed test is not accepted.* The plan corrected readout per qubit, the
  usual way. On one pair that produced correlations of 1.09–1.14, which is impossible (a correlation cannot exceed 1), yet the
  sealed acceptance still passed in the first run. A rule the plan lacked — every corrected correlation must stay physical —
  was written down before the second run; both runs fail it. The cause, measured from the same counts and confirmed by the
  independent arm: one qubit's readout depends on the state of its partner (it reads 0 with probability 0.958 or 0.810,
  a difference of 0.148 ± 0.005), which a per-qubit correction cannot represent.
- *What a pairwise correction gives, reported as post hoc:* with the pair's own 4×4 assignment matrix, fidelities 0.962 / 0.977
  and 0.971 / 0.991 (bootstrap of 500), all physical and all within the predicted band — but this was not in the sealed plan,
  so it is shown as an analysis, not as a passed prediction.
- *The vendor changed its calibration during the first 81-second job:* the circuits ran under two different calibration ids.
  The second run had one id and over-corrected the same way, so this was not the cause — but every plan now records the
  calibration id per circuit and requires a single one.
Limits: one machine, two runs, two pairs, zero wait (this cloud has no idle instruction).

**28 October 2026 — a random-number module on a real quantum source.** Our reference software for a quantum random-number
module (health tests in the style of SP 800-90B, an on-line min-entropy bound, a replay filter, SHA-256 conditioning, and a
receipt signed with two schemes, Ed25519 and ML-DSA-65) was run end to end on raw samples of an IBM processor: every one of
156 qubits put into an equal superposition with one gate and measured, 4096 times, with no mitigation of any kind — the raw
device, bias included. The plan (design minimum 6.0 bits of min-entropy per byte, four acceptance criteria) was fingerprinted
before the run (`sealed-runs/2026-10-28_ibm_qrng_r0/`):
- 79 872 raw bytes; health tests 0 failures; min-entropy estimate 7.52 bits per byte (a 99 % bound on the most common value),
  within the predicted 6.5–8.0; fraction of ones 0.5054; lag-1 correlation 0.0035. The module accepted the block and conditioned
  it to 37 024 output bytes; an independent checker, sharing no code with the module, re-derived every number from the raw file
  and the signed receipt. All four criteria met. 3 seconds of processor time.
- *What it does not certify:* the receipt says `statistical`. Statistics cannot distinguish a quantum source from a good
  classical generator; that needs physics evidence this test does not have, and the receipt will keep saying so until it does.
- Afterwards, outside the sealed plan, a per-qubit test showed 40 of 156 qubits below a 0.9 bit-per-bit bound at this shot
  count (bias and readout asymmetry). We did not tune the threshold to the data; it goes into the next sealed plan.
- The raw samples are published because this is an audit block. A production block of the module never keeps its raw samples:
  with a public conditioning function, the raw samples *are* the output.

**31 October 2026 — the same module, second sealed run: a per-qubit rule, and a prediction that failed.** The lesson of the
first run was written into the plan before any new data (`sealed-runs/2026-10-31_ibm_qrng_r1/`): every qubit is a channel; a
channel counts as broken when a 99 % bound leaves it less than 0.5 bit of min-entropy per bit; a broken channel is named in the
receipt and its bits count zero in the entropy accounting, but the block is not refused. Every number in the plan was derived by
a published script from the first run's raw samples — on those, the rule excludes exactly one qubit, where the 0.9 default had
failed 40. A public time-stamping authority stamped the plan at 09:06 UTC, the second arm's notary channel received it at 09:08
and returned its adversary call at 09:09; the processor created the job at 09:10:40 UTC — the provider's own record is in
`receipts/`.
- Six of seven criteria held: the module accepted the block (0 health failures, min-entropy estimate 7.57 bits per byte,
  fraction of ones 0.5057), no qubit fell below the 0.5-bit line, the per-channel accounting gave 7.30 bits per byte and sized the
  output (35 968 bytes), and the independent checker recomputed exclusion and accounting from the raw bytes. 3 seconds of
  processor time.
- **The seventh failed.** We had predicted that the per-qubit bias pattern measured on 28 October is a property of the device and
  would repeat (correlation at least 0.651; 0.90 expected). Measured: 0.36. The qubit that was badly biased on the 28th
  (p(1) = 0.277) read 0.514 three days later, while the vendor's published readout-error figure for it barely moved (0.33 →
  0.31); the qubit we had flagged as unexplained (0.595) read 0.486. The vendor's readout-error table was almost identical
  across the two days (correlation 0.95); the biases a user actually measures were not. So the bias is real on any given day
  (its spread is 2.4 times the sampling noise) but it drifts between days, and the published calibration does not predict it.
  The second arm had named this criterion as the most vulnerable one before the reveal — "calibration drift" — and it was right.
- *What it does not certify:* unchanged — `statistical`. One machine, two runs, three days apart. The next plan predicts the bias
  from a calibration taken minutes before the run, not days, and carries the calibration's age as a parameter.

**2 November 2026 — the same module, third sealed run: the bias is a property of the calibration, not of time.** The plan
(`sealed-runs/2026-11-02_ibm_qrng_r2/`) asked the question the second run had opened: does the per-qubit bias pattern repeat within
*minutes*, under one vendor calibration? Two jobs with the r1 circuit were submitted back to back (1.3 seconds apart, same vendor
`last_update` before and after); every number came from a published script run on the two earlier runs' raw samples; a public
time-stamping authority stamped the plan at 18:02 UTC, the second arm returned its adversary call at 18:04:48, and the processor
created the jobs at 18:05:31 and 18:05:32 UTC (provider records in `receipts/`). 6 seconds of processor time.
- Both blocks passed all six module criteria (accepted, 0 health failures, min-entropy 7.53 and 7.54 bits per byte, one excluded
  qubit each — the same one — accounting 7.25 and 7.23 bits per byte, checker PASS on both).
- **The bias repeats within minutes: correlation 0.91** between the two blocks (floor 0.622, 0.87 expected from the constant-bias
  model). The second arm's pre-registered control — shuffle one block's qubit labels 10 000 times — never reached it (maximum 0.69).
- **The age prediction failed.** We had predicted the correlation falls with the calibration's age. Today's pattern matches the
  five-day-old first run (0.85) far better than the two-day-old second run (0.47). The bias belongs to the *calibration state*, not
  to elapsed time: one qubit read p(1) = 0.277, then 0.514, then 0.256 and 0.259 across the four runs, while the vendor's readout-error
  table could not tell the states apart (0.94 against both). The second arm had named this criterion the most vulnerable before the reveal.
- *What it does not certify:* unchanged — `statistical`. One machine, four runs. The module's channel test keeps working from the
  current block only; a learned fingerprint is valid until the vendor's next `last_update`, and whether a pattern returns after a
  recalibration is the next sealed question.

**2 November 2026, evening — fourth sealed run: the pattern returns, and a validated prior pays the buyer.** The plan
(`sealed-runs/2026-11-02_ibm_qrng_r3/`) separated two questions and was stamped at 18:33 UTC; the vendor's next recalibration was the
trigger, and the processor created the two jobs at 18:41:38 and 18:41:39 UTC under a calibration stamped 18:20 UTC. The prior — the
afternoon run's two blocks — was chosen before the run, not after.
- *Physics:* after the recalibration the per-qubit bias pattern came back to the afternoon's state (correlation 0.91; 0.79 with the
  28 October run, 0.46 with the 31 October one), and the new state was stable in itself (0.92 between the two blocks). The same qubit
  was excluded again.
- *The buyer:* with the prior validated on the current block (correlation 0.91 above the 0.622 floor), the per-channel bound got
  tighter: +0.21 bit per byte of accounting and 1 056 more output bytes (+2.9 %) from the same raw block, while the bound still covered
  the hold-out block in 92 % of channels (floor 0.865). The prior's predicted exclusion list matched exactly, and it predicted the new
  block three times better than knowing nothing. The independent checker recomputed every arm from the raw bytes and the same prior file.
- *The rule that came out of it:* an old pattern may sharpen the bound only after it proves itself on the current block; a blind use
  of a stale pattern (the 31 October state) would have credited 0.19 bit per byte without evidence — shown in the sealed dry run and
  refused by the validated mode. Every criterion fixed before the data held. *What it does not certify:* unchanged — `statistical`.

**3 November 2026 — fifth sealed run: no third state, and the value of an old pattern is graded by its age.** The plan
(`sealed-runs/2026-11-03_ibm_qrng_r4/`) was stamped at 03:52 UTC; the vendor's next recalibration (03:27 UTC) was the trigger; the
processor created the two jobs at 03:54:28 and 03:54:29 UTC. Four earlier runs were chosen as priors *before* the run, by age.
- *Physics:* after the fourth recalibration we have watched, the per-qubit bias pattern is still the state seen on 28 October and
  twice on 2 November (correlations 0.78–0.87; 0.48 with the 31 October state), and the two new blocks agree at 0.92. The same qubit
  is excluded every time in this state.
- *The buyer:* a pattern one or two recalibrations old, validated on the current block, buys +0.20 bit per byte and 1 056 more output
  bytes; the five-day-old pattern of the same state still buys +0.13 and 544 bytes, with a few channels left out by the per-channel
  check; the pattern from the other state is refused. Every tighter bound still covered the hold-out block in 88–92 % of channels.
  Every criterion fixed before the data held; the independent checker recomputed all five receipt stores from the raw bytes.
- *What it does not certify:* unchanged — `statistical`. Two states on one machine so far, one of them seen once.

**From 25 October 2026 — watching the vendors' own numbers, every hour.** Two manufacturers' published calibrations are
archived hourly by a read-only engine, recomputed by an independent checker, and break-tested with planted faults (a third
vendor's public history is archived as well; its terms do not allow us to publish results from it). What the archive shows so
far, as measured:
- On Quafu, across 25 hourly pulls over three days, the published two-qubit gate fidelities of all three machines never
  changed; a "new calibration" moved one qubit's T1 on one machine and the T2 values on another. One machine's published
  summary medians (T1 71.507 µs, T2 23.856 µs) differ from the medians of its own raw per-qubit table (70.578 µs, 23.790 µs).
- On IBM, the "last updated" stamp is often minutes old while the numbers behind it are hours old: on 30 October the ibm_fez
  stamp was 0.3 h old, its T1/T2 values 15.7 h and its two-qubit errors 14.9 h; on ibm_kingston 0.8 h against 14.1 h and 10.4 h.
  The age of a number is not the age of its stamp — our requests carry the former.
- The calibration swap inside one job (above) was found by the same archive.
Limits: the numbers are the vendors' own; what we measure is that they were published, when, and how old they were at the
time. The archive is young (days), and it does not test the processors.

These are small test programs and a model, not production workloads. That is exactly why the next steps are tests
against independent measurement.
