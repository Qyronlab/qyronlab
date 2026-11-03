# RFC 3161 timestamp token on the sealed plan plan_r1.json (sha256 ffef322b403580b41b2d209ff3bf6b59e74fb439d9fdc0d99d9c97812a7cf5a9)

Requested from freetsa.org BEFORE the IBM job was created (the job's own created time is in receipts/ after the run). Verify:

    openssl ts -verify -in plan_r1.json.tsr -queryfile plan_r1.json.tsq -CAfile freetsa_cacert.pem -untrusted freetsa_tsa.crt
    openssl ts -reply -in plan_r1.json.tsr -text
