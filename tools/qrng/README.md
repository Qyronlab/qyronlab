# QRNG reference module — the software that produced the receipts under `sealed-runs/*_ibm_qrng_*`

Three files, Python 3.10+ and the `cryptography` package. **ML-DSA-65 needs `cryptography` 45 or newer** (the module cannot run
without it; the checker can). On an older `cryptography` (e.g. 41 on Ubuntu 24.04's system Python) the checker still verifies
Ed25519, the hash chain and every recomputed number, reports `"mldsa65": "UNAVAILABLE(...)"` and its verdict is **PASS-PARTIAL
(rc 2), never PASS** — the second signature was not checked. `pip install "cryptography>=45"` in a venv gives the full PASS.
No network, no other dependency.

| file | role |
|---|---|
| `qrng_modul.py` | the module: health tests (SP 800-90B style), most-common-value min-entropy at the 99 % bound, lag-1, replay check, optional per-channel rule (`--channels N --h-bit H --channel-policy refuse\|exclude`) with per-channel entropy accounting, SHA-256 conditioning, Ed25519 + ML-DSA-65 signed receipt chain |
| `qrng_fuggetlen.py` | the buyer's checker: recomputes every number of a ledger from the raw bytes with its own code (imports nothing from the module), verifies both signatures and the chain, refuses any receipt that claims more than "statistical" certification |
| `tores_qrng.py` | break test: 71 cases, including planted-insider cases that the checker must catch; `QM_MODUL=<path>` runs it against a mutant module, `QM_CHK=<path>` against a mutant checker (the test must then fail somewhere) |

## A prior from earlier blocks (r3 design, 2 November 2026)

r2 showed that the per-qubit bias is a property of the vendor's calibration state (two blocks 1.3 s apart agree at r = 0.91; a run five
days old under the same state agrees at 0.85, a run two days old under another state at 0.47). `qrng_prior.py` sums the per-channel
counts of earlier raw blocks into a prior file (it carries the sha256 of every raw it was built from). The module takes it with
`--prior FILE --prior-mode validated|blind --prior-r-min R`:

- *validated* (the production mode): the prior is used only if the current block correlates with it, Pearson r >= R (default 0.622,
  the r2 floor) AND the per-channel two-proportion z between prior and current looks like the same probabilities (mean |z| <= 1.5;
  measured 0.76-0.92 for blocks under one calibration); a channel is combined only if its own |z| <= 4. The second condition is the
  second arm's finding of 3 November 2026: Pearson r is blind to a common offset or scale, so a prior with the same *order* of biases
  but a larger magnitude passed the r gate and, combined, excluded 78 of 156 channels and halved the accounting (that counterexample
  is now break-test case 7b, mean |z| = 3.29, refused). When used, the per-channel 99 % bound of the channels that *stay in* is taken at the combined counts - a
  tighter bound, hence more credit. The broken-channel decision itself is the current block's alone: the second arm's second
  counterexample (3 November, break-test case 7c) showed that at a channel rule sitting exactly on the entropy threshold a compatible
  prior would otherwise tip every channel into exclusion and zero the output; now a prior can only refine credit, and a compatible
  prior can lower it by a small amount (7.208 -> 7.190 bit/byte in that example), never to zero. "Never worse than no prior" is still
  **not** a theorem; the receipt carries r, z and the channel count combined, and the buyer recomputes all of it;
- *blind*: always used - a test arm that shows what an unvalidated old pattern would do to the buyer's result.

The receipt records the prior's sha256, mode, R, the measured r, whether it was used, and the channels the prior alone would have
excluded. The buyer passes the same file (`qrng_fuggetlen.py DIR --prior FILE`) and recomputes r, the decision and the accounting; a
receipt that cites a prior the buyer was not given, an altered prior file, or an insider-signed receipt that claims `used` against its
own r, all FAIL (break test sections 7, 7b and 7c, 19 cases; planted mutants - a module that ignores R, a checker that skips the comparison, a module and a
checker without the z gate - each turn only the matching cases red). The accounting weights stay the current block's bits: the prior sharpens the estimate of each
channel's bias, it never adds bits to the output.

## Recomputing the r4 run (3 November 2026) from the committed bytes

Under `sealed-runs/2026-11-03_ibm_qrng_r4/`: block E five ways (`E/module_none`, `E/module_P1_r3CD`, `E/module_P2_r2AB`, `E/module_P3_r0`,
`E/module_P4_r1`) and block F (`F/module_none`); the four prior files sit next to them (rebuild each with `qrng_prior.py` from the
raw files its `raw_sha256` list names):

    python3 -I tools/qrng/qrng_fuggetlen.py sealed-runs/2026-11-03_ibm_qrng_r4/E/module_P1_r3CD --expect-rows 1 --prior sealed-runs/2026-11-03_ibm_qrng_r4/prior_r3CD.json

The plan's numbers: `sealed-runs/2026-11-03_ibm_qrng_r4/qrng_r4_numbers.py` (env `QRNG_JOSLATOK`, `QRNG_TOOLS`).

## Recomputing the r3 run (sealed 2 November 2026, run after the vendor's next recalibration) from the committed bytes

Under `sealed-runs/2026-11-02_ibm_qrng_r3/`: block C three ways (`C/module_none`, `C/module_validated`, `C/module_blind`) and block D
(`D/module_none`); the prior the receipts cite is `prior_r2AB.json` (rebuild it: `qrng_prior.py --channels 156 --out P.json
sealed-runs/2026-11-02_ibm_qrng_r2/A/raw.bin sealed-runs/2026-11-02_ibm_qrng_r2/B/raw.bin`, same sha256):

    python3 -I tools/qrng/qrng_fuggetlen.py sealed-runs/2026-11-02_ibm_qrng_r3/C/module_validated --expect-rows 1 --prior sealed-runs/2026-11-02_ibm_qrng_r3/prior_r2AB.json
    python3 -I tools/qrng/qrng_fuggetlen.py sealed-runs/2026-11-02_ibm_qrng_r3/C/module_blind --expect-rows 1 --prior sealed-runs/2026-11-02_ibm_qrng_r3/prior_r2AB.json
    python3 -I tools/qrng/qrng_fuggetlen.py sealed-runs/2026-11-02_ibm_qrng_r3/C/module_none --expect-rows 1

The plan's numbers: `sealed-runs/2026-11-02_ibm_qrng_r3/qrng_r3_numbers.py` (env `QRNG_JOSLATOK`, `QRNG_TOOLS`, or the four raw
paths as arguments) on the committed r0, r1, r2 raw samples; the correlations, the coverage of D and the arm comparison are in
`evaluation.json`.

## Recomputing the 2 November 2026 run (r2) from the committed bytes

Two blocks, A and B, under `sealed-runs/2026-11-02_ibm_qrng_r2/`; the plan fixed the same rule as r1 (156 channels, 0.5 bit/bit, exclude):

    python3 -I tools/qrng/qrng_fuggetlen.py sealed-runs/2026-11-02_ibm_qrng_r2/A/module --expect-rows 1
    python3 -I tools/qrng/qrng_fuggetlen.py sealed-runs/2026-11-02_ibm_qrng_r2/B/module --expect-rows 1
    python3 -I tools/qrng/qrng_modul.py --raw sealed-runs/2026-11-02_ibm_qrng_r2/A/raw.bin --out W --keydir W/keys \
        --source-id ibm_fez_H_all_qubits_r2A --h-design 6.0 --audit --channels 156 --h-bit 0.5 --channel-policy exclude

The plan's numbers: `sealed-runs/2026-11-02_ibm_qrng_r2/qrng_r2_numbers.py` against the committed r0 and r1 raw samples. The
per-qubit correlations (K7-K9) and the label-shuffle control are plain Pearson / permutation arithmetic on the per-channel p(1)
of the raw bytes (bit j of the MSB-first stream belongs to channel j mod 156) - `evaluation.json` lists the per-qubit values.

## Recomputing the 31 October 2026 run (r1) from the committed bytes

    python3 -I tools/qrng/qrng_fuggetlen.py sealed-runs/2026-10-31_ibm_qrng_r1/modul

`module/` holds the ledger, the raw block under `raw/<sha256>.bin` and the output block `blocks/000000.bin`, exactly as the module
left them. Expected: rc 0, every row `ok`, 0 excluded channels, accounting `h_acc` 7.299763 bits/byte, output 35 968 bytes.

## What the checker can and cannot establish (arm B's questions, 1 November 2026)

- **The row-0 key is not independent trust.** The ledger's first row carries the public keys; a ledger forged end-to-end with
  other keys is internally consistent. Pin the keys you got out-of-band: `--pin-ed25519 B64 --pin-mldsa65 B64`, or compare the
  `key_fingerprints` (SHA-256 of the raw public key bytes) the checker prints with the ones published here and in the TSA receipt.
  r1 (31 October 2026): Ed25519 `ecde6e0826fd01d00338a0e000869a35e4f5d580758ec382bf5b1f7c2e7bdac9`, ML-DSA-65
  `824c34bf60fe3222ee9a7777fdc30282d131c42dc87b8eb455f200c859c28c13`.
- **Truncation is invisible from the ledger alone.** A ledger cut after row k is a valid chain of k+1 rows. Pass `--expect-rows N`
  with the row count from an out-of-band source (the published `SHA256SUMS`, the TSA receipt, this README); fewer or more rows = FAIL.
  r1 has 1 row.
- **A forged ML-DSA-65 signature on a non-final row** is caught by the chain even without ML-DSA (the next row's `prev_sha256` covers
  the whole row); on the final row it is invisible in PASS-PARTIAL mode — which is why that mode never says PASS.
- **Bit decoding of the IBM raw bytes (channel = qubit).** Per shot the `n` classical bits are taken in the order `c0, c1, …, c(n-1)`
  (Qiskit returns the bitstring with `c0` as the rightmost character, so each shot's string is reversed), the shots are concatenated in
  the order the service returned them, the bit stream is packed MSB-first into bytes, and a trailing partial byte is dropped. Bit
  index `j` of the stream (0-based) therefore belongs to qubit/channel `j mod n` (r1: n = 156, no offset, no padding). The checker's
  `chan_stats` walks the bytes MSB-first with the same `pos mod n`; the module's rule and the checker's recomputation agree only
  under this decoding, which is why it is stated here and in the module's `--channels` help.
- **A TSA timestamp proves the plan existed before the run; it does not prove the run executed that plan.** The link is the
  committed plan's parameter values being the ones recorded in the receipt (`h_design`, `channels`, `h_bit`, `policy`) and the raw
  bytes' SHA-256 appearing in the receipt; a run with other parameters would show in the recomputation, a run on other bytes in the hash.

To re-derive the receipt itself with your own keys (the signatures differ, every other number and the output hash must not):

    python3 -I tools/qrng/qrng_modul.py --raw sealed-runs/2026-10-31_ibm_qrng_r1/raw.bin --out W --keydir W/keys \
        --source-id ibm_fez_H_all_qubits_r1 --h-design 6.0 --audit --channels 156 --h-bit 0.5 --channel-policy exclude

The parameters are the ones fixed in `plan_r1.json` before the run. The break test writes only under its scratch argument:

    python3 -I tools/qrng/tores_qrng.py /tmp/qrng_break_test

The sealed plan's numbers come from `sealed-runs/2026-10-31_ibm_qrng_r1/qrng_r1_numbers.py` (run it against the committed r0
raw to reproduce `numbers_r1.json`). Statistics cannot prove a quantum source; the receipts say "statistical" and nothing more.
