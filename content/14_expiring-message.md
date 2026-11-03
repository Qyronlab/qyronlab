---
title: "Expiring message"
slug: expiring-message
order: 4.6
demo: demo/expiring-message/index.html
---

# A message that cannot be copied — and expires

An ordinary message bus keeps every message forever, and any message can be copied. A quantum network carries a
different kind of message: an **entangled pair**. It cannot be copied, it can be used only once, and it loses quality
while it waits. We took the rooms, receipts and notary ledger of an ordinary message bus and asked what survives when the
message is a pair: receipts and the ledger carry over unchanged; copying and archiving become impossible; and every
message needs an age and a quality label, because it expires.

**Real data.** One entangled pair on IBM's ibm_kingston processor (qubits 32 and 33), measured on 21 October 2026 after
waits from 0 to 800 µs, raw and with one echo pulse. The decay model was written down and sealed by its fingerprint
**before** the measurement; it met 9 of 11 raw points and 11 of 11 echo points within 0.03.

**The rule.** A pair is usable while its fidelity minus three standard errors stays at or above 0.5 — above 0.5 the pair
is entangled, and sending a quantum state over it beats every classical method. From the sealed model, the same pair stays
usable for **63 µs raw** and **216 µs with one echo pulse**.

**Try it.** The page below lets you create pairs, use them after a waiting time you choose, and then try to cheat: use a
pair twice, edit a receipt, or delete a line of the ledger. Every receipt and every ledger line is signed twice — Ed25519
and the post-quantum ML-DSA-65 — and the checker in your browser recomputes everything from the sealed model. It refuses
each of the three cheats.

**Limits.** One processor, one pair, one day. The pair waits inside a chip, so it lives for microseconds; a network memory
would live longer — the receipts and the ledger would stay the same, only the curve would change. The pairs you create
on the page are simulated from the sealed model; the points on the chart are measured.
