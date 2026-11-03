# IBM DD-teszt v0 — felfedés (2026-10-21)

Kérdés (the owner): segít-e a pár folyamatos átfordítása (0→1→0→1…), ha egy helyett sokszor csináljuk?
Lenyomat a mérés előtt: `../2026-10-21_ibm_dd_v0.sha256.md` (1a8c9121…768f).

**Eredmény: a lezárt jóslat igazolva (6/6, ±0,04); a modellnek NEM kell DD-tag.** 300 µs várakozás, ibm_kingston (32,33):

| átfordítások | F mért | F jósolt |
|---|---|---|
| 0 | 0,329 | 0,291 |
| 1 | 0,432 | 0,448 |
| 2 | 0,463 | 0,448 |
| 4 | 0,440 | 0,448 |
| 8 | 0,439 | 0,448 |
| 16 | 0,431 | 0,448 |

**Mit mutat:** egy átfordítás visszahozza, ami visszahozható (0,33 → 0,43); a további átfordítások nem adnak többet
(2–16: 0,43–0,46, a tűrésen belül azonos), mert ami marad, az az energia elszivárgása (T₁) — azt a fordítás nem éri el.
A ZZ-populáció 0,49 (0 fordítás) → ~0,15 (bármennyi fordítás) az átfordított relaxáció modellje szerint. Ezen a gépen,
ezen az időskálán tehát a „folyamatos átfordítás” pontosan annyit ér, mint egy — a két számla határa ott van, ahol a
modell mondja. Fájlok: `plan_dd.json`, `r1dd_raw.json`, `calibration.json`, `report.json`. Gépidő ~12 s.
