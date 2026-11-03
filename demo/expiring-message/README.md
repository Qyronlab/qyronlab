# Expiring message — browser demo

`index.html` (self-contained page; loads @noble/curves 2.4.0, @noble/post-quantum 0.7.1 and @noble/hashes 2.4.0 from
jsDelivr, pinned), `logic.mjs` (model, rule, receipts, ledger, checker — shared with the test), `data.json` (built from
`sealed-runs/2026-10-21_ibm_bell_v1/plan_v1.json` and `report.json`; their sha256 values are inside).
Test: `node test_logic.mjs <dir with @noble packages> <python model reference>` — 9/9 PASS on 2026-10-26: the JS model equals
the sealed Python model to 1e-16 and meets the measured points 9/11 raw, 11/11 echo; four cheats refused.
In a browser, `index.html#selftest` clicks through every action and prints the verdicts (headless Chromium 2026-10-26:
still good / used twice refused / edited receipt refused / deleted ledger row refused / raw pair honestly expired).
