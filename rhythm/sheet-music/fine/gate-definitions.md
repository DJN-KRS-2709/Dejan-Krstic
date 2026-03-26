# FinE Gate Definitions

> Read by `scan-horizon` to know what transitions to detect.
> Other areas would have their own gate definitions (or none).

## Gates

### Gate 1: Understand It → Think It

**What happened:** Initiative approved for technical discovery.
**Decision maker:** GPM confirms, with validation from GPO/Finance Tower and FinE leads for large/strategic initiatives.

**Detection signals:**
- Groove initiative status changed from IN_PLANNING to READY_FOR_DELIVERY
- Groove annotations show recent status changes
- FTI Discovery epic status changed to "Think It" in the last 14 days

**Detection queries:**
```
# Groove: initiatives in planning/ready states
mcp__groove__list-initiatives(
  indirectOrgs: ["[Groove parent org from team.md]"],
  status: ["IN_PLANNING", "READY_FOR_DELIVERY"],
  periodIds: ["[Groove current cycle period from team.md]"]
)

# Jira: FTI epics with recent status changes
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from team.md] AND labels = [discovery filter label from team.md] AND status changed AFTER -14d",
  fields: "key,summary,status,priority,assignee,duedate"
)
```

**Work created by this transition:**
- Assign engineers to Think It work in Discovery epics
- Create HLD document
- Technical feasibility analysis and effort estimates
- PRD refinement with engineering input

**Follow-up skill:** `gate-1-review` *(demo-tape)*

---

### Gate 2: Think It → Build It

**What happened:** Initiative approved for delivery.
**Decision maker:** GPM + SEM confirm, with validation from GPO/Finance Tower and FinE leads for large/strategic initiatives.

**Detection signals:**
- Groove initiative status is IN_PROGRESS but no Build It epics exist in Jira
- Groove has BACKLOG epics without Jira counterparts (partial setup)
- Recently created Build It epics (last 14 days)

**Detection queries:**
```
# Groove: initiatives in delivery
mcp__groove__list-initiatives(
  indirectOrgs: ["[Groove parent org from team.md]"],
  status: ["IN_PROGRESS"],
  periodIds: ["[Groove current cycle period from team.md]"]
)

# Jira: recently created Build epics
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from team.md] AND type = Epic AND created >= -14d",
  fields: "key,summary,status,priority,assignee,duedate"
)

# Groove: check initiative trees for partial setup
mcp__groove__get-initiative-tree(initiativeId: "[INIT-ID]")
```

**Work created by this transition:**
- Create Build epics in squad Jira project
- Wire epics to Groove DoDs
- Break work into stories
- Create test plan
- Set start/end dates based on MW estimate, capacity, and priority

**Follow-up skill:** `start-build` *(green-light)*

---

## Planning cycles

### Semi-annual planning items

**Time-gated** — only check during sprints immediately following cycle planning deadlines:
- **Spring:** First 1-2 sprints of the new year (after ~late November priorities)
- **Fall:** First 1-2 sprints after May 27 (after Plan/Wrap/Transition)

During planning windows: *"The cycle planning just completed. Any new company bets or P0TH items assigned to the team?"*

**Outside these windows: skip this check.**

### Fall/Spring planning cycle detection

Detect active planning cycles by checking for discovery work with planning-related labels or recent planning documents:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from team.md] AND labels = [discovery filter label from team.md] AND status changed AFTER -14d AND status in ('In Progress', 'To Do')",
  fields: "key,summary,status,duedate,assignee"
)
```

If discovery items with upcoming deadlines are found during a period that overlaps with cycle planning, note: *"Active planning cycle detected — [N] discovery items in progress with deadlines in the next [M] weeks. This may affect Build It capacity."*
