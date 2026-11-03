#!/usr/bin/env python3
"""qrng_r4_numbers.py - every number of the r4 sealed plan comes from HERE, from the committed runs (r0 10-28, r1 10-31, r2 A/B 11-02
afternoon, r3 C/D 11-02 evening) and the published module's own functions (tools/qrng, with the compatibility z gate of 3 November).
r3 showed the bias pattern returns after a recalibration and that a prior validated on the current block pays the buyer. r4 asks, fixed
before the data, to be run after the vendor's NEXT recalibration (last_update newer than the r3 one):
  Q1 (physics)  does a THIRD calibration state appear, or does the pattern stay in a known one?
     K-S1: max over references {r0, r1, r2AB, r3CD} of r(E, ref) >= r_min  (predicted: known state);  K-S2: r(E, r3CD) >= r_min (the latest
     state persists; predicted from the two returns seen);  K-S3: r(E, F) >= r_min (the new state is stable in itself).
  Q2 (the buyer) how many recalibrations back does a validated prior stay usable?  four priors chosen BEFORE the run - P1 = r3 C+D (one
     recalibration back), P2 = r2 A+B (two), P3 = r0 (same state, five days and four recalibrations back), P4 = r1 (the other state) - each
     run through the validated gate (r >= r_min AND mean |z| <= 1.5, per-channel |z| <= 4) on block E; F is the hold-out.
     K-V1..K-V4: used / not used per prior, as the dry runs on the committed data predict (code decides, below);
     K-V5: every USED prior's validated arm is never worse than none (h_acc >=, out_bytes >=) and covers F in >= cov_min channels;
     K-V6: among the used priors the accounting gain does not grow with age (gain(P1) >= gain(P2) >= gain(P3) for the used ones).
    python3 -I qrng_r4_numbers.py [OUT]   (env QRNG_JOSLATOK, QRNG_TOOLS; stdlib + the published module; no network)
"""
import hashlib, json, math, os, pathlib, random, sys

HERE = pathlib.Path(__file__).resolve().parent
_J = pathlib.Path(os.environ.get("QRNG_JOSLATOK", HERE.parent))
_T = pathlib.Path(os.environ.get("QRNG_TOOLS", _J.parent / "tools" / "qrng"))
sys.path.insert(0, str(_T))
import qrng_modul as M                                                     # noqa: E402

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "numbers_r4.json"
_R = {"r0": "2026-10-28_ibm_qrng_r0/raw.bin", "r1": "2026-10-31_ibm_qrng_r1/raw.bin", "r2A": "2026-11-02_ibm_qrng_r2/A/raw.bin", "r2B": "2026-11-02_ibm_qrng_r2/B/raw.bin",
      "r3C": "2026-11-02_ibm_qrng_r3/C/raw.bin", "r3D": "2026-11-02_ibm_qrng_r3/D/raw.bin"}
NQ, SHOTS, H_CH, R_MIN = 156, 4096, 0.5, 0.622


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


raw = {k: (_J / v).read_bytes() for k, v in _R.items()}
cnt = {k: M.channel_counts(b, NQ) for k, b in raw.items()}
def pool(*ks):
    return [sum(cnt[k][0][i] for k in ks) for i in range(NQ)], [sum(cnt[k][1][i] for k in ks) for i in range(NQ)]
cnt["r2AB"], cnt["r3CD"] = pool("r2A", "r2B"), pool("r3C", "r3D")
p1 = {k: [o / c for o, c in zip(*v)] for k, v in cnt.items()}
PRIORS = {"P1_r3CD": "r3CD", "P2_r2AB": "r2AB", "P3_r0": "r0", "P4_r1": "r1"}


def gate(prior, cur):
    r = M.pearson(p1[prior], p1[cur]); z = M.compat_z(cnt[prior][0], cnt[prior][1], cnt[cur][0], cnt[cur][1])
    zm = sum(z) / NQ; return {"r": round(r, 4), "z_mean": round(zm, 4), "z_max": round(max(z), 4), "used": r >= R_MIN and zm <= M.Z_MEAN,
                               "channels_combined": sum(1 for x in z if x <= M.Z_CH)}


def arm(cur, prior=None):
    o, c = cnt[cur]
    if prior:
        z = M.compat_z(cnt[prior][0], cnt[prior][1], o, c)
        o = [o[i] + (cnt[prior][0][i] if z[i] <= M.Z_CH else 0) for i in range(NQ)]; c = [c[i] + (cnt[prior][1][i] if z[i] <= M.Z_CH else 0) for i in range(NQ)]
    p, h = M.stats_from_counts(o, c)
    excl = [i for i in range(NQ) if h[i] < H_CH]
    h_acc = sum(cnt[cur][1][i] * (0.0 if i in excl else h[i]) for i in range(NQ)) / len(raw[cur])
    h_eff = min(M.mcv_entropy(list(raw[cur])), h_acc); per = max(1, math.ceil(512 / h_eff))
    bound = [min(1.0, max(x, 1 - x) + 2.576 * math.sqrt(max(x, 1 - x) * (1 - max(x, 1 - x)) / cc)) for x, cc in zip(p, c)]
    return {"excluded": excl, "h_acc": round(h_acc, 6), "out_bytes": 32 * ((len(raw[cur]) - per) // per + 1), "bound": bound}


def cov(bound, hold):
    pm = [max(x, 1 - x) for x in p1[hold]]; return round(sum(1 for i in range(NQ) if pm[i] <= bound[i]) / NQ, 4)


# dry runs: the latest block pair stands in for E/F - priors on r3C (E), r3D the hold-out; and the gate on every historical pair
dry = {}
none_C = arm("r3C")
for name, ref in PRIORS.items():
    if ref == "r3CD":                                                       # cannot use r3 itself on r3C: stand-in = r2AB on r3C (one recalibration back, measured)
        g = gate("r2AB", "r3C"); a = arm("r3C", "r2AB"); note = "stand-in: r2AB on r3C (one recalibration back at the time)"
    else:
        g = gate(ref, "r3C"); a = arm("r3C", ref); note = "%s on r3C" % ref
    dry[name] = {"note": note, **g, "none_h_acc": none_C["h_acc"], "validated_h_acc": a["h_acc"] if g["used"] else none_C["h_acc"],
                 "gain": round((a["h_acc"] - none_C["h_acc"]) if g["used"] else 0.0, 6), "out_bytes": a["out_bytes"] if g["used"] else none_C["out_bytes"],
                 "coverage_of_r3D": cov(a["bound"] if g["used"] else none_C["bound"], "r3D")}
pairs = {"%s->%s" % (a_, b_): gate(a_, b_) for a_, b_ in (("r2A", "r2B"), ("r3C", "r3D"), ("r2AB", "r3C"), ("r2AB", "r3D"), ("r0", "r3CD"), ("r0", "r2AB"), ("r1", "r3CD"), ("r1", "r2AB"), ("r0", "r1"))}
# coverage floor: Monte Carlo under the constant-bias model, prior = r3CD counts, p = r3CD pooled
rng = random.Random(20261104); covs = []
for _ in range(2000):
    oE = [max(0, min(SHOTS, int(rng.gauss(SHOTS * p, math.sqrt(SHOTS * p * (1 - p))) + 0.5))) for p in p1["r3CD"]]
    oF = [max(0, min(SHOTS, int(rng.gauss(SHOTS * p, math.sqrt(SHOTS * p * (1 - p))) + 0.5))) for p in p1["r3CD"]]
    o = [cnt["r3CD"][0][i] + oE[i] for i in range(NQ)]; c = [cnt["r3CD"][1][i] + SHOTS for i in range(NQ)]
    pp, _ = M.stats_from_counts(o, c)
    bound = [min(1.0, max(x, 1 - x) + 2.576 * math.sqrt(max(x, 1 - x) * (1 - max(x, 1 - x)) / cc)) for x, cc in zip(pp, c)]
    pmF = [max(x / SHOTS, 1 - x / SHOTS) for x in oF]; covs.append(sum(1 for i in range(NQ) if pmF[i] <= bound[i]) / NQ)
covs.sort(); cov_min = round(covs[int(0.01 * len(covs))], 4)
used_pred = {k: v["used"] for k, v in dry.items()}
res = {"source": {k: {"raw": v, "raw_sha256": sha(_J / v), "bytes": len(raw[k])} for k, v in _R.items()},
       "rule": {"H_ch": H_CH, "policy": "exclude", "shots": SHOTS, "channels": NQ, "r_min": R_MIN, "z_mean_max": M.Z_MEAN, "z_ch_max": M.Z_CH,
                "basis": "r2 floor 0.622 (expected 0.87 within one calibration minus 0.25); z gate from the 3 November counterexample (same calibration mean |z| 0.76-0.92)"},
       "references": {"r0": "r0 raw", "r1": "r1 raw", "r2AB": "r2 A+B pooled (8192 bits/channel)", "r3CD": "r3 C+D pooled (8192 bits/channel)"},
       "priors": {k: {"reference": v, "bits_per_channel": cnt[v][1][0], "age": {"P1_r3CD": "1 recalibration back", "P2_r2AB": "2 back", "P3_r0": "same state, 5 days, 4+ back", "P4_r1": "the other state"}[k]} for k, v in PRIORS.items()},
       "gate_on_history": pairs, "dry_runs_on_r3C": dry, "coverage_model": {"n_mc": 2000, "seed": 20261104, "cov_1pct_quantile": cov_min, "cov_median": round(covs[len(covs) // 2], 4)},
       "predictions_r4": {
           "per_job (E and F)": {"K1": "module accepts", "K2": {"h_mcv_range": [6.5, 8.0]}, "K3": {"ones_fraction_range": [0.40, 0.60]}, "K4": "checker PASS (--expect-rows 1; --prior where cited)",
                                 "K5": {"excluded_channels_range": [0, 4]}, "K6": {"h_acc_range": [round(min(arm(k)["h_acc"] for k in ("r0", "r1", "r2A", "r2B", "r3C", "r3D")) - 0.5, 3), 8.0]}},
           "K-S1": {"claim": "known state: max over {r0, r1, r2AB, r3CD} of r(E, ref) >= %s" % R_MIN, "predicted": True, "basis": "three recalibrations seen, every one landed in a state already seen"},
           "K-S2": {"claim": "the latest state persists: r(E, r3CD) >= %s" % R_MIN, "predicted": True, "basis": "r2->r3 returned to the same state; r0/r2/r3 are one state, r1 the other"},
           "K-S3": {"claim": "stable in itself: r(E, F) >= %s" % R_MIN, "predicted": True, "basis": "r2 0.907, r3 0.919"},
           "K-V": {"claim": "validated gate decision per prior on E", "predicted_used": used_pred, "basis": "dry runs on r3C above (P1 stand-in = r2AB)"},
           "K-V5": {"claim": "every used prior: h_acc_val >= h_acc_none, out_val >= out_none, coverage of F >= cov_min", "cov_min": cov_min, "predicted": True},
           "K-V6": {"claim": "among used priors the gain does not grow with age: gain(P1) >= gain(P2) >= gain(P3)", "predicted": True,
                    "basis": "dry gains: %s" % {k: v["gain"] for k, v in dry.items()}}}}
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: res[k] for k in ("gate_on_history", "dry_runs_on_r3C", "coverage_model", "predictions_r4")}, indent=1, ensure_ascii=False)[:6000])
print(OUT, "sha256", sha(OUT))
