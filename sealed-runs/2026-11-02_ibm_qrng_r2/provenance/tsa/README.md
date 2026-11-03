# RFC 3161 timestamp token on the sealed plan plan_r2.json (sha256 f631d095d5477037ed06df5f6193ecd2fc0166c057f4477a5ddcfa0293edef94)

Requested from freetsa.org BEFORE the IBM jobs were created (the jobs' own created times are in receipts/ after the run). Verify:

    openssl ts -verify -in plan_r2.json.tsr -queryfile plan_r2.json.tsq -CAfile freetsa_cacert.pem -untrusted freetsa_tsa.crt
    openssl ts -reply -in plan_r2.json.tsr -text
