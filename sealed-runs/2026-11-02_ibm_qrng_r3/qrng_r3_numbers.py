#!/usr/bin/env python3
"""qrng_r3_numbers.py - every number of the r3 sealed plan comes from HERE, derived from the committed runs on the same machine
(r0 2026-10-28, r1 2026-10-31, r2 A/B 2026-11-02) and from the published module's own functions (tools/qrng). r2 showed the per-qubit
bias is a property of the vendor's calibration state (r 0.91 within one calibration; r0 and r2 match at 0.85, r1 does not). r3 separates
two questions, fixed before the data, to be run after the vendor's NEXT recalibration (last_update != the r2 one):
  Q1 (physics)  does the bias pattern RETURN to a state already seen?  K-R1: max_S r(C, S) >= r_min over S in {r0, r1, r2AB}; K-R2: r(C, D) >= r_min.
  Q2 (the buyer) does a prior chosen BEFORE the run improve the buyer's result?  prior = r2 A+B counts (8192 bits/channel), three arms on
     block C: none / validated (used only if r(prior, C) >= r_min) / blind (always used); D is the hold-out for the bound's coverage.
     K-P1 (always): validated arm never worse than none (h_acc >=, out_bytes >=) and its bound covers D's per-channel max(p0,p1) in
           >= cov_min channels (cov_min = 1 % quantile of coverage under the constant-bias model, Monte Carlo here);
     K-P2 (branch: return to the r2 state, r(prior, C) >= r_min): the prior is used; its predicted failing list == C's excluded list;
           RMSE(prior p1, C p1) < RMSE(0.5, C p1); h_acc gain in [gain_dry - 0.1, gain_dry + 0.1] where gain_dry is the r2A -> r2B dry run;
     K-P3 (branch: no return): the validated arm is identical to none; the blind arm differs (h_acc or excluded) - the harm validation prevents.
    python3 -I qrng_r3_numbers.py [R0_RAW R1_RAW R2A_RAW R2B_RAW] [OUT]        (stdlib + the published module; no network)
"""
import hashlib, json, math, pathlib, random, statistics, sys

import os
HERE = pathlib.Path(__file__).resolve().parent
_J = pathlib.Path(os.environ.get("QRNG_JOSLATOK", HERE.parent))             # sealed-runs/ (default: the script sits in sealed-runs/<r3 dir>/)
_T = pathlib.Path(os.environ.get("QRNG_TOOLS", _J.parent / "tools" / "qrng"))  # the published module (tools/qrng of the same repo)
sys.path.insert(0, str(_T))
import qrng_modul as M                                                     # noqa: E402  (channel_counts, stats_from_counts, pearson)

a = sys.argv[1:]
_R = {"r0": "2026-10-28_ibm_qrng_r0/raw.bin", "r1": "2026-10-31_ibm_qrng_r1/raw.bin", "r2A": "2026-11-02_ibm_qrng_r2/A/raw.bin", "r2B": "2026-11-02_ibm_qrng_r2/B/raw.bin"}
RAW = dict(zip(_R, [pathlib.Path(x) for x in a[:4]])) if len(a) >= 4 else {k: _J / v for k, v in _R.items()}
OUT = pathlib.Path(a[4]) if len(a) >= 5 else HERE / "numbers_r3.json"
NQ, SHOTS, H_CH, R_MIN = 156, 4096, 0.5, 0.622


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def rmse(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / len(a))


raw = {k: v.read_bytes() for k, v in RAW.items()}
cnt = {k: M.channel_counts(b, NQ) for k, b in raw.items()}
p1 = {k: [o / c for o, c in zip(*cnt[k])] for k in cnt}
prior_ones = [a_ + b_ for a_, b_ in zip(cnt["r2A"][0], cnt["r2B"][0])]; prior_cnt = [a_ + b_ for a_, b_ in zip(cnt["r2A"][1], cnt["r2B"][1])]
p1["r2AB"] = [o / c for o, c in zip(prior_ones, prior_cnt)]


def arm(cur, prior=None):
    """the module's accounting on block `cur` (key) with an optional prior (ones, cnt) ALREADY decided as used -> dict"""
    o, c = cnt[cur]
    if prior:
        o = [x + y for x, y in zip(prior[0], o)]; c = [x + y for x, y in zip(prior[1], c)]
    p, h = M.stats_from_counts(o, c)
    excl = [i for i in range(NQ) if h[i] < H_CH]
    h_acc = sum(cnt[cur][1][i] * (0.0 if i in excl else h[i]) for i in range(NQ)) / len(raw[cur])
    h_mcv = M.mcv_entropy(list(raw[cur]))
    h_eff = min(h_mcv, h_acc); per = max(1, math.ceil(512 / h_eff))
    out_bytes = 32 * ((len(raw[cur]) - per) // per + 1)
    bound = [min(1.0, max(p[i], 1 - p[i]) + 2.576 * math.sqrt(max(p[i], 1 - p[i]) * (1 - max(p[i], 1 - p[i])) / c[i])) for i in range(NQ)]
    return {"excluded": excl, "h_acc": round(h_acc, 6), "h_mcv": round(h_mcv, 6), "out_bytes": out_bytes, "bound": bound}


def coverage(bound, hold):
    pm = [max(x, 1 - x) for x in p1[hold]]
    return sum(1 for i in range(NQ) if pm[i] <= bound[i]) / NQ


# dry runs on the committed data
r_prior_A_B = M.pearson(p1["r2A"], p1["r2B"]); r_prior_AB_r1 = M.pearson(p1["r2AB"], p1["r1"]); r_prior_AB_r0 = M.pearson(p1["r2AB"], p1["r0"])
none_B = arm("r2B"); val_B = arm("r2B", cnt["r2A"])                              # same state: prior r2A on r2B (validated would use it)
none_r1 = arm("r1"); blind_r1 = arm("r1", (prior_ones, prior_cnt))               # other state: prior r2AB on r1 (blind uses it)
none_r0 = arm("r0"); val_r0 = arm("r0", (prior_ones, prior_cnt))                 # r0 is the r2 state too (0.85): a second same-state dry run
_, h_prior = M.stats_from_counts(prior_ones, prior_cnt)
predicted_failing = [i for i in range(NQ) if h_prior[i] < H_CH]
gain_dry = round(val_B["h_acc"] - none_B["h_acc"], 6); gain_dry_r0 = round(val_r0["h_acc"] - none_r0["h_acc"], 6)
# coverage of D by the C-based bound, Monte Carlo under the constant-bias model (p per channel = r2AB pooled), prior = r2AB counts
rng = random.Random(20261103); covs = []
for _ in range(2000):
    cC = [0] * NQ; cD = [0] * NQ
    for i in range(NQ):
        p = p1["r2AB"][i]
        cC[i] = int(rng.gauss(SHOTS * p, math.sqrt(SHOTS * p * (1 - p))) + 0.5)                 # normal approximation of binomial(4096, p)
        cD[i] = int(rng.gauss(SHOTS * p, math.sqrt(SHOTS * p * (1 - p))) + 0.5)
    o = [prior_ones[i] + max(0, min(SHOTS, cC[i])) for i in range(NQ)]; c = [prior_cnt[i] + SHOTS for i in range(NQ)]
    pp, _ = M.stats_from_counts(o, c)
    bound = [min(1.0, max(x, 1 - x) + 2.576 * math.sqrt(max(x, 1 - x) * (1 - max(x, 1 - x)) / cc)) for x, cc in zip(pp, c)]
    pmD = [max(0, min(SHOTS, cD[i])) / SHOTS for i in range(NQ)]; pmD = [max(x, 1 - x) for x in pmD]
    covs.append(sum(1 for i in range(NQ) if pmD[i] <= bound[i]) / NQ)
covs.sort(); cov_min = covs[int(0.01 * len(covs))]
cov_dry = {"val_r2A_on_B_covers_r0": round(coverage(val_B["bound"], "r0"), 4), "none_B_covers_r0": round(coverage(none_B["bound"], "r0"), 4),
           "blind_r2AB_on_r1_covers_r1_itself": round(coverage(blind_r1["bound"], "r1"), 4)}
res = {
    "source": {k: {"raw": str(RAW[k].name), "raw_sha256": sha(RAW[k]), "bytes": len(raw[k])} for k in RAW},
    "prior": {"built_from": ["r2A", "r2B"], "bits_per_channel": prior_cnt[0], "predicted_failing": predicted_failing,
              "note": "qrng_prior.py --channels 156 r2 A/raw.bin B/raw.bin -> prior_r2AB.json; its sha256 is in the plan"},
    "rule": {"H_ch": H_CH, "policy": "exclude", "shots": SHOTS, "channels": NQ, "r_min": R_MIN,
             "r_min_basis": "the r2 sealed floor: expected 0.87 within one calibration minus 0.25; r2 measured 0.907"},
    "states": {"r_r0_r1": round(M.pearson(p1["r0"], p1["r1"]), 4), "r_r0_r2AB": round(r_prior_AB_r0, 4), "r_r1_r2AB": round(r_prior_AB_r1, 4), "r_r2A_r2B": round(r_prior_A_B, 4)},
    "dry_runs": {"same_state_prior_r2A_on_r2B": {"r": round(r_prior_A_B, 6), "none": {k: none_B[k] for k in ("excluded", "h_acc", "out_bytes")},
                                                  "validated": {k: val_B[k] for k in ("excluded", "h_acc", "out_bytes")}, "h_acc_gain": gain_dry,
                                                  "rmse_prior_vs_B": round(rmse(p1["r2A"], p1["r2B"]), 6), "rmse_half_vs_B": round(rmse([0.5] * NQ, p1["r2B"]), 6)},
                 "same_state_prior_r2AB_on_r0": {"r": round(r_prior_AB_r0, 6), "h_acc_gain": gain_dry_r0, "none_excluded": none_r0["excluded"], "validated_excluded": val_r0["excluded"]},
                 "other_state_prior_r2AB_on_r1": {"r": round(r_prior_AB_r1, 6), "validated_used": r_prior_AB_r1 >= R_MIN,
                                                   "none": {k: none_r1[k] for k in ("excluded", "h_acc", "out_bytes")}, "blind": {k: blind_r1[k] for k in ("excluded", "h_acc", "out_bytes")}},
                 "coverage": cov_dry},
    "coverage_model": {"n_mc": 2000, "seed": 20261103, "cov_1pct_quantile": round(cov_min, 4), "cov_median": round(covs[len(covs) // 2], 4),
                       "note": "Monte Carlo: C and D ~ binomial(4096, p_i) with p_i = r2AB pooled p1; bound from prior r2AB + C; coverage = share of channels whose D max(p0,p1) <= bound"},
    "predictions_r3": {
        "per_job (C and D)": {"K1": "module accepts", "K2": {"h_mcv_range": [6.5, 8.0]}, "K3": {"ones_fraction_range": [0.40, 0.60]}, "K4": "checker PASS (--expect-rows 1; with --prior where cited)",
                              "K5": {"excluded_channels_range": [0, 4]}, "K6": {"h_acc_range": [round(min(none_B["h_acc"], none_r1["h_acc"], none_r0["h_acc"]) - 0.5, 3), 8.0]}},
        "K-R1": {"claim": "the pattern RETURNS: max over S in {r0, r1, r2AB} of r(C, S) >= %s" % R_MIN, "predicted": True,
                 "basis": "of the two recalibrations seen (r0->r1, r1->r2) one left the state and one returned to it; the alternative outcome 'new state' is the refutation"},
        "K-R2": {"claim": "the new state is stable within itself: r(C, D) >= %s" % R_MIN, "predicted": True, "basis": "r2 measured 0.907 for 1.3 s apart"},
        "K-P1": {"claim": "validated arm never worse than none: h_acc_val >= h_acc_none, out_val >= out_none, and coverage of D by the validated bound >= cov_min", "cov_min": round(cov_min, 4), "predicted": True},
        "K-P2": {"branch": "r(prior, C) >= r_min (return to the r2 state)", "claims": ["prior used", "predicted_failing == excluded_C (both %s on the dry runs)" % predicted_failing,
                 "RMSE(prior, C) < RMSE(0.5, C)", "h_acc gain in [%s, %s]" % (round(gain_dry - 0.1, 3), round(gain_dry + 0.1, 3))], "basis": "dry run r2A->r2B gain %s; r2AB->r0 gain %s" % (gain_dry, gain_dry_r0)},
        "K-P3": {"branch": "r(prior, C) < r_min (no return)", "claims": ["validated arm identical to none (excluded, h_acc, out_bytes)", "blind arm differs from none in h_acc or excluded"],
                 "basis": "dry run r2AB->r1: validated unused, blind h_acc %s vs none %s" % (blind_r1["h_acc"], none_r1["h_acc"])},
    },
}
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: res[k] for k in ("states", "dry_runs", "coverage_model", "predictions_r3")}, indent=1, ensure_ascii=False))
print(OUT, "sha256", sha(OUT))
