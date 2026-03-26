# Product Coach Plugin

Evaluates PRDs, decision docs, and overall body of work against Spotify's official PM Career Framework (August 2023). Gap-to-next-level coaching for any PM.

## Usage

Supports both structured flags and natural language. Be as specific or casual as you want.

```
# Structured
/product-coach prd.md                           # Evaluate a single artifact
/product-coach ./my-bet/                        # Evaluate body of work
/product-coach --self-review                    # Full self-review across active bets
/product-coach --setup                          # Configure your level and track
/product-coach prd.md --level 5                 # "What would a Principal PM expect?"
/product-coach prd.md --dev-plan dev_plan.md    # Cross-reference against dev plan

# Natural language
/product-coach review my prd                    # Finds prd.md in current directory
/product-coach Minimize Unpayable Creators      # Finds bet by name, evaluates body of work
/product-coach this bet                         # Evaluates current directory
/product-coach how am I doing                   # Self-review mode
/product-coach prd.md as a senior PM            # Level 4 override
/product-coach prd.md one level up              # Override to current level + 1
```

## Evaluation Modes

| Mode | Trigger | What it does |
|------|---------|--------------|
| Single artifact | `<file.md>` or "review my prd" | Detect type, scan for signals, calibrate to NEXT level bar, gap coaching |
| Body of work | `<directory>` or bet name | Inventory all artifacts, per-artifact + cross-artifact coherence, criteria heatmap |
| Self-review | `--self-review` or "how am I doing" | Discover active bets, gather external signals (Slack, Drive, GHE), WHAT+HOW overlay, differentiation check, 30-day focus |
| Setup | `--setup` or "configure" | Auto-detect from Bandmanager or Q&A for track + level |
| Level override | `--level N` or "as a [title]" | Use level N for this run only |
| Dev plan | `--dev-plan <path>` or "against my dev plan" | Cross-reference evaluation against development plan goals |

## Supported Artifact Types

- PRD
- Problem Frame
- Decision Document / Decision Log
- Feature Requirement
- Hypothesis
- Status Update
- Evidence / Research

## PM Career Framework — Levels

### Expert Track (IC)

| Level | Title | Workday |
|-------|-------|---------|
| 1 | Associate Product Manager | Level K |
| 2 | Product Manager I | Level J |
| 3 | Product Manager II | Level I |
| 4 | Senior Product Manager | Level H |
| 5 | Principal Product Manager | Level G |
| 6 | Senior Principal | Level F |

### Manager Track

| Level | Title | Workday |
|-------|-------|---------|
| 4 | Senior Product Manager (mgr) | Level H |
| 5 | Group Product Manager | Level G |
| 6 | Director | Level F |
| 7 | Senior Director | Level E |

## 9 Evaluation Criteria (IC)

1. Portfolio size & complexity
2. Roadmap horizon
3. Ambiguity
4. Roadmapping
5. Trade-offs
6. Trust & influence
7. Communication
8. Community & mentorship
9. Scale of impact

Manager track adds: Team size, People growth, Organization health.

## Current Limitations & Future Improvements

The coach's assessment quality depends on what data it can access. Today, MCP capabilities limit the depth of external signal gathering:

| Capability | Current State | What would improve it |
|-----------|--------------|----------------------|
| **Slack message content** | Search results only (titles, snippets) | Full message read + thread traversal — would allow assessing stakeholder communication quality, not just volume |
| **Slack thread depth** | Can find threads, limited context | Full thread read — would reveal mentorship quality (how deeply the PM helps) vs just presence |
| **Google Drive doc content** | Metadata + preview only | Full document read — would allow evaluating distributed decision briefs against the same rubric as local artifacts |
| **Google Drive comments** | Can list comments | Comment content + reply chains — would measure stakeholder engagement quality (substantive feedback vs "LGTM") |
| **GHE PR diffs** | PR metadata + file lists | Full diff read — would assess code review quality and tooling contribution depth |
| **Calendar** | Not currently used | Meeting attendee analysis would strengthen Trust & Influence (stakeholder network breadth from actual meeting patterns) |
| **Jira** | Not currently used | Ticket history would strengthen Scale of Impact (delivery velocity, shipped vs planned) |

When these MCP capabilities improve, the coach can move from **metadata-based** external signal gathering to **content-based** evaluation — making criteria #6-#9 assessable with the same rigor as local artifacts.

Track MCP availability and configure servers at: **https://backstage.spotify.net/mcp-explorer**

## Privacy

User configuration is stored in `.product-coach/<username>.yaml`, excluded from git via `.git/info/exclude` (per-clone, survives `.gitignore` changes). No personal data leaves the local machine.
