# Decision Record (ADR)

ADR ID: ADR-2026-08-03-01
Title: Pre-production Go decision for the Trend Intelligence Engine
Status: [x] Accepted (agent-recommended; owner owns the final sign-off)
Date: 2026-08-03
Deciders: Marcel (owner) — recommended by Claude (Cowork), audit 2026-08-03
Related audit: scorecard.md (this folder)

## Context
Pre-production audit against the Automation System Auditor kit (15 weighted domains,
8 red-flag blockers). Blast radius is internal content operations: no money, no customer
PII, no auto-publishing. Score 78.75/100, zero active blockers. Four domains scored 2
(problem baseline numbers, value quantification, deployment environments, operational
readiness owner-confirmation).

## Decision
Go for the intended low-blast-radius scope (scheduled pipeline delivering briefs to
Airtable/Slack for human approval), under AUDITOR.md Section 7 rule 4 (>=75, zero
Blockers), with the six findings tracked as follow-ups. Expanding scope to "real trends
from live APIs" requires closing AF-03 first and is a separate gate.

## Options Considered
| Option | Pros | Cons |
|---|---|---|
| Go with tracked follow-ups (chosen) | matches 75-89 band; blast radius internal; zero blockers | baseline numbers + owner sign-off still open |
| Conditional Go | more conservative | not required — score >=75 and no active blockers |
| No-Go | forces all [confirm] items first | disproportionate for internal, reversible, non-destructive system |

## Consequences
- Positive: engine can run on schedule producing briefs; all invariants gated in CI.
- Trade-offs accepted: live source adapters emit sample data until AF-03; alerting
  covers terminal failures only until AF-05.
- Follow-up: findings AF-01..06; owner confirmation; baseline numbers.

## Reversibility
- [x] Easily reversible — stateless runs; idempotent, non-destructive delivery; rollback
  is a code revert (docs/deployment-and-rollback.md).

## Human checkpoints the agent cannot close (AGENTS.md §7)
- Owner sign-off (the agent is not the second person).
- Confirming Marcel as named owner (AF-01).
- Any first production run with real credentials.
