# File names: original (Hungarian, as cited inside the sealed plans) -> published (English)

The sealed plan files are byte-identical to the time-stamped originals and cite the original names of their inputs (for example `terv_szamok_r2.json` → `numbers_r2.json`, `prior_r2AB.json` unchanged); this map resolves them. Hashes are unchanged.

| original | published |
|---|---|
| FELFEDES | REVEAL |
| kiertekeles | evaluation |
| ertekeles | evaluation |
| riport_eltolt_96perc | report_shifted_96min |
| riport | report |
| terv_szamok | numbers |
| TERV_IBM_ | PLAN_IBM_ |
| terv_r | plan_r |
| joslat | plan |
| kalibracio_elott | calibration_before |
| kalibracio_utan | calibration_after |
| kalibracio | calibration |
| kal_es_r1_kozti_ido_eltolt | time_between_cal_and_r1_shifted |
| kal_es_r1_kozti_ido | time_between_cal_and_r1 |
| kalt1_nyers | cal_t1_raw |
| eltolt_96perc | shifted_96min |
| _nyers | _raw |
| utolag | posthoc |
| valasztas | selection |
| parkorrekcio | pair_correction |
| _csere_ | _swap_ |
| _CSERE_ | _SWAP_ |
| v1b_kor | v1b_age |
| modul, modul_* (directories) | module, module_* |

## Redacted sealed copies

These sealed files carried a personal first name. The published copy replaces it with a neutral word and nothing else; the companion `.sha256` and fingerprint files cite the ORIGINAL hash, which is held privately.

| published file | original sha256 | published sha256 |
|---|---|---|
| sealed-runs/2026-10-21_ibm_dd_v0/plan_dd.json | 1a8c912132ce32c726a0d33e42cdfcb78dfed8de5d01a11c00ee967184bd768f | e35fd64518b03eedfe03189b955934579a6b432008e96a5cf1957064376053df |
| sealed-runs/2026-10-25_ibm_fib_v0/plan_fib.json | 7057c34d8d4508f45a2346961f66ab243722043e563fc1533f252c6020565f32 | 4e1677bc5badf123445410d5fc9c55963941ca75dab298072508bbf1bd2e419f |
