---
title: "What we are building: the choreographer"
slug: what-we-are-building
order: 3
---

# What we are building: the choreographer

A program spread over several quantum machines needs a choreographer: something that decides which state lives on
which machine, when to ask for a pair, and how long each pair may wait.

**It derives the request from the program itself.** From what the program does — which pairs it needs, how long it
holds each one, what quality it needs at the moment of use — the choreographer computes what to ask the network for.
A program that needs one pair turns out to need a quality, not a time window; a program that needs nothing gets no
request at all; a program that needs two pairs alive *together* gets a tie between them — something the published
request formats we have studied cannot express.

**It keeps the books.** Nothing is lost, it changes form:
- a quantum state is in exactly one place at every step;
- every pair ends in exactly one way — used, expired while waiting, sacrificed to make a better one, or broken by
  someone looking;
- quality is a budget: what a pair has at birth, minus what it loses while it waits and while it is worked on, must
  still meet the program's floor at the moment of use.

What fades while waiting is kept in two accounts: the part that can be won back before use, and the part that has
gone into the environment for good.

**Anyone can check the books.** The choreographer's output comes with its ledger, and a separate checker — written
independently, sharing no code — re-derives the timing and the request and confirms that every balance closes.
Compute once, check anywhere: the same principle our own network software, Zynko (zynko.dev, part of Qyronlab), applies to results.
