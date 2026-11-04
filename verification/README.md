# Seat verification records

**What you get.** A permanent, citable record stating that the second signature of a seal — its *qubit seat* — was checked: which
bytes, with which keys, what each check returned, by whom and when, and what the record does **not** prove. The record is itself a
seal: its `record_id` is the SHA-256 of its content, it carries its own signatures, it gets its own public time-stamp, and it is
published here so that anyone can re-run every check offline without talking to us.

**What a qubit seat is, in plain words.** The seal's bytes are committed into a sealed plan; a public time-stamping authority stamps the
plan; only then does a named quantum processor run; the provider's own job record, the raw output and the calibration snapshot are
bound to that commitment and countersigned by the verifier set. That is a device-witnessed attestation with a provenance guarantee —
*this run happened after this commitment existed* — not a key-based unforgeability guarantee. The record says exactly that.

**Label.** *dual-signature ready / seat verified.* Never "quantum-safe": statistics cannot distinguish a quantum source from a good
classical one, and the record lists that among the things it does not prove.

**How to re-check a record (offline).**
1. `record_id` must equal the SHA-256 of the record's canonical content (sort_keys, separators `,` `:`, UTF-8) without `record_id` and `alairasok`.
2. Each classical signature on the seal verifies under the pinned public keys (ed25519, ML-DSA-65, SLH-DSA).
3. The seat evidence: the commitment equals the hash of the seal's signed bytes; the sealed plan file hashes as stated and contains the
   commitment verbatim; the RFC 3161 token verifies over that plan and its time precedes the provider's job creation time; the raw output
   and the provider's records hash as stated; the published checker returns the stated verdict; the countersignature verifies.
4. The verdict is one of *supported / refuted / unknown / unverifiable*, recomputed from those checks alone.

**Sample.** `SAMPLE_RECORD.json` is a synthetic record from the tool's self-test (stand-in device, stubbed time-stamp, test keys) — the
shape, not a certification. Issued records live under `sealed-runs/verification-records/` with their public bytes next to them.

**Two tiers.** *Tier 1 — seat verification record*: the seal's classical signatures (ed25519, ML-DSA-65, SLH-DSA) under pinned keys and the
qubit seat checked; verdict `seat verified`. *Tier 2 — QSN, Quantum-safe Number*: tier 1 plus both post-quantum legs proven separately (FIPS 204
lattice, FIPS 205 hash) plus a blind recheck of the record by an independent second arm (another model family or a person); only then is the
number issued and the record's level reads `quantum-safe`. The name never precedes the measurement: a record that did not reach tier 2 has no QSN.
A tier-1 record can be upgraded later; the old record stays valid and the new one cites it.

**Ordering.** Through the Replay Seal on our site, three items: *Make my seal + seat* — you bring only the content's hash; Qyronlab issues the
seal, signs it with its published issuer key set (the record says so: it is a notary-style issuance, not your own key), runs the seat and issues
the tier-1 record; you may add your own signature to the list later. *Verify my seal* — you bring a signed seal; we verify and issue the record.
*QSN* — the tier-2 number with the second-arm recheck. Details follow when the order path is live.
