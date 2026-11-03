# IBM Bell-teszt v1 — a v0 két hibája javítva, új lezárás (2026-10-21)

Előzmény: notes/81 (v0 megcáfolva). A v0 adatát NEM használjuk a v1 jóslatához; a v1 saját kalibrációt mér.

## 1. Modell [számolt, a v0 két hibája javítva]
- **Elhangolás.** Külön Ramsey-kalibráció (RC) qubitenként: H · delay(t) · {H | S†H} · mérés → ⟨X⟩ + i⟨Y⟩ =
  A·e^{−t/T2*}·e^{i2πδt}. Ebből δ_A, δ_B (előjellel) és T2*_A, T2*_B. A pár fázisa φ(t) = 2π(δ_A + δ_B)t.
  Nyers ág: XX(t) = XX₀·e^{−t/T2*_A − t/T2*_B}·cos φ, YY(t) = YY₀·e^{…}·cos φ, XY(t) = XX₀·e^{…}·sin φ.
  Visszhang ág: φ kiesik; XX(t) = XX₀·e^{−t/T2_A − t/T2_B} (echo-T₂ a napi kalibrációból), YY ugyanígy.
- **Populáció (ZZ).** Független amplitúdó-csillapítás γ = 1 − e^{−τ/T1}. Nyers: ZZ(t) = ZZ₀·½[1 + (1−2γ_A)(1−2γ_B)]
  (v0, jól egyezett). Visszhang: a 4 populáció (00,01,10,11) a t/2 csillapítás → X-flip (00↔11, 01↔10) → t/2 csillapítás
  láncán, zárt alakban, szabad paraméter nélkül; ZZ = ZZ₀·(P00+P11−P01−P10)/(kezdeti).
- F = ¼(1 + XX − YY + ZZ) (a Φ⁺ projektor; XY nem kell F-hez, csak a φ ellenőrzéséhez).

## 2. Futások
| # | mi | lövés | gépidő |
|---|---|---|---|
| RC | Ramsey qubitenként: 8 késleltetés {0,20,40,60,80,120,160,240 µs} × 2 bázis (X,Y) × 2 qubit × 1024 | 32 768 | ~14 s |
| RC2 | **Kiegészítés a lezárás ELŐTT (10-21, az RC után):** az egyqubites Ramsey összege +1,6 kHz, a v0 nyers adata ~3,3 kHz forgást mutatott → gyanú: statikus ZZ-csatolás a páron, amit a Ramsey nem lát. Pár-fázis kalibráció: Bell-pár, rövid késleltetések {0,10,20,30,40,60 µs} × {XX, XY} × 2048; φ(t) = atan2(XY, XX) egyenes-illesztése → a pár tényleges forgása (δ_A+δ_B+ζ). A jóslat φ-je ebből; a Ramsey T₂*-ot ad. | 24 576 | ~10 s |
| R0 | Bell t = 0, XX/YY/ZZ/XY × 4096 | 16 384 | ~8 s |
| — | JÓSLAT LEZÁRVA (plan_v1.json, sha256 → busz + qyronlab) | | |
| R1 | 11 késleltetés {0,25,50,75,100,150,200,300,400,600,800 µs} × 2 variáns × 4 bázis (XX,YY,ZZ,XY) × 2048 | 180 224 | ~65 s |

## 3. Elfogadás — a kód előtt
- K1 F-jóslat ±0,03 legalább 9/11 pontban, külön a nyers és a visszhang ágra.
- K2 (két számla a koherencián): a visszhang-ág (|XX|+|YY|)/2 ≥ a nyersé minden t > 0-ra, alsó konfidencia-határral
  (±0,019 @ 2048); és a különbség 50–200 µs között ≥ 0,1 legalább egy pontban.
- K3 a nyers XX első előjelváltásának ideje a jósolt (φ = π/2) ±1 lépés; XY előjele a jósolttal egyezik az első
  negyedperiódusban.
- K4 törés-tesztek (hash-csere, hiányzó bázis, utólagos illesztés tiltva) pirosak. K5 bájt-azonos újraértékelés.
- Negatív kontroll: a v0 modell (Δ nélkül) a v1 adaton is ≤ 3/11 legyen — ha a v0 átmenne, a v1 nem bizonyít semmit.
