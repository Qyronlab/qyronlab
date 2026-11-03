# IBM teleportáció-teszt v1 — felfedés (2026-10-22)

Lenyomat a mérés előtt: `../2026-10-22_ibm_teleport_v1.sha256.md` (584f9940…8c39). Ellenőrzés: `sha256sum -c plan_t1.sha256`.

**Eredmény: a jóslat igazolva, 6/6 — K1–K5 és a negatív kontroll mind zöld.**
| K | | |
|---|---|---|
| K1 jóslat ±0,03, ≥ 5/6 | **6/6**, a legnagyobb eltérés 0,018 (25 µs) | zöld |
| K3 t = 0 a klasszikus határ (2/3) fölött | F̄₀ = **0,944** (jósolt 0,943) | zöld |
| K4 törés-tesztek (hash-csere, hiányzó bemenet) | 2/2 piros | zöld |
| K5 bájt-azonos újraértékelés | igen | zöld |
| negatív kontroll: korrekció nélkül, 100 µs | 0,48–0,51 mind a 6 bemenetre (küszöb 0,80 alatt) | rendben |

| várakozás (µs) | mért F̄ | jósolt F̄ | eltérés |
|---|---|---|---|
| 0 | 0,944 | 0,943 | +0,000 |
| 25 | 0,868 | 0,886 | −0,018 |
| 50 | 0,820 | 0,835 | −0,014 |
| 100 | 0,752 | 0,751 | +0,001 |
| 150 | 0,685 | 0,687 | −0,002 |
| 300 | 0,580 | 0,572 | +0,008 |

**Mit mutat:** a v0 tanulságát a v1 beváltotta. A pár saját lecsengését nem a napi kalibrációból vettük, hanem a
teszt előtt közvetlenül mértük (pár-visszhang 4 időpont × 3 bázis, egy jobban a t = 0 teleporttal), és a jóslatot az
egzakt nyílt-rendszerű szimuláció adta ezzel a pár-kalibrált T₂-vel plusz a t = 0-ból vett bemenetenkénti kapu-tényezővel.
Így a felhasználáskori minőség 300 µs-ig három ezreden belül jósolható (a 25–50 µs-os pontokon −0,014…−0,018, még a
tűrésen belül: itt a modell kicsit optimista, valószínűleg a dinamikus áramkör klasszikus visszacsatolási ideje, ami a
mérésben benne van, a modellben nincs). A kalibráció vége és a teszt indítása között 2 perc 25 s telt el (cél < 5 perc).
Koreográfus-szabály, immár kétszer mérve (csere v1, teleport v1): **a párt kell kalibrálni, a felhasználás előtt
közvetlenül, nem a qubiteket a napi táblából**; a visszhang-számla tervezhető, a nyers nem.

Fájlok: `plan_t1.json` + `.sha256`, `cal_t1_raw.json` (kalibrációs job: pár-visszhang + t = 0 teleport), `calibration.json`
(napi gépi tábla), `r1t1_raw.json`, `report.json`, `time_between_cal_and_r1.txt`, `PLAN_IBM_TELEPORT_v0.md` (§6 a v1 terv).
Gép: ibm_kingston, hármas (31, 32, 33). Gépidő a tesztre 51 s; összesen 395 s a 600-ból.

## Eltolt ismétlés ugyanaznap (05:26 UTC) — 96 perces pár-kalibrációval a jóslat NEM áll: K1 0/6
Ugyanaz a lezárt jóslat, ugyanazok az áramkörök, ugyanaz a hármas; a futás a pár-kalibráció vége után 95,9 perccel ment
(a gép sora miatt; beadva 04:20 UTC). Negatív kontroll rendben, K3 áll (F̄₀ = 0,904 > 2/3), K5 bájt-azonos — K1 **0/6**:
| várakozás (µs) | 0 | 25 | 50 | 100 | 150 | 300 |
|---|---|---|---|---|---|---|
| friss kalibráció (2,5 perc) | 0,944 | 0,868 | 0,820 | 0,752 | 0,685 | 0,580 |
| 96 perces kalibráció | 0,904 | 0,784 | 0,707 | 0,626 | 0,578 | 0,538 |
| jósolt | 0,943 | 0,886 | 0,835 | 0,751 | 0,687 | 0,572 |

A gép napi kalibrációs táblája a két futás között bájtra változatlan maradt (T₁, T₂, kiolvasási hiba, kapuhiba mind a
három qubiten ugyanaz) — a romlást a tábla nem látta, csak a párra mért lecsengés és a t = 0 hűség. A plafon így két oldalról
mért: 2,5 perc és 40 perc jó, 96 perc rossz. A koreográfus kérése ezért hordozza a pár-kalibráció korát, és 40 percnél
idősebb kalibrációra nem ad jóslatot. Fájlok: `r1t1_shifted_96min_raw.json`, `report_shifted_96min.json`,
`time_between_cal_and_r1_shifted.txt`. Gépidő 34 s; összesen 429 s a 600-ból.

## Gyártói job-rekordok (receipts/, 2026-10-22 este, Arm B kérésére)
A három job (kalibráció, friss futás, 96 perces futás) saját rekordja a gyártó REST API-jából (`GET /jobs/{id}` és
`/jobs/{id}/metrics`), **nyers válasz-bájtok** sha256-tal (`receipts/SHA256SUMS`): a job létrehozási és futási időbélyege
így nem a mi átiratunk, hanem a szolgáltató válasza. created / running: kal 03:49:19Z / 03:49:20Z; friss R1 03:51:22Z /
03:51:24Z; eltolt R1 04:20:44Z / 05:26:10Z. A lenyomat közzétételének független órája (közjegyzői befoglalás) a következő
tesztektől áll rendelkezésre; a v1-re ez a sorrend UNMEASURED marad (Arm B #13).

## Futás előtti közzététel két harmadik fél órájával (mérve 2026-10-23 reggel, Arm B kérésére)
A lenyomatot vivő commit (03ceca4) pusholását a GitHub szerveroldali PushEvent **2026-10-22T03:51:07Z**-re teszi (ezt a
szerver írja, nem a pusholó); a gyártó saját job-rekordja szerint a tesztjob (dbcogek24mrc73ck2d00) **03:51:22.846Z**-kor
jött létre (`receipts/`). A sorrend tehát két, egymástól és a labortól független napló egyezése, 15,8 másodperc különbséggel.
A GitHub-válasz származtatott kivonata és a nyers válasz sha256-a: `provenance/github_push_events.json`. Korlát: a
GitHub Events API „best effort", a lista nem teljes garanciával; ennél a tesztnél a kérdéses push szerepel benne.
