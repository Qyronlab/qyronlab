"""z5_meret_ido.py - roadmap 1e Z5: measured size/time table for the seat's three signature schemes on the lab's own machine.
Two independent runs (separate processes) must agree within 5 % on every timing; sizes must be byte-identical.
Output: JSON on stdout. Run: nice -n 15 .venv-pq/bin/python z5_meret_ido.py [N]"""
import json, os, statistics, sys, time, platform
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mesh import attest
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
MSG = b"seat/z5 measurement message " * 4
def med_ms(fn, n):
    t = []
    for _ in range(n):
        a = time.perf_counter(); fn(); t.append((time.perf_counter() - a) * 1000.0)
    return round(statistics.median(t), 4)
out = {"n": N, "host": platform.node(), "python": platform.python_version(), "pid": os.getpid(), "schemes": {}}
for scheme in ("ed25519", "ml-dsa-65", "sphincs+-sha2-128s"):
    if scheme not in attest.SCHEMES:
        out["schemes"][scheme] = {"error": "not in registry"}; continue
    priv, pub, _ = attest.generate(scheme)
    sig = priv.sign(MSG)
    pubk = attest.SCHEMES[scheme]["load_public"](pub)
    pubk.verify(sig, MSG)
    out["schemes"][scheme] = {
        "public_key_bytes": len(pub), "signature_bytes": len(sig),
        "keygen_ms_median": med_ms(lambda: attest.generate(scheme), max(5, N // 10)),
        "sign_ms_median": med_ms(lambda: priv.sign(MSG), N),
        "verify_ms_median": med_ms(lambda: pubk.verify(sig, MSG), N),
    }
# the seat's seal: one attestation per scheme, canonical JSON size with 2 and with 3 schemes
seal = {}
for combo in (("ed25519", "ml-dsa-65"), ("ed25519", "ml-dsa-65", "sphincs+-sha2-128s")):
    atts = []
    for s in combo:
        priv, pub, _ = attest.generate(s)
        atts.append(attest.make(priv, s, subject="z5-subject", claim="authored"))
    seal["+".join(combo)] = {"attestations": len(atts), "canonical_bytes": len(attest.canonical(atts))}
out["seal_size"] = seal
print(json.dumps(out, indent=1, sort_keys=True))
