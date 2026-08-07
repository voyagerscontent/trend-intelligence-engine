# Audit Scorecard

System/Concept name: Trend Intelligence Engine (voyagerscontent)
Auditor: Claude (Cowork) — agent-run; owner holds Go/No-Go per AGENTS.md §7
Date: 2026-08-03
Audit type: [x] Pre-production
Capabilities this session: file read, shell/exec, file write, web (read); version control via
GitHub connector NOT reliably reachable (repo 404) — push handled by the owner via bundle.
Evidence folder: audits/2026-08-03-trend-intelligence-engine/evidence/

> Scored against the DEPLOYED code (tests run, dry-run executed, greps run), not just docs.
> Live source adapters currently emit SAMPLE data by design (documented, P1 to wire real APIs).

| # | Domain | Weight | Raw (0-4) | Weighted | Evidence |
|---|---|---|---|---|---|
| 2.1 | Problem Clarity | 8 | 2 | 4.0 | docs/problem-and-goals.md — goals present, baseline numbers are [confirm] placeholders |
| 2.2 | Value & Prioritization | 6 | 2 | 3.0 | docs/requirements.md P0/P1/P2; value/cost horizon not yet quantified |
| 2.3 | Scope & Non-Goals | 6 | 3 | 4.5 | docs/requirements.md — explicit non-goals (real, not "N/A") |
| 2.4 | Architecture & Modularity | 10 | 3 | 7.5 | docs/architecture.md, architecture/*.mmd, AUDIT.md; audit_static pipeline_wires PASS (verified vs code) |
| 2.5 | Contracts & Interfaces | 10 | 3 | 7.5 | models.py + schemas/*.schema.json + docs/data-contracts.md; factor-key drift blocked by audit_static |
| 2.6 | Data Handling | 8 | 3 | 6.0 | docs/data-contracts.md lineage + PII scan none; idempotent upsert; retention [confirm] |
| 2.7 | Modularity & Reuse | 6 | 3 | 4.5 | shared obs.py/models/config_loader; sources behind one SignalSource contract; no copy-paste |
| 2.8 | Security & Secrets | 10 | 3 | 7.5 | evidence/secret-scan.txt clean; settings.py centralises env; .env.example documents all; scopes [confirm] |
| 2.9 | Reliability & Error Handling | 10 | 3 | 7.5 | obs.RetryPolicy bounded backoff+timeout; alert_failure + non-zero exit; docs/error-handling.md; no DLQ yet |
| 2.10 | Testing | 8 | 3 | 6.0 | evidence/pytest.txt 10 passed; static-audit.txt 7 PASS; dry-run.txt briefed=3; live-adapter test P1 |
| 2.11 | Observability | 8 | 3 | 6.0 | structured JSON logs w/ run_id (dry-run.txt); terminal alert; broader alerting [confirm] |
| 2.12 | Deployment & Environments | 6 | 2 | 3.0 | 3 workflows + docs/deployment-and-rollback.md; staging base + rollback drill [confirm] |
| 2.13 | Documentation | 6 | 3 | 4.5 | README, AUDIT.md, full docs/ set + runbook + diagrams; new operator can run it |
| 2.14 | Maintainability | 5 | 3 | 3.75 | docs/naming-and-versioning.md; audit_static gate; no changelog yet |
| 2.15 | Operational Readiness | 7 | 2 | 3.5 | docs/operations-runbook.md names owner + recovery; owner acceptance pending; no incident drill |
| | **Total** | **100** | | **78.75** | |

**Total weighted score: 78.75 / 100**

## Red-Flag Blockers (see AUDITOR.md Section 4) — evidence/blocker-checks.txt

| Blocker | Present? | Notes |
|---|---|---|
| Secrets in plaintext | N | clean scan; no_hardcoded_secrets PASS |
| Unauthenticated public webhook writing/spending/publishing | N | no inbound listener; schedule-triggered pull |
| No idempotency on retryable write | N | Airtable upsert on Title+Brand |
| No error path / silent data loss | N | fatal log + Slack alert + non-zero exit |
| Irreversible destructive action w/o dry-run/rollback | N | no deletes; upsert only; dry-run default |
| Unbounded retry against rate-limited/paid API | N | RetryPolicy max_attempts=3 + backoff + timeout |
| No named owner for data/public-facing system | N* | owner named (Marcel) — *pending his explicit confirmation |
| PII/regulated data w/o basis/retention/minimization | N | keyword/topic/aggregate only; PII scan none |

**Active blockers: 0.**

## Result
- [x] Go (Section 7 rule 4: score >= 75 with zero active Blockers) — for the intended
      low-blast-radius scope (internal briefs; no money, customer PII, or auto-publishing).
      Ship with tracked follow-ups for the four domains scored 2 (see findings).
- [ ] Conditional Go
- [ ] No-Go

Rationale: decision-record.md. Next audit due: 2026-11-03 (90-day cadence) or on first
live-API wiring / auth or schema change, whichever first.

## Findings Opened This Audit
| ID | Domain | Severity | Owner | Due | Status |
|---|---|---|---|---|---|
| AF-2026-08-03-01 | 2.15 Operational Readiness | Critical | Marcel | before go-live | Open |
| AF-2026-08-03-02 | 2.1 Problem Clarity | Major | Marcel | 1 quarter | Open |
| AF-2026-08-03-03 | 2.10/2.9 Live wiring | Critical | Marcel | before "real trends" scope | Open |
| AF-2026-08-03-04 | 2.12 Deployment | Major | Marcel | 1 quarter | Open |
| AF-2026-08-03-05 | 2.11 Observability | Major | Marcel | 1 quarter | Open |
| AF-2026-08-03-06 | 2.9 Reliability (DLQ) | Minor | Marcel | backlog | Open |
