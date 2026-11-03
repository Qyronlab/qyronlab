# IBM teleportáció-teszt v1b — a kalibráció korának sávja — felfedés (2026-10-22 este)

Lenyomat a mérés előtt: `../2026-10-22_ibm_teleport_v1b_age.sha256.md` (7010b356…3d72), és ugyanez a hash a futás előtt
a második kar saját, közjegyzős csatornáján is (17:3x UTC). Ellenőrzés: `sha256sum -c plan_t1.sha256`.

**Eredmény: a jóslat áll 40,5 perces pár-kalibrációval — K1 5/6, K3–K5 és a negatív kontroll zöld.**
| K | | |
|---|---|---|
| K1 jóslat ±0,03, ≥ 5/6 | **5/6** — 0–150 µs mind belül (max |0,014|), 300 µs +0,033 (a mért jobb a jósoltnál) | zöld |
| K3 t = 0 a klasszikus határ fölött | F̄₀ = **0,945** (jósolt 0,945) | zöld |
| K4 törés-tesztek | 2/2 piros | zöld |
| K5 bájt-azonos | igen | zöld |
| negatív kontroll (korrekció nélkül, 100 µs) | 0,49–0,53 (küszöb 0,80 alatt) | rendben |

| várakozás (µs) | 0 | 25 | 50 | 100 | 150 | 300 |
|---|---|---|---|---|---|---|
| mért | 0,945 | 0,869 | 0,817 | 0,749 | 0,686 | 0,598 |
| jósolt | 0,945 | 0,884 | 0,831 | 0,745 | 0,679 | 0,565 |

**Időrend a gyártó saját rekordjából** (`receipts/`, nyers API-válasz sha256-tal): kalibrációs job created 17:05:22 UTC,
finished 17:05:52; tesztjob created **17:46:22 UTC**, running 17:46:24, finished 17:47:03 → a pár-kalibráció kora a futáskor
**40,5 perc**. A gép sora üres volt, ezért a kor pontosan a tervezett minimum lett.

**Mit mutat:** a kalibráció megengedett kora most két oldalról mért ugyanazon a napon, ugyanazon a hármason: 2,5 perc 6/6,
40,5 perc 5/6, 96 perc 0/6. A [41, 96] perces sáv nyitott. A pár lecsengése napközben is változott (τ_pár reggel 191, este
174 µs), a napi tábla ugyanaz maradt — a párt a felhasználás előtt mérni kell, és 40 percen belül fel kell használni, amit
erre a mérésre terveztünk. A 300 µs-os pont kis pozitív eltérése a lecsengés-illesztés korlátja (4 pont, legfeljebb 200 µs):
a következő kalibráció 300 µs-os pontot is kap.

A második kar előre rögzített ellenfél-jóslata (a futás előtt, a `research/REPEATER_CONSULTATION.md`-ben): 40–60 perces korra
nem mondott pass/fail-t, 60 perc fölött bukást — a 40,5 perc a nyitott sávba esett, így az ő jóslata nem dőlt el.

Fájlok: `plan_t1.json` + `.sha256`, `cal_t1_raw.json`, `calibration.json`, `r1t1_raw.json`, `report.json`,
`time_between_cal_and_r1.txt`, `receipts/`. Gép: ibm_kingston, hármas (31, 32, 33). Gépidő ~51 s; összesen 480 s a 600-ból.

## Időrend két független órával (2026-10-22 este)
A lenyomat a második kar közjegyzős csatornáján **17:34:47.620 UTC**-kor került a láncba (közjegyzői bejegyzés seq 65, a
seq 100-as aláírt ellenőrzőpont alatt; a láncszelet és az ellenőrző recept a második karnak átadva, sha256
1d0ae4eb…31cde). A gyártó saját rekordja szerint a tesztjob **17:46:22.751 UTC**-kor jött létre (`receipts/`). A sorrend
így nem a mi állításunk, hanem két, egymástól független napló egyezése: a jóslat 11 perc 35 másodperccel a futás előtt
volt lezárva és közzétéve. A második kar ellenőrzése után ez a teszt az első, ahol a „futás előtt közzétéve" mért.

**Arm B ellenőrzése (2026-10-22 este) és a válasz (10-23 reggel):** a lánc és a két aláírt ellenőrzőpont rendben, de a
leírt hash-szabály pontatlan volt: a bejegyzés hash-e a {seq, prev_hash, received_at_ms, envelope_sha256, sender_identity,
sender_auth, recipient, kind, decision, reason, claimed_ts_ms (+cursor)} mezők kanonikus bájtjaiból készül, a `type` mező
nincs benne (integritás-rés, a kód gazdájának jelezve). A seq 65 boríték-hash-e és a kézbesítési bejegyzés hash-e azért tér
el, mert az egyik a beküldött üzenetet (8 mező, 1443 bájt), a másik a kiadott válasz-rekordot (11 mező, 1495 bájt) hash-eli;
mindkettő bájtra reprodukálható a tárolt sorból, a recept Arm B-nél. **A saját közjegyzőnk nem független óra** — ezt Arm B
jogosan mondta ki. Külső horgony ennél a tesztnél: a GitHub szerveroldali push-idő a lenyomat-commitra NEM áll rendelkezésre
(az Events API listájából ez a push hiányzik), így a „futás előtt közzétéve" itt **UNMEASURED** marad; ami független a labortól,
az Arm B saját gépén rögzített átvétel (17:36:33Z) a job létrehozása (17:46:22.751Z) előtt — hogy ezt horgonynak fogadja,
az ő döntése. Ezentúl minden lezárt fájl a beküldés előtt RFC 3161 időbélyeget kap nyilvános TSA-tól (`provenance/tsa/`,
a recept ott; az itt lévő token a futás UTÁN készült, csak a receptet mutatja). A teleport v1 (reggel) tesztnél ez a két
harmadik fél órájával mért: lásd annak REVEAL.md-jét.
