#!/usr/bin/env python3
"""build_results.py - one machine-readable summary of every sealed-then-revealed test under sealed-runs/, for the public
evidence board on the site (see DESIGN.md, "Evidence board"). Stdlib only; reads only files already in this repository.

    python3 tools/build_results.py            -> writes data/results.json and prints one summary line

Every number in the output comes from a report.json / plan*.json under sealed-runs/; nothing is typed in here except the
English titles and the limits sentences, which mirror the REVEAL.md of each test. Series: x = waiting time in µs (or
number of echo pulses for the DD test), measured and predicted per point, with the tolerance fixed before the run.
"""
import glob
import hashlib
import json
import os
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
J = ROOT / "sealed-runs"
OUT = ROOT / "data" / "results.json"

# id -> (English title, what was measured, limits, verdict override or None, x label)
META = {
    "2026-10-21_ibm_bell_v0": ("Pair decay while waiting, v0", "Fidelity of an entangled pair after waiting, raw and with one echo",
                               "one device, one qubit pair, one day; the model lacked the pair's phase rotation", "refuted", "waiting time (µs)"),
    "2026-10-21_ibm_bell_v1": ("Pair decay while waiting, v1", "Same test with the pair's rotation calibrated; a negative control without it",
                               "one device, one qubit pair, one day; waiting inside a chip, not a network memory", "confirmed", "waiting time (µs)"),
    "2026-10-21_ibm_dd_v0": ("How many echo pulses", "Fidelity after 300 µs with 0–16 echo pulses",
                             "300 µs only, one pair; energy decay sets the bound", "confirmed", "number of echo pulses"),
    "2026-10-21_ibm_teleport_v0": ("Teleportation over a waiting pair, v0", "Average fidelity of six input states, raw and echo arm",
                                   "echo arm confirmed 6/6, raw arm refuted 1/6: the pair drifted in the 40 minutes since calibration", "partial", "waiting time (µs)"),
    "2026-10-21_ibm_swap_v0": ("Entanglement swap at a middle node, v0", "Fidelity of the swapped outer pair after the first pair waited",
                                "4 of 6 within tolerance; the product model was pessimistic", "partial", "waiting time (µs)"),
    "2026-10-21_ibm_swap_v1": ("Entanglement swap at a middle node, v1", "Same with the pair's own decay measured before the run",
                                "one chain of four qubits, one day", "confirmed", "waiting time (µs)"),
    "2026-10-22_ibm_teleport_v1b_age": ("Teleportation, v1b: a 40-minute-old calibration", "Same protocol, fresh calibration at 17:05 UTC, test run 40.5 minutes later (processor's own timestamps in receipts/)",
                                        "one triple, one day; 300 µs point +0.033 just outside tolerance (measured better than predicted); the 41–96 min band stays open", "confirmed", "waiting time (µs)"),
    "2026-10-22_ibm_teleport_v1": ("Teleportation over a waiting pair, v1", "Echo arm only; the pair's decay measured 2.5 minutes before the run",
                                   "one triple, one day; waiting inside a chip", "confirmed", "waiting time (µs)"),
    "2026-10-25_quafu_r0s": ("Bell pair at zero wait on a second vendor (Quafu Shenglian)", "Pair fidelity of two qubit pairs, two runs of one sealed plan; raw and readout-corrected",
                             "sealed per-qubit readout correction gave correlations above 1, so the sealed result is NOT accepted; entanglement stands without correction (raw F 0.79-0.83); the pairwise correction shown is post hoc", "refuted", "run/pair index"),
    "2026-10-28_ibm_qrng_r0": ("QRNG reference module on a 156-qubit processor", "Min-entropy estimate of 79 872 raw bytes (H on every qubit, 4096 shots) against the sealed design minimum; health tests, independent checker",
                              "one run, one processor; certification is statistical only - statistics cannot prove a quantum source; per-qubit bias found afterwards, outside the sealed plan", "confirmed", "block"),
    "2026-10-31_ibm_qrng_r1": ("QRNG module, second sealed run: per-qubit rule and bias stability", "Same circuit three days later; per-qubit channel rule (0.5 bit/bit, exclude) and per-channel accounting fixed before the data; K7: does the r0 per-qubit bias pattern repeat?",
                              "K1-K6 confirmed (module accepts, 0 excluded channels, accounting 7.30 bits/byte, checker PASS); K7 refuted: per-qubit bias correlation r0-r1 is 0.36, not >= 0.651 - the bias moves between days while the vendor's readout-error table stays put; statistical certification only", "partial", "block"),
    "2026-11-02_ibm_qrng_r2": ("QRNG module, third sealed run: bias within one calibration", "Two jobs 1.3 s apart under one vendor calibration; K1-K6 per job; K7: does the per-qubit bias repeat within minutes? K8: does its correlation fall with calibration age? K9: vendor table stable?",
                              "K1-K6 on both jobs, K7 (r 0.91 >= 0.622; label-shuffle control p = 1/10001) and K9 (0.94) confirmed; K8 refuted: the five-day-old run matches today (0.85) better than the two-day-old one (0.47) - the bias is a property of the calibration state, not of time; statistical certification only", "partial", "block"),
    "2026-11-02_ibm_qrng_r3": ("QRNG module, fourth sealed run: the pattern returns; a validated prior pays", "After the vendor's recalibration: Q1 does the per-qubit bias pattern return to a known state; Q2 does a prior chosen before the run (validated on the current block) improve the buyer's bound - three arms on C, D as hold-out",
                              "All sealed criteria held: the pattern returned (r 0.91 with the r2 state), the new state is stable (0.92), the validated prior gave +0.21 bit/byte and +1056 output bytes with the bound covering the hold-out in 92 % of channels; statistical certification only", "confirmed", "block"),
    "2026-11-03_ibm_qrng_r4": ("QRNG module, fifth sealed run: no third state; prior value graded by age", "After the next recalibration: Q1 does a third calibration state appear; Q2 how far back does a validated prior reach - four priors chosen before the run by age (r3, r2, r0, r1), block F as hold-out",
                              "All sealed criteria held: known state (r 0.87 with r2, 0.86 with r3, 0.48 with r1), stable (0.92); priors 1-2 recalibrations old +0.20 bit/byte, the 5-day-old one +0.13, the other-state one refused; hold-out coverage 0.88-0.92; statistical certification only", "confirmed", "block"),
}
SHIFTED = ("2026-10-22_ibm_teleport_v1", "report_shifted_96min.json", "2026-10-22_ibm_teleport_v1_shifted",
           "Same prediction, 96-minute-old calibration", "The identical sealed prediction re-run 96 minutes after the pair calibration",
           "single repeat; the processor's daily table was byte-identical between the two runs; the 40–96 min band is unmeasured", "refuted")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def series_from(rows):
    """Uniform series from the different report row shapes."""
    out = {}
    for r in rows:
        x = r.get("t", r.get("t_wait", r.get("n_flip")))
        pairs = []
        if "F_raw" in r and "plan" in r:                       # bell v0: one prediction for both arms
            pairs = [("raw", r["F_raw"], r["plan"]), ("echo", r["F_visszhang"], r["plan"])]
        elif "F_raw" in r and "jos_raw" in r:                  # bell v1
            pairs = [("raw", r["F_raw"], r["jos_raw"]), ("echo", r["F_vh"], r["jos_vh"])]
        elif "Fbar_raw" in r:                                     # teleport v0
            pairs = [("raw", r["Fbar_raw"], r["jos_raw"]), ("echo", r["Fbar_vh"], r["jos_vh"])]
        elif "Fbar_mert" in r:                                      # teleport v1
            pairs = [("echo", r["Fbar_mert"], r["Fbar_jos"])]
        elif "F_mert" in r:                                         # swap, DD
            pairs = [("echo", r["F_mert"], r["F_jos"])]
        for name, m, p in pairs:
            out.setdefault(name, []).append({"x": x, "measured": round(m, 4), "predicted": round(p, 4)})
    return [{"arm": k, "points": v} for k, v in out.items()]


def one(tid, report_name="report.json", override=None):
    d = J / tid
    rep = json.loads((d / report_name).read_text())
    jos_files = sorted(glob.glob(str(d / "plan*.json")))
    jos = json.loads(pathlib.Path(jos_files[0]).read_text()) if jos_files else {}
    sha_files = sorted(glob.glob(str(d / "plan*.sha256")))
    sealed = pathlib.Path(sha_files[0]).read_text().split()[0] if sha_files else None
    title, what, limits, verdict, xlabel = override or META[tid]
    k = {kk: v for kk, v in rep.items() if kk.startswith("K") and isinstance(v, (bool, int, float))}
    return {"id": tid if not override else SHIFTED[2], "date": tid[:10], "title": title, "what": what, "limits": limits,
            "verdict": verdict, "acceptance": k, "ok": bool(rep.get("ok")),
            "tolerance": jos.get("tures", jos.get("tures_F")), "floor": jos.get("floor", jos.get("kuszob")), "machine": jos.get("gep"),
            "sealed_sha256": sealed, "sealed_matches_file": (sealed == sha(jos_files[0])) if jos_files else None,
            "x_label": xlabel, "series": series_from(rep.get("sorok", [])),
            "files": {"reveal": f"sealed-runs/{tid}/REVEAL.md", "report": f"sealed-runs/{tid}/{report_name}",
                      "prediction": f"sealed-runs/{tid}/{os.path.basename(jos_files[0])}" if jos_files else None,
                      "fingerprint": f"sealed-runs/{tid}.sha256.md"}}


def main():
    tests = [one(t) for t in sorted(META) if (J / t / "report.json").exists()]
    tid, rn, _, title, what, limits, verdict = SHIFTED
    if (J / tid / rn).exists():
        tests.append(one(tid, rn, (title, what, limits, verdict, "waiting time (µs)")))
    counts = {}
    for t in tests:
        counts[t["verdict"]] = counts.get(t["verdict"], 0) + 1
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tests": tests, "counts": counts,
           "rule": "prediction sealed by SHA-256 before the run; raw data revealed after; tolerance fixed in advance",
           "classical_bound_teleportation": 2 / 3}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(tests)} tests -> {OUT.relative_to(ROOT)} | {counts} | sealed hashes match files: "
          f"{all(t['sealed_matches_file'] for t in tests)}")


if __name__ == "__main__":
    main()
