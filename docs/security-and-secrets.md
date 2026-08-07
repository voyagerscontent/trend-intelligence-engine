# Security & Secrets

## Checklist
- [x] No credentials in code, config, or git — secret scan clean
      (`scripts/audit_static.py:no_hardcoded_secrets`; evidence in the audit folder).
- [x] All secret access centralised in `settings.py` (`_get`); no `os.getenv`
      scattered elsewhere. Enforced by `env_vars_documented`.
- [x] Every env var documented in `.env.example` with placeholder values only.
- [x] `.gitignore` excludes `.env` and `*.local`.
- [x] Secrets provided to CI via GitHub Actions `secrets.*` (see the three workflows),
      never inlined.
- [ ] Least-privilege API scopes for each provider key — set when wiring live
      credentials (P1). [confirm]
- [ ] Key rotation cadence agreed with the owner. [confirm]

## Attack surface
No inbound webhook / listener — the engine is **schedule-triggered pull only**, so
there is no unauthenticated public endpoint (red-flag blocker #2 not applicable).
Outbound calls go to Airtable and Slack over HTTPS with bounded retries and timeouts.

## Handling secret-bearing evidence
Never print or commit a real secret. Reference location + variable name and redact the
value (e.g. `AIRTABLE_TOKEN=<redacted, set>`).
