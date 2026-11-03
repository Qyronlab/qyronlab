---
title: "The problem"
slug: the-problem
order: 2
---

# The problem

Today's largest quantum processors hold a few hundred qubits; useful algorithms need far more. Scale will come from
connecting machines, not only from growing them — and a gate between two machines is not a local operation. It
consumes an entangled pair that has to be created, delivered and used.

That pair is a strange resource:
- **it cannot be copied** — a quantum state is only ever in one place;
- **it is used up once** — the connection is a stock that is spent, not a wire that stays;
- **it fades while it waits** — a pair delivered too early sits in memory and loses quality; delivered too late, the
  program stalls.

So the question a quantum network has to answer for every program is not only *where* and *how many*, but *how
good, how soon, and for how long*. Networks being built today let an application state endpoints, rate, fidelity
and timing. What those numbers should be for a given program is still mostly set by hand, one value per
application.
