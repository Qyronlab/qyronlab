#!/usr/bin/env python3
"""qrng_r1_numbers.py - every number of the r1 sealed plan comes from HERE (rule 10-23: plan numbers from code, not by hand),
derived from the committed r0 raw samples (sealed-runs/2026-10-28_ibm_qrng_r0/raw.bin, sha256 01edd075...) and the r0 vendor calibration.
Nothing is tuned to pass: the r0 block is the only prior, r1 is a NEW run on the same machine, same circuit.
  1. per-channel (per-qubit) p(1) of r0; the 99 % upper-bound margin at shot count N; failing channels for a grid of (H_ch, N);
  2. the chosen r1 rule: H_ch = 0.5 bit/bit (a BROKEN channel: max(p0,p1) > 0.707 even after the 99 % margin), policy EXCLUDE
     (the block is not refused; the channel's bits count 0 in the entropy accounting and it is named in the receipt);
  3. per-channel entropy accounting on r0: h_acc = sum_c cnt_c*h_c / bytes -> h_eff = min(h_mcv, h_acc) -> output length;
  4. stability: spread of the r0 per-qubit bias vs the binomial noise -> expected r0<->r1 correlation if the bias is a device property;
  5. the K-predictions with their margins, written to numbers_r1.json (sha256 printed; the plan cites it).
    python3 -I qrng_r1_numbers.py [RAW] [KALIB] [OUT]          (stdlib only; no network)
"""
import hashlib, json, math, pathlib, statistics, sys

_R0 = pathlib.Path(__file__).resolve().parent.parent / "2026-10-28_ibm_qrng_r0"      # when the script sits in sealed-runs/<r1 dir>/
RAW = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else _R0 / "raw.bin")
KAL = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else _R0 / "calibration.json")
OUT = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else pathlib.Path(__file__).resolve().parent / "numbers_r1.json")
NQ, Z99 = 156, 2.576


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


raw = RAW.read_bytes()
kal = json.loads(KAL.read_text())
p1, cnt = channels(raw, NQ)
shots = cnt[0]
ro = [float(kal["readout_error"][str(i)]) for i in range(NQ)]
# 1. grid: failing channels if r0 p1 were the true p and N shots were taken
grid = {}
for H in (0.5, 0.6, 0.7, 0.8, 0.9):
    for N in (4096, 8192, 16384):
        bad = [i for i in range(NQ) if h_bound(p1[i], N) < H]
        grid["H%.1f_N%d" % (H, N)] = {"failing": len(bad), "qubits": bad[:12]}
margin = {N: Z99 * math.sqrt(0.25 / N) for N in (4096, 8192, 16384)}
# 2. the chosen rule
H_CH, N_R1 = 0.5, 4096
pm_broken = 2 ** -H_CH                                           # max(p0,p1) above this (after margin) = broken channel
excluded = [i for i in range(NQ) if h_bound(p1[i], shots) < H_CH]
# 3. accounting on r0 with that rule
h_c = [h_bound(p, shots) for p in p1]
h_acc = sum(c * (0 if i in excluded else h) for i, (c, h) in enumerate(zip(cnt, h_c))) / len(raw)
h_mcv = mcv_entropy(list(raw))
h_eff = min(h_mcv, h_acc)
per = max(1, math.ceil(512 / h_eff))
out_bytes = 32 * ((len(raw) - per) // per + 1)
# 4. stability of the per-qubit bias
sd_obs = statistics.pstdev(p1)
sd_noise = math.sqrt(0.25 / shots)
var_bias = max(0.0, sd_obs ** 2 - sd_noise ** 2)
r_expected = var_bias / (var_bias + sd_noise ** 2) if var_bias + sd_noise ** 2 > 0 else 0.0
dev3 = [i for i in range(NQ) if abs(p1[i] - 0.5) > 3 * sd_noise]
dev10 = [i for i in range(NQ) if abs(p1[i] - 0.5) > 10 * sd_noise]
# vendor-explains check: a readout error e on a 0.5 source moves p1 by at most e/2 in either direction (asymmetric worst case)
unexplained = [i for i in dev3 if abs(p1[i] - 0.5) > ro[i] / 2 + 3 * sd_noise]
res = {
    "source": {"raw": "sealed-runs/2026-10-28_ibm_qrng_r0/" + RAW.name, "raw_sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
               "calibration": "sealed-runs/2026-10-28_ibm_qrng_r0/" + KAL.name,
               "calibration_sha256": hashlib.sha256(KAL.read_bytes()).hexdigest(), "shots": shots, "qubits": NQ},
    "r0_channels": {"p1_min": round(min(p1), 6), "p1_max": round(max(p1), 6), "p1_median": round(statistics.median(p1), 6),
                    "p1_sd": round(sd_obs, 6), "binomial_sd": round(sd_noise, 6), "dev_gt_3sd": len(dev3), "dev_gt_10sd": dev10,
                    "unexplained_by_vendor_readout": [[i, round(p1[i], 4), round(ro[i], 4)] for i in unexplained]},
    "margin_99pct_at_N": {str(k): round(v, 6) for k, v in margin.items()},
    "grid_failing_channels": grid,
    "rule_r1": {"H_ch": H_CH, "max_p_broken": round(pm_broken, 6), "policy": "exclude", "shots": N_R1,
                "why": "0.9 at 4096 shots fails 40/156 healthy-but-biased qubits (margin 0.020 alone costs 0.057 bit) = false red; "
                       "0.5 names a channel broken only when max(p0,p1) exceeds 0.707 after the 99 % margin - on r0 that is exactly the "
                       "qubit whose vendor readout error (0.33) explains it; biased-but-usable channels are charged in the accounting instead"},
    "r0_under_rule_r1": {"excluded": [[i, round(p1[i], 4), round(h_c[i], 4), round(ro[i], 4)] for i in excluded], "h_mcv": round(h_mcv, 6),
                         "h_acc": round(h_acc, 6), "h_eff": round(h_eff, 6), "samples_per_chunk": per, "out_bytes": out_bytes},
    "stability": {"var_bias": round(var_bias, 9), "var_noise": round(sd_noise ** 2, 9), "r_expected_if_device_property": round(r_expected, 4)},
}
# 5. predictions (margins stated here, not after the data)
res["predictions_r1"] = {
    "K1": "module ACCEPTS the block under policy exclude (health tests 0 failures, h_mcv >= 6.0, |lag1| <= 5/sqrt(N), no replay)",
    "K2": {"h_mcv_range": [6.5, 8.0]},
    "K3": {"ones_fraction_range": [0.40, 0.60]},
    "K4": "buyer checker (qrng_fuggetlen) PASS, accounting and exclusion recomputed",
    "K5": {"excluded_channels_range": [0, 4], "basis": "r0 under the same rule excludes %d (%s); a second run on the same machine at most "
           "a handful - more than 4 = the rule or the machine changed" % (len(excluded), excluded)},
    "K6": {"h_acc_range": [round(h_acc - 0.5, 3), 8.0], "basis": "r0 h_acc %.3f; the accounting may drop by the drift of a few channels, "
           "not by half a bit per sample" % h_acc},
    "K7": {"pearson_r_p1_r0_vs_r1_min": round(max(0.0, r_expected - 0.25), 3), "basis": "expected r %.3f if the per-qubit bias is a device "
           "property (var_bias/(var_bias+var_noise)); 0.25 margin for calibration drift between the runs; r below the minimum = the "
           "bias pattern is NOT stable = the guard finding on q45 was a one-off" % r_expected},
}
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: res[k] for k in ("r0_channels", "margin_99pct_at_N", "rule_r1", "r0_under_rule_r1", "stability", "predictions_r1")}, indent=1, ensure_ascii=False))
print("grid:", {k: v["failing"] for k, v in grid.items()})
print(OUT, "sha256", hashlib.sha256(OUT.read_bytes()).hexdigest())
