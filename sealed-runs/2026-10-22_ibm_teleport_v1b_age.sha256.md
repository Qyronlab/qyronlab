# IBM teleportáció-teszt v1b — a kalibráció korának sávja; befagyasztott jóslat lenyomata (2026-10-22 este, R1 ELŐTT)

sha256(plan_t1.json) = 7010b356fc0d98c10ad10f405b26804c36f5073f923a32ab003be82dfa2a3d72

Ugyanaz a v1 protokoll (csak visszhang-ág, pár-kalibráció + t = 0 teleport egy jobban, egzakt szimuláció), friss
kalibrációval (vége 17:05:53 UTC). A tesztrészt szándékosan ≥ 40 perccel a kalibráció után adjuk be; a tényleges futási
idő a gép sorától függ, és naplózva lesz. Kérdés: a [40, 96] perces sávban hol szűnik meg a jóslat (reggel: 2,5 perc
6/6, 96 perc 0/6). Elfogadás: K1 ±0,03 ≥ 5/6, K3, K4, K5, negatív kontroll — ugyanaz, mint a v1-ben. Felfedés utána,
akár igazol, akár cáfol.
