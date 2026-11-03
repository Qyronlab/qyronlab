# RFC 3161 timestamp token on the sealed plan plan_r4.json (sha256 d430f33f781132ecd6cf7bfab358599a0098c48868cd25bd691d0f3615187468)

Requested from freetsa.org BEFORE the IBM jobs were created. Verify:

    openssl ts -verify -in plan_r4.json.tsr -queryfile plan_r4.json.tsq -CAfile freetsa_cacert.pem -untrusted freetsa_tsa.crt
    openssl ts -reply -in plan_r4.json.tsr -text
