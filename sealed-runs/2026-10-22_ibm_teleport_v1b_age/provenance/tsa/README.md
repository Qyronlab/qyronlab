# RFC 3161 timestamp token on the sealed prediction (plan_t1.json, sha256 7010b356…)

Issued by a public time-stamping authority (freetsa.org) on **2026-10-23 04:11:48 UTC**, i.e. AFTER the run. It therefore
proves only that the prediction bytes existed by that time; it is NOT a pre-run anchor for this test. It is kept as the
recipe that every later sealed test uses BEFORE job submission (token requested on the sealed file, stored next to it).

Verify (the TSA's certificates are fetched from the authority, not stored here):
    openssl ts -verify -in plan_t1.json.tsr -queryfile plan_t1.json.tsq -CAfile cacert.pem -untrusted tsa.crt
    openssl ts -reply -in plan_t1.json.tsr -text      # shows the sha256 of the data and the TSA time
