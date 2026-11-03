#!/usr/bin/env python3
"""qrng_prior.py - build a per-channel PRIOR from earlier raw blocks of the same source: counts of ones and bits per channel
(bit j of the MSB-first stream belongs to channel j mod N), summed over the given raw files. The module uses it with --prior
(validated: only if the current block correlates with it, r >= r_min; blind: always - a test arm), the buyer re-checks it with
the same file. The file carries the sha256 of every raw it was built from, so anyone can rebuild it from the published bytes.
    python3 -I qrng_prior.py --channels N --out prior.json [--source TEXT] RAW [RAW ...]
"""
import argparse, hashlib, json, sys

ap = argparse.ArgumentParser(); ap.add_argument("--channels", type=int, required=True); ap.add_argument("--out", required=True)
ap.add_argument("--source", default=""); ap.add_argument("raws", nargs="+")
a = ap.parse_args()
n = a.channels; ones, cnt, shas = [0] * n, [0] * n, []
for path in a.raws:
    raw = open(path, "rb").read(); shas.append(hashlib.sha256(raw).hexdigest())
    for i, byte in enumerate(raw):
        for k in range(8):
            c = (8 * i + k) % n
            cnt[c] += 1; ones[c] += (byte >> (7 - k)) & 1
if min(cnt) == 0:
    sys.exit("every channel needs bits")
d = {"v": 1, "n": n, "source": a.source, "raw_sha256": shas, "ones": ones, "cnt": cnt}
b = (json.dumps(d, sort_keys=True, separators=(",", ":")) + "\n").encode()
open(a.out, "wb").write(b)
print(json.dumps({"out": a.out, "sha256": hashlib.sha256(b).hexdigest(), "n": n, "bits_per_channel": cnt[0], "raws": len(shas)}))
