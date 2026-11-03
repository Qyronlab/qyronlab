// Expiring message — the logic shared by the browser demo (index.html) and its test (test_logic.mjs).
// No crypto library is imported here: the caller passes { ed25519, ml_dsa65, sha256 } (@noble), so the same file runs in
// a browser and in Node. Nothing in this file is a hand-typed number: the physics comes from data.json, which is built
// from the sealed prediction and the measured report of the 2026-10-21 IBM test (their sha256 values are in data.json).

// ---- the sealed decay model (a line-by-line port of the model that was fixed BEFORE the measurement) ----
function popEcho(T1a, T1b, t) {                       // ZZ population factor with one echo: damp t/2, X-flip, damp t/2
  const damp = (P, ga, gb) => {
    const Q = { "00": 0, "01": 0, "10": 0, "11": 0 };
    for (const [s, p] of Object.entries(P)) {
      const [a, b] = s;
      const ta = a === "1" ? [["0", ga], ["1", 1 - ga]] : [["0", 1], ["1", 0]];
      const tb = b === "1" ? [["0", gb], ["1", 1 - gb]] : [["0", 1], ["1", 0]];
      for (const [a2, pa] of ta) for (const [b2, pb] of tb) Q[a2 + b2] += p * pa * pb;
    }
    return Q;
  };
  const ga = 1 - Math.exp(-t / 2 / T1a), gb = 1 - Math.exp(-t / 2 / T1b);
  let P = damp({ "00": 0.5, "11": 0.5, "01": 0, "10": 0 }, ga, gb);
  P = { "00": P["11"], "11": P["00"], "01": P["10"], "10": P["01"] };
  P = damp(P, ga, gb);
  return P["00"] + P["11"] - P["01"] - P["10"];
}

export function modelF(model, t) {                    // -> { raw, echo } predicted pair fidelity after waiting t microseconds
  const { E0, A, B } = model;
  const phi = 2 * Math.PI * (A.delta + B.delta) * t * 1e-6;
  const envS = Math.exp(-t / A.T2s - t / B.T2s), envE = Math.exp(-t / A.T2 - t / B.T2);
  const ga = 1 - Math.exp(-t / A.T1), gb = 1 - Math.exp(-t / B.T1);
  const F = (E) => 0.25 * (1 + E.XX - E.YY + E.ZZ);
  const raw = { XX: E0.XX * envS * Math.cos(phi), YY: E0.YY * envS * Math.cos(phi), ZZ: E0.ZZ * 0.5 * (1 + (1 - 2 * ga) * (1 - 2 * gb)) };
  const echo = { XX: E0.XX * envE, YY: E0.YY * envE, ZZ: E0.ZZ * popEcho(A.T1, B.T1, t) };
  return { raw: F(raw), echo: F(echo) };
}

export const sigmaBound = (shots) => Math.sqrt(3 / shots) / 4;      // largest binomial error of F from 3 bases
export function rule(data, mode, t) {                 // usable iff predicted F - 3 sigma >= F_min (and t within the model range)
  if (!(t >= 0 && t <= 800)) return { F: null, usable: false };
  const F = modelF(data.model, t)[mode];
  return { F, usable: F - 3 * sigmaBound(data.shots_per_basis) >= data.F_min };
}

export function lifetime(data, mode) {                // the last microsecond (0.1 us steps) at which the rule still says usable
  let last = null;
  for (let t = 0; t <= 800; t = Math.round((t + 0.1) * 10) / 10) if (rule(data, mode, t).usable) last = t;
  return last;
}

// ---- the bus: signed ledger rows and receipts ----
const DOMAIN = "qyronlab-pair-demo-v0\n";
const enc = (s) => new TextEncoder().encode(s);
const hex = (u) => Array.from(u, (x) => x.toString(16).padStart(2, "0")).join("");
export function canon(o) {                            // sorted keys, no spaces (the receipt's byte image)
  if (Array.isArray(o)) return "[" + o.map(canon).join(",") + "]";
  if (o && typeof o === "object") return "{" + Object.keys(o).sort().map((k) => JSON.stringify(k) + ":" + canon(o[k])).join(",") + "}";
  return JSON.stringify(o);
}

export function makeIssuer(lib) {
  const ek = lib.ed25519.utils.randomSecretKey(), epk = lib.ed25519.getPublicKey(ek);
  const mk = lib.ml_dsa65.keygen();
  const sign = (obj) => {
    const text = DOMAIN + canon(obj), m = enc(text);
    return { text, sha256: hex(lib.sha256(m)), sig_ed25519: hex(lib.ed25519.sign(m, ek)), sig_mldsa65: hex(lib.ml_dsa65.sign(m, mk.secretKey)) };
  };
  return { pub: { ed25519: epk, mldsa65: mk.publicKey }, sign };
}

const unhex = (h) => Uint8Array.from(h.match(/../g).map((x) => parseInt(x, 16)));
function openSigned(lib, pub, s) {
  const m = enc(s.text);
  const ok = (() => { try { return lib.ed25519.verify(unhex(s.sig_ed25519), m, pub.ed25519) && lib.ml_dsa65.verify(unhex(s.sig_mldsa65), m, pub.mldsa65); } catch { return false; } })();
  if (!ok || !s.text.startsWith(DOMAIN)) return null;
  return { obj: JSON.parse(s.text.slice(DOMAIN.length)), sha: hex(lib.sha256(m)) };
}

export function newBus(lib, data) {
  const issuer = makeIssuer(lib), ledger = [];
  let n = 0;
  const append = (event) => {
    const prev = ledger.length ? ledger[ledger.length - 1].sha256 : "0".repeat(64);
    const row = issuer.sign({ prev_sha256: prev, ...event });
    ledger.push(row);
    return row.sha256;
  };
  return {
    pub: issuer.pub, ledger,
    create(mode) { n += 1; const id = "pair-" + String(n).padStart(3, "0"); append({ event: "created", pair_id: id, mode }); return id; },
    use(id, mode, wait_us) {                           // the honest issuer: it states what its rule says
      const h = append({ event: "used", pair_id: id, mode, wait_us });
      return issuer.sign({ pair_id: id, mode, wait_us, claim: rule(data, mode, wait_us).usable ? "usable" : "expired", ledger_row_sha256: h });
    },
  };
}

export function verify(lib, data, pub, ledger, receipt) {   // trusts nothing the issuer computed
  let prev = "0".repeat(64); const bySha = new Map(), firstUse = new Map(), created = new Map();
  for (let i = 0; i < ledger.length; i++) {
    const o = openSigned(lib, pub, ledger[i]);
    if (!o) return { verdict: "REFUSED", why: `ledger row ${i}: bad signature` };
    if (o.obj.prev_sha256 !== prev) return { verdict: "REFUSED", why: `ledger row ${i}: chain broken` };
    prev = o.sha; bySha.set(o.sha, { i, ...o.obj });
    if (o.obj.event === "created" && !created.has(o.obj.pair_id)) created.set(o.obj.pair_id, i);
    if (o.obj.event === "used" && !firstUse.has(o.obj.pair_id)) firstUse.set(o.obj.pair_id, o.sha);
  }
  const o = openSigned(lib, pub, receipt);
  if (!o) return { verdict: "REFUSED", why: "receipt signature does not hold" };
  const r = o.obj, row = bySha.get(r.ledger_row_sha256), calc = rule(data, r.mode, r.wait_us);
  if (!row || row.event !== "used" || row.pair_id !== r.pair_id || row.mode !== r.mode || row.wait_us !== r.wait_us)
    return { verdict: "REFUSED", why: "no matching ledger row" };
  if (firstUse.get(r.pair_id) !== r.ledger_row_sha256) return { verdict: "REFUSED", why: "this pair was already used — a pair can be used only once" };
  if (!(created.get(r.pair_id) < row.i)) return { verdict: "REFUSED", why: "pair used before it was created" };
  if ((r.claim === "usable") !== calc.usable) return { verdict: "REFUSED", why: `the claim '${r.claim}' contradicts the model (F = ${calc.F === null ? "out of range" : calc.F.toFixed(3)})` };
  return { verdict: calc.usable ? "ACCEPTED: the pair was still good when it was used" : "ACCEPTED: honestly marked as expired", F: calc.F, receipt: r };
}
