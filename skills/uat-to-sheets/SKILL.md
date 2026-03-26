---
name: uat-to-sheets
description: "Convert a UAT validation markdown report into a formatted Google Sheet with Connected Sheets BQ tabs"
argument-hint: "<path-or-url> --bq-project \"project-id\" [--quota-project \"project-id\"] [--title \"Custom Title\"]"
allowed-tools: ["Bash(*)", "Read(*)", "Glob(*)", "Grep(*)", "Write(*)", "AskUserQuestion"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **gh** (GitHub CLI): Run `which gh`. If missing, install via `brew install gh`
3. **python3**: Run `which python3`. If missing, install via `brew install python3`
4. **curl**: Run `which curl`. If missing, install via `brew install curl`
5. **gcloud auth (spreadsheets/drive/cloud-platform/bigquery.readonly scopes)**: Run `gcloud auth application-default print-access-token`. If missing or expired, run:
   ```
   gcloud auth application-default login \
     --scopes=https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery.readonly
   ```

If any prerequisite is missing, walk the user through setting it up before proceeding.

# UAT to Google Sheets

Convert a UAT validation report (markdown) into a formatted Google Sheet with a Summary tab, Descriptions tab, and Connected Sheet BQ tabs (live BigQuery queries) per check.

## Overview

This skill:
1. Reads a UAT markdown report (local file or GHE URL)
2. Parses the report structure (summary table, detail sections with results and SQL)
3. Creates a Google Sheet via the Sheets API
4. Populates a Summary tab and Descriptions tab
5. Creates Connected Sheet BQ tabs via `addDataSource` — these are live BigQuery connections that stakeholders can refresh directly from the Sheets UI
6. Applies formatting (colors, bold headers, frozen rows, column sizing, conditional formatting)

## Output Structure

The generated sheet follows this tab structure:

| Tab | Purpose |
|-----|---------|
| `Summary` | Report title, status banner, metadata, checks grouped by section |
| `Descriptions` | Full reference table with Query ID, Name, Section, Status, Condition, Rows, Description |
| `BQ:{QueryID}` (one per check) | Connected Sheet — live BigQuery query (refreshable from Sheets UI) |

## Configuration

- **GCP Quota Project:** Provided via `--quota-project` argument, or defaults to the `--bq-project` value. This is the project billed for Sheets API quota (sent as `x-goog-user-project` header).
- **BigQuery Project:** Provided via `--bq-project` argument (required — used as the billing project for Connected Sheets queries)
- **Auth:** gcloud Application Default Credentials

---

## Instructions

### Step 1: Resolve Input

The user provides either a local file path or a GitHub/GHE URL.

**If local file path:**
Read the file directly.

**If GitHub/GHE URL:**
Extract the hostname, org, repo, branch, and file path from the URL, then fetch via `gh api`:

```bash
# Example URL: https://github.example.com/org/repo/blob/branch/path/to/report.md
# Extract: hostname, org, repo, ref (branch), path

gh api --hostname {hostname} \
  "repos/{org}/{repo}/contents/{path}?ref={branch}" \
  -q '.content' | base64 -d > /tmp/uat-report.md
```

For public GitHub URLs (`github.com`), omit the `--hostname` flag. For GitHub Enterprise instances, use the hostname from the URL.

Read the markdown content into memory. If the file cannot be resolved, ask the user to provide a valid path.

---

### Step 2: Parse the Markdown Report

UAT reports follow a consistent structure. Parse these sections:

#### 2a: Header and Metadata

Extract from the top of the file:
- **Report title** — the first `#` heading (e.g., `# UAT Validation Report: My Feature`)
- **Report slug** — if present in parentheses after the title (e.g., `(calm-bark)`)
- **Generated date** — look for a line like `Generated: YYYY-MM-DD HH:MM:SS`
- **Report ID** — look for a line like `Report ID: abc-123-def`
- **Table references** — any lines referencing table names or dataset paths. These typically appear as key-value pairs like:
  - `TEST_TABLE_NAME: project.dataset.table`
  - `PROD_TABLE_NAME: project.dataset.table`
  - `REVENUE_TABLE: project.dataset.table`
  - `BILLING_TABLE: project.dataset.table`
  - etc.
  Collect ALL table reference parameters as key-value pairs.

#### 2b: Summary Table

Find the markdown table in the summary section. It typically has columns like:
- `Status` (PASS, INFO, FAIL)
- `Query` or `Check` name
- `Rows` or row count
- `Condition` or description

Parse each row into a structured list: `{status, query_id, query_name, rows, condition}`.

#### 2c: Section Structure

UAT reports may group checks into sections. Detect sections from:
- Markdown `##` or `###` headings that group multiple checks (e.g., `## Data Quality Checks`, `## Reconciliation Checks`)
- Query ID prefixes that share a common letter (e.g., all `D` checks belong to one section, all `R` checks to another)
- If no explicit sections exist, infer from check naming patterns or treat all as one section

Do not assume any fixed prefix-to-section mapping — derive section names from the report's own headings and structure.

Record the section name for each check.

#### 2d: Detail Sections

Each check has a detail section. Parse these patterns:

```markdown
## B1: Check Title
or
## 01: Check Title
```

For each detail section, extract:
- **Query ID** — the alphanumeric prefix (e.g., `B1`, `P3`, `R2`). If the report uses sequential numbers (01, 02), map them to section-prefixed IDs based on the section they belong to.
- **Check name/title** (e.g., `Table Availability Check`)
- **Section** — which group this check belongs to (as determined from the report's section headings)
- **Purpose/Description** text — multi-line description of what the check validates and methodology
- **Expected/Condition** text
- **Result table** — column headers and all data rows
- **SQL query** — from the `<details>` / ````sql` block
- **Status** — PASS/INFO/FAIL (from the summary table or inline)
- **Row count** — number of result rows
- **Notes** — any additional text or annotations
- **Table references used** — extract any table names referenced in the SQL or metadata

**Important parsing rules:**
- Some checks may be combined (e.g., `B3-B4: Row Count`) — treat as one entry with the combined ID
- Result tables may have many columns (60+) — preserve all of them
- Numeric values with commas should be preserved as-is
- The `check_passed` column (typically last) contains TRUE/FALSE

---

### Step 3: Check Authentication

Verify the user has Sheets API and BigQuery access:

```bash
TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null) && \
curl -s "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=$TOKEN" | grep -q "googleapis.com/auth" && echo "OK" || echo "NEEDS_SETUP"
```

Required scopes: `spreadsheets`, `drive`, `cloud-platform`, `bigquery.readonly`.

#### If NEEDS_SETUP:

Tell the user:

```
Google Sheets and BigQuery access not configured. Run this command:

gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery.readonly"

Then try /uat-to-sheets again.
```

Also verify the `--bq-project` argument was provided. If missing, ask the user:

```
Connected Sheets requires a BigQuery billing project. Please provide one:

/uat-to-sheets <path> --bq-project "your-gcp-project-id"

Optionally, provide a separate quota project for Sheets API billing:
  --quota-project "your-quota-project-id"
If omitted, the --bq-project value is used for both.
```

---

### Step 4: Create the Google Sheet

Create a new spreadsheet. The title should follow the format `UAT: {Report Name} ({slug})` if a slug is present, otherwise `UAT: {Report Name}`:

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "title": "UAT: {Report Name} ({slug})"
    }
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets"
```

Extract the `spreadsheetId` and `sheets[0].properties.sheetId` (the default Sheet1, which becomes Summary) from the response.

---

### Step 5: Create Tabs

Use `batchUpdate` to create the Summary and Descriptions tabs. **BQ tabs are NOT created here** — they will be created as Connected Sheets in Step 8 via `addDataSource`.

1. Rename Sheet1 to `Summary`
2. Add `Descriptions` tab

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "updateSheetProperties": {
          "properties": {"sheetId": 0, "title": "Summary"},
          "fields": "title"
        }
      },
      {
        "addSheet": {
          "properties": {"title": "Descriptions", "index": 1}
        }
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}:batchUpdate"
```

**Important:** Collect the `sheetId` for each newly created tab from the response — you need these for formatting requests later.

---

### Step 6: Populate the Summary Tab

The Summary tab provides a high-level overview with checks grouped by section.

#### Layout:

**Row 1:** Report title (col A, merged across A:F) — e.g., `UAT: {Report Name} ({slug})`

**Row 2:** Overall status banner (col A, merged across A:F):
- If any check has FAIL status: `SOME CHECKS FAILED` (red background)
- If all checks pass: `ALL CHECKS PASSED` (green background)
- If no failures but some INFO: `ALL CHECKS PASSED (WITH NOTES)` (green background)

**Row 3:** blank

**Row 4+:** Key-value metadata, one per row:
- Column A: label (bold), Column B: value
- `Generated:` — timestamp
- `Report ID:` — report ID value
- Then each table reference parameter as its own row (e.g., `TEST_TABLE_NAME:` | `project.dataset.table`)
- Include ALL table reference parameters from the report

**Blank row after metadata**

**Section groups** — For each section (as detected from the report):

- **Section header row:** Section name in col A (bold, slightly larger font, light grey background) merged across A:E
- **Column headers row:** `Status` | `Query` | `Rows` | `Condition` | `Notes`
- **Data rows:** One per check in that section:
  - `Status`: PASS / INFO / FAIL
  - `Query`: Query ID and name (e.g., `B1: Table Availability`) — will be hyperlinked to the BQ tab
  - `Rows`: row count from results
  - `Condition`: condition text from summary table
  - `Notes`: any notes (leave blank if none)
- **Blank row** between sections

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  -H "Content-Type: application/json" \
  -d '{
    "valueInputOption": "USER_ENTERED",
    "data": [
      {
        "range": "Summary!A1:F50",
        "values": [
          ["UAT: {Report Name} ({slug})"],
          ["SOME CHECKS FAILED"],
          [""],
          ["Generated:", "2026-02-12 14:30:00"],
          ["Report ID:", "example-slug"],
          ["SOURCE_TABLE:", "project.dataset.source_table"],
          ["TARGET_TABLE:", "project.dataset.target_table"],
          [""],
          ["Data Quality"],
          ["Status", "Query", "Rows", "Condition", "Notes"],
          ["PASS", "Q1: Table Availability", "5", "All tables exist", ""],
          ["FAIL", "Q2: Schema Comparison", "3", "Schemas should match", "2 mismatches found"],
          [""],
          ["Reconciliation"],
          ["Status", "Query", "Rows", "Condition", "Notes"],
          ["PASS", "R1: Row Count", "1", "Counts should match", ""]
        ]
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values:batchUpdate"
```

---

### Step 7: Populate the Descriptions Tab

The Descriptions tab is a full reference table listing every check with its description.

#### Layout:

**Row 1:** `Check Descriptions` (title, bold, large font)
**Row 2:** blank
**Row 3:** Column headers (bold): `Query ID` | `Name` | `Section` | `Status` | `Condition` | `Rows` | `Description`
**Row 4+:** One row per check:
- `Query ID`: e.g., `B1`, `P3`, `R1`
- `Name`: Full check name
- `Section`: Section name (as detected from the report's headings)
- `Status`: PASS / INFO / FAIL
- `Condition`: The condition/expected outcome text
- `Rows`: Number of result rows
- `Description`: The full multi-line purpose/methodology text from the detail section. Include the complete description — this is the reference for understanding what each check does.

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  -H "Content-Type: application/json" \
  -d '{
    "valueInputOption": "USER_ENTERED",
    "data": [
      {
        "range": "Descriptions!A1:G50",
        "values": [
          ["Check Descriptions"],
          [""],
          ["Query ID", "Name", "Section", "Status", "Condition", "Rows", "Description"],
          ["Q1", "Table Availability", "Data Quality", "PASS", "All tables exist", "5", "Verifies that all required tables exist in both test and production environments..."],
          ["Q2", "Schema Comparison", "Data Quality", "FAIL", "Schemas match", "3", "Compares column names, types, and order between source and target tables..."]
        ]
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values:batchUpdate"
```

---

### Step 8: Create Connected Sheet BQ Tabs

Each check gets a `BQ:{QueryID}` tab as a **Connected Sheet** — a live BigQuery connection that stakeholders can refresh directly from the Sheets UI.

#### How Connected Sheets work:

Instead of populating static data via `values:batchUpdate`, Connected Sheets use the `addDataSource` request in the Sheets `batchUpdate` API. This creates a `DATA_SOURCE` sheet that executes a BigQuery query and displays live results.

#### 8a: Extract SQL and build addDataSource requests

For each check, extract the SQL query from the `<details>` block in the markdown. Then build an `addDataSource` request:

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "addDataSource": {
          "dataSource": {
            "spec": {
              "bigQuery": {
                "projectId": "{bq-project}",
                "querySpec": {
                  "rawQuery": "SELECT table_name, CASE WHEN table_exists THEN '\''EXISTS'\'' ELSE '\''MISSING'\'' END AS status FROM `project.dataset.INFORMATION_SCHEMA.TABLES` WHERE table_name IN ('\''table_a'\'', '\''table_b'\'')"
                }
              }
            }
          }
        }
      },
      {
        "addDataSource": {
          "dataSource": {
            "spec": {
              "bigQuery": {
                "projectId": "{bq-project}",
                "querySpec": {
                  "rawQuery": "SELECT table_name, column_name, data_type FROM `project.dataset.INFORMATION_SCHEMA.COLUMNS` WHERE ..."
                }
              }
            }
          }
        }
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}:batchUpdate"
```

Key details:
- `projectId` comes from the `--bq-project` argument
- Use `querySpec.rawQuery` (not `tableSpec`) — the SQL comes directly from the markdown report's `<details>` blocks
- Batch all `addDataSource` requests into a single `batchUpdate` call where possible
- The API auto-creates a `DATA_SOURCE` sheet for each `addDataSource` request

#### 8b: Rename auto-created BQ tabs

After the `addDataSource` call, each auto-created sheet needs to be renamed to `BQ:{QueryID}`. Use `updateSheetProperties` to rename them:

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "updateSheetProperties": {
          "properties": {
            "sheetId": AUTO_CREATED_SHEET_ID_1,
            "title": "BQ:Q1"
          },
          "fields": "title"
        }
      },
      {
        "updateSheetProperties": {
          "properties": {
            "sheetId": AUTO_CREATED_SHEET_ID_2,
            "title": "BQ:Q2"
          },
          "fields": "title"
        }
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}:batchUpdate"
```

Extract the auto-created sheet IDs from the `addDataSource` response — each reply contains the `dataSourceSheetId` for the newly created sheet.

BQ tab naming rules:
- `BQ:{QueryID}` (e.g., `BQ:B1`, `BQ:P3`, `BQ:R1`)
- For combined checks (e.g., `B3-B4`), use the combined ID: `BQ:B3-B4`

#### 8c: Poll for query execution completion

Data execution is **asynchronous**. After creating Connected Sheets, poll the spreadsheet to check execution status:

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}?includeGridData=false"
```

Check `sheets[].dataSourceSheetProperties.dataExecutionStatus.state` for each DATA_SOURCE sheet:
- `RUNNING` — query still executing, wait and retry
- `SUCCEEDED` — query completed successfully
- `FAILED` — query failed (check `errorMessage` for details)

Polling strategy:
- Poll every 5 seconds
- Use exponential backoff (5s, 10s, 20s)
- Timeout after ~2 minutes
- Report any failed queries to the user with the error message

```bash
# Example polling loop
for i in $(seq 1 20); do
  RESULT=$(curl -s \
    -H "Authorization: Bearer $TOKEN" \
    -H "x-goog-user-project: {quota-project}" \
    "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}?includeGridData=false")

  # Check if all DATA_SOURCE sheets have completed
  # Look for dataExecutionStatus.state on each sheet
  STATES=$(echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for sheet in data.get('sheets', []):
    props = sheet.get('properties', {})
    ds_props = sheet.get('dataSourceSheetProperties', {})
    status = ds_props.get('dataExecutionStatus', {})
    if status:
        print(f\"{props.get('title', 'unknown')}: {status.get('state', 'UNKNOWN')}\")
")
  echo "$STATES"

  # Break if no RUNNING states remain
  echo "$STATES" | grep -q "RUNNING" || break
  sleep 5
done
```

**Important:** Always include the full SQL query for each check. This is critical for auditability — stakeholders need to verify exactly what query produced each result, and Connected Sheets allow them to refresh the data directly.

---

### Step 9: Apply Formatting

Use `batchUpdate` with formatting requests. Build ALL formatting into a single `batchUpdate` call.

#### 9a: Summary Tab Formatting

```json
{
  "requests": [
    // Bold and size the report title (row 1)
    {
      "repeatCell": {
        "range": {"sheetId": SUMMARY_SHEET_ID, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 1},
        "cell": {
          "userEnteredFormat": {
            "textFormat": {"bold": true, "fontSize": 14}
          }
        },
        "fields": "userEnteredFormat.textFormat"
      }
    },
    // Status banner formatting (row 2)
    // If FAIL: red background, white bold text
    {
      "repeatCell": {
        "range": {"sheetId": SUMMARY_SHEET_ID, "startRowIndex": 1, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 6},
        "cell": {
          "userEnteredFormat": {
            "backgroundColor": {"red": 0.87, "green": 0.27, "blue": 0.27},
            "textFormat": {"bold": true, "fontSize": 12, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
            "horizontalAlignment": "CENTER"
          }
        },
        "fields": "userEnteredFormat"
      }
    },
    // If ALL PASS: use green instead
    // {"backgroundColor": {"red": 0.2, "green": 0.66, "blue": 0.33}}

    // Merge title row across columns
    {
      "mergeCells": {
        "range": {"sheetId": SUMMARY_SHEET_ID, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 6},
        "mergeType": "MERGE_ALL"
      }
    },
    // Merge status banner row
    {
      "mergeCells": {
        "range": {"sheetId": SUMMARY_SHEET_ID, "startRowIndex": 1, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 6},
        "mergeType": "MERGE_ALL"
      }
    },
    // Bold metadata labels (column A)
    {
      "repeatCell": {
        "range": {"sheetId": SUMMARY_SHEET_ID, "startRowIndex": 3, "endRowIndex": METADATA_END_ROW, "startColumnIndex": 0, "endColumnIndex": 1},
        "cell": {
          "userEnteredFormat": {
            "textFormat": {"bold": true}
          }
        },
        "fields": "userEnteredFormat.textFormat"
      }
    },
    // Section headers: bold, slightly larger, light grey background
    // Apply per section header row
    {
      "repeatCell": {
        "range": {"sheetId": SUMMARY_SHEET_ID, "startRowIndex": SECTION_ROW, "endRowIndex": SECTION_ROW + 1, "startColumnIndex": 0, "endColumnIndex": 5},
        "cell": {
          "userEnteredFormat": {
            "backgroundColor": {"red": 0.93, "green": 0.93, "blue": 0.93},
            "textFormat": {"bold": true, "fontSize": 11}
          }
        },
        "fields": "userEnteredFormat"
      }
    },
    // Merge section header across columns
    {
      "mergeCells": {
        "range": {"sheetId": SUMMARY_SHEET_ID, "startRowIndex": SECTION_ROW, "endRowIndex": SECTION_ROW + 1, "startColumnIndex": 0, "endColumnIndex": 5},
        "mergeType": "MERGE_ALL"
      }
    },
    // Bold column header rows (Status | Query | Rows | Condition | Notes)
    // Bold each section's header row
    // Freeze row 1
    {
      "updateSheetProperties": {
        "properties": {"sheetId": SUMMARY_SHEET_ID, "gridProperties": {"frozenRowCount": 1}},
        "fields": "gridProperties.frozenRowCount"
      }
    }
  ]
}
```

#### 9b: Descriptions Tab Formatting

- Bold title row (row 1, fontSize 14)
- Bold column headers (row 3)
- Freeze rows 1-3
- Wrap text in the Description column (column G)
- Auto-resize columns A-F, set column G width to 400px

#### 9c: BQ Tab Formatting (Connected Sheets — limited)

BQ tabs are `DATA_SOURCE` sheets (Connected Sheets). These have **limited formatting support** — the Sheets API does not allow most cell-level formatting on Connected Sheet tabs. The following limitations apply:

- Conditional formatting **cannot** be applied to DATA_SOURCE sheets
- Cell-level formatting (bold, font size, background color) is **not supported** on Connected Sheet cells
- Column widths and frozen rows **may not persist** after a data refresh
- Tab color can be set via `updateSheetProperties`

Focus formatting efforts on Summary and Descriptions tabs instead. For BQ tabs, optionally set a **tab color** to visually distinguish them:

```json
{
  "updateSheetProperties": {
    "properties": {
      "sheetId": BQ_SHEET_ID,
      "tabColorStyle": {
        "rgbColor": {"red": 0.26, "green": 0.52, "blue": 0.96}
      }
    },
    "fields": "tabColorStyle"
  }
}
```

**Status color mapping (apply to Summary tab):**
- `PASS` / `TRUE` / `MATCH` / `EXISTS` — light green: `{"red": 0.85, "green": 0.95, "blue": 0.85}`
- `INFO` / `EXPECTED` — light amber: `{"red": 1.0, "green": 0.95, "blue": 0.8}`
- `FAIL` / `FALSE` / `MISMATCH` / `MISSING` — light red: `{"red": 0.95, "green": 0.85, "blue": 0.85}`

#### 9d: Column Auto-Resize

Auto-resize all columns on all tabs:

```json
{
  "autoResizeDimensions": {
    "dimensions": {
      "sheetId": SHEET_ID,
      "dimension": "COLUMNS",
      "startIndex": 0,
      "endIndex": 26
    }
  }
}
```

Repeat for Summary and Descriptions sheets. BQ tabs (Connected Sheets) manage their own column sizing.

#### 9e: Hyperlinks from Summary to BQ Tabs

After creating all BQ tabs, update the Summary tab to add hyperlinks from each query name to its BQ tab. Use `values:update` with `USER_ENTERED` input option to write formulas:

```
=HYPERLINK("#gid=BQ_SHEET_ID", "B1: Table Availability")
```

Where `BQ_SHEET_ID` is the numeric sheet ID of the Connected Sheet BQ tab. The Summary links take users directly to the live query results.

Build the complete formatting `batchUpdate` with ALL requests across ALL tabs in a single API call.

```bash
TOKEN=$(gcloud auth application-default print-access-token)

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: {quota-project}" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      ... all formatting requests ...
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}:batchUpdate"
```

---

### Step 10: Report Success

Output the result to the user:

```
UAT report converted to Google Sheet.

**Sheet:** [Sheet Title]
**URL:** https://docs.google.com/spreadsheets/d/{spreadsheetId}

**Tabs created:**
- Summary
- Descriptions
- [N] Connected Sheet BQ tabs (live BigQuery queries)
- Total: [N + 2] tabs

**BQ tab status:**
- X queries SUCCEEDED
- Y queries FAILED (see error details above)

**Results:**
- X checks PASS
- Y checks INFO
- Z checks FAIL

BQ tabs are Connected Sheets — stakeholders can refresh data directly from the Sheets UI
by clicking Data > Refresh on any BQ tab.
```

---

## Handling Large Reports

If the markdown report has many checks (15+):

1. **Many checks:** Each check creates a Connected Sheet via `addDataSource`. For reports with many checks, batch all `addDataSource` requests into a single `batchUpdate` call. If the batch is too large, split into groups of 5-10 `addDataSource` requests per call.

2. **Long SQL queries:** Connected Sheets handle long queries natively via `rawQuery`. No need to split SQL across cells — the full query is passed as a single string in the `addDataSource` request.

3. **Many table references:** Some reports reference 10+ tables. Include all of them in the Summary metadata section.

---

## Error Handling

**Auth not configured:**
```
Google Sheets and BigQuery access not configured. Run:

gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery.readonly"

Then try /uat-to-sheets again.
```

**Missing `--bq-project` argument:**
```
Connected Sheets requires a BigQuery billing project. Please re-run with:

/uat-to-sheets <path> --bq-project "your-gcp-project-id"
```

**Missing `bigquery.readonly` scope:**
If BigQuery queries fail with a permissions error, the user may need to re-authenticate with the BigQuery scope:
```
BigQuery access denied. Your credentials may be missing the bigquery.readonly scope.
Re-authenticate with:

gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery.readonly"
```

**BigQuery query execution failure:**
If a Connected Sheet query fails (check `dataExecutionStatus.state == "FAILED"`), report the error to the user:
```
BigQuery query failed for BQ:{QueryID}:
Error: {errorMessage}

Possible causes:
- Permission denied: The billing project may not have access to the referenced tables
- Invalid SQL: The query syntax may have issues
- Table not found: Referenced tables may not exist or may have moved

The BQ tab has been created but contains no data. You can edit the query in the Sheets UI
or fix the SQL and re-run /uat-to-sheets.
```

**GitHub/GHE URL cannot be fetched:**
```
Could not fetch the report from GitHub. Check:
1. You have access to the repository
2. The branch and file path are correct
3. `gh auth login` (or `gh auth login --hostname <your-ghe-host>`) has been run

Alternatively, download the file and provide a local path.
```

**Markdown parsing fails:**
If the markdown structure doesn't match the expected format, ask the user:
```
The report structure doesn't match the expected UAT report format.
I found [N] detail sections but could not parse the summary table.

Would you like me to:
1. Try parsing with best effort (may miss some checks)
2. Show you what I found so you can guide me
```

**Sheets API quota error:**
```
Hit Google Sheets API rate limit. Waiting 10 seconds and retrying...
```
Retry with exponential backoff (10s, 20s, 40s) up to 3 times.

**Quota project error:**
If you see a "requires a quota project" error, ensure the `x-goog-user-project` header is included in ALL Sheets API calls. The value should be the `--quota-project` argument (or `--bq-project` if `--quota-project` was not provided).

---

## Report Format

UAT markdown reports should follow this structure for best results:

```markdown
# UAT Validation Report: [Report Name]

Generated: YYYY-MM-DD HH:MM:SS
Report ID: [slug-or-id]

## Table References
- SOURCE_TABLE: `project.dataset.source_table`
- TARGET_TABLE: `project.dataset.target_table`

## Summary

| Status | Query | Rows | Condition |
|--------|-------|------|-----------|
| PASS   | Q1: Table Availability | 5 | All tables exist |
| FAIL   | Q2: Schema Comparison | 3 | Schemas should match |

## Data Quality Checks

### Q1: Table Availability

**Description:** Verifies all required tables exist...

| table_name | status | check_passed |
|------------|--------|-------------|
| events | EXISTS | TRUE |

<details>
<summary>SQL Query</summary>

```sql
SELECT table_name, ...
FROM ...
```

</details>

### Q2: Schema Comparison

...

## Reconciliation Checks

### R1: Row Count

...
```

Key elements:
- **Query IDs** — alphanumeric prefixes (e.g., `Q1`, `R1`, `D3`). Prefix letters are derived from the report's own section structure, not a fixed mapping
- **Section headings** (e.g., `## Data Quality Checks`, `## Reconciliation Checks`) to group checks
- **Summary table** with Status, Query, Rows, Condition columns
- **Detail sections** with Description, result table, and SQL in a `<details>` block
- **Table references** listed as key-value metadata

---

## API Reference

**Create Spreadsheet:**
```
POST https://sheets.googleapis.com/v4/spreadsheets
Headers:
  Authorization: Bearer $TOKEN
  x-goog-user-project: {quota-project}
```

**Batch Update (structure: add tabs, formatting, conditional rules, addDataSource):**
```
POST https://sheets.googleapis.com/v4/spreadsheets/{id}:batchUpdate
Headers:
  Authorization: Bearer $TOKEN
  x-goog-user-project: {quota-project}
Body: {"requests": [...]}
```

**addDataSource request (for Connected Sheets BQ tabs):**
```json
{
  "addDataSource": {
    "dataSource": {
      "spec": {
        "bigQuery": {
          "projectId": "{bq-project}",
          "querySpec": {
            "rawQuery": "SELECT ... FROM ... WHERE ..."
          }
        }
      }
    }
  }
}
```
Response includes `dataSourceSheetId` — use this to rename the auto-created tab.

**Get Spreadsheet (for polling Connected Sheet execution status):**
```
GET https://sheets.googleapis.com/v4/spreadsheets/{id}?includeGridData=false
Headers:
  Authorization: Bearer $TOKEN
  x-goog-user-project: {quota-project}
```
Check `sheets[].dataSourceSheetProperties.dataExecutionStatus.state` for `RUNNING`, `SUCCEEDED`, or `FAILED`.

**Batch Update Values (data population):**
```
POST https://sheets.googleapis.com/v4/spreadsheets/{id}/values:batchUpdate
Headers:
  Authorization: Bearer $TOKEN
  x-goog-user-project: {quota-project}
Body: {"valueInputOption": "USER_ENTERED", "data": [{"range": "...", "values": [...]}]}
```

**Update Values (single range, for hyperlink formulas):**
```
PUT https://sheets.googleapis.com/v4/spreadsheets/{id}/values/{range}?valueInputOption=USER_ENTERED
Headers:
  Authorization: Bearer $TOKEN
  x-goog-user-project: {quota-project}
Body: {"values": [...]}
```
