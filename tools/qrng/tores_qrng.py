#!/usr/bin/env python3
"""Break test of qrng_modul.py + qrng_fuggetlen.py. No network, no bus; writes only under the scratch dir argv[1] (refused under /srv).
Sources are STAND-INS, not quantum: os.urandom for "good", Python's random for "classical generator", a rounded Gaussian for an
8-bit homodyne ADC. The point is what the module refuses and what the buyer's checker catches - and, stated as a test, what
statistics cannot catch (a good classical generator passes; the receipt must still say "statistical", never "quantum").
    quantum/mesh/.venv-pq/bin/python -I tores_qrng.py SCRATCH       -> PASS/FAIL lines, rc 0 = all as expected
QM_MODUL=<path> runs the same test against a planted module mutant (the test must then FAIL somewhere).
"""
import base64, json, math, os, random, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(sys.argv[1])
_NO = (os.sep + "srv" + os.sep, os.sep + "var" + os.sep + "www")          # no literal server paths in this file (public repo filter)
if R.startswith(_NO):
    sys.exit("refusing: scratch dir must be outside the server trees")
MOD = os.environ.get("QM_MODUL", os.path.join(HERE, "qrng_modul.py"))
CHK = os.environ.get("QM_CHK", os.path.join(HERE, "qrng_fuggetlen.py"))          # QM_CHK=<path>: planted checker mutant
N = 65536
res = []


def check(n, ok, d=""):
    res.append(ok); print(("PASS " if ok else "FAIL ") + n, d)


def raw(name, b):
    p = os.path.join(R, "src", name + ".bin"); open(p, "wb").write(b); return p


def modul(src, out, h=6.0, key="k", extra=(), audit=True):
    p = subprocess.run([sys.executable, "-I", MOD, "--raw", src, "--out", out, "--keydir", os.path.join(R, key), "--source-id", "test",
                        "--h-design", str(h), *(("--audit",) if audit else ()), *extra], capture_output=True, text=True)
    try:
        return p.returncode, json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return p.returncode, {"stderr": p.stderr[-300:]}


def checker(out, *extra):
    p = subprocess.run([sys.executable, "-I", CHK, out, *extra], capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout) if p.stdout.strip() else {"problems": [p.stderr[-200:]]}


def rows(out):
    return [json.loads(l) for l in open(os.path.join(out, "ledger.jsonl"))]


def write_rows(out, rs):
    open(os.path.join(out, "ledger.jsonl"), "w").write("".join(json.dumps(r, sort_keys=True) + "\n" for r in rs))


if os.path.exists(R):
    shutil.rmtree(R)
os.makedirs(os.path.join(R, "src"))
out = os.path.join(R, "store")
g1, g2 = os.urandom(N), os.urandom(N)
rng = random.Random(20261028)

# 1. good blocks accepted, chained, buyer's checker PASS
rc, o = modul(raw("good1", g1), out); check("good1 accepted", rc == 0 and o["accepted"] and o["out_bytes"] > 0, o)
rc, o = modul(raw("good2", g2), out); check("good2 accepted", rc == 0 and o["accepted"], o.get("h_mcv"))
crc, v = checker(out); check("checker PASS on good ledger", crc == 0, v["problems"][:2])

# 2. bad sources refused by the module (fail-closed: no output block), and the checker agrees
cases = {
    "stuck_at_zero": (bytes(N), "repetition"),
    "biased_16_symbols": (bytes(rng.randrange(16) * 16 for _ in range(N)), "min-entropy"),
    "correlated_walk": (bytes(int(128 + 60 * __import__("math").sin(i / 7.0) + rng.randrange(8)) % 256 for i in range(N)), "lag-1"),
    "exact_replay": (g1, "replay"),
    "chunk_replay": (os.urandom(8192) + g2[4096:8192] + os.urandom(N - 12288), "replay"),
    "gaussian_adc_sigma20_h6": (bytes(min(255, max(0, round(rng.gauss(128, 20)))) for _ in range(N)), "min-entropy"),
    # the two negative controls arm B asked for (#607) and a third: light source lost (electronic noise only, sigma 2 LSB),
    # a predictable classical signal with 1-LSB steps, and the same counter bit-reversed (weak but still visible lag-1)
    "light_source_lost": (bytes(min(255, max(0, round(rng.gauss(128, 2.0)))) for _ in range(N)), "min-entropy"),
    "counter_1lsb": (bytes(i & 255 for i in range(N)), "lag-1"),
    "counter_bit_reversed": (bytes(int(format(i & 255, "08b")[::-1], 2) for i in range(N)), "lag-1"),
}
for name, (b, why) in cases.items():
    rc, o = modul(raw(name, b), out)
    check(name + " refused (" + why + ")", rc == 2 and not o["accepted"] and o["out_bytes"] == 0 and any(why in r for r in o["reasons"]), o.get("reasons", o)[:1])
crc, v = checker(out); check("checker PASS after refusals (refusals are honest rows)", crc == 0, v["problems"][:2])

# 3. design entropy matters: the same Gaussian ADC model is accepted at an honest lower design entropy
rc, o = modul(raw("gaussian_adc_sigma20_h5", bytes(min(255, max(0, round(rng.gauss(128, 20)))) for _ in range(N))), out, h=5.0)
check("gaussian ADC accepted at h_design 5.0", rc == 0 and o["accepted"], o.get("h_mcv"))

# 4. the honest limit: a good CLASSICAL generator passes every statistical test; the receipt must not claim quantum
rc, o = modul(raw("classical_prng", random.Random(7).randbytes(N)), out)
last = rows(out)[-1]["receipt"]
check("classical PRNG passes statistics (expected - the limit)", rc == 0 and o["accepted"])
check("...but its receipt says statistical / NOT CERTIFIED", last["certification"] == "statistical" and last["quantumness"].startswith("NOT CERTIFIED"))
crc, v = checker(out); check("checker PASS on the full honest ledger", crc == 0, v["problems"][:2])

# 4b. one bad channel among 16 (the 10-28 IBM r0 lesson): block-level tests pass, the per-channel test refuses
def one_bad_channel(n_ch=16, bad=5, p1=0.7, seed=99):
    r = random.Random(seed); bits = [(1 if r.random() < p1 else 0) if i % n_ch == bad else r.getrandbits(1) for i in range(8 * N)]
    return bytes(int("".join(map(str, bits[j:j + 8])), 2) for j in range(0, len(bits), 8))
bc = one_bad_channel()
o2 = os.path.join(R, "store_channel")
rc, o = modul(raw("bad_channel_block_only", bc), o2)
check("one bad channel: block-level tests alone ACCEPT (the blind spot)", rc == 0 and o["accepted"], o.get("h_mcv"))
rc, o = modul(raw("bad_channel_with_test", one_bad_channel(seed=100)), o2, extra=("--channels", "16", "--h-bit", "0.9"))
fl = rows(o2)[-1]["receipt"]["channels"]["failing"]
check("one bad channel: per-channel test REFUSES and names it", rc == 2 and any("channel test" in r for r in o["reasons"]) and [f[0] for f in fl] == [5], fl)
rc, o = modul(raw("good_with_channel_test", os.urandom(N)), o2, extra=("--channels", "16", "--h-bit", "0.9"))
check("good source with channel test accepted", rc == 0 and o["accepted"], o.get("reasons"))
crc, v = checker(o2); check("checker PASS on channel ledger", crc == 0, v["problems"][:2])
# 4c. policy EXCLUDE (the r1 rule, 10-31): a broken channel (p1 0.75 -> h_99 below 0.5) is NAMED and charged, the block is
#     accepted with a SHORTER output; the buyer recomputes exclusion and accounting; an insider cannot hide either
o4 = os.path.join(R, "store_exclude")
rc, o = modul(raw("bad_channel_exclude", one_bad_channel(p1=0.75, seed=101)), o4, extra=("--channels", "16", "--h-bit", "0.5", "--channel-policy", "exclude"))
rx = rows(o4)[-1]["receipt"]; chx = rx["channels"]
check("exclude policy: block ACCEPTED, broken channel excluded and named", rc == 0 and o["accepted"] and chx["excluded"] == [5] and [f[0] for f in chx["failing"]] == [5], chx.get("excluded"))
per_x = max(1, math.ceil(512 / chx["h_eff"]))
check("exclude policy: h_eff = min(h_mcv, h_acc) < h_mcv and the output is sized by h_eff (32 bytes per ceil(512/h_eff) samples)",
      chx["h_eff"] == min(rx["h_mcv"], chx["h_acc"]) and chx["h_acc"] < rx["h_mcv"] and o["out_bytes"] == 32 * (N // per_x)
      and o["out_bytes"] <= 32 * (N // max(1, math.ceil(512 / rx["h_mcv"]))), (rx["h_mcv"], chx["h_acc"], o["out_bytes"]))
rc, o = modul(raw("bad_channel_refuse_same", one_bad_channel(p1=0.75, seed=102)), o4, extra=("--channels", "16", "--h-bit", "0.5"))
check("same broken channel under policy refuse: block REFUSED (default unchanged)", rc == 2 and not o["accepted"], o.get("reasons"))
crc, v = checker(o4); check("checker PASS on exclude ledger (accounting recomputed)", crc == 0, v["problems"][:2])
def hide_exclusion(t):
    rs = rows(t)
    for r in rs:
        if r["receipt"]["channels"] and r["receipt"]["channels"]["excluded"]:
            r["receipt"]["channels"]["excluded"], r["receipt"]["channels"]["failing"] = [], []
    write_rows(t, rs)
def inflate_accounting(t):
    rs = rows(t)
    for r in rs:
        if r["receipt"]["channels"] and r["receipt"]["channels"]["excluded"]:
            r["receipt"]["channels"]["h_acc"] = r["receipt"]["channels"]["h_eff"] = r["receipt"]["h_mcv"]
    write_rows(t, rs)
t = os.path.join(R, "t_hide_exclusion"); shutil.copytree(o4, t); hide_exclusion(t)
crc, v = checker(t)
check("insider hides the excluded channel -> checker FAIL", crc == 1 and any("channel" in p for p in v["problems"]), v["problems"][:1])
t = os.path.join(R, "t_inflate_accounting"); shutil.copytree(o4, t); inflate_accounting(t)
crc, v = checker(t)
check("insider inflates the accounting to MCV -> checker FAIL", crc == 1 and any("accounting" in p for p in v["problems"]), v["problems"][:1])
# 4d. arm B #665 (B18c) negative controls: every channel broken -> no positive-entropy output under EXCLUDE either (fail-closed)
def all_broken(n_ch=16, p1=0.8, seed=103):
    g = random.Random(seed); bits = [1 if g.random() < p1 else 0 for _ in range(N * 8)]
    return bytes(int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, N * 8, 8))
rc, o = modul(raw("all_channels_broken", all_broken()), o4, extra=("--channels", "16", "--h-bit", "0.5", "--channel-policy", "exclude"))
rx = rows(o4)[-1]["receipt"]
check("every channel broken under EXCLUDE -> block REFUSED, 0 output bytes", rc == 2 and not o["accepted"] and o["out_bytes"] == 0 and len(rx["channels"]["excluded"]) == 16, o.get("reasons"))
crc, v = checker(o4); check("checker PASS on exclude ledger incl. the all-broken refusal row", crc == 0, v["problems"][:2])
def hide_channel(t):
    from cryptography.hazmat.primitives import serialization
    ld = lambda p: serialization.load_pem_private_key(open(os.path.join(R, "k", p), "rb").read(), None)
    ek, mk = ld("ed25519.pem"), ld("mldsa65.pem")
    rs = rows(t); prev = "0" * 64
    for r in rs:
        r["receipt"]["prev_sha256"] = prev
        if r["receipt"]["seq"] == 1:
            r["receipt"]["channels"]["failing"], r["receipt"]["accepted"], r["receipt"]["reasons"] = [], True, []
        m = json.dumps(r["receipt"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        r["sig_ed25519_b64"] = base64.b64encode(ek.sign(m)).decode(); r["sig_mldsa65_b64"] = base64.b64encode(mk.sign(m)).decode()
        prev = __import__("hashlib").sha256(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    write_rows(t, rs)
t = os.path.join(R, "t_hide_channel"); shutil.copytree(o2, t); hide_channel(t)
crc, v = checker(t)
check("insider hides the bad channel -> checker FAIL", crc == 1 and any("channel test differs" in p for p in v["problems"]), v["problems"][:1])

# 4c. production vs audit blocks (arm B #607: raw + public extractor = output)
o3 = os.path.join(R, "store_prod")
rc, o = modul(raw("prod1", os.urandom(N)), o3, audit=False)
rp = os.path.join(o3, "raw")
check("production block accepted, raw NOT retained", rc == 0 and o["accepted"] and not o["audit"] and not os.path.exists(rp), o)
rc, o = modul(raw("audit1", os.urandom(N)), o3, audit=True)
check("audit block accepted, raw retained", rc == 0 and o["audit"] and len(os.listdir(rp)) == 1)
crc, v = checker(o3); check("checker PASS on mixed ledger (audit_rows 1)", crc == 0 and v["audit_rows"] == 1, v["problems"][:2])
t = os.path.join(R, "t_prod_raw"); shutil.copytree(o3, t)
r0 = rows(t)[0]["receipt"]; open(os.path.join(t, "raw", r0["raw_sha256"] + ".bin"), "wb").write(open(os.path.join(R, "src", "prod1.bin"), "rb").read())
crc, v = checker(t); check("production raw retained -> checker FAIL", crc == 1 and any("retained" in p for p in v["problems"]), v["problems"][:1])
t = os.path.join(R, "t_prod_out"); shutil.copytree(o3, t); open(os.path.join(t, "blocks", "000000.bin"), "wb").write(os.urandom(64))
crc, v = checker(t); check("production output swapped -> checker FAIL", crc == 1 and any("output block" in p for p in v["problems"]), v["problems"][:1])
rc, o = modul(raw("prod_replay", open(os.path.join(R, "src", "prod1.bin"), "rb").read()), o3, audit=False)
check("replay of a production block refused without its raw (receipt hashes)", rc == 2 and any("replay" in r for r in o["reasons"]))

# 5. tampering after the fact: the buyer's checker must FAIL
def tamper(label, fn, expect):
    t = os.path.join(R, "t_" + label); shutil.copytree(out, t); fn(t)
    crc, v = checker(t)
    check(label + " -> checker FAIL", crc == 1 and any(expect in p for p in v["problems"]), v["problems"][:1])

def edit_entropy(t):
    rs = rows(t); rs[0]["receipt"]["h_mcv"] = 7.99; write_rows(t, rs)
def drop_row(t):
    rs = rows(t); del rs[1]; write_rows(t, rs)
def swap_block(t):
    open(os.path.join(t, "blocks", "000000.bin"), "wb").write(os.urandom(64))
def flip_raw(t):
    r0 = rows(t)[0]["receipt"]["raw_sha256"]; p = os.path.join(t, "raw", r0 + ".bin"); b = bytearray(open(p, "rb").read()); b[100] ^= 1; open(p, "wb").write(bytes(b))
def resign_quantum(t):            # an insider WITH the key re-signs a "quantum" claim: signatures valid, claim still refused
    sys.path.insert(0, HERE)
    from cryptography.hazmat.primitives import serialization
    ld = lambda p: serialization.load_pem_private_key(open(os.path.join(R, "k", p), "rb").read(), None)
    ek, mk = ld("ed25519.pem"), ld("mldsa65.pem")
    rs = rows(t); prev = "0" * 64
    for r in rs:
        r["receipt"]["prev_sha256"] = prev
        if r["receipt"]["seq"] == 0:
            r["receipt"]["certification"] = "quantum"
        m = json.dumps(r["receipt"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        r["sig_ed25519_b64"] = base64.b64encode(ek.sign(m)).decode(); r["sig_mldsa65_b64"] = base64.b64encode(mk.sign(m)).decode()
        prev = __import__("hashlib").sha256(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    write_rows(t, rs)
def resign_accept_bad(t):         # insider re-signs a refused stuck-at block as accepted
    from cryptography.hazmat.primitives import serialization
    ld = lambda p: serialization.load_pem_private_key(open(os.path.join(R, "k", p), "rb").read(), None)
    ek, mk = ld("ed25519.pem"), ld("mldsa65.pem")
    rs = rows(t); prev = "0" * 64
    for r in rs:
        r["receipt"]["prev_sha256"] = prev
        if r["receipt"]["seq"] == 2:
            r["receipt"]["accepted"], r["receipt"]["reasons"] = True, []
        m = json.dumps(r["receipt"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        r["sig_ed25519_b64"] = base64.b64encode(ek.sign(m)).decode(); r["sig_mldsa65_b64"] = base64.b64encode(mk.sign(m)).decode()
        prev = __import__("hashlib").sha256(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    write_rows(t, rs)

tamper("edited entropy", edit_entropy, "signature")
tamper("deleted row", drop_row, "chain broken")
tamper("swapped output block", swap_block, "output block")
tamper("flipped raw bit", flip_raw, "raw")
tamper("insider re-signs quantum claim", resign_quantum, "certification")
tamper("insider re-signs a stuck block as accepted", resign_accept_bad, "accepted=True")

# 5a. production (audit=false) rows keep no raw, so the checker can test only the receipt hashes; arm B (11-02, probe on the
#     inline checker) showed two accepted production rows on the SAME raw passed. An insider WITH the key appends such a row to the
#     production store o3 (no raw retained anywhere, so the only catch is the replay).
def replay_production(t):
    rs = rows(t); prev_row = rs[-1]; src = next(r for r in rs if r["receipt"]["accepted"])
    from cryptography.hazmat.primitives import serialization
    ld = lambda n: serialization.load_pem_private_key(open(os.path.join(R, "k", n), "rb").read(), None)
    ek, mk = ld("ed25519.pem"), ld("mldsa65.pem")
    r = json.loads(json.dumps(src)); rec = r["receipt"]
    rec["seq"] = len(rs); rec["prev_sha256"] = __import__("hashlib").sha256(json.dumps(prev_row, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    m = json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    r["sig_ed25519_b64"] = base64.b64encode(ek.sign(m)).decode(); r["sig_mldsa65_b64"] = base64.b64encode(mk.sign(m)).decode()
    rs.append(r); write_rows(t, rs)
    shutil.copy(os.path.join(t, "blocks", "%06d.bin" % src["receipt"]["seq"]), os.path.join(t, "blocks", "%06d.bin" % rec["seq"]))
t = os.path.join(R, "t_replay_prod"); shutil.copytree(o3, t); replay_production(t)
crc, v = checker(t); check("insider appends an accepted production row replaying an earlier raw -> checker FAIL (replay)", crc == 1 and any("replay" in p for p in v["problems"]) and len(v["problems"]) == 1, v["problems"])
crc, v = checker(t, "--without-mldsa"); check("...and the replay is caught without ML-DSA too", crc == 1 and any("replay" in p for p in v["problems"]), v["problems"][:1])

# 5b. graceful mode (arm B 11-01: Python 3.12 + cryptography 41 has no ML-DSA): the checker must still run, and must
#     NEVER say PASS without the second signature checked; the honest limit is stated as a test (a forged ML-DSA signature
#     is invisible in that mode, so the verdict stays PARTIAL)
crc, v = checker(out, "--without-mldsa")
check("without ML-DSA -> PASS-PARTIAL, rc 2, never PASS", crc == 2 and v["verdict"] == "PASS-PARTIAL" and v["mldsa65"].startswith("forced-off"), v.get("verdict"))
def forge_mldsa(t):                 # LAST row: an earlier row's forged signature is caught by the chain (the next row's prev_sha256)
    rs = rows(t); rs[-1]["sig_mldsa65_b64"] = base64.b64encode(os.urandom(3309)).decode(); write_rows(t, rs)
t = os.path.join(R, "t_forged_mldsa"); shutil.copytree(out, t); forge_mldsa(t)
crc, v = checker(t); check("forged ML-DSA signature -> FAIL in full mode", crc == 1 and any("signature" in p for p in v["problems"]), v["problems"][:1])
crc, v = checker(t, "--without-mldsa")
check("forged ML-DSA signature invisible without ML-DSA -> still only PASS-PARTIAL (the stated limit)", crc == 2 and v["verdict"] == "PASS-PARTIAL", v.get("verdict"))
# 5c. truncation: the ledger alone cannot show a cut tail; with the out-of-band row count it must
rs_all = rows(out); t = os.path.join(R, "t_truncated"); shutil.copytree(out, t); write_rows(t, rs_all[:-1])
crc, v = checker(t); check("truncated ledger passes alone (the limit, stated)", crc == 0, v["problems"][:1])
crc, v = checker(t, "--expect-rows", str(len(rs_all)))
check("truncated ledger + --expect-rows -> FAIL", crc == 1 and any("row count" in p for p in v["problems"]), v["problems"][:1])
crc, v = checker(out, "--expect-rows", str(len(rs_all))); check("full ledger + --expect-rows -> PASS", crc == 0)
check("key fingerprints reported", bool(v["key_fingerprints"]["ed25519_sha256"]) and bool(v["key_fingerprints"]["mldsa65_sha256"]))

# 6. a foreign key, pinned by the buyer: FAIL
t = os.path.join(R, "t_foreign"); shutil.rmtree(t, ignore_errors=True)
modul(raw("good_foreign", os.urandom(N)), t, key="other")
pin = rows(out)[0]
crc, v = checker(t, "--pin-ed25519", pin["pub_ed25519_b64"], "--pin-mldsa65", pin["pub_mldsa65_b64"])
check("foreign key vs pinned key -> checker FAIL", crc == 1 and any("pinned" in p for p in v["problems"]), v["problems"][:1])

# 7. prior (r3, 2026-11-02): per-channel counts from earlier blocks; validated = used only if the current block correlates (r >= r_min),
#    blind = always. The buyer must recompute r/used/accounting from the same prior file; a missing or altered prior, or a receipt that
#    claims "used" against its own r, must FAIL. Stand-in source: 16 channels with FIXED per-channel biases (two blocks of the same
#    pattern) and a third block with a different pattern.
def biased(n_ch, biases, seed, nbytes=N):
    rg = random.Random(seed); bits = []
    for j in range(nbytes * 8):
        bits.append(1 if rg.random() < biases[j % n_ch] else 0)
    return bytes(int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8))
PRI = os.path.join(HERE, "qrng_prior.py")
def prior_file(name, *raws, n=16):
    out = os.path.join(R, name + ".json")
    p = subprocess.run([sys.executable, "-I", PRI, "--channels", str(n), "--out", out, "--source", name, *raws], capture_output=True, text=True)
    return out, json.loads(p.stdout)["sha256"]
pat1 = [0.5 + 0.03 * math.sin(c) for c in range(16)]; pat1[5] = 0.74          # channel 5 broken in pattern 1
pat2 = [0.5 - 0.03 * math.cos(c) for c in range(16)]                           # a different calibration state, nothing broken
s1a, s1b, s2 = raw("pat1_a", biased(16, pat1, 201)), raw("pat1_b", biased(16, pat1, 202)), raw("pat2", biased(16, pat2, 203))
pf, psha = prior_file("prior_pat1", s1a)
CH = ("--channels", "16", "--h-bit", "0.5", "--channel-policy", "exclude")
t0 = os.path.join(R, "t_prior_none"); rc0, o0 = modul(s1b, t0, extra=CH); r0 = rows(t0)[0]["receipt"]["channels"]
tv = os.path.join(R, "t_prior_valid"); rcv, ov = modul(s1b, tv, extra=(*CH, "--prior", pf, "--prior-mode", "validated", "--prior-r-min", "0.622"))
rv = rows(tv)[0]["receipt"]["channels"]
check("validated prior, same pattern -> used, r >= 0.622, broken channel predicted and excluded",
      rv["prior"]["used"] and rv["prior"]["r"] >= 0.622 and rv["prior"]["predicted_failing"] == [5] and rv["excluded"] == [5], rv["prior"])
check("validated prior tightens the bound: h_acc >= no-prior h_acc, output >= no-prior output", rv["h_acc"] >= r0["h_acc"] and ov["out_bytes"] >= o0["out_bytes"], (r0["h_acc"], rv["h_acc"]))
crc, v = checker(tv, "--prior", pf); check("buyer with the same prior file -> PASS", crc == 0, v["problems"][:1])
crc, v = checker(tv); check("buyer WITHOUT the prior file -> FAIL (cites a prior it cannot check)", crc == 1 and any("prior" in p for p in v["problems"]), v["problems"][:1])
alt = os.path.join(R, "prior_altered.json"); d = json.load(open(pf)); d["ones"][5] -= 500; open(alt, "w").write(json.dumps(d, sort_keys=True, separators=(",", ":")) + "\n")
crc, v = checker(tv, "--prior", alt); check("altered prior file (sha differs) -> FAIL", crc == 1 and any("prior" in p for p in v["problems"]), v["problems"][:1])
tm = os.path.join(R, "t_prior_mismatch_valid"); modul(s2, tm, extra=(*CH, "--prior", pf, "--prior-mode", "validated", "--prior-r-min", "0.622"))
rm_ = rows(tm)[0]["receipt"]["channels"]; tn = os.path.join(R, "t_mismatch_none"); modul(s2, tn, extra=CH); rn = rows(tn)[0]["receipt"]["channels"]
check("validated prior, OTHER pattern -> r < 0.622, NOT used, accounting identical to no-prior", (not rm_["prior"]["used"]) and rm_["prior"]["r"] < 0.622
      and rm_["h_acc"] == rn["h_acc"] and rm_["excluded"] == rn["excluded"], (rm_["prior"]["r"], rm_["excluded"]))
crc, v = checker(tm, "--prior", pf); check("buyer recomputes the unused prior -> PASS", crc == 0, v["problems"][:1])
tb = os.path.join(R, "t_prior_mismatch_blind"); modul(s2, tb, extra=(*CH, "--prior", pf, "--prior-mode", "blind"))
rb = rows(tb)[0]["receipt"]["channels"]
check("blind prior, OTHER pattern -> used anyway and the buyer's result CHANGES (the harm the validated mode prevents)",
      rb["prior"]["used"] and (rb["excluded"] != rn["excluded"] or rb["h_acc"] != rn["h_acc"]), (rn["excluded"], rb["excluded"]))
crc, v = checker(tb, "--prior", pf); check("blind prior row is still recomputable -> PASS (the receipt says blind)", crc == 0, v["problems"][:1])
def resign(t, edit):                # insider WITH the key: edit the receipt, re-sign, re-chain (signatures valid; only the logic can catch it)
    from cryptography.hazmat.primitives import serialization
    ld = lambda p: serialization.load_pem_private_key(open(os.path.join(R, "k", p), "rb").read(), None)
    ek, mk = ld("ed25519.pem"), ld("mldsa65.pem")
    rs = rows(t); prev = "0" * 64
    for r in rs:
        r["receipt"]["prev_sha256"] = prev; edit(r["receipt"])
        m = json.dumps(r["receipt"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        r["sig_ed25519_b64"] = base64.b64encode(ek.sign(m)).decode(); r["sig_mldsa65_b64"] = base64.b64encode(mk.sign(m)).decode()
        prev = __import__("hashlib").sha256(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    write_rows(t, rs)
def claim_used(rc):                 # the receipt claims the prior was used (tighter credit) although r < r_min in validated mode
    rc["channels"]["prior"]["used"] = True
t = os.path.join(R, "t_prior_claim_used"); shutil.copytree(tm, t); resign(t, claim_used)
crc, v = checker(t, "--prior", pf); check("insider re-signs used=True against its own r < r_min -> FAIL on the prior logic", crc == 1 and any("prior" in p for p in v["problems"]), v["problems"][:1])
def edit_r(rc):                     # an inflated r so the validated mode looks satisfied, and the credit taken accordingly
    rc["channels"]["prior"]["r"] = 0.9; rc["channels"]["prior"]["used"] = True; rc["channels"]["h_acc"] = round(rc["channels"]["h_acc"] + 0.2, 6)
t = os.path.join(R, "t_prior_edit_r"); shutil.copytree(tm, t); resign(t, edit_r)
crc, v = checker(t, "--prior", pf); check("insider re-signs an inflated r and credit -> FAIL on the prior logic", crc == 1 and any("prior" in p for p in v["problems"]), v["problems"][:1])

# 7b. arm B counterexample (2026-11-03, #770): a prior with the same ORDER of biases but a larger magnitude: r = 0.9999, yet combining
#     it would exclude 78 channels at h_bit 0.9 and halve the accounting. The r gate alone let it through; the z gate must not.
def from_counts(name, ones, per_ch, n_ch, seed):
    rg = random.Random(seed); bits = []
    for c in range(n_ch):
        b = [1] * ones[c] + [0] * (per_ch - ones[c]); rg.shuffle(b); bits.append(b)
    stream = [bits[j % n_ch][j // n_ch] for j in range(n_ch * per_ch)]
    return raw(name, bytes(int("".join(map(str, stream[i:i + 8])), 2) for i in range(0, len(stream), 8)))
cur_ones = [2027, 2039, 2056, 2068] * 39; pri_ones = [3686, 3932, 4259, 4505] * 39
cx = from_counts("tengri_cur", cur_ones, 4096, 156, 301); px = from_counts("tengri_prior", pri_ones, 8192, 156, 302)
pfx, _ = prior_file("prior_tengri", px, n=156)
CH9 = ("--channels", "156", "--h-bit", "0.9", "--channel-policy", "exclude")
t0 = os.path.join(R, "t_tengri_none"); rc0, o0 = modul(cx, t0, extra=CH9); r0_ = rows(t0)[0]["receipt"]["channels"]
tv = os.path.join(R, "t_tengri_valid"); modul(cx, tv, extra=(*CH9, "--prior", pfx, "--prior-mode", "validated", "--prior-r-min", "0.622"))
rv = rows(tv)[0]["receipt"]["channels"]
check("arm B counterexample: r > 0.99 but z_mean > 1.5 -> NOT used, accounting identical to none", rv["prior"]["r"] > 0.99 and not rv["prior"]["compatible"]
      and not rv["prior"]["used"] and rv["h_acc"] == r0_["h_acc"] and rv["excluded"] == r0_["excluded"], (rv["prior"]["r"], rv["prior"]["z_mean"], len(r0_["excluded"])))
crc, v = checker(tv, "--prior", pfx); check("buyer recomputes the z gate -> PASS", crc == 0, v["problems"][:1])
tb = os.path.join(R, "t_tengri_blind"); modul(cx, tb, extra=(*CH9, "--prior", pfx, "--prior-mode", "blind")); rb = rows(tb)[0]["receipt"]["channels"]
check("the same prior blind -> used, and the damage is visible as a lower credit (exclusion stays the current block's: unchanged)",
      rb["prior"]["used"] and rb["excluded"] == r0_["excluded"] and rb["h_acc"] < r0_["h_acc"], (len(rb["excluded"]), r0_["h_acc"], rb["h_acc"]))
def claim_compat(rc):               # insider re-signs compatible=True / used=True on the counterexample
    rc["channels"]["prior"]["compatible"] = True; rc["channels"]["prior"]["used"] = True
t = os.path.join(R, "t_tengri_claim"); shutil.copytree(tv, t); resign(t, claim_compat)
crc, v = checker(t, "--prior", pfx); check("insider re-signs compatible/used on the counterexample -> FAIL", crc == 1 and any("prior" in p for p in v["problems"]), v["problems"][:1])
check("same-pattern prior (section 7) still used with the z gate", rows(os.path.join(R, "t_prior_valid"))[0]["receipt"]["channels"]["prior"]["used"]
      and rows(os.path.join(R, "t_prior_valid"))[0]["receipt"]["channels"]["prior"]["z_mean"] <= 1.5)

# 7c. arm B second counterexample (#782): every channel sits just above the 0.9 threshold (h_none 0.90105); a compatible prior (r = 1,
#     |z| 1.47) combined would push the bound just below -> all 156 excluded, h_acc 0. Exclusion must stay the current block's decision.
cx2 = from_counts("edge_cur", [1985, 2111] * 78, 4096, 156, 303); px2 = from_counts("edge_prior", [3855, 4337] * 78, 8192, 156, 304)
pfx2, _ = prior_file("prior_edge", px2, n=156)
t0 = os.path.join(R, "t_edge_none"); modul(cx2, t0, extra=CH9); e0 = rows(t0)[0]["receipt"]["channels"]
tv = os.path.join(R, "t_edge_valid"); modul(cx2, tv, extra=(*CH9, "--prior", pfx2, "--prior-mode", "validated", "--prior-r-min", "0.622")); ev = rows(tv)[0]["receipt"]["channels"]
check("edge counterexample: prior passes the gate, yet NO channel is excluded by it; h_acc moves only slightly", ev["prior"]["used"] and ev["excluded"] == e0["excluded"] == []
      and abs(ev["h_acc"] - e0["h_acc"]) < 0.05, (e0["h_acc"], ev["h_acc"], ev["prior"]["z_mean"]))
crc, v = checker(tv, "--prior", pfx2); check("buyer recomputes the edge case -> PASS", crc == 0, v["problems"][:1])
def excl_by_prior(rc):              # insider re-signs an exclusion list the prior would have produced (credit-shifting)
    rc["channels"]["excluded"] = list(range(156)); rc["channels"]["failing"] = [[c, 0.5, 0.89] for c in range(156)]; rc["channels"]["h_acc"] = 0.0; rc["channels"]["h_eff"] = 0.0
t = os.path.join(R, "t_edge_claim"); shutil.copytree(tv, t); resign(t, excl_by_prior)
crc, v = checker(t, "--prior", pfx2); check("insider re-signs prior-driven exclusions -> FAIL", crc == 1, v["problems"][:1])

ok = all(res)
print("%d/%d %s" % (sum(res), len(res), "PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
