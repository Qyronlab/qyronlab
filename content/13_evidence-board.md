---
title: "Evidence board"
slug: evidence
order: 4.5
live_data: data/results.json
---

# Evidence board

Every test we run follows one rule: the prediction is written down and sealed by its fingerprint before the run, the raw
data are revealed after it, and the tolerance was fixed in advance. This board shows those tests as they are — confirmed,
partly confirmed, or refuted — with the measured points next to the predicted curve.

[Ez az oldal nem szöveg, hanem a `data/results.json`-ból épülő műszerfal; a paneleket a `DESIGN.md` „Evidence board"
szakasza adja. A JSON-t a `tools/build_results.py` írja a `sealed-runs/` mappából — kézzel beírt szám nincs benne. Amíg az
oldal nem épül meg, a menüben nem jelenik meg.]

Every number on this board can be traced to a file in this repository: the sealed fingerprint, the prediction, the raw
counts, and the evaluation. Nothing here is a product; the limits of each test are shown with it.
