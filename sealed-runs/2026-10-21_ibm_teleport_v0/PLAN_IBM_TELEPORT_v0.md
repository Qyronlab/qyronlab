# IBM teleportáció-teszt v0 — az A eset hardveren, lezárt jóslattal (terv, 2026-10-21)

Cél: a koreográfus A esete (állapotátvitel egy páron) valódi qubiteken: a pár várakozik, aztán teleportálunk; a
felhasználáskori minőséget a v1 modell jósolja (notes/82). Három qubit egy láncon: adat q0, pár (q1,q2).

## 1. Áramkör
Bell(q1,q2) · delay(t) [nyers | visszhang X(q1,q2) t/2-nél] · állapot-előkészítés q0 ∈ {|0⟩,|1⟩,|+⟩,|−⟩,|+i⟩,|−i⟩}
· cx(q0,q1), h(q0) · mérés q0,q1 · feltételes x(q2) ha m1, z(q2) ha m0 (dinamikus áramkör, if_test) · q2 mérése a
bemenet saját bázisában. Kimenet: a 6 bemenet átlagos hűsége F̄(t); klasszikus határ 2/3 (arm B 10-21).

## 2. Jóslat (lezárva a futás előtt)
A pár minősége t-nél a v1 modellből (pár-kalibráció RC2 az új hármason!); teleportációs hűség egy Φ⁺-hűségű párral:
F̄ = (2F_pár + 1)/3 [számolt, standard összefüggés tiszta Bell-keverékre] · a kapu/kiolvasási veszteség a t = 0
kalibrációból (R0: teleport t = 0, a 6 bemeneten). F̄(t) = F̄₀ · korrekció(F_pár(t)/F_pár(0)) — az egyszerű szorzat-
feltevés, a tervben jelölve. A koreográfus kérése: F_min(t) = az a pár-minőség, amelynél F̄ ≥ 0,80 (floor, feltevés).

## 3. Futások
RC2′ (pár-fázis az új páron, 6 × 2 × 2048 ≈ 10 s) · R0 (t = 0, 6 bemenet × 2048 ≈ 6 s) · lezárás · R1: 6 késleltetés
{0, 25, 50, 100, 150, 300 µs} × 2 variáns × 6 bemenet × 2048 = 147 456 lövés ≈ 55 s. Dinamikus áramkör: a klasszikus
visszacsatolás ideje (~1 µs nagyságrend) maga is várakozás — a mérésben benne lesz, a modellben nem: ez a terv egyik
kérdése.

## 4. Elfogadás a kód előtt
K1 F̄(t) a lezárt jóslat ±0,04-én belül ≥ 5/6 pontban mindkét variánsra (a 6-bemenetes átlag szórása kisebb, a
korrekció-feltevés hibája nagyobb — ezért 0,04). K2 a visszhang-variáns F̄ ≥ a nyersé 50–150 µs-nál. K3 t = 0-nál
F̄₀ > 2/3 (a klasszikus határ fölött, 95 % alsó határral). K4 törés: hash-csere, hiányzó bemenet, a feltételes
korrekció kikapcsolva (F̄ ≈ ½ körül → piros). K5 bájt-azonos. Negatív kontroll: a korrekció nélküli ág 6/6 pontban a
küszöb alatt.

## 5. Nyitott a kód előtt
A dinamikus áramkör (if_test) ISA-fordítása és a Sampler-támogatás ezen a gépen; a feltételes kapu késleltetése.
Ha a dinamikus út nem megy: utófeldolgozott (post-selected) változat, jelölve — ez nem teleportáció, csak a korreláció.
