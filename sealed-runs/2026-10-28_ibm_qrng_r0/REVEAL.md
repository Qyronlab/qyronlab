# Reveal — QRNG reference module on real quantum samples (IBM ibm_fez), 2026-10-28

**Sealed before the run:** `plan_r0.json` (backend, circuit, shots, packing, design entropy 6.0 bits per byte, K1–K4),
sha256 0c3f39db…. Run: job dbh3lghq260s73bued8g, 156 qubits each put into |+⟩ with one gate and measured, 4096 shots, no dynamical
decoupling, no twirling, no readout mitigation — the raw device, bias included. 3 seconds of processor time.

**What came out** (`meta.json`, `raw.bin` 79 872 bytes, sha256 01edd075…, `ledger.jsonl` the signed receipt):
- K1 the module accepted the block: repetition-count and adaptive-proportion health tests 0 failures, min-entropy estimate 7.52 bits
  per byte (99 % upper bound on the most common value) against the design minimum 6.0, lag-1 correlation 0.0035 (bound 0.0177), no replay.
- K2 min-entropy within the predicted [6.5, 8.0]. K3 fraction of ones 0.5054 within [0.40, 0.60]. K4 the independent checker
  (own code, imports nothing from the module) re-derived every number from the raw file and the receipt: PASS.
- Output: 37 024 bytes after SHA-256 conditioning (512 estimated bits per chunk, factor-2 margin). Receipt signed with Ed25519 and
  ML-DSA-65; this run is an *audit* block, so the raw samples are kept for anyone to recompute.
- **What this does not say:** the receipt's certification is `statistical`. Statistics cannot tell a quantum source from a good
  classical generator; that needs physics evidence this test does not have.
- Afterwards, outside the sealed plan: a per-qubit test shows 40 of 156 qubits below a 0.9 bit/bit lower bound at this shot count
  (bias and readout asymmetry). Not tuned post hoc; the per-channel threshold goes into the next sealed plan.

**Limits.** One processor, one run, 4096 shots; a free-tier allowance (600 s per 28 days); the module is reference software, not a device.
