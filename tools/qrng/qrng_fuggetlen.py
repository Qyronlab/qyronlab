#!/usr/bin/env python3
"""qrng_fuggetlen.py - INDEPENDENT checker of a qrng_modul.py ledger (imports nothing from it): what the buyer runs.
  1. every row: both signatures (Ed25519, ML-DSA-65) valid over the canonical receipt, the keys equal the first row's keys
     (or --pin-ed25519 / --pin-mldsa65 if given); seq = 0,1,2,..; prev_sha256 = sha256 of the previous row's canonical JSON;
     rc 0 = PASS (both signatures checked), rc 2 = PASS-PARTIAL (ML-DSA-65 not checked: cryptography < 45 or --without-mldsa),
     rc 1 = FAIL. Truncation is not detectable from the ledger alone: pass --expect-rows N from an out-of-band source.
  2. audit rows: the kept raw file hashes to raw_sha256; health tests, min-entropy, lag-1 and chunk hashes recomputed here with
     own code and equal to the receipt; accepted == (no failing test and no replay), with replay judged from EARLIER rows only;
  3. accepted rows: the output block file exists and hashes to out_sha256, and the extraction is recomputed from raw;
  4. no receipt claims quantum certification ("certification" must be "statistical");
  5. production rows (audit false): raw must be ABSENT (a retained raw with a public extractor equals the output); only signatures,
     chain, replay (from receipt hashes) and the output block's hash are checked - the buyer verifies the SOURCE on audit rows.
    quantum/mesh/.venv-pq/bin/python -I qrng_fuggetlen.py DIR [--pin-ed25519 B64] [--pin-mldsa65 B64]   -> JSON, rc 0 = all hold
"""
import argparse, base64, hashlib, json, math, os, sys
from cryptography.hazmat.primitives.asymmetric import ed25519
try:                                                     # ML-DSA-65 needs cryptography >= 45; older installs still get every
    from cryptography.hazmat.primitives.asymmetric import mldsa   # other check, but the verdict can then only be PASS-PARTIAL
    MLDSA_IMPORT = None
except ImportError as _e:
    mldsa, MLDSA_IMPORT = None, "UNAVAILABLE(cryptography<45: %s)" % type(_e).__name__


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def binom_cut(w, p, alpha):
    tail, c = 0.0, w
    while c >= 0:
        tail += math.comb(w, c) * p ** c * (1 - p) ** (w - c)
        if tail > alpha:
            return c + 1
        c -= 1
    return 1


def recompute(raw, h):
    x = list(raw); n = len(x)
    rc = 1 + math.ceil(20 / h); ac = binom_cut(512, 2.0 ** -h, 2.0 ** -20)
    rf, run = 0, 1
    for i in range(1, n):
        if x[i] == x[i - 1]:
            run += 1
            if run >= rc:
                rf += 1; run = 1
        else:
            run = 1
    af = sum(1 for s in range(0, n - 511, 512) if x[s:s + 512].count(x[s]) >= ac)
    cnt = [0] * 256
    for v in x:
        cnt[v] += 1
    p = max(cnt) / n
    hm = -math.log2(min(1.0, p + 2.576 * math.sqrt(p * (1 - p) / (n - 1))))
    mu = sum(x) / n; var = sum((v - mu) ** 2 for v in x)
    r1 = 0.0 if var == 0 else sum((x[i] - mu) * (x[i + 1] - mu) for i in range(n - 1)) / var
    chunks = [sha(raw[i:i + 4096]) for i in range(0, n - 4095, 4096)]
    return {"rct_cutoff": rc, "rct_failures": rf, "apt_window": 512, "apt_cutoff": ac, "apt_failures": af}, hm, r1, chunks


def chan_counts(raw, n):
    ones, cnt = [0] * n, [0] * n
    pos = 0
    for byte in raw:
        for k in range(7, -1, -1):
            cnt[pos % n] += 1; ones[pos % n] += (byte >> k) & 1; pos += 1
    return ones, cnt


def chan_stats(raw, n, h_bit, prior=None, mode="validated", r_min=0.0):
    """Own recomputation of the per-channel test: -> (failing [[c, p1, h]], per-channel h list, CURRENT per-channel bit counts, prior record).
    With a prior (counts from earlier blocks): r = Pearson of the per-channel p1 (prior vs current); used = blind, or r >= r_min;
    when used the bound is taken at the combined counts. The accounting weights stay the current block's counts."""
    ones, cnt = chan_counts(raw, n)
    prec = None
    if prior is not None:
        pp = [o / c for o, c in zip(prior["ones"], prior["cnt"])]; pc = [o / c for o, c in zip(ones, cnt)]
        ma, mb = sum(pp) / n, sum(pc) / n
        sa = math.sqrt(sum((x - ma) ** 2 for x in pp)); sb = math.sqrt(sum((y - mb) ** 2 for y in pc))
        r = sum((x - ma) * (y - mb) for x, y in zip(pp, pc)) / (sa * sb) if sa and sb else 0.0
        z = []
        for op, cp, oc, cc in zip(prior["ones"], prior["cnt"], ones, cnt):      # two-proportion z per channel (arm B #770: r alone is blind to scale)
            q = (op + oc) / (cp + cc); sd = math.sqrt(max(q * (1 - q), 1e-12) * (1 / cp + 1 / cc)); z.append(abs(op / cp - oc / cc) / sd)
        z_mean = sum(z) / n; compatible = z_mean <= 1.5
        used = True if mode == "blind" else (r >= r_min and compatible)
        comb = (list(range(n)) if mode == "blind" else [c for c in range(n) if z[c] <= 4.0]) if used else []
        hp = []
        for o, c in zip(prior["ones"], prior["cnt"]):
            q = o / c; m = q if q > 0.5 else 1 - q
            hp.append(-math.log2(min(1.0, m + 2.576 * math.sqrt(m * (1 - m) / c))))
        prec = {"r": round(r, 6), "z_mean": round(z_mean, 4), "z_max": round(max(z), 4), "compatible": compatible, "used": used,
                "channels_combined": len(comb), "predicted_failing": [c for c in range(n) if hp[c] < h_bit]}
        bo = [ones[c] + (prior["ones"][c] if c in comb else 0) for c in range(n)]
        bc = [cnt[c] + (prior["cnt"][c] if c in comb else 0) for c in range(n)]
    else:
        bo, bc = ones, cnt
    out, hs = [], []
    for c in range(n):
        p = ones[c] / cnt[c]; m = p if p > 0.5 else 1 - p                         # the failing list is the CURRENT block's alone
        hb = -math.log2(min(1.0, m + 2.576 * math.sqrt(m * (1 - m) / cnt[c])))
        if hb < h_bit:
            out.append([c, round(p, 6), round(hb, 6)])
        q = bo[c] / bc[c]; mq = q if q > 0.5 else 1 - q                           # the credit h may come from the combined counts
        hs.append(-math.log2(min(1.0, mq + 2.576 * math.sqrt(mq * (1 - mq) / bc[c]))))
    return out, hs, cnt, prec


def chan_fail(raw, n, h_bit):
    return chan_stats(raw, n, h_bit)[0]


def load_prior(path):
    b = open(path, "rb").read(); d = json.loads(b); d["_sha256"] = sha(b); return d


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--pin-ed25519"); ap.add_argument("--pin-mldsa65")
    ap.add_argument("--without-mldsa", action="store_true", help="skip the ML-DSA-65 check (same path as an old cryptography); verdict is then PASS-PARTIAL at best")
    ap.add_argument("--expect-rows", type=int, help="row count the buyer got out-of-band (e.g. the published SHA256SUMS); fewer rows = truncated ledger")
    ap.add_argument("--prior", action="append", default=[], help="prior counts file(s) the receipts cite (qrng_prior.py output); matched by sha256")
    a = ap.parse_args(argv)
    mldsa_state = "forced-off(--without-mldsa)" if a.without_mldsa else (MLDSA_IMPORT or "verified")
    use_mldsa = mldsa_state == "verified"
    bad, rows = [], [json.loads(l) for l in open(os.path.join(a.dir, "ledger.jsonl"), encoding="utf-8") if l.strip()]
    priors = {}
    for pp in a.prior:
        d = load_prior(pp); priors[d["_sha256"]] = d
    pe = a.pin_ed25519 or (rows[0]["pub_ed25519_b64"] if rows else None)
    pm = a.pin_mldsa65 or (rows[0]["pub_mldsa65_b64"] if rows else None)
    seen_raw, seen_chunks, prev = set(), set(), "0" * 64
    for i, row in enumerate(rows):
        r = row["receipt"]; m = canon(r)
        try:
            if row["pub_ed25519_b64"] != pe or row["pub_mldsa65_b64"] != pm:
                raise ValueError("key differs from the pinned key")
            ed25519.Ed25519PublicKey.from_public_bytes(base64.b64decode(pe)).verify(base64.b64decode(row["sig_ed25519_b64"]), m)
            if use_mldsa:
                mldsa.MLDSA65PublicKey.from_public_bytes(base64.b64decode(pm)).verify(base64.b64decode(row["sig_mldsa65_b64"]), m)
        except Exception as e:
            bad.append("row %d: signature: %s" % (i, type(e).__name__ if not isinstance(e, ValueError) else e))
        if r.get("seq") != i:
            bad.append("row %d: seq %r" % (i, r.get("seq")))
        if r.get("prev_sha256") != prev:
            bad.append("row %d: chain broken" % i)
        prev = sha(canon(row))
        if r.get("certification") != "statistical":
            bad.append("row %d: certification %r claimed without physics evidence" % (i, r.get("certification")))
        rp = os.path.join(a.dir, "raw", r["raw_sha256"] + ".bin")
        if not r.get("audit"):                                   # production block: raw must NOT be retained; only what the
            if os.path.exists(rp):                               # receipt and the ledger give can be checked
                bad.append("row %d: production block but its raw samples are retained (secrecy)" % i)
            if r["accepted"]:
                try:
                    got = open(os.path.join(a.dir, "blocks", "%06d.bin" % i), "rb").read()
                    if sha(got) != r["out_sha256"] or len(got) != r["out_bytes"]:
                        raise ValueError("mismatch")
                except Exception:
                    bad.append("row %d: output block missing or not matching its receipt" % i)
                # replay is the one source test still checkable without the raw: the receipt's own hashes against earlier rows
                # (arm B 11-02 found this branch skipped it: two accepted production rows on the same raw passed)
                if r["raw_sha256"] in seen_raw or any(c in seen_chunks for c in r["chunk_sha256"]):
                    bad.append("row %d: accepted=True but its raw/chunks repeat an earlier row (replay)" % i)
            seen_raw.add(r["raw_sha256"]); seen_chunks.update(r["chunk_sha256"])
            continue
        try:
            raw = open(rp, "rb").read()
            if sha(raw) != r["raw_sha256"] or len(raw) != r["raw_bytes"]:
                raise ValueError("raw file does not match")
        except Exception as e:
            bad.append("row %d: raw: %s" % (i, e)); continue
        hl, hm, r1, chunks = recompute(raw, r["h_design"])
        if hl != r["health"] or round(hm, 6) != r["h_mcv"] or round(r1, 6) != r["lag1"] or chunks != r["chunk_sha256"]:
            bad.append("row %d: health/entropy/chunks differ from recomputation" % i)
        ch = r.get("channels")
        h_use, chan_refuses = hm, False
        if ch is not None:
            pr = ch.get("prior"); prior = None
            if pr is not None:
                prior = priors.get(pr.get("sha256"))
                if prior is None:
                    bad.append("row %d: receipt cites a prior %s... that the buyer was not given (--prior)" % (i, str(pr.get("sha256"))[:12])); continue
                if pr.get("mode") not in ("validated", "blind") or not isinstance(pr.get("r_min"), (int, float)):
                    bad.append("row %d: prior mode/r_min malformed" % i); continue
            fails, hs, cnts, prec = chan_stats(raw, ch["n"], ch["h_bit"], prior, pr.get("mode") if pr else "validated", pr.get("r_min", 0.0) if pr else 0.0)
            if pr is not None and (prec["r"] != pr.get("r") or prec["used"] != pr.get("used") or prec["predicted_failing"] != pr.get("predicted_failing")
                                   or prior["n"] != ch["n"] or prior["cnt"][0] != pr.get("bits_per_channel")
                                   or ("z_mean" in pr and (prec["z_mean"] != pr.get("z_mean") or prec["compatible"] != pr.get("compatible")
                                                           or prec["channels_combined"] != pr.get("channels_combined")))
                                   or ("z_mean" not in pr and pr.get("used") and pr.get("mode") == "validated")):   # a receipt without the z gate claiming validated use: refused (old rule)
                bad.append("row %d: prior r/used/predicted list differ from recomputation" % i)
            if fails != ch["failing"]:
                bad.append("row %d: channel test differs from recomputation" % i)
            policy = ch.get("policy", "refuse")
            exp_excl = [f[0] for f in fails] if policy == "exclude" else []
            chan_refuses = bool(fails) and policy == "refuse"
            if "h_acc" in ch:                                    # receipts with per-channel accounting (10-31): recompute it
                if ch.get("excluded", []) != exp_excl:
                    bad.append("row %d: excluded channels differ from recomputation" % i)
                h_acc = sum(cnts[c] * (0.0 if c in exp_excl else hs[c]) for c in range(ch["n"])) / len(raw)
                h_use = min(hm, h_acc)
                if round(h_acc, 6) != ch.get("h_acc") or round(h_use, 6) != ch.get("h_eff"):
                    bad.append("row %d: channel accounting (h_acc/h_eff) differs from recomputation" % i)
                if h_use < 0.5:
                    chan_refuses = True
        replay = r["raw_sha256"] in seen_raw or any(c in seen_chunks for c in chunks)
        ok = not (hl["rct_failures"] or hl["apt_failures"] or hm < r["h_design"] or abs(r1) > 5 / math.sqrt(len(raw)) or replay
                  or chan_refuses)
        if ok != r["accepted"]:
            bad.append("row %d: accepted=%s but recomputed tests say %s" % (i, r["accepted"], ok))
        if r["accepted"] and ok:                     # accepted-but-failing is already named above; no extraction from it
            per = max(1, math.ceil(512 / h_use))
            exp = b"".join(hashlib.sha256(raw[j:j + per]).digest() for j in range(0, len(raw) - per + 1, per))
            try:
                got = open(os.path.join(a.dir, "blocks", "%06d.bin" % i), "rb").read()
            except OSError:
                got = None
            if got is None or sha(got) != r["out_sha256"] or got != exp:
                bad.append("row %d: output block missing or not the extraction of the raw" % i)
        seen_raw.add(r["raw_sha256"]); seen_chunks.update(chunks)
    if a.expect_rows is not None and len(rows) != a.expect_rows:
        bad.append("row count %d differs from the expected %d (truncated or padded ledger)" % (len(rows), a.expect_rows))
    fp = {"ed25519_sha256": sha(base64.b64decode(pe)) if pe else None, "mldsa65_sha256": sha(base64.b64decode(pm)) if pm else None}
    verdict = "FAIL" if bad else ("PASS" if use_mldsa else "PASS-PARTIAL")      # never PASS without the second signature checked
    v = {"rows": len(rows), "accepted": sum(1 for r in rows if r["receipt"]["accepted"]), "audit_rows": sum(1 for r in rows if r["receipt"].get("audit")),
         "mldsa65": mldsa_state, "key_fingerprints": fp, "problems": bad, "verdict": verdict}
    print(json.dumps(v, indent=1))
    return 1 if bad else (0 if verdict == "PASS" else 2)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
