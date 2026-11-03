"""z5_sema_n.py - Z5 per-scheme timing with the raw per-sample distribution (replaces the ad-hoc N=2000 one-liner of 2026-10-23).
Usage: nice -n 15 .venv-pq/bin/python z5_sema_n.py <scheme> <N> <raw_out.json>
stdout: JSON summary (median, p10, p90, min, max per op; loadavg before/after; sha256 of the raw file).
raw_out.json: all N samples (ms) per op, so the second arm can recompute every summary number."""
import hashlib, json, os, statistics, sys, time, platform
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mesh import attest
scheme, N, raw_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
MSG = b"seat/z5 measurement message " * 4
def samples(fn, n):
    t = []
    for _ in range(n):
        a = time.perf_counter(); fn(); t.append((time.perf_counter() - a) * 1000.0)
    return t
def summary(t):
    q = statistics.quantiles(t, n=10)
    return {"median_ms": round(statistics.median(t), 4), "p10_ms": round(q[0], 4), "p90_ms": round(q[8], 4),
            "min_ms": round(min(t), 4), "max_ms": round(max(t), 4), "n": len(t)}
load_before = os.getloadavg()
priv, pub, _ = attest.generate(scheme)
sig = priv.sign(MSG)
pubk = attest.SCHEMES[scheme]["load_public"](pub)
pubk.verify(sig, MSG)
raw = {"scheme": scheme, "n": N, "pid": os.getpid(),
       "keygen_ms": samples(lambda: attest.generate(scheme), N),
       "sign_ms": samples(lambda: priv.sign(MSG), N),
       "verify_ms": samples(lambda: pubk.verify(sig, MSG), N)}
load_after = os.getloadavg()
raw_bytes = json.dumps(raw, sort_keys=True).encode()
with open(raw_path, "wb") as f:
    f.write(raw_bytes)
out = {"scheme": scheme, "n": N, "pid": os.getpid(), "host": platform.node(), "python": platform.python_version(),
       "public_key_bytes": len(pub), "signature_bytes": len(sig),
       "loadavg_before": load_before, "loadavg_after": load_after,
       "keygen": summary(raw["keygen_ms"]), "sign": summary(raw["sign_ms"]), "verify": summary(raw["verify_ms"]),
       "raw_file": os.path.basename(raw_path), "raw_sha256": hashlib.sha256(raw_bytes).hexdigest()}
print(json.dumps(out, indent=1, sort_keys=True))
