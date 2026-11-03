# IBM Bell-teszt v1 — felfedés (2026-10-21)

Lenyomat a mérés előtt: `../2026-10-21_ibm_bell_v1.sha256.md` (c1edbc03…c0bf). Ellenőrzés: `sha256sum plan_v1.json`.

**Eredmény: a lezárt jóslat IGAZOLVA.**
| K | | |
|---|---|---|
| K1 F-jóslat ±0,03, ≥ 9/11 | nyers **9/11**, visszhang **11/11** | zöld |
| K2 két számla a koherencián (visszhang ≥ nyers; 50–200 µs-ban ≥ 0,1 különbség) | legnagyobb különbség **0,69** (150 µs) | zöld |
| K3 első előjelváltás (jósolt 80 µs) és az XY előjele | mért 75–100 µs között; XY előjele egyezik | zöld |
| K4 törés-tesztek | 3/3 piros | zöld |
| K5 bájt-azonos újraértékelés | igen | zöld |
| negatív kontroll: a v0 modell (forgás nélkül) ugyanezen az adaton | 2/11 | rendben — a v1 többet tud |

A három kalibráció (Ramsey qubitenként, pár-fázis, t = 0 Bell) külön futásból jött; a tesztadat nem illesztett semmit.
Mért: a nyers pár F-je 150 µs-nál 0,19, visszhanggal 0,61; a pár forgása −3,1 kHz (a két qubit Ramsey-összege +1,6 kHz,
a maradék pár-csatolás). Gép: ibm_kingston, (32,33). Gépidő a v1-re ~120 s (összesen 195 s a 600-ból).

Fájlok: `plan_v1.json`, `rc_raw.json` (Ramsey), `rc2_raw.json` (pár-fázis), `r0v1_raw.json`, `calibration.json`,
`r1v1_raw.json` (88 áramkör × 2048), `report.json`, `PLAN_IBM_BELL_v1.md`.
