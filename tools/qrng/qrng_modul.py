#!/usr/bin/env python3
"""qrng_modul.py - reference software of the QRNG module (modem plan §12, M1; the owner's go, 10-28). Hardware-free: it takes a file
of raw 8-bit samples (from whatever source - later the module's ADC) and does what the module firmware must do for ONE block:
  1. health tests in the SP 800-90B 4.4 style, with the DESIGN entropy H (bits/sample) fixed before the data:
     repetition count test (cutoff 1 + ceil(20/H)) and adaptive proportion test (window 512, binomial cutoff at alpha 2^-20);
  2. on-line min-entropy estimate of the block: most-common-value with the 99 % upper bound (SP 800-90B 6.3.1 form);
     lag-1 serial correlation |r1| <= 5/sqrt(N) (threshold fixed here, before any data);
  3. replay check against the ledger: the raw block hash and every 4096-byte aligned chunk hash must be new;
  3c. optional prior (--prior FILE, --prior-mode validated|blind, --prior-r-min R): per-channel counts from EARLIER blocks of the
     same source; validated (default) uses them only if r(prior, current) >= R AND the per-channel two-proportion z says the same p
     (mean |z| <= 1.5; arm B counterexample 2026-11-03), and combines a channel only if its own |z| <= 4; blind always (test arm);
     when used, the per-channel 99 % bound of the channels that stay in is taken at the combined counts (the broken-channel decision is
     the current block's alone - arm B 2026-11-03 #782). The receipt records sha, mode, r, z, used; the buyer recomputes with the same file.
  3b. optional per-channel test (--channels N --h-bit H): the bit stream is N interleaved sources (one per qubit / detector);
     every channel must keep a per-bit min-entropy >= H at the 99 % bound (10-28 r0 lesson: a block can pass while one channel is bad);
     --channel-policy refuse (default): a failing channel refuses the block; exclude (r1 rule, 10-31): the failing channels are
     NAMED in the receipt and their bits count 0 in the entropy accounting, the block is accepted with a shorter output.
     Per-channel accounting (always with --channels): h_acc = sum_c cnt_c*h_c / bytes; h_eff = min(h_mcv, h_acc) sizes the output
     (a small bias costs output, not the block; r1 plan: numbers_r1.json);
  4. conditioning: SHA-256 over chunks that each carry >= 512 bits of ESTIMATED min-entropy (factor 2 margin) -> 32 output bytes per chunk;
  4b. block kind (arm B #607): AUDIT block (--audit) keeps the raw samples for the buyer's recomputation - its output is diagnostic
     only, never key material; PRODUCTION block (default) never stores the raw: with a public deterministic extractor, raw = output.
  5. a block receipt (seq, prev hash, raw sha256, health, entropy, output sha256, time, source id, audit flag, entropy model), signed with Ed25519 + ML-DSA-65
     (the two schemes of mesh/attest.py), appended to a hash-chained ledger. Output bytes only if every test passed (fail-closed).
What statistics CANNOT do, and the receipt says so: tell a quantum source from a good classical generator. "certification" is
always "statistical" here; "quantum" needs physics evidence (source-independent protocol) that this tool does not have.
    quantum/mesh/.venv-pq/bin/python -I qrng_modul.py --raw FILE --out DIR --keydir DIR --source-id ID [--h-design 6.0]
rc 0 = block accepted (DIR/blocks/<seq>.bin written), 2 = refused (reason in the receipt, which is logged too), 1 = error.
"""
import argparse, base64, hashlib, json, math, os, sys, time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, mldsa

APT_W, ALPHA_LOG2, CHUNK, CHUNK_BITS = 512, 20, 4096, 512


def b64(b):
    return base64.b64encode(b).decode()


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def rct_cutoff(h):
    return 1 + math.ceil(ALPHA_LOG2 / h)


def apt_cutoff(h, w=APT_W):
    """Smallest c with P[Binomial(w, 2^-h) >= c] <= 2^-20."""
    p, alpha = 2.0 ** -h, 2.0 ** -ALPHA_LOG2
    pmf = [math.comb(w, k) * p ** k * (1 - p) ** (w - k) for k in range(w + 1)]
    tail = 0.0
    for c in range(w, -1, -1):
        tail += pmf[c]
        if tail > alpha:
            return c + 1
    return 1


def health(x, h):
    rc, ac = rct_cutoff(h), apt_cutoff(h)
    rct_fail, run = 0, 1
    for i in range(1, len(x)):
        run = run + 1 if x[i] == x[i - 1] else 1
        if run >= rc:
            rct_fail += 1; run = 1
    apt_fail = 0
    for s in range(0, len(x) - APT_W + 1, APT_W):
        w = x[s:s + APT_W]
        if w.count(w[0]) >= ac:
            apt_fail += 1
    return {"rct_cutoff": rc, "rct_failures": rct_fail, "apt_window": APT_W, "apt_cutoff": ac, "apt_failures": apt_fail}


def mcv_entropy(x):
    n = len(x)
    p = max(x.count(v) for v in set(x)) / n
    pu = min(1.0, p + 2.576 * math.sqrt(p * (1 - p) / (n - 1)))
    return -math.log2(pu)


def lag1(x):
    n = len(x); m = sum(x) / n
    v = sum((a - m) ** 2 for a in x)
    return 0.0 if v == 0 else sum((x[i] - m) * (x[i + 1] - m) for i in range(n - 1)) / v


def channel_counts(raw, n):
    """Bit stream MSB-first; channel = bit index mod n. -> (ones, cnt) per channel."""
    ones, cnt = [0] * n, [0] * n
    for i, byte in enumerate(raw):
        for k in range(8):
            c = (8 * i + k) % n
            cnt[c] += 1; ones[c] += (byte >> (7 - k)) & 1
    return ones, cnt


def stats_from_counts(ones, cnt):
    """-> per channel (p1, h_99); h_99 = per-bit min-entropy from the 99 % upper bound of max(p1, p0) at that channel's count."""
    p1s, hs = [], []
    for o, c in zip(ones, cnt):
        p1 = o / c; pm = max(p1, 1 - p1)
        p1s.append(p1); hs.append(-math.log2(min(1.0, pm + 2.576 * math.sqrt(pm * (1 - pm) / c))))
    return p1s, hs


def channel_stats(raw, n):
    """-> per channel (p1, h_99, count) of the raw block alone."""
    ones, cnt = channel_counts(raw, n)
    p1s, hs = stats_from_counts(ones, cnt)
    return p1s, hs, cnt


def pearson(a, b):
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else 0.0


def apply_prior(raw, n, prior, mode, r_min):
    """Prior per-channel counts from EARLIER blocks of the same source (built by qrng_prior.py from published raw bytes).
    validated: the prior is used only if Pearson r(prior p1, current p1) >= r_min (the r2 lesson, 2026-11-02: the per-qubit bias
    is a property of the vendor's calibration state, so an old pattern must prove itself on the current block); blind: always used.
    When used, the per-channel 99 % bound is taken at the COMBINED counts (prior + current): a tighter bound, hence more credit -
    which is exactly what must never happen without validation. -> (ones, cnt used for the bound, record for the receipt)."""
    if prior["n"] != n or len(prior["ones"]) != n or len(prior["cnt"]) != n:
        sys.exit("prior: channel count %r differs from --channels %d" % (prior.get("n"), n))
    o_cur, c_cur = channel_counts(raw, n)
    p_prior = [o / c for o, c in zip(prior["ones"], prior["cnt"])]
    p_cur = [o / c for o, c in zip(o_cur, c_cur)]
    r = pearson(p_prior, p_cur)
    z = compat_z(prior["ones"], prior["cnt"], o_cur, c_cur)
    z_mean = sum(z) / n; z_max = max(z)
    # arm B 2026-11-03 (#770): Pearson r ignores a common offset / scale - a prior with the same ORDER of biases but a different
    # magnitude passes the r gate and then wrecks the combined bound. So, besides r: the per-channel two-proportion z must look like
    # the same p (mean |z| <= Z_MEAN; same calibration measured 0.76-0.92, the counterexample 3.29), and a channel is combined only
    # if its own |z| <= Z_CH (same calibration measured max 3.5; a run 5 days and two recalibrations away 9.1 on its worst channel).
    compatible = z_mean <= Z_MEAN
    used = True if mode == "blind" else (r >= r_min and compatible)
    _, h_prior = stats_from_counts(prior["ones"], prior["cnt"])
    combined = (list(range(n)) if mode == "blind" else [c for c in range(n) if z[c] <= Z_CH]) if used else []   # blind = truly blind (test arm)
    rec = {"sha256": prior["_sha256"], "source": prior.get("source"), "bits_per_channel": prior["cnt"][0], "mode": mode, "r_min": r_min,
           "r": round(r, 6), "z_mean": round(z_mean, 4), "z_max": round(z_max, 4), "z_mean_max": Z_MEAN, "z_ch_max": Z_CH, "compatible": compatible,
           "used": used, "channels_combined": len(combined), "predicted_failing": [c for c in range(n) if h_prior[c] < prior.get("_h_bit", 0.0)]}
    if used:
        ones = [o_cur[c] + (prior["ones"][c] if c in combined else 0) for c in range(n)]
        cnt = [c_cur[c] + (prior["cnt"][c] if c in combined else 0) for c in range(n)]
        return ones, cnt, rec
    return o_cur, c_cur, rec


Z_MEAN, Z_CH = 1.5, 4.0


def compat_z(o_p, c_p, o_c, c_c):
    """per-channel two-proportion z between the prior and the current block (pooled p, both counts) -> list of |z|"""
    out = []
    for op, cp, oc, cc in zip(o_p, c_p, o_c, c_c):
        p = (op + oc) / (cp + cc); s = math.sqrt(max(p * (1 - p), 1e-12) * (1 / cp + 1 / cc))
        out.append(abs(op / cp - oc / cc) / s)
    return out


def channel_test(raw, n, h_bit):
    """A channel fails when its h_99 is below h_bit. -> list of [channel, p1, h_upper_bound] for failing channels."""
    p1s, hs, _ = channel_stats(raw, n)
    return [[c, round(p1s[c], 6), round(hs[c], 6)] for c in range(n) if hs[c] < h_bit]


def keys(keydir):
    os.makedirs(keydir, exist_ok=True)
    pe, pm = os.path.join(keydir, "ed25519.pem"), os.path.join(keydir, "mldsa65.pem")
    if not os.path.exists(pe):
        for path, k in ((pe, ed25519.Ed25519PrivateKey.generate()), (pm, mldsa.MLDSA65PrivateKey.generate())):
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.write(fd, k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            os.close(fd)
    ld = lambda p: serialization.load_pem_private_key(open(p, "rb").read(), None)
    return ld(pe), ld(pm)


def pub_b64(k):
    return b64(k.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))


def ledger(out):
    p = os.path.join(out, "ledger.jsonl")
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True); ap.add_argument("--out", required=True); ap.add_argument("--keydir", required=True)
    ap.add_argument("--source-id", required=True); ap.add_argument("--h-design", type=float, default=6.0)
    ap.add_argument("--channels", type=int, default=0, help="per-channel rule: bit j of the MSB-first stream belongs to channel j mod N (IBM: c0..c(n-1) per shot, shots concatenated, no offset)")
    ap.add_argument("--h-bit", type=float, default=0.9)
    ap.add_argument("--channel-policy", choices=("refuse", "exclude"), default="refuse",
                    help="refuse: a failing channel refuses the block; exclude: name it, count its bits as 0 entropy, accept")
    ap.add_argument("--audit", action="store_true", help="audit block: raw kept for recomputation, output diagnostic only")
    ap.add_argument("--prior", help="per-channel prior counts JSON from earlier blocks of the same source (qrng_prior.py); needs --channels")
    ap.add_argument("--prior-mode", choices=("validated", "blind"), default="validated",
                    help="validated (default): use the prior only if r(prior, current) >= --prior-r-min; blind: always use it (test arm, not for production)")
    ap.add_argument("--prior-r-min", type=float, default=0.622, help="r2 sealed floor (2026-11-02): expected 0.87 within one calibration minus 0.25")
    a = ap.parse_args(argv)
    if a.prior and not a.channels:
        sys.exit("--prior needs --channels")
    if not 0.5 <= a.h_design <= 8:
        sys.exit("h-design must be in [0.5, 8] bits per 8-bit sample")
    raw = open(a.raw, "rb").read()
    if len(raw) < 2 * CHUNK:
        sys.exit("raw block too short (< %d bytes)" % (2 * CHUNK))
    x = list(raw)
    os.makedirs(os.path.join(a.out, "blocks"), exist_ok=True)
    rows = ledger(a.out)
    seen_raw = {r["receipt"]["raw_sha256"] for r in rows}
    seen_chunks = {c for r in rows for c in r["receipt"]["chunk_sha256"]}
    chunks = [hashlib.sha256(raw[i:i + CHUNK]).hexdigest() for i in range(0, len(raw) - CHUNK + 1, CHUNK)]
    hl = health(x, a.h_design)
    h_mcv = mcv_entropy(x)
    r1 = lag1(x)
    reasons = []
    if hl["rct_failures"]:
        reasons.append("repetition count test failed %d times" % hl["rct_failures"])
    if hl["apt_failures"]:
        reasons.append("adaptive proportion test failed %d times" % hl["apt_failures"])
    if h_mcv < a.h_design:
        reasons.append("min-entropy estimate %.4f < design %.4f bits/sample" % (h_mcv, a.h_design))
    if abs(r1) > 5 / math.sqrt(len(x)):
        reasons.append("lag-1 correlation %.5f beyond %.5f" % (r1, 5 / math.sqrt(len(x))))
    chan, h_eff = None, h_mcv
    if a.channels:
        if not (1 <= a.channels <= 4096 and 0.1 <= a.h_bit <= 1):
            sys.exit("channels must be 1..4096 and h-bit 0.1..1")
        prior_rec = None
        p1s, hs, cnts = channel_stats(raw, a.channels); cur_cnt = cnts
        failing = [[c, round(p1s[c], 6), round(hs[c], 6)] for c in range(a.channels) if hs[c] < a.h_bit]     # the broken-channel decision is the CURRENT block's alone
        excluded = [f[0] for f in failing] if a.channel_policy == "exclude" else []
        if a.prior:
            # arm B 2026-11-03 (#782): at a channel rule sitting on the entropy threshold a compatible prior could tip every channel into
            # exclusion (h_acc -> 0). So the prior never decides exclusion; it only refines the credit h of the channels that stay in.
            pb = open(a.prior, "rb").read(); prior = json.loads(pb); prior["_sha256"] = hashlib.sha256(pb).hexdigest(); prior["_h_bit"] = a.h_bit
            ones, cnts_c, prior_rec = apply_prior(raw, a.channels, prior, a.prior_mode, a.prior_r_min)
            _, hs = stats_from_counts(ones, cnts_c)
        h_acc = sum(cur_cnt[c] * (0.0 if c in excluded else hs[c]) for c in range(a.channels)) / len(raw)   # bits per 8-bit sample
        h_eff = min(h_mcv, h_acc)
        chan = {"n": a.channels, "h_bit": a.h_bit, "policy": a.channel_policy, "failing": failing, "excluded": excluded,
                "h_acc": round(h_acc, 6), "h_eff": round(h_eff, 6)}
        if prior_rec:
            chan["prior"] = prior_rec
        if failing and a.channel_policy == "refuse":
            reasons.append("channel test: %d of %d channels below %.2f bit/bit" % (len(failing), a.channels, a.h_bit))
        if h_eff < 0.5:
            reasons.append("channel accounting: effective entropy %.4f < 0.5 bits/sample" % h_eff)
    if hashlib.sha256(raw).hexdigest() in seen_raw:
        reasons.append("replay: raw block already in the ledger")
    rep = sum(1 for c in chunks if c in seen_chunks)
    if rep:
        reasons.append("replay: %d aligned 4096-byte chunks already in the ledger" % rep)
    out_bytes = b""
    if not reasons:
        per = max(1, math.ceil(CHUNK_BITS / h_eff))          # samples per output chunk carrying >= 512 estimated bits (h_eff = min(MCV, accounting))
        out_bytes = b"".join(hashlib.sha256(raw[i:i + per]).digest() for i in range(0, len(raw) - per + 1, per))
    seq = len(rows)
    prev = hashlib.sha256(canon(rows[-1])).hexdigest() if rows else "0" * 64
    rec = {"v": 1, "seq": seq, "prev_sha256": prev, "source_id": a.source_id, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "raw_sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw), "chunk_sha256": chunks,
           "h_design": a.h_design, "health": hl, "channels": chan, "audit": bool(a.audit), "entropy_model": "iid-MCV-99", "h_mcv": round(h_mcv, 6), "lag1": round(r1, 6),
           "accepted": not reasons, "reasons": reasons, "out_sha256": hashlib.sha256(out_bytes).hexdigest() if out_bytes else None,
           "out_bytes": len(out_bytes), "certification": "statistical",
           "quantumness": "NOT CERTIFIED: statistics cannot distinguish a quantum source from a good classical generator"}
    ek, mk = keys(a.keydir)
    m = canon(rec)
    row = {"receipt": rec, "pub_ed25519_b64": pub_b64(ek), "pub_mldsa65_b64": pub_b64(mk),
           "sig_ed25519_b64": b64(ek.sign(m)), "sig_mldsa65_b64": b64(mk.sign(m))}
    if out_bytes:
        with open(os.path.join(a.out, "blocks", "%06d.bin" % seq), "wb") as f:
            f.write(out_bytes)
    if a.audit:                                                          # raw kept ONLY for audit blocks (secrecy, arm B #607)
        os.makedirs(os.path.join(a.out, "raw"), exist_ok=True)
        rp = os.path.join(a.out, "raw", rec["raw_sha256"] + ".bin")
        if not os.path.exists(rp):
            with open(rp, "wb") as f:
                f.write(raw)
    with open(os.path.join(a.out, "ledger.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({"seq": seq, "accepted": rec["accepted"], "audit": rec["audit"], "h_mcv": rec["h_mcv"], "reasons": reasons, "out_bytes": len(out_bytes)}))
    return 0 if rec["accepted"] else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
