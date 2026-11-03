# Qubit repeater — consultation record (two arms)

Opened 22 October 2026 at the owner's request. Two arms discuss the qubit repeater ("the external qubit forwarder"),
split the work, and start. This file is the public, substantive record: every question with its owner and state, every
result with its source and limit. The exchange itself runs on a private channel; what is publishable lands here.
States: **open** · **measured** (our own sealed test, raw data under `sealed-runs/`) · **read** (a published source, arXiv ID)
· **assumed** (named as such). Nothing moves from read or assumed to measured without a sealed test.

## Framing
A courier carries a capsule; the capsule is the entangled pair; every machine on the road has an amplifier — and an
amplifier for a qubit is a repeater: a node that catches a photon into a memory, waits, and swaps. Nothing is lost, it
changes form: the choreographer keeps two accounts of the waiting cost — recoverable (undone by one echo) and final
(energy decay and what the echo cannot undo). A third account, the catch, is the probability that the photon is stored
at all; expected attempts per link = 1 / catch efficiency.

## What is measured (ours, sealed then revealed)
| Date | Test | Result | Limit |
|---|---|---|---|
| 2026-10-21 | Pair decay while waiting (Bell v1) | 9/11 raw, 11/11 echo within 0.04; the pair rotates (−3.1 kHz) ≠ sum of single-qubit values | one device, one pair, one day |
| 2026-10-21 | Echo count (DD v0) | one echo recovers what is recoverable; 2–16 add nothing; 6/6 | 300 µs, one pair |
| 2026-10-21 | Entanglement swap at a middle node (swap v1) | 6/6 within 0.04 with the pair's own decay measured (τ 174.5 µs vs 147 from the daily table) | one chain of four qubits |
| 2026-10-22 | Teleportation over a waiting pair (teleport v1) | 6/6 within 0.03 with a 2.5-min-old pair calibration; F̄₀ 0.944 | one triple, one day |
| 2026-10-22 | Same prediction, 96-min-old calibration | 0/6; F̄₀ 0.904; the processor's daily table byte-identical between the runs | single repeat; the 40–96 min band unmeasured |
| 2026-10-22 | Feed-forward cost | dynamic correction 0.943 = post-selected 0.943 at zero wait | derived from the same data, not a separate sealed test |

## What is read (catch efficiency, photon → memory)
| Memory | Catch | Storage | Temperature | Source |
|---|---|---|---|---|
| Er:YSO (2021) | 0.035 % | — | cryogenic | Ma et al. 2021 |
| Er:YSO / SiC | 8.3 % | — | 7 mK | arXiv:2607.01324 |
| Cold Rb ensemble | 85 % | 28 µs | cold atoms | arXiv:2603.01156 |
| NV ↔ 795 nm conversion | ≈ 7 % (two-step 32 % × 22 %) | teleport 75.5 % | cryogenic | arXiv:2403.18581 |
| Warm Rb vapour, 2U rack | > 5 % storage-and-retrieval (not catch alone) | 160 µs = 1/e of retrieval efficiency | room temperature | arXiv:2205.13091 (reading corrected by Arm B) |
| NV + ¹³C nuclear spin | — | 3.3 ms | room temperature | arXiv:1210.8278 |
| Warm Cs vapour, Raman (62 °C) | storage 43 %, single read pulse 56.5 % — write and read reported SEPARATELY (optical energy bookkeeping, not heralded single-photon capture) | — | room temperature | arXiv:1203.2328 (Reim et al.), found by Arm B |
| Warm Cs vapour, Raman (105 °C) | storage 39.5 ± 0.6 %, internal write+read 14.6 ± 0.1 % at 200 ns; end-to-end ≈ 0.3 % | 200 ns shown | room temperature | Zhang et al., Nature Sensors 2026 (s44460-026-00073-9), found by Arm B; supplementary not audited |

## Choreographer finding (step 2, acceptance L1–L5 green)
With today's published memory figures, only about one run in four has the second pair arrive while the first is still
usable; a request format that cannot tie two pairs together counts both requests as served. The request now carries:
pair, minimum delivered quality, echo-account window, catch efficiency, expected attempts, the age of the pair
calibration (ceiling 2400 s), and together-ties.

## Question list
| # | Question | Owner | State | Moved by |
|---|---|---|---|---|
| Q1 | Do the revealed raw data reproduce (Bell v1, DD, swap v0/v1, teleport v0/v1, 96-min run) in independent code? | Arm B | **measured** (2026-10-22, two rounds): all eight board tests recomputed from the raw count dictionaries with independent code; every K1 count matches the reports (Bell v0 1/10 raw, 2/10 echo; Bell v1 9/11, 11/11; DD 6/6; teleport v0 1/6, 6/6; swap v0 4/6, v1 6/6; teleport v1 6/6; 96-min 0/6). Provenance (2026-10-23): pre-run publication is **measured for teleport v1** by two third-party clocks (GitHub server-side push 03:51:07Z < processor job created 03:51:22.846Z, provider record bytes in receipts/); for v1b it stays **unmeasured** (no GitHub push event listed; the lab's own notary is not an independent clock, as Arm B stated). Arm B's notary audit found the stated hash rule imprecise: the entry `type` field is outside the hash (integrity gap, reported to the code owner) | Arm B audits #9, #16, notary audit |
| Q2 | Is the request shape {pair, F_min, window(echo), catch_eta, expected_attempts, pair_calibration_age, ties} complete for a repeater node? | Arm B → both | **answered by Arm B (read + arithmetic), accepted by Arm A**: not complete — catch_eta must split into write (capture) efficiency, time-dependent retrieval efficiency, heralding probability and false-herald rate; add source/channel/detector transmission, attempt spacing, classical latency, memory mode count, swap success/error, and F_min at the final use time; keep pair_calibration_age separate. **built** 2026-10-22 evening: the request carries write / read(t) / herald with false-herald rate, transmission, attempt spacing, classical latency, modes, swap success/error, link probability and expected attempts, an echo-account basis per memory (measured / assumed — assumed is marked, not planned on), F_min at final use; acceptance L1–L5 green, break tests 8/8 (a longer hold raises expected attempts through the read decay; zero write efficiency → infeasible). Every link number is *stated* until Q8 delivers partner data. **Compared with the QEGP link-layer request (Dahlberg et al. 2019, read by Arm B from the delivered excerpt, 2026-10-23):** CREATE carries remote node, type (keep/measure), number of pairs, atomic, consecutive, t_max, purpose ID, priority and F_min; the OK reply carries pair ID, qubit ID, goodness, measurement outcome and creation time. Overlaps: F_min and a deadline. Absent there: the three catch accounts, calibration age, expected attempts, echo basis (the words attempt / calibration / echo do not occur in the CREATE list). Rarely changing hardware data are queried separately in that design | Arm B, 2026-10-22; QEGP comparison 2026-10-23 |
| Q3 | Ranked table of repeater memories with the catch mechanism, the storage limit and what is testable at room temperature | Arm B | open | — |
| Q4 | Is there a repeater design where the catch is not the bottleneck (heralded absorption, emitter-based)? Mechanism, not just paper | Arm B | open | — |
| Q5 | Is warm Rb vapour (5 %, 160 µs) enough for a first node if planning only on the echo account with a fresh pair calibration? | both | **corrected**: Arm A's 'yes for a two-node demo' is withdrawn. Arm B: the paper's > 5 % is storage-AND-retrieval efficiency, not a separately measured catch probability, and 160 µs is the 1/e constant of retrieval efficiency, not a deadline; the IBM-measured echo account cannot be transferred to vapour (diffusion, field gradients) without measurement. Verdict: plausible lab demonstrator candidate; node usefulness unmeasured; chain unmeasured | Arm B, 2026-10-22 |
| Q6 | Where in the 40–96 min band does a pair calibration stop predicting? | Arm A | **measured, partial** (2026-10-22 evening, v1b): 40.5 min → K1 5/6 (prediction holds); with the morning's 2.5 min 6/6 and 96 min 0/6 the band is now [41, 96] min; Arm B's pre-registered call (no verdict for 40–60 min) undecided. Processor timestamps preserved in receipts/ | v1b reveal |
| Q7 | Room-temperature passport of the memory node: what can be measured warm, with acceptance written first | Arm A | open | — |
| Q8 | A partner measurement, bound to a protocol, of write efficiency, time-dependent read efficiency and heralding (with false-herald rate) on one warm memory — the first measured values of the three catch accounts. Literature pattern exists (Reim 2012; Zhang 2026); for the Rb device studied, write_eta, herald_p, false_herald_rate are UNMEASURED | Arm A formulates the request (sealed-first), Arm B drafts the acceptance | **acceptance sheet v0.1 received** (Arm B, 2026-10-22 evening, 5250 bytes, sha256 b7102e4b…59e1); partner request draft ready, awaiting the lab's decision on recipients; all three numerical accounts UNMEASURED | Arm B sheet v0.1 |
| Q9 | **Planned test (before code):** the request shape measured end to end on one chip — a heralded, attempt-based 'catch' emulated by an ancilla rotation + measurement (p per attempt, the measurement is the herald, readout error = false herald), up to 3 nested attempts, the first pair waiting meanwhile, swap on success; sealed prediction = {attempt distribution, outer-pair fidelity per attempt index, the request's feasible verdict per variant}; acceptance K1–K6 fixed before code (fidelity per cell ±0.04, attempt distribution TV ≤ 0.05, expected attempts ±0.3, p = 0 control infeasible and F ≈ ¼, byte-identical, the request's verdict right 4/4). Arm B: adversary call + acceptance review before code | Arm A plans, Arm B reviews | **plan v1 written 2026-10-23** after Arm B's review of v0 (12 mandatory cells, n ≥ 450 per basis and cell → 4000 shots per circuit, herald rate readout-corrected q = p(1−f_neg)+(1−p)f_pos, k = 0 counted, interleaved variants with per-attempt conditional rates and time-block drift, simulated negative-control band, per-branch waiting measured, five separate hashes, K6 with bootstrap bounds and UNMEASURED on overlap; ≈ 70–85 s of the remaining 120 s, one run, no repeat); under Arm B's second review; no code before it | Arm B #36 → v1 |
| Q10 | **Proposed 2026-10-23 (relaxation-mode frame, 'quantum Mpemba' literature):** does the single-rate calibration table (T₁, T₂ per qubit) predict the *order* in which three two-qubit states (Bell, product |+⟩|+⟩, |11⟩) relax towards the ground state on the same calibrated pair, at six wait times? Mechanism: relaxation = sum of generator modes with device-fixed rates and state-chosen weights; a farther state can arrive first if it carries less weight on the slowest mode. Candidate explanation for the calibration-age ceiling (rates unchanged, mode weights drifting) and the v1b +0.033 residual at 300 µs. Sealed prediction = 18 curve cells ±0.04 plus 18 pairwise-order cells; an order reversal the model does not predict, larger than twice the half-width, would be the finding. ≈ 30 s (reduced form 15 s); decided 2026-10-23: Q9 first, Q10 in November. Arm B read the reset-via-Mpemba paper (Lejeune et al. 2026) from delivered text: speed-up needs T₂ > T₁ (asymptotic factor T₂/T₁); on the lab's evening triple only one qubit meets it (≈ 5 %), so the method does not apply to the Q9 reset step now | Arm A plans, Arm B reads the literature as adversary | open (plan v0 written; order decided) | Arm B reading 2026-10-23 |
| Q11 | **Company-side readiness thread (opened 2026-10-23):** the chains' own post-quantum signature proposals (Bitcoin, Ethereum) read with identifiers and status — what shape the second signature takes on-chain, when | Arm B | open | — |
| Q12 | QKD numbers checked against sources: metro key rates (kbit/s–Mbit/s deployed; ~110 Mbit/s lab record over 10 km), satellite rates (kbit/s) and link latency (ms) — the claim 'hundreds of Mbit/s typical' refuted or confirmed | Arm B | open | — |
| Q13 | Bank-side requirement list for a second-signature slot (audit trail, rotation with log, HSM binding, exposed-key list, scheme agility, independent verifier) beyond the seat's five rules; every line measurable on a demo | both | open | — |
| Q14 | The seat as a signing plugin on an open-source wallet's signing path: which wallet, where, the minimal change; acceptance = two-scheme signature accepted by a verifier not written by the lab | Arm A | open | — |

## Work split (draft, under discussion)
- **Arm A (owner arm, the lab):** hardware line with sealed predictions; the request shape and ledger with break tests; the room-temperature passport.
- **Arm B (independent arm, the partner side):** independent recomputation; memory survey with mechanism; adversary role before each reveal; number-and-date
  check of the site's translations.
- **Shared:** this question list; content on the private channel, status on the main one; publishable results here and,
  when agreed, on the site.

## Arm B — independent audit (2026-10-22)
Checked at commit c1934ba (tree b057c72): the six evidence-board files match their SHA-256; all eight sealed hashes match the
prediction bytes, the sidecars and the fingerprint documents; every series and acceptance field on the board matches the
named report; `tools/build_results.py` regenerates `data/results.json` identically apart from the timestamp. Recomputed from the
raw count dictionaries with independent code: teleport v1 fresh 6/6 (max |error| 0.0180), 96-minute run 0/6 (max 0.1279);
swap v0 4/6 (max 0.0485), swap v1 6/6 (max 0.0264). Verdict: measured, partial — not a GO for all eight claims.
**Stated limit:** equality of a prediction file and a fingerprint file does not prove the fingerprint was published *before*
the run. What exists for that: the fingerprint's commit time and the bus message carrying the hash both precede the job's
creation time recorded by the processor; from 22 October evening on, every fingerprint is also posted to Arm B's own
notarised channel before the run (v1b: posted 17:3x UTC, job submitted 17:46 UTC), so Arm B can measure the order itself.

## Company-side readiness thread (opened 2026-10-23)
Scope: how the second-signature slot and the seat sit inside a wallet, a chain service or a bank before the NIST transition
dates (NIST IR 8547, Nov 2024: 112-bit classical schemes deprecated after 2030, disallowed after 2035). Threat model stated
precisely: Shor breaks asymmetric schemes from an *exposed public key* (spend, forge); Grover halves hash and symmetric
strength, so SHA-256/Keccak and hash-based signatures stay sound; on a public chain the 'harvest now' risk is key derivation,
not data decryption. QKD is key agreement between two points, not a signature and not a randomness source. Every number in
this thread carries 'measured' or 'read, with source'. Questions Q11–Q14 above.

**First deliverable, measured 2026-10-23 (two independent runs on the lab's machine, under load, so times are upper bounds;
sizes byte-identical in both runs and equal to the standards' tables):**

| scheme | public key | signature | keygen (median) | sign | verify |
|---|---|---|---|---|---|
| Ed25519 | 32 B | 64 B | 0.08 ms | 0.07 ms | 0.22 ms |
| ML-DSA-65 (FIPS 204) | 1 952 B | 3 309 B | 0.47 ms | 1.65 ms | 0.40 ms |
| SPHINCS+-SHA2-128s (hash-based; FIPS 205 predecessor encoding) | 32 B | 7 856 B | 380 ms | 2 683 ms | 2.6 ms |

The seat's seal (one attestation per scheme, canonical JSON): 7 195 B with two schemes, 23 141 B with three. Reading for a
company: the second signature slot costs about 3.3 KB and 2 ms per signature next to Ed25519; the hash-based third scheme
costs 7.9 KB and about 2.7 s to sign (2.6 ms to verify), so it suits rare, high-value seals rather than per-transaction signing.
Method note: ML-DSA signing uses rejection sampling, so its median needs ≥ 2000 samples to reproduce within 1 %; with 100
samples the two runs differed by 26 %. Arm B has the raw result files for recomputation.

**Arm B's reading (2026-10-23, from the two N = 100 result files):** sizes and seal sizes recomputed and equal (negative control:
a one-byte size change and a 6 % time change were both flagged). **The pre-registered acceptance "all timings within 5 %"
FAILED on 1 of 9 values** (ML-DSA-65 sign, 26.07 %); the N = 2000 rerun agrees to 0.8 % but is a post-hoc measurement, not the
criterion passing. Arm B's GO is pending the standards' tables, the measuring program's bytes and the raw per-sample data.
Deposited for that in `research/z5/`: both measuring programs, the four N = 100 / N = 2000 result files, and two fresh N = 2000
ML-DSA-65 runs with every sample (`z5_mldsa65_n2000_raw_v2_run{1,2}.json`; medians 1.569 / 1.536 ms, 2.1 % apart, p10 0.69 ms,
p90 4.28 ms, load 15.5), with `SHA256SUMS`. Seal layout, answering Arm B's 15 946-byte question: each attestation is canonical
JSON with the signature hex-encoded, so the hash-based attestation is 15 712 hex characters + 233 bytes of fields = 15 945 B.
Environment: Python 3.12.3, cryptography 50.0.2, pyspx 0.5.0. Status: measured; Arm B verification in progress; no GO yet.

## Arm B — notary audit and the lab's answer (2026-10-22 evening → 2026-10-23 morning)
Arm B recomputed the notarised chain slice handed over for v1b: 50 links and two Ed25519-signed checkpoints valid, a
modified head rejected. Two findings. (1) The hash rule the lab had stated was **refuted**: the entry hash covers
{seq, prev_hash, received_at_ms, envelope_sha256, sender_identity, sender_auth, recipient, kind, decision, reason,
claimed_ts_ms, cursor} and *not* the entry's `type` field (0/50 with the stated rule, 50/50 with `type` excluded) — an
integrity gap, now reported to the code owner with a versioned-schema proposal. (2) The fingerprint entry's envelope hash
differed from the delivery entry's hash; the lab reproduced both byte-for-byte from the stored row (the submitted message
of 8 fields, 1443 bytes, vs. the delivered record of 11 fields, 1495 bytes; canonical JSON fell back to a sorted-key dump
because the client timestamp exceeds the JCS integer range) and handed Arm B the recipe to reproduce them from its own copy.
**Anchors.** Arm B's position, accepted: the lab's own notary is not an independent clock. What exists: for teleport v1 the
GitHub server-side push time of the fingerprint commit (03:51:07Z) precedes the processor's job-creation time
(03:51:22.846Z) — two third-party clocks, 15.8 s apart (`sealed-runs/2026-10-22_ibm_teleport_v1/provenance/`). For v1b the
GitHub Events listing lacks the relevant push, so the external anchor is **unmeasured**; Arm B's own receipt of the
fingerprint on its machine (17:36:33Z, before the job at 17:46:22.751Z) is Arm B's to weigh. From now on every sealed file
gets an RFC 3161 token from a public time-stamping authority *before* submission, stored beside the prediction
(`provenance/tsa/`, recipe tested 2026-10-23). Provider receipts: raw job/metrics responses with SHA-256 are deposited; the
raw *results* endpoint response will be deposited too from the next run so counts can be checked against provider bytes.

## Arm B — pre-registered adversary call on teleport v1b (2026-10-22, before the run)
Made from the sealed-test notice and the earlier v1 / 96-minute data only; no v1b result opened. **If the hardware start is
≥ 60 minutes after the 17:05:53 UTC pair calibration:** K1 < 5/6 within ±0.03, measured F̄ below the sealed prediction at one
or more of 25, 50, 100, 150 µs, with the largest negative residual around 50–100 µs rather than only at the 300 µs tail
(reason: in the 96-minute run the residual was negative everywhere and largest at 50–100 µs, ≈ −0.128, and t = 0 also moved
down; stale pair decay and the t = 0 gate factor can both contribute). **If the start is 40–60 minutes after:** no pass/fail
call — the 40-minute (good) and 96-minute (bad) examples leave that interval open. A failure at t = 0 would specifically
challenge the assumption that the t = 0 factor stays fresh, not only the decay constant. Recorded here before the reveal; the
reveal will carry the processor's job-creation timestamp.

## Arm B — first request-shape challenge (2026-10-22; read + explicit arithmetic, not a hardware measurement)
Toy arithmetic from Arm B, stated as illustration only: if a complete per-link trial had p = 0.05 independently, simultaneous
success of two links is p² = 0.0025 (400 paired trials expected); if the first success can wait for N second-link trials at
one per 10 µs over 160 µs, P(success by N = 16) = 1 − 0.95¹⁶ = 0.56 — but 160 µs is a decay constant, so the usable probability
must be weighted by the retrieval efficiency at time t and by the delivered-fidelity threshold, not truncated at N = 16.
These numbers are not a node feasibility estimate. Consequence for the lab: the 'catch' account becomes three accounts
(write, read(t), herald), the echo account carries a per-memory label *measured / assumed*, and any node claim waits for an
end-to-end link probability and timing measured on an instrument.

## Q8 — acceptance requirements (Arm B, 2026-10-22; adopted by Arm A)
A partner measurement of the three catch accounts counts only if it names its operational denominators: photons in per trial,
the window actually usable for writing, the read-back signal, the herald event and the false herald. Classical pulse-energy
bookkeeping (as in Reim 2012) and heralded single-photon capture are different bases and never share one "write efficiency,
measured" label. Read(t): pre-fixed t points, raw counters, background, fit range, uncertainty. Herald: event window,
dark/false events, conditional ratio. Without the partner's raw data all of this is a requirement, not a number.
Caveat on the request shape (Arm B): the link probability and the expected attempts assume independent, identical trials;
common-mode noise, a deadline and parallel modes need their own test — recorded next to the field, not hidden in it.

**Acceptance sheet v0.1 (Arm B, 2026-10-22 evening; 5250 bytes, sha256 b7102e4b248e9019f73faac4ad3e86c40d9d0498717035ecf7a3a8d3d43e59e1; adopted by Arm A as the request's acceptance):**
1. *Lock the protocol first:* device, transition, temperature, field and its uniformity, wavelength/bandwidth, pulses, timing
   windows, detector chain, trial clock, software revisions; seal a protocol hash, acceptance definitions, fit model, t-grid,
   exclusion rules and the intended use time before the first accepted run; UTC instrument time with uncertainty, run IDs,
   calibration age, every trial's raw time tags or count table; failed/empty trials stay in the denominator; raw files,
   calibrations and analysis code hashable; reveal only after the sealed request.
2. *Write account:* denominator = photons (or mean photon number) at a named optical plane inside the predeclared writable
   window, source and coupling losses calibrated separately; report leaked energy/counts during write and retrieved signal in
   a disjoint read window; a weak-coherent-pulse energy ratio is a classical-probe end-to-end efficiency and is labelled so.
3. *Read(t) account:* at least the near-zero reference plus a range bracketing the proposed use time with a point beyond it;
   per hold point the eligible trials, herald strata, raw retrieved counts, background, timing window, calibrated losses and
   uncertainty; the predeclared fit form R(t) = R₀·exp(−t/τ) + B only if the residuals allow it.
4. *Herald account:* herald detector, event window, trial opportunity and which physical event it claims; N_eligible, N_herald,
   N_true_joint, N_false_joint, N_no_herald with a predeclared truth method and raw event IDs; P(H|eligible), precision,
   sensitivity, false-herald probability.
5. *Recomputation:* Arm B must recompute every numerator, denominator, correction, fit and uncertainty from the supplied raw
   bytes and calibration files; tolerance and minimum sample budget fixed per metric before measurement; a missing
   denominator, correction, truth channel or loss calibration yields UNMEASURED for that field.
Literature context named by Arm B (not a substitute for partner data): Reim et al., PRL 107, 053603 (2011); Buser et al., PRX
Quantum 3, 020349 (2022). Verdict: acceptance protocol *proposed*; the measurements themselves UNMEASURED until a partner
instrument delivers raw bytes under the sealed protocol.
