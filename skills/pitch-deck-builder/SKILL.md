---
name: pitch-deck
description: Generate a pitch deck for your bet
long_description: |
  Creates a **single-slide pitch summary** for your bet following the FinE Unified Intake format.

  **Output:** Google Slides presentation (copied from the canonical P2 Pitch Template).

  The deck is built from your bet's existing documentation (problem_frame.md, hypothesis.md, evidence.md, etc.)
  and condenses everything into one dense, executive-ready slide matching the standard Finance intake layout:

  - **Owner strip:** Finance Owner, FinE Owner, Ent Process, Date
  - **Title**
  - **Executive Summary** (2-3 sentences)
  - **Impact** (per stakeholder group)
  - **Problem Statement** (scale + urgency)
  - **Definition of Done** (numbered items with MW estimates)

  This is designed for intake review meetings where each bet gets one slide.

  Copies the Google Slides template directly and fills it in via the Slides API —
  no HTML intermediate step required.
usage: pitch-deck [--bet-path PATH]
examples:
  - "pitch-deck --bet-path domains/adjustments/self-serve-adjustments"
  - "pitch-deck --bet-path domains/royalties/music-label-uplifts"
allowed-tools: ["Bash(*)", "Read(*)", "Write(*)", "Glob(*)", "Grep(*)", "AskUserQuestion"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **curl**: Run `which curl`. If missing, install via `brew install curl`
3. **gcloud auth (presentations/drive/cloud-platform scopes)**: Run `gcloud auth application-default print-access-token`. If missing or expired, run:
   ```
   gcloud auth application-default login \
     --scopes=https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform
   ```

If any prerequisite is missing, walk the user through setting it up before proceeding.

Generate a 1-page pitch slide for your bet following the FinE Unified Intake format.

## Google Slides Template

- **Template ID:** `1MNkGr0XU5-T5wLD08ttFewPW-BUxp4vZBrP5V3xLoN0`
- **Template URL:** https://docs.google.com/presentation/d/1MNkGr0XU5-T5wLD08ttFewPW-BUxp4vZBrP5V3xLoN0/edit
- **GCP Project:** `fine-pm-em-staff`

### Slide Structure

The template has one slide (`g3912db0859f_0_367`) with these elements:

| Element ID | Type | Content |
|------------|------|---------|
| `g3912db0859f_0_368` | Table (3x4) | Owner strip — row 0: labels (FINANCE OWNER, FINE OWNER, ENT PROCESS, DATE), row 0 spans 2 rows, row 2: values (empty) |
| `g3912db0859f_0_372` | Text box | Title — contains placeholder text "Title" |
| `g3912db0859f_0_369` | Table (2x1) | Executive Summary — row 0: label, row 1: content (empty) |
| `g3912db0859f_0_370` | Table (2x1) | Impact — row 0: label, row 1: content (empty) |
| `g3912db0859f_0_371` | Table (2x1) | Problem Statement — row 0: label, row 1: content (empty) |
| `g3912db0859f_0_373` | Table (6x3) | Definition of Done — row 0: headers (#, Definition of Done, MW), rows 1-5: numbered items with empty description and "TBD" MW |

## Workflow

### Step 1: Identify Bet Path

If `--bet-path` is provided, use it. Otherwise, ask the user which bet to generate for.

### Step 2: Read Bet Files

Read all available files from the bet directory:
- `status.md` — phase, Jira/Groove links, milestones, team
- `problem_frame.md` — problem statement, scale, stakeholders
- `hypothesis.md` — core hypothesis, assumptions, expected outcomes
- `prd.md` — goals, non-goals, success metrics, risks, phased approach, DoD
- `evidence.md` — validated data, user research findings
- `success_metrics.md` — north star metric, supporting metrics with targets

Not all files may exist — use what's available.

### Step 3: Extract Content

From the bet files, extract values for each field:

| Field | Source | Guidance |
|-------|--------|----------|
| `FINANCE_OWNER` | prd.md stakeholders (Accountable) | Finance sponsor name |
| `FINE_OWNER` | prd.md stakeholders (Responsible) | FinE product + eng leads |
| `ENT_PROCESS` | problem_frame.md | Which enterprise process (e.g. OTC/Content) |
| `DATE` | status.md | Target date or season (e.g. "Spring 2026") |
| `TITLE` | status.md or problem_frame.md | Bet name |
| `EXECUTIVE_SUMMARY` | problem_frame.md, hypothesis.md | 2-3 sentences max. What + why + approach. |
| `IMPACT` | prd.md strategic positioning | Bullet per stakeholder group with one-line impact |
| `PROBLEM_STATEMENT` | problem_frame.md | 2-3 sentences. Scale + urgency + why now. |
| `DOD_1` through `DOD_5` | prd.md phases, hypothesis.md | Concrete deliverables. Start with a verb. |
| `DOD_1_MW` through `DOD_5_MW` | Estimates or "TBD" | Man-weeks if known |

**Writing guidance:**
- Executive Summary: No more than 3 sentences. State what the project does, why it matters, and the approach.
- Impact: One line per stakeholder. Use bullet character (•). Use their language.
- Problem Statement: Lead with scale (numbers), then urgency (deadlines, blockers).
- DoD: Each item is a concrete deliverable, not a phase. Start with a verb.

### Step 4: Verify Authentication

Before making any API calls, verify that the user has valid credentials with the required scopes.

```bash
# Check if application-default credentials exist and have the right scopes
TOKEN=$(gcloud auth application-default print-access-token 2>&1)
if echo "$TOKEN" | grep -qi "error\|could not\|not found\|invalid"; then
    echo "AUTH_MISSING"
else
    # Test Drive access by trying to get the template metadata
    DRIVE_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "Authorization: Bearer $TOKEN" \
      -H "x-goog-user-project: fine-pm-em-staff" \
      "https://www.googleapis.com/drive/v3/files/1MNkGr0XU5-T5wLD08ttFewPW-BUxp4vZBrP5V3xLoN0?fields=id")
    echo "DRIVE_STATUS=$DRIVE_CHECK"

    # Test Slides access
    SLIDES_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "Authorization: Bearer $TOKEN" \
      -H "x-goog-user-project: fine-pm-em-staff" \
      "https://slides.googleapis.com/v1/presentations/1MNkGr0XU5-T5wLD08ttFewPW-BUxp4vZBrP5V3xLoN0?fields=presentationId")
    echo "SLIDES_STATUS=$SLIDES_CHECK"
fi
```

**If AUTH_MISSING, or DRIVE_STATUS/SLIDES_STATUS is not 200**, run the login command to set up credentials with the correct scopes:

```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform"
```

This opens a browser for OAuth consent. After completing, re-run the check above to confirm.

**Do not proceed to Step 5 until both DRIVE_STATUS and SLIDES_STATUS return 200.**

Common failures:
- `403` — credentials exist but lack the required scopes. Re-run the login command above.
- `401` — credentials expired. Re-run the login command above.
- `404` — template file not accessible. Check that the user has view access to the template.

### Step 5: Copy the Google Slides Template

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d '{"name": "<Bet Title>: P2 Pitch"}' \
  "https://www.googleapis.com/drive/v3/files/1MNkGr0XU5-T5wLD08ttFewPW-BUxp4vZBrP5V3xLoN0/copy"
```

Save the returned `id` as `PRES_ID`.

### Step 6: Fill in the Slide via Slides API

Send a single `batchUpdate` request to fill all fields:

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d '{
    "requests": [
      {
        "replaceAllText": {
          "containsText": { "text": "Title", "matchCase": true },
          "replaceText": "<TITLE>",
          "pageObjectIds": ["g3912db0859f_0_367"]
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_368",
          "cellLocation": { "rowIndex": 2, "columnIndex": 0 },
          "text": "<FINANCE_OWNER>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_368",
          "cellLocation": { "rowIndex": 2, "columnIndex": 1 },
          "text": "<FINE_OWNER>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_368",
          "cellLocation": { "rowIndex": 2, "columnIndex": 2 },
          "text": "<ENT_PROCESS>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_368",
          "cellLocation": { "rowIndex": 2, "columnIndex": 3 },
          "text": "<DATE>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_369",
          "cellLocation": { "rowIndex": 1, "columnIndex": 0 },
          "text": "<EXECUTIVE_SUMMARY>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_370",
          "cellLocation": { "rowIndex": 1, "columnIndex": 0 },
          "text": "<IMPACT>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_371",
          "cellLocation": { "rowIndex": 1, "columnIndex": 0 },
          "text": "<PROBLEM_STATEMENT>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_373",
          "cellLocation": { "rowIndex": 1, "columnIndex": 1 },
          "text": "<DOD_1>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_373",
          "cellLocation": { "rowIndex": 2, "columnIndex": 1 },
          "text": "<DOD_2>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_373",
          "cellLocation": { "rowIndex": 3, "columnIndex": 1 },
          "text": "<DOD_3>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_373",
          "cellLocation": { "rowIndex": 4, "columnIndex": 1 },
          "text": "<DOD_4>",
          "insertionIndex": 0
        }
      },
      {
        "insertText": {
          "objectId": "g3912db0859f_0_373",
          "cellLocation": { "rowIndex": 5, "columnIndex": 1 },
          "text": "<DOD_5>",
          "insertionIndex": 0
        }
      }
    ]
  }' \
  "https://slides.googleapis.com/v1/presentations/$PRES_ID:batchUpdate"
```

**Notes on the batchUpdate:**
- Replace `<PLACEHOLDER>` values with the actual extracted content
- For DoD MW values: only replace "TBD" if you have actual estimates. Use `replaceAllText` scoped to the DoD table if needed.
- If a bet has fewer than 5 DoD items, leave the remaining rows empty (don't insert text)
- If a bet has more than 5 DoD items, consolidate to the 5 most important
- Use bullet character `•` for Impact items, with `\n` between lines
- Escape special characters in JSON (quotes, backslashes, newlines)

### Step 7: Report Success

Print to the user:

```
Pitch deck created!

**Title:** <Bet Title>: P2 Pitch
**URL:** https://docs.google.com/presentation/d/<PRES_ID>/edit

Fields filled:
- Finance Owner: <value>
- FinE Owner: <value>
- Ent Process: <value>
- Date: <value>
- Executive Summary: ✓
- Impact: ✓
- Problem Statement: ✓
- Definition of Done: <N> items

<Any fields that couldn't be filled due to missing bet files>
```

## Troubleshooting

**Authentication fails:**
```
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform"
```

**Template copy fails:**
- Verify you have access to the template: https://docs.google.com/presentation/d/1MNkGr0XU5-T5wLD08ttFewPW-BUxp4vZBrP5V3xLoN0/edit
- Check GCP project billing is active

**batchUpdate fails with element not found:**
- The template slide structure may have changed. Re-inspect the template using the Slides API to get current element IDs.
