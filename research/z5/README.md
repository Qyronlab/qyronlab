# Z5 — measured size/time table for the seat's three signature schemes (2026-10-23)

Raw material for Arm B's recomputation of the table in `../REPEATER_CONSULTATION.md` ("First deliverable, measured 2026-10-23").
Hashes of every file: `SHA256SUMS` (`sha256sum -c SHA256SUMS`).

| file | what it is |
|---|---|
| `z5_meret_ido.py` | the measuring program for all three schemes + the seal sizes; run as `python z5_meret_ido.py 100` (N = 100) through the seat's `attest` registry (cryptography 50.0.2 for Ed25519 and ML-DSA-65, PySPX 0.5.0 for SPHINCS+-SHA2-128s; Python 3.12.3) |
| `z5_run1.json`, `z5_run2.json` | the two independent N = 100 runs (separate processes). Sizes byte-identical; 8 of 9 timings within 3.64 %; ML-DSA-65 sign 2.4252 vs 1.7930 ms = 26.07 % → the pre-registered "all timings within 5 %" criterion FAILED |
| `z5_mldsa_n2000_run1.json`, `..._run2.json` | the post-hoc N = 2000 ML-DSA-65 rerun of the same day (medians only; produced by a 12-line one-off program with the same `med()` function as `z5_meret_ido.py`, kept with its hash in the two arms' channel) |
| `z5_sema_n.py` | the v2 per-scheme measurer: writes every sample to a raw file (sha256 in the summary), reports median / p10 / p90 / min / max and the load average before and after; run as `python z5_sema_n.py ml-dsa-65 2000 raw.json` |
| `z5_mldsa65_n2000_v2_run{1,2}.json` | two fresh independent N = 2000 ML-DSA-65 runs with v2: sign median 1.5694 / 1.5363 ms (2.11 %), keygen 0.86 %, verify 0.36 %; p10 0.69 ms, p90 4.28 ms, max 13.3 ms; load average ≈ 15.5 |
| `z5_mldsa65_n2000_raw_v2_run{1,2}.json` | all 3 × 2000 samples (ms) of those two runs, so every summary number can be recomputed |

Seal layout (answers the 23 141 − 7 195 = 15 946 B question): one attestation per scheme, canonical JSON (sorted keys, no spaces,
ASCII) with keys `audience, claim, evidence, outcome, scheme, signer, subject, version, witnesses`; `evidence` is the signature in
hex, 2 characters per byte. Measured attestation sizes: Ed25519 350 B (128 hex), ML-DSA-65 6 842 B (6 618 hex), SPHINCS+-128s
15 945 B (15 712 hex); the list adds `[`, `,`, `]`: 3 B for 2 elements, 4 B for 3. 350 + 6 842 + 3 = 7 195 and
350 + 6 842 + 15 945 + 4 = 23 141, byte-exact. The `signer` field is fixed-length (`sha256:` + 64 hex), so the seal size does
not depend on the generated key. (An earlier version of this file wrote +7/+10 and "≈"; Arm B caught the two-byte discrepancy.)

Standards the sizes are compared with: FIPS 204 Table 2 (ML-DSA-65: pk 1952, sig 3309), FIPS 205 Table 2 (SLH-DSA-SHA2-128s:
pk 32, sig 7 856), RFC 8032 §5.1.5–5.1.6 (Ed25519: pk 32, sig 64). Times were measured on a loaded machine and are upper bounds
for that machine only; nothing here claims times for other hardware.
