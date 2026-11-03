---
title: "Vendor-number simulator"
slug: vendor-simulator
order: 4.7
demo: demo/vendor-sim/index.html
---

# How would an entangled pair run today?

Cloud quantum processors publish their calibration: how long each qubit keeps its state, how often a gate fails, how often
a readout is misread. We read these numbers every hour from two independent vendors (IBM Quantum and the Quafu cloud of the
Beijing Academy of Quantum Information Sciences), keep every file with its fingerprint, and record how old each number is.

The page below takes **only those published numbers** and computes, in your browser, how good an entangled pair would come
out on any coupled pair of qubits. Before each of our own runs we seal such a prediction; after the run we compare.

**First sealed comparison (26 October 2026).** On IBM's ibm_kingston the published numbers predicted the result: a sealed
prediction of 0.947, a measured 0.936. On Quafu's Shenglian processor, the same day and the same method, they did not: for one pair the published readout numbers allow a raw
correlation of at most 0.48, and we measured 0.81 — fifty standard errors above the ceiling. The test needs no model: if
the readout errors are independent, as the per-qubit numbers assume, a measured correlation cannot exceed that ceiling.
We also saw the published calibration identifier change every few minutes while the readout values stayed byte-identical.

**Limits.** A deliberately simple model (gate errors as depolarizing noise, independent readout); crosstalk, leakage,
drift and correlated readout errors are ignored — so its misses show where the published numbers fall short. A handful of
runs so far; the comparison table grows with every sealed run.
