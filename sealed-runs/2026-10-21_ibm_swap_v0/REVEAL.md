# IBM csere-teszt v0 — felfedés (2026-10-21)

Lenyomat a mérés előtt: `../2026-10-21_ibm_swap_v0.sha256.md` (66f7b560…2c21). Ellenőrzés: `sha256sum plan_c.json`.

**Eredmény: K1 4/6 → piros egy ponttal; a modell egyirányúan pesszimista (+0,02…+0,05); K2–K5 + negatív kontroll zöld.**
| t_wait (µs) | 0 | 25 | 50 | 100 | 150 | 300 |
|---|---|---|---|---|---|---|
| F mért | 0,846 | 0,760 | 0,694 | 0,579 | 0,496 | 0,345 |
| F jósolt | 0,838 | 0,740 | 0,658 | 0,533 | 0,448 | 0,324 |

- K3: a csere t = 0-nál **0,846** — a kulcs-küszöb (0,78) fölött; korrekció nélkül 0,25 (negatív kontroll rendben).
- K2: a küszöb-átlépés jósolt 15 µs, mért **19 µs** — a C eset ezen a gépen ennyi várakozást bír kulcs-minőséggel.
- K1: 4 pont a ±0,04-en belül, 2 kívül (100, 150 µs) — a szorzat-modell alábecsüli a cserélt párt: a két pár
  populációs tagja a csere után nem egyszerű szorzat. Az elfogadást nem lazítjuk; a v1 a cserélt pár ZZ-jét
  zárt alakban számolja.
- Eltérés a tervtől, jelezve: az RC2 pár-fázis mérést kihagytuk (a jóslat csak a visszhang-ágat használja, ahol a
  forgás kiesik); a lezárás előtt egy előjel-hibát javítottunk a modellkódban (commit 647f920d a saját fában).

Fájlok: `plan_c.json`, `r0c_raw.json`, `calibration.json`, `r1c_raw.json`, `report.json`, `PLAN_IBM_SWAP_v0.md`.
Gép: ibm_kingston, lánc (q0, 32, 33, 34). Gépidő ~25 s.
