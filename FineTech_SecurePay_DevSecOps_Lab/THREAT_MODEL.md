# Threat model — SecurePay Lab

This is a toy financial API using fake balances; **never use it for real money**.

## Data flow

Training client → `HTTP /transfer` → Bearer token validation → In-memory ledger → JSON response

Trust boundaries: the HTTP client is untrusted; the server environment supplies a demo token.

| Threat | STRIDE | Defensive control | Test |
|---|---|---|---|
| Unauthorized transfer | Spoofing | Demo bearer check | `test_authentication_required` |
| Repeated transaction | Tampering | Idempotency key per process | `test_idempotent_retry_does_not_double_debit` |
| Reuse same key for different amount | Tampering | Reject HTTP 409 | `test_reusing_key_for_different_amount_rejected` |
| Invalid amount | Tampering | Pydantic amount validation | `test_negative_amount_rejected` |
| Hardcoded secrets | Information disclosure | Token only from environment, `.gitignore`, Gitleaks later | Review + future scanner |
| Unsafe Python patterns | Elevation of privilege | Custom Semgrep rules | Semgrep stage |

## Explicitly missing for real financial systems

Durable transactional database, cross-process idempotency, strong identity, fine-grained
authorization, immutable ledger/audit, fraud controls, monitoring, rate limiting,
TLS termination, secret rotation, threat-model reviews, production-quality tests,
independent deployment controls, and real recovery procedures.
