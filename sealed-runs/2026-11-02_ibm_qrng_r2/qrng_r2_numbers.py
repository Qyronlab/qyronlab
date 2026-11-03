#!/usr/bin/env python3
"""qrng_r2_numbers.py - every number of the r2 sealed plan comes from HERE (rule 10-23: plan numbers from code, not by hand),
derived from the two committed earlier runs on the same machine (r0 2026-10-28, r1 2026-10-31: raw.bin + the vendor calibration
snapshot of each). r1 refuted K7 (the per-qubit bias pattern does not repeat across three days, r = 0.356 against a sealed floor of
0.651). r2 asks the next question, fixed before the data: does the per-qubit bias repeat within MINUTES, under one calibration?
  1. per-channel p(1) of r0 and r1; the within-run excess variance of the bias over binomial noise (var_bias) in each run;
  2. the expected correlation of two runs minutes apart if the bias is constant within one calibration:
     r_expected = var_bias / (var_bias + var_noise), var_bias pooled over r0 and r1 (same formula as r1, two independent samples);
     the sealed floor is r_expected - 0.25 (the same margin r1 used);
  3. the day-scale reference: the observed r(r0, r1) (3 days) - the order claim K8 says r(A,B) > r(A,r1) > r(A,r0) (age: minutes, ~2 days, ~5 days);
  4. the vendor table: r(readout_error r0, r1) observed - K9 asks the same stability for r2 vs r1 (>= 0.9);
  5. K1-K6 per job as in r1 (bands recomputed from r0 AND r1 under the r1 rule); written to numbers_r2.json (sha256 printed).
    python3 -I qrng_r2_numbers.py [R0_RAW R0_KAL R1_RAW R1_KAL] [OUT]          (stdlib only; no network)
"""
import hashlib, json, math, pathlib, statistics, sys

_J = pathlib.Path(__file__).resolve().parent.parent                      # when the script sits in sealed-runs/<r2 dir>/
_R0, _R1 = _J / "2026-10-28_ibm_qrng_r0", _J / "2026-10-31_ibm_qrng_r1"
a = sys.argv[1:]
R0_RAW, R0_KAL, R1_RAW, R1_KAL = [pathlib.Path(x) for x in (a[:4] if len(a) >= 4 else (_R0 / "raw.bin", _R0 / "calibration.json", _R1 / "raw.bin", _R1 / "calibration.json"))]
OUT = pathlib.Path(a[4]) if len(a) >= 5 else pathlib.Path(__file__).resolve().parent / "numbers_r2.json"
NQ, Z99, SHOTS = 156, 2.576, 4096


def channels(raw, n):
    ones, cnt = [0] * n, [0] * n
    for i, byte in enumerate(raw):
        for k in range(8):
            c = (8 * i + k) % n
            cnt[c] += 1; ones[c] += (byte >> (7 - k)) & 1
    return [o / c for o, c in zip(ones, cnt)], cnt


def h_bound(p1, n):
    pm = max(p1, 1 - p1)
    return -math.log2(min(1.0, pm + Z99 * math.sqrt(pm * (1 - pm) / n)))


def mcv_entropy(x):
    n = len(x); p = max(x.count(v) for v in set(x)) / n
    return -math.log2(min(1.0, p + Z99 * math.sqrt(p * (1 - p) / (n - 1))))


def pearson(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((v - mx) ** 2 for v in x)); sy = math.sqrt(sum((v - my) ** 2 for v in y))
    return sum((u - mx) * (v - my) for u, v in zip(x, y)) / (sx * sy) if sx and sy else 0.0


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


H_CH, POLICY = 0.5, "exclude"
runs = {}
for name, rp, kp in (("r0", R0_RAW, R0_KAL), ("r1", R1_RAW, R1_KAL)):
    raw = rp.read_bytes(); kal = json.loads(kp.read_text())
    p1, cnt = channels(raw, NQ); shots = cnt[0]
    sd_obs = statistics.pstdev(p1); sd_noise = math.sqrt(0.25 / shots)
    h_c = [h_bound(p, shots) for p in p1]
    excluded = [i for i in range(NQ) if h_c[i] < H_CH]
    h_acc = sum(c * (0 if i in excluded else h) for i, (c, h) in enumerate(zip(cnt, h_c))) / len(raw)
    runs[name] = {"raw": str(rp.name), "raw_sha256": sha(rp), "raw_bytes": len(raw), "calibration_sha256": sha(kp), "shots": shots,
                  "calib_last_update": kal.get("last_update"), "p1": p1, "ro": [float(kal["readout_error"][str(i)]) for i in range(NQ)],
                  "sd_p1": round(sd_obs, 6), "sd_noise": round(sd_noise, 6), "var_bias": max(0.0, sd_obs ** 2 - sd_noise ** 2),
                  "excluded": excluded, "h_acc": round(h_acc, 6), "h_mcv": round(mcv_entropy(list(raw)), 6)}
var_noise = 0.25 / SHOTS
var_bias_pooled = (runs["r0"]["var_bias"] + runs["r1"]["var_bias"]) / 2
r_expected = var_bias_pooled / (var_bias_pooled + var_noise)
r_min = round(max(0.0, r_expected - 0.25), 3)
r_r0_r1 = pearson(runs["r0"]["p1"], runs["r1"]["p1"])
ro_r0_r1 = pearson(runs["r0"]["ro"], runs["r1"]["ro"])
h_acc_floor = round(min(runs["r0"]["h_acc"], runs["r1"]["h_acc"]) - 0.5, 3)
res = {
    "source": {k: {kk: v for kk, v in r.items() if kk not in ("p1", "ro")} for k, r in runs.items()},
    "rule": {"H_ch": H_CH, "policy": POLICY, "shots": SHOTS, "channels": NQ, "max_p_broken": round(2 ** -H_CH, 6),
             "why": "the r1 rule unchanged: a channel is broken only when max(p0,p1) exceeds 0.707 after the 99 % margin; "
                    "biased-but-usable channels are charged in the per-channel accounting"},
    "stability": {"var_noise": round(var_noise, 9), "var_bias_r0": round(runs["r0"]["var_bias"], 9), "var_bias_r1": round(runs["r1"]["var_bias"], 9),
                  "var_bias_pooled": round(var_bias_pooled, 9), "r_expected_minutes_apart_if_bias_constant": round(r_expected, 4),
                  "r_observed_r0_r1_3_days": round(r_r0_r1, 4), "readout_table_r_r0_r1": round(ro_r0_r1, 4)},
    "predictions_r2": {
        "per_job": {"K1": "module ACCEPTS the block under policy exclude (health tests 0 failures, h_mcv >= 6.0, |lag1| <= 5/sqrt(N), no replay)",
                    "K2": {"h_mcv_range": [6.5, 8.0]}, "K3": {"ones_fraction_range": [0.40, 0.60]},
                    "K4": "buyer checker (qrng_fuggetlen, --expect-rows 1) PASS, accounting and exclusion recomputed",
                    "K5": {"excluded_channels_range": [0, 4], "basis": "r0 under the rule excludes %d, r1 %d" % (len(runs["r0"]["excluded"]), len(runs["r1"]["excluded"]))},
                    "K6": {"h_acc_range": [h_acc_floor, 8.0], "basis": "r0 h_acc %.3f, r1 %.3f; floor = min - 0.5 bit" % (runs["r0"]["h_acc"], runs["r1"]["h_acc"])}},
        "K7": {"pearson_r_p1_A_vs_B_min": r_min, "basis": "two jobs minutes apart under ONE vendor calibration; expected r %.3f if the per-qubit bias is "
               "constant within a calibration (var_bias pooled over r0 and r1 / (var_bias + var_noise)); 0.25 margin as in r1; below the floor = the "
               "bias is not even stable over minutes = uncalibratable drift above shot noise" % r_expected,
               "scored_only_if": "calibration last_update before job A == after job B; otherwise K7 and K8 are UNMEASURED (reported, not re-scored)"},
        "K8": {"order": "r(A,B) > r(A,r1) > r(A,r0)", "basis": "the bias correlation falls with calibration age (minutes, ~2 days, ~5 days); "
               "day-scale reference r(r0,r1) = %.3f" % r_r0_r1},
        "K9": {"readout_table_r_r2_vs_r1_min": 0.9, "basis": "the vendor's readout-error table was stable r0<->r1 (r %.3f); r2 (snapshot before A) vs r1" % ro_r0_r1},
    },
}
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: res[k] for k in ("stability", "predictions_r2")}, indent=1, ensure_ascii=False))
print("excluded r0", runs["r0"]["excluded"], "r1", runs["r1"]["excluded"], "| h_acc r0", runs["r0"]["h_acc"], "r1", runs["r1"]["h_acc"])
print(OUT, "sha256", sha(OUT))
