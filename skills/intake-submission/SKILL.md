---
name: submit
description: "Submit a bet to the FinE monthly intake review document"
argument-hint: "<bet-path>"
allowed-tools: ["Bash(*)", "Read(*)", "Glob(*)", "AskUserQuestion"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **python3**: Run `which python3`. If missing, install via `brew install python3`
3. **gcloud auth (documents/drive/cloud-platform scopes)**: Run `gcloud auth application-default print-access-token`. If missing or expired, run:
   ```
   gcloud auth application-default login \
     --scopes=https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform
   ```

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Intake Submission Skill

Submit a bet to the Fin/FinE Monthly Intake Review document so it can be discussed at the next intake meeting.

## Overview

This skill:
- Reads bet files to gather submission details
- Finds the most recent intake meeting table in the Google Doc
- Asks you to confirm details before submitting (document is visible to stakeholders)
- Inserts a new row into the intake table via the Google Docs API

## Usage

```
/submit domains/adjustments/self-serve adjustments
/submit domains/booking/Subledger
```

## Arguments

- `<bet-path>`: Path to the bet directory (required)

---

## Instructions

### Step 1: Validate Bet Directory

Check that the path is a valid bet directory:

```bash
BET_PATH="$1"
ls "$BET_PATH"/*.md 2>/dev/null | head -5
```

If no markdown files found, tell the user:
```
No markdown files found in [path]. Is this a valid bet directory?
```

---

### Step 2: Read Bet Metadata

Read the bet files to extract submission details:

From **status.md**:
- Bet name (from heading)
- Jira ticket
- Groove Initiative/DoD
- Current phase
- Owner

From **problem_frame.md**:
- Problem statement (1-2 sentences)
- Why it matters

From **hypothesis.md**:
- Core hypothesis (1 sentence)
- Expected outcomes

---

### Step 3: Check Authentication

Verify Google Docs API access:

```bash
gcloud auth application-default print-access-token >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "AUTH_MISSING"
fi
```

If AUTH_MISSING, tell the user:
```
Google authentication required. Run:
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform"
```

---

### Step 4: Find the Most Recent Intake Table

Fetch the intake document and find the most recent table in the "New Intake" tab:

```bash
TOKEN=$(gcloud auth application-default print-access-token)
DOC_ID="1ZptcAu79FXTDUM1RJMgTRnxFlDEZE8HGmlM-_uVPRrY"

# Fetch document with tabs
curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  "https://docs.googleapis.com/v1/documents/$DOC_ID?includeTabsContent=true" > /tmp/intake_doc.json
```

Parse the document to find the most recent dated table:

```python
import json

doc = json.load(open('/tmp/intake_doc.json'))

# The "New Intake" tab is the one with tabId "t.0"
intake_tab = None
for tab in doc.get('tabs', []):
    if tab.get('tabProperties', {}).get('tabId') == 't.0':
        intake_tab = tab
        break

if not intake_tab:
    print("ERROR: New Intake tab not found")
    exit(1)

body = intake_tab['documentTab']['body']['content']

# Find dates and their tables
# Dates use dateElement (not textRun) inside HEADING_2 paragraphs
tables = []
for i, el in enumerate(body):
    if 'paragraph' in el:
        for elem in el['paragraph'].get('elements', []):
            if 'dateElement' in elem:
                de = elem['dateElement']['dateElementProperties']
                date_text = de['displayText']
                timestamp = de['timestamp']
                # Find the table after this heading
                for j in range(i+1, min(i+5, len(body))):
                    if 'table' in body[j]:
                        t = body[j]['table']
                        tables.append({
                            'date': date_text,
                            'timestamp': timestamp,
                            'table_index': j,
                            'start_index': body[j]['startIndex'],
                            'end_index': body[j]['endIndex'],
                            'rows': t['rows'],
                            'cols': t['columns'],
                            'table_element': body[j]
                        })
                        break

if not tables:
    print("ERROR: No intake tables found")
    exit(1)

# Most recent table is first
latest = tables[0]
print(f"LATEST_DATE={latest['date']}")
print(f"LATEST_TABLE_INDEX={latest['table_index']}")
print(f"LATEST_TABLE_START={latest['start_index']}")
print(f"LATEST_TABLE_END={latest['end_index']}")
print(f"LATEST_TABLE_ROWS={latest['rows']}")
print(f"LATEST_TABLE_COLS={latest['cols']}")

# Get the endIndex of the last row (where we'll insert after)
last_row = latest['table_element']['table']['tableRows'][-1]
print(f"LAST_ROW_END={last_row['endIndex']}")

# Get the table startIndex for insertTableRow
print(f"TABLE_START={latest['start_index']}")
```

---

### Step 5: Confirm Submission Details

Before submitting, present the details to the user for confirmation using AskUserQuestion:

Show:
- **Bet name**
- **Target table date** (e.g., "Feb 9, 2026")
- **Area** (which Finance area — e.g., "FinE", "OTC", "Revenue Accounting")
- **Finance Sponsor** (ask user — must be a Finance leader)
- **Tech Sponsor** (ask user — the technical lead or PM)
- **Pitch Link** (link to pitch deck, if available — check bet directory for presentation.html or link in status.md)
- **Finance cross-team dependencies** (which Finance teams are impacted)

Ask the user to confirm or modify these details.

---

### Step 6: Insert Row into Intake Table

Use the Google Docs API `batchUpdate` to insert a new row and populate cells.

**Important:** The table is in the "New Intake" tab (tabId=`t.0`). All requests must include the `tabId` field.

**Step 6a: Insert a new empty row at the end of the table:**

```bash
TOKEN=$(gcloud auth application-default print-access-token)
DOC_ID="1ZptcAu79FXTDUM1RJMgTRnxFlDEZE8HGmlM-_uVPRrY"

# Insert a new table row at the end of the table
# rowIndex is 0-based, so to add after the last row, use the current row count
ROW_INDEX=$LATEST_TABLE_ROWS  # e.g., if table has 4 rows (header + 3 data), insert at index 4

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d "{
    \"requests\": [
      {
        \"insertTableRow\": {
          \"tableCellLocation\": {
            \"tableStartLocation\": {
              \"index\": $TABLE_START,
              \"tabId\": \"t.0\"
            },
            \"rowIndex\": $(($ROW_INDEX - 1)),
            \"columnIndex\": 0
          },
          \"insertBelow\": true
        }
      }
    ]
  }" \
  "https://docs.googleapis.com/v1/documents/$DOC_ID:batchUpdate"
```

**Step 6b: Re-fetch the document to get updated indices after row insertion:**

```bash
curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  "https://docs.googleapis.com/v1/documents/$DOC_ID?includeTabsContent=true" > /tmp/intake_doc_updated.json
```

Parse the updated document to find the new row's cell indices.

**Step 6c: Insert text into each cell of the new row.**

The table has 9 columns split into two sections:

**INTAKE section (cols 0-4):**

| Col | Column | Example Value |
|-----|--------|---------------|
| 0 | Area | FinE |
| 1 | Finance Sponsor | corroy@spotify.com |
| 2 | Tech Sponsor | jamals@spotify.com |
| 3 | Pitch Link | Google Slides URL |
| 4 | Name | Self-Serve Adjustments |

**MEETING REVIEW section (cols 5-8) — filled during the meeting:**

| Col | Column | Example Value |
|-----|--------|---------------|
| 5 | Finance cross-team dependencies | OTC, Revenue Accounting |
| 6 | Comments | (filled during meeting) |
| 7 | Qualification agreement | (filled during meeting) |
| 8 | Hard deadline (if any) | (optional) |

For each cell that needs text, find its startIndex from the updated document and insert text:

```python
import json

doc = json.load(open('/tmp/intake_doc_updated.json'))

intake_tab = None
for tab in doc.get('tabs', []):
    if tab.get('tabProperties', {}).get('tabId') == 't.0':
        intake_tab = tab
        break

body = intake_tab['documentTab']['body']['content']

# Re-find the most recent table (same logic as Step 4)
tables = []
for i, el in enumerate(body):
    if 'paragraph' in el:
        for elem in el['paragraph'].get('elements', []):
            if 'dateElement' in elem:
                de = elem['dateElement']['dateElementProperties']
                for j in range(i+1, min(i+5, len(body))):
                    if 'table' in body[j]:
                        tables.append(body[j])
                        break

latest_table = tables[0]
table = latest_table['table']

# The new row is the LAST row in the table
new_row = table['tableRows'][-1]

# Get startIndex for each cell's paragraph content
cell_indices = []
for cell in new_row['tableCells']:
    # The insertText index is the startIndex of the paragraph inside the cell
    para = cell['content'][0]
    cell_indices.append(para['startIndex'])

print("Cell indices for new row:")
for i, idx in enumerate(cell_indices):
    print(f"  Col {i}: startIndex={idx}")
```

Batch all insertions into a single `batchUpdate` request with multiple `insertText` operations, ordered from **highest index to lowest** to prevent index shifts:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d "{
    \"requests\": [
      {\"insertText\": {\"location\": {\"index\": $CELL_5_INDEX, \"tabId\": \"t.0\"}, \"text\": \"$DEPENDENCIES\"}},
      {\"insertText\": {\"location\": {\"index\": $CELL_4_INDEX, \"tabId\": \"t.0\"}, \"text\": \"$BET_NAME\"}},
      {\"insertText\": {\"location\": {\"index\": $CELL_3_INDEX, \"tabId\": \"t.0\"}, \"text\": \"$PITCH_LINK\"}},
      {\"insertText\": {\"location\": {\"index\": $CELL_2_INDEX, \"tabId\": \"t.0\"}, \"text\": \"$TECH_SPONSOR\"}},
      {\"insertText\": {\"location\": {\"index\": $CELL_1_INDEX, \"tabId\": \"t.0\"}, \"text\": \"$FINANCE_SPONSOR\"}},
      {\"insertText\": {\"location\": {\"index\": $CELL_0_INDEX, \"tabId\": \"t.0\"}, \"text\": \"$AREA\"}}
    ]
  }" \
  "https://docs.googleapis.com/v1/documents/$DOC_ID:batchUpdate"
```

**To bold the bet name in column 4**, add an `updateTextStyle` request after the `insertText`:

```bash
{
  "updateTextStyle": {
    "range": {
      "startIndex": $CELL_4_INDEX,
      "endIndex": $CELL_4_INDEX + len("$BET_NAME"),
      "tabId": "t.0"
    },
    "textStyle": {"bold": true},
    "fields": "bold"
  }
}
```

---

### Step 7: Report Success

```
Intake submission added!

**Bet:** [BET_NAME]
**Table:** [DATE] intake meeting
**Document:** https://docs.google.com/document/d/1ZptcAu79FXTDUM1RJMgTRnxFlDEZE8HGmlM-_uVPRrY/edit?tab=t.0

Row added with:
- Area: [AREA]
- Finance Sponsor: [FINANCE_SPONSOR]
- Tech Sponsor: [TECH_SPONSOR]
- Pitch Link: [PITCH_LINK]
- Name: [BET_NAME]
- Dependencies: [DEPENDENCIES]

Next step: Prepare your pitch deck using /create and present at the intake meeting.
```

---

## Document Reference

- **Document:** "Fin/FinE: Monthly Intake Review"
- **Document ID:** `1ZptcAu79FXTDUM1RJMgTRnxFlDEZE8HGmlM-_uVPRrY`
- **Tab:** "New Intake" (tabId: `t.0`)
- **API:** Google Docs REST API v1
- **Auth:** `gcloud auth application-default print-access-token`
- **Project:** `fine-pm-em-staff` (required as `x-goog-user-project` header)

### Table Columns (9 total)

The table has two merged header sections:

**INTAKE (cols 0-4):**

| Col | Column | Example Value |
|-----|--------|---------------|
| 0 | Area | FinE |
| 1 | Finance Sponsor | corroy@spotify.com |
| 2 | Tech Sponsor | jamals@spotify.com |
| 3 | Pitch Link | Google Slides URL |
| 4 | Name | **Self-Serve Adjustments** |

**MEETING REVIEW (cols 5-8):**

| Col | Column | Example Value |
|-----|--------|---------------|
| 5 | Finance cross-team dependencies | OTC, CA, PTP |
| 6 | Comments | (filled during meeting) |
| 7 | Qualification agreement | (filled during meeting) |
| 8 | Hard deadline (if any) | Q1 2026 |

**Note:** Row 0 is a merged header row ("INTAKE" | "MEETING REVIEW"). Row 1 contains the actual column headers. Data rows start at row 2.

### Date Handling

Dates in the document use `dateElement` objects (not text runs). When looking for meeting dates, parse the `dateElement.dateElementProperties.displayText` and `timestamp` fields.

---

## Troubleshooting

**Authentication fails:**
```
Ensure you have the required scopes:
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform"
```

**Table not found:**
- The document has two tabs: "Overview" and "New Intake". The intake tables are in the "New Intake" tab (tabId: `t.0`).
- Ensure you're using `?includeTabsContent=true` when fetching the document.
- Include `tabId: "t.0"` in all `batchUpdate` requests.

**Index errors on insert:**
- Always re-fetch the document after `insertTableRow` to get updated indices before inserting text.
- When batching multiple `insertText` operations, order them from highest index to lowest to prevent index shifts.

**No upcoming meeting table:**
- If there's no table for the next meeting yet, add the row to the most recent table. The intake committee will see it at the next meeting.
- Alternatively, ask the user if they want to wait for the next meeting's table to be created.
