# IBM Bell-teszt v0 — a várakozás ára valódi qubiteken, két számlával (2026-10-21)

the owner GO (10-21: IBM-fiók, Open-terv, kulcs ellenőrizve). Cél: a koreográfus minőség-modelljének ELSŐ valódi
második karja. A jóslat a futás előtt befagyasztva (sha256), a mérés után felfedve. Jelölés: [olvasott] IBM-adatlap,
[számolt] saját, [feltevés].

## 1. Kérdés
Egy összefonódott pár (Φ⁺) két qubiten mennyit veszít a minőségéből, ha t ideig várakozik — és ebből mennyi a
**visszahozható számla** (egy visszhang-impulzus visszaadja) és mennyi a **végleges** (T₁-relaxáció, maradék)?

## 2. Gép, qubit-pár, zajmodell
- Gép: ibm_kingston (156 qubit, Heron; cz/rz/sx/x; delay támogatott; dinamikus áramkör támogatott) [olvasott].
- Pár-választás DETERMINISZTIKUS szabállyal a futás napi kalibrációjából (gepek/<gép>_properties.json, hash-elve):
  max (1−e_cz)(1−r_A)(1−r_B)·min(T2_A,T2_B); 10-21 14:29Z pillanatkép: (150,149) vagy (33,32) — T₂ 400–566 µs,
  T₁ 345–395 µs, cz 0,22–0,25 %, kiolvasás 0,2–2,9 % [olvasott].
- Modell [számolt, arm B ½-formájának bővítése T₁-gyel]: független relaxáció (T₁) + fázisvesztés (T₂) a két qubiten,
  γ_i = 1 − e^{−t/T1_i}, Λ = t/T2_A + t/T2_B:
  ⟨XX⟩(t) = ⟨XX⟩₀·e^{−Λ}, ⟨YY⟩(t) = ⟨YY⟩₀·e^{−Λ}, ⟨ZZ⟩(t) = ⟨ZZ⟩₀·½[1 + (1−2γ_A)(1−2γ_B)],
  F(t) = ¼[1 + ⟨XX⟩ − ⟨YY⟩ + ⟨ZZ⟩]. A t = 0 korrelátorok KÜLÖN kalibrációs futásból (kapu + kiolvasási hiba
  benne), T₁/T₂ az IBM napi kalibrációjából. Visszhang-variáns: X mindkét qubiten t/2-nél → a statikus elhangolás
  (fázisforgás) kiesik; a modell ugyanaz. A két számla: F_visszhang(t) − F_raw(t) = visszahozható;
  F₀ − F_visszhang(t) = végleges (+ impulzushiba).
- Nem modellezett: korrelált zaj, ZZ-áthallás, kiolvasási hiba időfüggése, TLS-ugrások [feltevés: kicsi].

## 3. Futások (Open-terv, 10 perc / 28 nap)
| # | mi | lövés | becsült gépidő |
|---|---|---|---|
| R0 | kalibráció: Bell-pár t = 0, XX/YY/ZZ bázis, 4096 lövés | 12 288 | ~6 s |
| — | JÓSLAT BEFAGYASZTÁSA: plan.json (modell, T₁/T₂, R0 korrelátorok, 10 késleltetés × 2 variáns), sha256 → busz Polarisnak + a qyronlab repóba csak a hash | — | — |
| R1 | 10 késleltetés {0, 25, 50, 100, 150, 200, 300, 400, 600, 800 µs} × 2 variáns (nyers / visszhang) × 3 bázis × 2048 | 122 880 | ~45 s |
Sorrend randomizált (rögzített mag), minden áramkör ugyanazon a fizikai páron, DD és twirling KIKAPCSOLVA (a
várakozást mérjük, nem a mérséklést). Minden nyers eredmény (bitstringek, ISA-áramkör, job-id, kalibrációs pillanatkép)
helyben mentve.

## 4. Elfogadás — a kód ELŐTT rögzítve
- K1 **Jóslat**: a 10 késleltetés nyers F-jének mért értéke a befagyasztott jóslat ±0,03-án belül legalább 8/10 pontban
  (statisztika ±0,019 @ 2048 + modellhiba-tartalék); a visszhang-variánsra ugyanez.
- K2 **Két számla**: a visszhang-variáns F-je minden t > 0-ra ≥ a nyersé (alsó konfidencia-határral); a különbség
  t-vel nő legalább a 100–400 µs tartományban.
- K3 **Küszöb-átlépés**: a modellből jósolt t* (ahol F_raw átlépi a 0,78-as kulcs-küszöböt, notes/32 C eset) és a
  mért átlépés ±1 késleltetés-lépésen belül.
- K4 **Törés-teszt** (helyben, futás előtt): az értékelő pirosat ad, ha (a) a jóslat-fájl hash-e nem egyezik, (b) egy
  bázis hiányzik, (c) a modellt utólag a mért adatra illesztjük (T₂ szabad paraméter) — ezt a kód tiltja.
- K5 **Bájt-azonos újraértékelés**: ugyanabból a nyers fájlból két futtatás azonos reportot ad (sha256).
Negatív kontroll: egy „mindent elutasító” szabály nem nyerhet; a report minden ágat közöl, kidobás nincs.

## 5. Ami nem következik belőle
A csomópontok távolsága, optikai veszteség, heraldált kapcsolat, a saját memória — semmi. Ez a *várakozás* fizikája
egy chipen belül; a koreográfus modelljének első hardveres kara, nem a doboz igazolása.
