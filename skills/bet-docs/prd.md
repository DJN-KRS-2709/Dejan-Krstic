---
name: prd
description: "Generate a PRD from bet artifacts and publish to Google Docs"
argument-hint: "[path/to/bet]"
allowed-tools: ["Bash(*)", "Read(*)", "Write(*)", "Glob(*)", "AskUserQuestion"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **python3**: Run `which python3`. If missing, install via `brew install python3`
3. **gcloud auth (documents/drive scopes)**: Run `gcloud auth application-default print-access-token`. If missing or expired, run:
   ```
   gcloud auth application-default login \
     --scopes=https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive
   ```
4. **Python packages**: Run `python3 -c "import google.auth"`. If missing, install:
   ```
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

If any prerequisite is missing, walk the user through setting it up before proceeding.

# PRD from Bet Docs

Generate a comprehensive Product Requirements Document from a bet's existing artifacts and publish it as a Google Doc.

## Step 1: Locate the Bet

If a path was provided in `$ARGUMENTS`, use it as the bet directory.

Otherwise:
1. Check if the current directory contains any of: `hypothesis.md`, `problem_frame.md`, `evidence.md`, `status.md`
2. If not found locally, look for a `domains/` directory and list available bets for the user to choose from
3. If still ambiguous, ask the user to specify the path

## Step 2: Read All Bet Artifacts

Read each of these files from the bet directory if they exist (silently skip missing ones):

- `status.md` — bet name, owner, phase, Jira ticket, Groove ID
- `problem_frame.md` — problem definition, target users, context
- `hypothesis.md` — core hypothesis, success metrics
- `evidence.md` — supporting signals, data, research
- `decision_log.md` — key decisions, rationale, open questions
- `prd.md` — any existing PRD content (supplement, don't replace)

Note which files were found and which were absent.

## Step 3: Synthesize the PRD

Generate a complete PRD using this structure. Each section maps to a source file:

```markdown
# [Bet Name] — Product Requirements Document

**Status:** [phase]  **Owner:** [owner]  **Last Updated:** [today]
**Jira:** [ticket]  **Groove:** [initiative]

---

## 1. Problem Statement
### 1.1 Background
### 1.2 Problem We're Solving
### 1.3 Who Is Affected
### 1.4 Current State & Pain Points

## 2. Hypothesis & Success Metrics
### 2.1 Core Hypothesis
> [exact hypothesis statement]

### 2.2 Success Metrics
| Metric | Baseline | Target | Measurement |

### 2.3 Counter-Metrics (Guardrails)

## 3. Background & Evidence
### 3.1 Quantitative Signals
### 3.2 Qualitative Signals
### 3.3 Competitive Context

## 4. Scope
### 4.1 In Scope
### 4.2 Out of Scope
### 4.3 Assumptions

## 5. Requirements
### 5.1 Functional Requirements
| ID | Requirement | Priority (P0/P1/P2) | Notes |

### 5.2 Non-Functional Requirements
| Category | Requirement |
| Performance | |
| Availability | |
| Security | |
| Accessibility | |

## 6. Key Decisions & Constraints
### 6.1 Decisions Made
| Decision | Rationale | Date |

### 6.2 Open Questions
| Question | Owner | Due |

### 6.3 Technical Constraints

## 7. Timeline & Milestones
| Milestone | Target Date | Status |

## 8. Risks
| Risk | Likelihood | Impact | Mitigation |

## 9. Open Items
[All [TODO: ...] placeholders grouped by section]

---
*Generated from bet artifacts: [list source files used]*
```

Synthesis rules:
- Draw each section from the mapped source file (see Step 2)
- Preserve exact metric values, percentages, and numbers — never round or paraphrase
- Write `[TODO: ...]` for any section where source material is missing — never fabricate
- Use the bet name from `status.md` as the document title

## Step 4: Save Local Copy

Write the synthesized PRD to `prd.md` in the bet directory (overwrite if exists, after confirming with the user).

## Step 5: Publish to Google Doc

Find the creation script from the plugin:

```bash
for candidate in \
  ".claude/plugins/bet-docs/scripts/create_google_doc.py" \
  "$HOME/.claude/plugins/local/bet-docs/scripts/create_google_doc.py"; do
  if [ -f "$candidate" ]; then
    SCRIPT="$candidate"
    break
  fi
done
```

Then run:

```bash
python3 "$SCRIPT" \
  --title "[BET_NAME] — PRD" \
  --content-file "[BET_PATH]/prd.md"
```

If the script fails (missing auth or dependencies), tell the user:
```
Could not publish to Google Docs automatically.
PRD saved locally at: [bet-path]/prd.md

To authenticate, run:
  gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive

To install dependencies:
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 6: Report

```
PRD generated!

**[BET_NAME] — PRD**
- Google Doc: [URL]
- Local copy: [bet-path]/prd.md

Sources used: [list]
Missing files (TODOs added): [list or "none"]
```
