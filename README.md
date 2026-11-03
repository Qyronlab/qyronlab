# Qyronlab — public research repository

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23908657.svg)](https://doi.org/10.5281/zenodo.23908657)

Everything here is either a sealed plan, a measurement, a recomputation, or a disagreement about one of those. Nothing is
claimed that was not measured or read from a cited source; what a result does not certify is written next to it.

| path | what |
|---|---|
| `content/` | the text of qyronlab.com, one file per page — the canon the site is built from |
| `sealed-runs/` | sealed runs on public quantum processors: the plan (hashed and time-stamped *before* the run), the raw data, the provider's job records, the evaluation, the reveal (`REVEAL.md`), and `SHA256SUMS` |
| `tools/qrng/` | the random-number reference module, the buyer's independent checker, the prior builder and the break test (71 planted-fault cases) |
| `tools/build_results.py`, `data/results.json` | the results board: every sealed run with its criteria and verdict |
| `research/` | reading notes with sources, the shared download library (`research/library`), signature-size measurements (`research/z5`) |
| `demo/` | small browser demos (expiring message, vendor simulator) |
| `room/`, `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/` | the research room: how to file a claim, an objection or a blind recheck here |

**Recompute anything.** Each sealed run folder states the exact commands; the checkers under `tools/` are stdlib Python and
run offline. If a recipe is not enough to reproduce a number, file that as a recheck — it counts.

**History.** This repository starts clean on 3 November 2026; the earlier private working repository is not published.
Provenance does not depend on git history: the RFC 3161 tokens, the file hashes and the provider records are in the files.

**Cite.** Each GitHub release is archived on Zenodo with a DOI. This release: `10.5281/zenodo.23908657` (all versions: `10.5281/zenodo.23908656`). Author: Qyronlab.
