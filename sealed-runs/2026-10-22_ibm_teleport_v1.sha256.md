# IBM teleportáció-teszt v1 — befagyasztott jóslat lenyomata (2026-10-22, R1 futás ELŐTT)

sha256(plan_t1.json) = 584f994030c1ca36790e2a8541bb327fdcdae1885b9c9d05a7135c4291708c39

Állapotátvitel egy várakozó páron, csak visszhang-ág; a pár saját lecsengése a közvetlenül előtte futott kalibrációs
jobból (pár-visszhang 4 időpont × 3 bázis + t = 0 teleport 6 bemeneten, egy jobban). Jóslat: egzakt nyílt-rendszerű
szimuláció a pár-kalibrált T₂-vel, + bemenetenkénti kapu/kiolvasási tényező a t = 0-ból. 6 késleltetés × 6 bemenet.
Elfogadás a terv szerint: K1 ±0,03 legalább 5/6; K3 F̄₀ > 2/3; K4 törés; K5 bájt-azonos; negatív kontroll (korrekció
nélkül) 6/6 küszöb alatt. Felfedés az értékelés után.
