# IBM csere-teszt v1 — felfedés (2026-10-21)

Lenyomat a mérés előtt: `../2026-10-21_ibm_swap_v1.sha256.md` (db622e67…dd63). Ellenőrzés: `sha256sum plan_c1.json`.

**Eredmény: a lezárt jóslat IGAZOLVA — K1 6/6 (±0,04), K2, K3, K4, K5 és a negatív kontroll zöld.**
| t_wait (µs) | 0 | 25 | 50 | 100 | 150 | 300 |
|---|---|---|---|---|---|---|
| F mért | 0,835 | 0,768 | 0,699 | 0,568 | 0,487 | 0,334 |
| F jósolt | 0,838 | 0,749 | 0,673 | 0,555 | 0,472 | 0,343 |

Küszöb-átlépés (0,78): jósolt 16 µs, mért 20 µs. Korrekció nélkül 0,25.

**Mi változott a v0-hoz képest (gépidő nélkül kiderítve):** az egzakt nyílt-rendszerű szimuláció bájtra a v0
szorzat-modelljét adta — a v0 eltérése tehát nem a modell szerkezetéből jött, hanem a bemenő számokból: a napi
egy-qubites kalibráció a várakozó pár koherencia-idejét 147 µs-nak adta, a páron közvetlenül mérve 174,5 µs. A v1 ezt
a pár-kalibrációt használja (külön futás, nem a tesztadat). Tanulság a koreográfusnak: **a párt kell kalibrálni, nem a
qubiteket** — a forgásnál (v1 Bell) és a lecsengésnél (csere) is.

Fájlok: `plan_c1.json`, `rce_raw.json` (pár-visszhang kalibráció), `r1c1_raw.json`, `calibration.json`, `report.json`.
Gép: ibm_kingston, lánc (q0, 32, 33, 34). Gépidő ~30 s.
