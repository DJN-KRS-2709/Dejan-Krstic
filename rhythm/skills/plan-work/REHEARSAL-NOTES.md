# Work Breakdown — Rehearsal Notes

> Companion to `SKILL.md`. Lessons learned from rehearsal cycles and performance optimizations.
> Steps, templates, and MCP calls stay in SKILL.md; detailed lessons and examples live here.

## Lessons learned from rehearsal cycle 1 (DOD-3465, Mar 2026)

**Scope lives in many places, not just the HLD:**
Phase 1.5 scope for the MLC Standalone Calculator was documented in meeting notes ("MLC Standalone Phase 2 Sync"), not in the PRD or HLD. The PRD Build It section was a template placeholder. Skills that derive stories from scope must search broadly — HLD, PRD, meeting notes, working docs, epic descriptions.

**Mislinked stories are silent data quality issues:**
OTTR-4352 and OTTR-4353 (royalty floor, rev share) were linked to OTTR-4296 (Addons) but were actually Phase 1.5 scope (OTTR-4300). Jira doesn't flag this — the only way to catch it is by comparing story scope against epic scope. Added mislinked story detection in Step 2.

**Architectural decisions can obsolete stories without cancellation:**
OTTR-4309 (UAL Test Plan) was rendered obsolete when OTTR-4331 absorbed the UAL into the Pocket Calculator. No one cancelled the story — it sat in Backlog undetected. Added obsolete story detection in Step 3.

**Cross-squad stories need different handling:**
Proposing engineer assignments for Royaltea-owned stories under OTTR-4296 was incorrect — Otter tracks them on the board but doesn't staff them. Skills must detect cross-squad ownership and skip assignment.

**Initiative scope verification prevents contamination:**
OTTR-4342 appeared related by keyword search but was under DOD-5566 (separate initiative), not DOD-3465. Verifying each epic's parent DoD linkage via Groove prevents including unrelated epics in the breakdown.

## Lessons learned from rehearsal cycle 2 (DOD-5566 / OTTR-4342, Mar 2026)

**Non-team assignees are not always cross-squad engineers:**
OTTR-4348 was assigned to Cara Veneziano (Content Accounting). Cycle 1's "cross-squad ownership" check would have classified her as a cross-squad engineer and skipped the story. In reality, she was a UAT stakeholder — the story was Otter-owned work with an external validation dependency. Added a 3-type classification (cross-squad engineer, external stakeholder, unknown) in Step 2.

**Single-engineer initiatives break the parallel staffing option:**
OTTR-4342 has only one engineer (Will Soto) across all 12 stories. Presenting a "parallel workstreams" option was meaningless — you can't parallelize with one person. Added staffing shape detection in Step 5 to skip irrelevant options.

**Internal tooling needs different ship-it stories than user-facing products:**
The standard ship-it story template (Go/No-Go, Release Notes, Launch Checklist) doesn't apply to internal tooling like a calculation engine used by Content Accounting. Internal tooling needs monitoring/alerting, operational runbooks, and data parity validation instead. Added user-facing vs internal tooling paths in Step 6.

**HLD scope may span multiple delivery phases:**
The MLC Transaction Tagging HLD covered both Phase 1 (core tagging) and future scope (reporting, analytics). Flagging all uncovered HLD scope as "needs a story" would generate stories for future-phase work. Added phase classification in Step 3 — distinguish "not covered (current phase)" from "not covered (future phase)."

## Performance optimizations applied

| Optimization | Steps affected | Impact |
|-------------|---------------|--------|
| Parallel: HLD + PRD + supplementary docs + Jira + Groove + roadmap | Step 1-2 | 6 sequential reads → 1 parallel batch |
| Batch: Jira story query for all epics | Step 2 | N queries → 1 query with `parent in (...)` |
| Pre-fetch: Drive search for supplementary docs | Step 1 → Step 3 | Eliminate wait in Step 3 |
