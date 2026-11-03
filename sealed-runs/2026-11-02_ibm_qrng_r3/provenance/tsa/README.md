# RFC 3161 timestamp token on the sealed plan plan_r3.json (sha256 72e659f9dc1afcdb280c2070eb887e15454c73bfe8124bd8bae08b910234380f)

Requested from freetsa.org BEFORE the IBM jobs were created. Verify:

    openssl ts -verify -in plan_r3.json.tsr -queryfile plan_r3.json.tsq -CAfile freetsa_cacert.pem -untrusted freetsa_tsa.crt
    openssl ts -reply -in plan_r3.json.tsr -text
