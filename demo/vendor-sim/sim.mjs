// Vendor-number simulator, browser half: a Bell pair at t = 0 on two physical qubits, predicted ONLY from the numbers the
// vendor publishes (gate errors as depolarizing noise, independent readout confusion). A port of the research simulator's
// two-qubit path; test_sim.mjs checks it against the Python original. No library, plain arrays of complex numbers.

const c = (re, im = 0) => ({ re, im });
const add = (a, b) => c(a.re + b.re, a.im + b.im), mul = (a, b) => c(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
const conj = (a) => c(a.re, -a.im), scale = (a, s) => c(a.re * s, a.im * s);
const S2 = Math.SQRT1_2;
const M1 = { I: [[c(1), c(0)], [c(0), c(1)]], X: [[c(0), c(1)], [c(1), c(0)]], Y: [[c(0), c(0, -1)], [c(0, 1), c(0)]], Z: [[c(1), c(0)], [c(0), c(-1)]],
  H: [[c(S2), c(S2)], [c(S2), c(-S2)]], RX90: [[c(S2), c(0, -S2)], [c(0, -S2), c(S2)]] };
const kron = (A, B) => { const R = []; for (let i = 0; i < 4; i++) { R.push([]); for (let j = 0; j < 4; j++) R[i].push(mul(A[i >> 1][j >> 1], B[i & 1][j & 1])); } return R; };
const CZ = [0, 1, 2, 3].map((i) => [0, 1, 2, 3].map((j) => c(i === j ? (i === 3 ? -1 : 1) : 0)));
function apply(U, rho) {                       // U rho U^dag, 4x4
  const T = rho.map((_, i) => rho.map((__, j) => { let s = c(0); for (let k = 0; k < 4; k++) s = add(s, mul(U[i][k], rho[k][j])); return s; }));
  return T.map((_, i) => T.map((__, j) => { let s = c(0); for (let k = 0; k < 4; k++) s = add(s, mul(T[i][k], conj(U[j][k]))); return s; }));
}
const lin = (A, B, a, b) => A.map((r, i) => r.map((x, j) => add(scale(x, a), scale(B[i][j], b))));
const on = (G, q) => (q === 0 ? kron(G, M1.I) : kron(M1.I, G));        // qubit 0 = first of the pair (most significant)
function depol1(rho, lam, q) {
  if (lam <= 0) return rho;
  let out = rho.map((r) => r.map((x) => scale(x, 1 - 3 * lam / 4)));
  for (const P of ["X", "Y", "Z"]) out = lin(out, apply(on(M1[P], q), rho), 1, lam / 4);
  return out;
}
function depol2(rho, lam) {
  if (lam <= 0) return rho;
  let out = rho.map((r) => r.map((x) => scale(x, 1 - 15 * lam / 16)));
  for (const a of ["I", "X", "Y", "Z"]) for (const b of ["I", "X", "Y", "Z"]) if (a !== "I" || b !== "I") out = lin(out, apply(kron(M1[a], M1[b]), rho), 1, lam / 16);
  return out;
}

// qa, qb: [T1, T2, e1q, P(1|0), P(0|1)] ; e2: two-qubit gate error. Returns { E: {X, Y, Z}, F, bound }.
export function bell(qa, qb, e2) {
  const g1 = (rho, G, q) => depol1(apply(on(G, q), rho), 2 * (q === 0 ? qa : qb)[2], q);
  const corr = {};
  for (const basis of ["X", "Y", "Z"]) {
    let rho = [0, 1, 2, 3].map((i) => [0, 1, 2, 3].map((j) => c(i === 0 && j === 0 ? 1 : 0)));
    rho = g1(rho, M1.H, 0); rho = g1(rho, M1.H, 1);
    rho = depol2(apply(CZ, rho), 4 / 3 * e2);
    rho = g1(rho, M1.H, 1);
    if (basis === "X") { rho = g1(rho, M1.H, 0); rho = g1(rho, M1.H, 1); }
    if (basis === "Y") { rho = g1(rho, M1.RX90, 0); rho = g1(rho, M1.RX90, 1); }
    const p = [0, 1, 2, 3].map((i) => Math.max(0, rho[i][i].re));
    let e = 0;                                 // readout confusion, then <Z Z>
    for (let i = 0; i < 4; i++) for (let ra = 0; ra < 2; ra++) for (let rb = 0; rb < 2; rb++) {
      const ta = i >> 1, tb = i & 1;
      const pa = ta === 0 ? (ra ? qa[3] : 1 - qa[3]) : (ra ? 1 - qa[4] : qa[4]);
      const pb = tb === 0 ? (rb ? qb[3] : 1 - qb[3]) : (rb ? 1 - qb[4] : qb[4]);
      e += p[i] * pa * pb * (ra === rb ? 1 : -1);
    }
    corr[basis] = e;
  }
  return { E: corr, F: (1 + corr.X - corr.Y + corr.Z) / 4, bound: (1 - qa[3] - qa[4]) * (1 - qb[3] - qb[4]) };
}
