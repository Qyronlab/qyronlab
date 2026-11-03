# IBM teleportáció-teszt v0 — felfedés (2026-10-21)

Lenyomat a mérés előtt: `../2026-10-21_ibm_teleport_v0.sha256.md` (2a945bdf…5c77). Ellenőrzés: `sha256sum plan_t.json`.

**Eredmény: a visszhang-ág jóslata igazolva (6/6), a nyers ágé megcáfolva (1/6) → K1 összességében piros.**
| K | | |
|---|---|---|
| K1 jóslat ±0,04, ≥ 5/6 mindkét ágra | nyers **1/6**, visszhang **6/6** | piros (a nyers ág miatt) |
| K2 visszhang ≥ nyers 50–150 µs | igen (100 µs: 0,79 vs 0,46) | zöld |
| K3 t = 0 a klasszikus határ (2/3) fölött | F̄₀ = **0,934** (95 % alsó határral is) | zöld |
| K4 törés-tesztek | 2/2 piros | zöld |
| K5 bájt-azonos | igen | zöld |
| negatív kontroll: korrekció nélkül | 0,47–0,51 mind a 6 bemenetre (küszöb 0,80 alatt) | rendben |

**Mit mutat:** a teleportáció dinamikus áramkörrel (a mérési eredménytől függő javítás futás közben) valódi qubiteken
0,93 átlagos hűséggel ment, és a visszhanggal őrzött pár felhasználáskori minőségét a modell pontosan előre adta
(150 µs várakozás után 0,74 mért, 0,71 jósolt). A nyers (visszhang nélküli) ág **nem jósolható** egy órával korábbi
kalibrációból: a pár forgása 40 perc alatt −3,1 kHz-ről −5,0 kHz-re vándorolt, és 100 µs-nál ez fél periódusnyi
különbség. Tanulság a koreográfusnak: a nyers számla nem tervezhető erőforrás — vagy visszhang, vagy folyamatos újra-
kalibrálás. Az elfogadást nem lazítjuk; a v1 a nyers ágat vagy elhagyja, vagy a forgást közvetlenül a futás előtt méri.

Fájlok: `plan_t.json`, `rc2t_raw.json`, `r0t_raw.json`, `calibration.json`, `r1t_raw.json`, `report.json`,
`PLAN_IBM_TELEPORT_v0.md`. Gép: ibm_kingston, hármas (q0, 32, 33). Gépidő a tesztre ~74 s; összesen 269 s a 600-ból.
