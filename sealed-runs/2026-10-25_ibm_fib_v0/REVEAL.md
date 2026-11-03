# IBM Fibonacci-időzítés v0 — felfedés (2026-10-25)

Kérdés (the owner): segít-e, ha az átfordítások Fibonacci-sorrendben jönnek, nem egyenletesen?
Lenyomat a mérés előtt: `../2026-10-25_ibm_fib_v0.sha256.md` (7057c34d…5f32). Önteszt a futás előtt 5/5.

**Eredmény: a lezárt jóslat igazolva — az időzítés nem számít.** ibm_kingston (32,33), 300 µs, 3 bázis × 2048 lövés:

| beállítás | F mért |
|---|---|
| nyers (0 fordítás) | 0,320 |
| echo (1) | 0,462 |
| egyenletes, 8 | 0,469 |
| Fibonacci, 8 | 0,457 |
| egyenletes, 13 | 0,459 |
| Fibonacci, 13 | 0,477 |

Fibonacci − egyenletes: −0,012 (8 fordítás), +0,018 (13) — a ±0,04-es tűrésen belül, ~1σ-n belül (σ ≈ 0,014). Egyenletes-8 −
echo: +0,007 — a 10-21-i DD-teszt négy nappal később megismételve. Bájt-azonos újraértékelés: igen. Gépidő 23 s.
**Mit mutat:** ezen a gépen, 300 µs-on a megmaradó veszteség az energia elszivárgása (T₁), azt semmilyen fordítás-sorrend
nem éri el. Ahol a fázisvesztés a korlát, ott lehet különbség — az másik mérés.
**Korlát:** egy gép, egy pár, egy várakozási idő; a Fibonacci-szakaszok a forgó keret kiegyenlítése miatt két részben
skálázva (az aranymetszés-arány csak az azonos előjelű szakaszokon belül pontos).
Fájlok: `plan_fib.json`, `r1fib_raw.json`, `calibration.json`, `report.json`.
