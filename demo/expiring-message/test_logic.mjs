// Test of logic.mjs in Node:  node test_logic.mjs NOBLE_NODE_MODULES_DIR MODEL_REF.json
// (1) the JS port of the sealed model equals the Python original to 1e-12 at 12 waits; (2) the bus: honest receipts accepted,
// four tamperings refused; (3) the lifetimes. Prints PASS/FAIL lines; exit 0 only if all pass.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
const [NM, REF] = process.argv.slice(2);
const imp = (p) => import(pathToFileURL(join(NM, p)).href);
const lib = { ...(await imp("@noble/curves/ed25519.js")), ...(await imp("@noble/post-quantum/ml-dsa.js")), ...(await imp("@noble/hashes/sha2.js")) };
const L = await import(new URL("./logic.mjs", import.meta.url).href);
const data = JSON.parse(readFileSync(new URL("./data.json", import.meta.url), "utf8"));
let all = true; const check = (n, ok, d = "") => { all &&= ok; console.log((ok ? "PASS " : "FAIL ") + n, d); };

let maxd = 0;
for (const r of JSON.parse(readFileSync(REF, "utf8"))) { const f = L.modelF(data.model, r.t); maxd = Math.max(maxd, Math.abs(f.raw - r.raw), Math.abs(f.echo - r.echo)); }
check("M1 JS model = the sealed Python model (12 waits)", maxd < 1e-12, "max |diff| " + maxd.toExponential(2));
const meas = data.measured.map((p) => [p.F_raw - L.modelF(data.model, p.t_us).raw, p.F_echo - L.modelF(data.model, p.t_us).echo]);
const within = meas.filter(([a]) => Math.abs(a) <= 0.03).length, withinE = meas.filter(([, b]) => Math.abs(b) <= 0.03).length;
check("M2 the model meets the measured points as in the sealed test (raw 9/11, echo 11/11 within 0.03)", within === 9 && withinE === 11, `raw ${within}/11 echo ${withinE}/11`);

const bus = L.newBus(lib, data);
const a = bus.create("echo"), ra = bus.use(a, "echo", 120);
check("B1 echo pair used at 120 us: accepted as still good", L.verify(lib, data, bus.pub, bus.ledger, ra).verdict.startsWith("ACCEPTED: the pair was still good"));
const b = bus.create("raw"), rb = bus.use(b, "raw", 120);
check("B2 raw pair used at 120 us: accepted as honestly expired", L.verify(lib, data, bus.pub, bus.ledger, rb).verdict.startsWith("ACCEPTED: honestly marked"));
const again = bus.use(a, "echo", 130);
check("T1 the same pair used again: refused", /already used/.test(L.verify(lib, data, bus.pub, bus.ledger, again).why || ""));
const edited = { ...ra, text: ra.text.replace('"wait_us":120', '"wait_us":60') };
check("T2 receipt wait edited after signing: refused", /signature/.test(L.verify(lib, data, bus.pub, bus.ledger, edited).why || ""));
const lie = (() => { const c = bus.create("raw"); bus.use(c, "raw", 150); const o = JSON.parse(bus.ledger.at(-1).text.slice(bus.ledger.at(-1).text.indexOf("\n") + 1));
  return { c, o }; })();
const forged = L.makeIssuer(lib).sign({ pair_id: lie.c, mode: "raw", wait_us: 150, claim: "usable", ledger_row_sha256: bus.ledger.at(-1).sha256 });
check("T3 a receipt signed by someone else: refused", /signature/.test(L.verify(lib, data, bus.pub, bus.ledger, forged).why || ""));
const cut = bus.ledger.slice(0, 1).concat(bus.ledger.slice(2));
check("T4 a ledger row removed: refused (chain)", /chain/.test(L.verify(lib, data, bus.pub, cut, ra).why || ""));
const lr = L.lifetime(data, "raw"), le = L.lifetime(data, "echo");
check("L1 lifetimes from the sealed model: raw < echo", lr !== null && le !== null && lr < le, `raw ${lr} us, echo ${le} us`);
console.log(all ? "ALL PASS" : "SOME FAILED"); process.exit(all ? 0 : 1);
