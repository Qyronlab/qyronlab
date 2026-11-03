# IBM csere-teszt v0 — a C eset hardveren: két pár, a második várat (terv, 2026-10-21 este)

Cél: a koreográfus C esete (notes/32): egy középső gép két szomszéd felé egy-egy párral; a cserélt pár minősége a
két pár szorzata és a VÁRAKOZÁS ára, amíg a második pár elkészül. Hardveren: négy qubit egy láncon (q0,q1 | q2,q3),
az első pár (q0,q1) t_wait ideig várakozik (visszhanggal — a DD-teszt szerint egy elég), aztán elkészül a második
(q2,q3), Bell-mérés a középen (q1,q2) dinamikus korrekcióval, a külső pár (q0,q3) hűsége XX/YY/ZZ-ből.

## Jóslat (lezárva a futás előtt) — a v1/teleport modellből
F_csere(t) = modell: a két pár korrelátorainak szorzata; az első pár t_wait-ig a visszhang-ágon (echo-T₂ + átfordított
populáció), a második friss; a középső Bell-mérés + korrekció vesztesége a t = 0 kalibrációból (R0: csere azonnal).
Negatív kontroll: korrekció nélkül F ≈ ½ körül. A koreográfus kérése ebből: a C eset „együtt” kötése számokban —
mekkora t_wait fér bele egy 0,78-as (kulcs) küszöbbe ezen a gépen.

## Futások
RC2 (pár-fázis az első páron; a visszhang miatt csak a T₂/T₁ kell, de a nyers kontrollhoz mérjük) ~10 s · R0 (csere t = 0,
3 bázis × 2048, + korrekció nélkül) ~6 s · lezárás · R1: 6 t_wait {0, 25, 50, 100, 150, 300 µs} × 3 bázis × 2048 =
36 864 lövés + negatív kontroll ≈ 20 s. Összesen ≈ 40 s (maradna ~270 s).

## Elfogadás a kód előtt
K1 F_csere(t) ±0,04 legalább 5/6; K2 a mért küszöb-átlépés (0,78) ±1 lépés a jósolthoz; K3 R0: F_csere(0) > 0,78 (a
kulcs-küszöb — ha nem, a C eset ezen a gépen már t = 0-nál sem kulcs-képes, és ezt mondjuk ki); K4 hash / hiányzó bázis /
korrekció-kikapcsolás piros; K5 bájt-azonos; negatív kontroll (korrekció nélkül) küszöb alatt 6/6.

## Mit nem mér
A második pár elkészülésének VÉLETLEN idejét (memoryless érkezés, notes/32 §3 C) — itt t_wait rögzített; a 25,7 %-os
„időben érkezik” szám a modellé marad, a mérés a t_wait → F görbét adja, amiből az a szám számolható.
