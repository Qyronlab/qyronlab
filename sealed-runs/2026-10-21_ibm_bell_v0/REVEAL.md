# IBM Bell-teszt v0 — felfedés (2026-10-21)

A jóslat lenyomata a mérés előtt: `../2026-10-21_ibm_bell_v0.sha256.md` (54fc9ba3…7852). Ellenőrzés: `sha256sum plan.json`.

**Eredmény: a befagyasztott modell MEGCÁFOLVA.** K1 (jóslat ±0,03 legalább 8/10 pontban): nyers 1/10, visszhang 2/10 → piros.
K2 (visszhang ≥ nyers): piros. K3 (küszöb-átlépés): zöld, enyhe lépésközzel. K4 törés-tesztek 3/3, K5 bájt-azonos: zöld.
Az elfogadást utólag nem lazítjuk; a v1 új jóslattal és új lezárással jön.

**Amit a mérés megmutatott:** a várakozás közben a nyers pár XX-korrelátora csillapított koszinuszt ír le (előjelet vált
50–100 µs között) — koherens elhangolás ≈ 3,3 kHz, ami a modellből hiányzott. A visszhang-ág koherenciája a T₂-vel jól
egyezik; a visszhang-ág populációs (ZZ) tagját a modell rosszul írta le. 100 µs-nál: nyers F 0,29, visszhang F 0,69 →
a veszteség 0,40-e **visszahozható**, a két számla valódi, mérhető különbség.

Fájlok: `plan.json` (lezárt jóslat), `r0_raw.json` (kalibrációs futás), `calibration.json` (napi IBM-kalibráció,
hash-elve), `r1_raw.json` (60 áramkör × 2048 lövés, nyers számlálók), `report.json` (az értékelő kimenete),
`PLAN_IBM_BELL_v0.md` (a terv az elfogadással). Gép: ibm_kingston, qubit-pár (32,33). Gépidő: 72 s.
