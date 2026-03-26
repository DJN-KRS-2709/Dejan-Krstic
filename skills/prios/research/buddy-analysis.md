# Buddy Repo Analysis — Patterns for /prios

> Researched: 2026-02-26
> Source: `/Users/vinits/Repos/buddy` (Dan Rayne, Pi ecosystem)

## What Buddy Is

Local-first AI work assistant. Full-stack monorepo (Node/TS, React, iOS) with persistent services. Runs a gateway server on `:3003`, maintains SQLite-backed session state, does background work (heartbeats every 30min, scheduled tasks, morning briefings at 7am). Architecturally closer to a **personal OS** than a CLI skill.

**Integrations:** Google Calendar, Gmail, Drive, Linear
**Platforms:** Web UI (:5173), iOS app (SwiftUI), Raycast extension, Chrome extension

### Architecture

```
buddy/
├── packages/
│   ├── gateway/         # Core engine (~5500 LOC)
│   │   ├── chat/       # Agentic loop (PiChatEngine)
│   │   ├── sessions/   # SQLite session store + compaction
│   │   ├── scheduled/  # Cron-like task scheduling
│   │   ├── heartbeat/  # 30-min health checks
│   │   ├── today/      # Daily briefing aggregation
│   │   ├── approvals/  # Action queueing + generator
│   │   └── tools/      # Tool registry + MCP bridge
│   ├── api/            # Auth proxy + persona management
│   ├── web/            # React dashboard
│   ├── relay/          # Cloud Run WebSocket relay
│   ├── memory-mcp/     # SQLite semantic search (QMD fallback)
│   └── permission-mcp/ # Tool execution permission prompts
└── skills/             # Bundled skills (GitHub, Google Workspace)
```

---

## Patterns Applied to /prios

| # | Pattern | Buddy's approach | /prios implementation |
|---|---------|-----------------|----------------------|
| 1 | **Carry-forward** | Session compaction tracks incomplete items across sessions | Phase 7a: read previous day's unchecked `- [ ]` items, carry with ⏳ prefix |
| 2 | **Meeting doc context** | Fetches Drive docs linked in calendar events during morning briefing | Phase 1: regex for Google Doc links in event descriptions, fetch via Drive MCP |
| 3 | **Declined meeting filtering** | `responseStatus !== "declined"` filter, skip prep for declined | Phase 1: accepted→full prep, tentative→❓ lighter, declined→~~strikethrough~~ no prep |
| 4 | **Proactive actions** | Approval generator creates queued actions (unresponded invites, conflicts) | Phase 7: "Suggested Actions" — invites, conflicts, stale tickets, overdue replies |
| 5 | **Weekend handling** | Morning briefing is weekday-only, respects schedule | Phase 0: Fri tomorrow→Mon, Sat/Sun→target Monday |

**Unplanned work detection** (Phase 7a) is original to /prios — not from Buddy.

---

## Patterns NOT Applied (and Why)

| Pattern | What Buddy does | Why we skipped it |
|---------|----------------|-------------------|
| **Session summaries** | Auto-generates structured markdown after each chat, injects into next session | /prios is stateless by design. The daily file IS the cross-session context. Carry-forward handles continuity. |
| **Approval queueing** | All write actions queued for review before execution | /prios only writes to a local file — no destructive actions. Revisit if we add "auto-decline conflicts". |
| **Heartbeat checks** | 30-min background polling for blockers, urgent emails | Requires persistent service. /prios is a one-shot CLI skill. Architectural mismatch. |
| **Configurable prompt templates** | HEARTBEAT.md, MORNING_BRIEFING.md are user-editable files | Maybe later — could let users customize output format via template. Low priority. |
| **Semantic search** | QMD (local embeddings) for searching across memory/sessions | Overkill for a daily checklist. Grep works fine. |

---

## Key Buddy Implementation Details

### Cross-Session Continuity

Session compaction runs when tokens exceed 92% of context window. Walks backwards, keeps 20k recent tokens, summarizes the rest:

```markdown
## Goal
## Constraints & Preferences
## Progress (Done/In Progress/Blocked)
## Key Decisions
## Next Steps
## Discussions & Outcomes
## Observations
## Critical Context
<read-files>
<modified-files>
```

Summaries stored as human-readable markdown in `~/.buddy/memory/sessions/YYYY-MM-DD-{id}.md`. Auto-injected into next session.

### Morning Briefing (Three Layers)

1. **Basic priorities** — synchronous, no LLM (pattern-matched from calendar)
2. **Daily briefing file** — LLM-generated narrative + schedule + attention items → `~/.buddy/memory/daily/YYYY-MM-DD.md`
3. **Structured JSON** — for UI rendering: `PreparedMeeting[]`, `ImportantDoc[]`, `ImportantEmail[]`

### Declined Meeting Filtering

```typescript
// Only prep non-declined, non-OOO meetings
const importantMeeting = schedule.find(
  e => e.responseStatus !== "declined" && e.eventType !== "outOfOffice"
)

// Don't suggest actions on already-declined meetings
if (event.responseStatus === "declined" || other.responseStatus === "declined") {
  continue
}
```

### Approval System

Queue → Review → Execute pattern. Types: `calendar.accept`, `calendar.decline`, `email.send`, `linear.update`. Deterministic generator (no LLM) creates approvals for unresponded invites and conflicts. Deduplicates against pending approvals. UI supports batch approve/decline.

---

## Open Questions for Future /prios Iterations

1. **Structured output format** — Buddy uses YAML frontmatter + JSON for machine-parseable briefings. Our daily.md is pure markdown. If carry-forward parsing gets flaky, adding frontmatter per day section would help.
2. **Auto-run at session start** — Buddy's morning briefing runs at 7am automatically. Could /prios auto-run on first Claude Code session of the day?
3. **Approval queue for actions** — If /prios grows to suggest "decline this meeting" or "send this Slack reply", we'd need Buddy's approval pattern to avoid unsafe auto-execution.

---

## Tech Choices Worth Noting

- **Pi submodule** as the agent framework (tool execution, file ops, bash)
- **QMD** for local embeddings (embeddinggemma-300M, offline, no API cost)
- **SQLite** everywhere (sessions, memory index, compaction) + markdown for long-term storage
- **Hono + EventEmitter** for SSE streaming (web + iOS sync)
