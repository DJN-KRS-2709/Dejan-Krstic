<!--
  Template source: [Framework] - Test Plan/UAT Formats
  Google Sheet: https://docs.google.com/spreadsheets/d/1h47QNVMgJHiORuJZBK2rbTDWGrA5RhJfF93dAefzWbs
  Real example: US Direct Deals Delta Calculation UAT
  Google Sheet: https://docs.google.com/spreadsheets/d/1cuuMHuz6yQycAc8N5BWwKXoorITwTeCxbcnyONn9eAo
  Last synced: 2026-03-21
  Sync policy: This template is derived from the FinE UAT Framework spreadsheet.
               The authoritative version is the Google Sheet above. Review periodically for changes.

  NOTE: UATs are created as Google Sheets, not markdown docs. This template documents
  the expected structure and guidance so skills can reference it. Use the Google Sheet
  template above as the starting point for new UATs.
-->

# UAT (User Acceptance Testing) Template

This template defines the structure and expectations for Finance UATs. UATs are created as **Google Sheets** (not Google Docs or markdown) because they contain SQL query outputs, data comparisons, and tabular validation evidence.

**Source template:** [Framework - Test Plan/UAT Formats](https://docs.google.com/spreadsheets/d/1h47QNVMgJHiORuJZBK2rbTDWGrA5RhJfF93dAefzWbs)
**Real example:** [US Direct Deals Delta Calculation UAT](https://docs.google.com/spreadsheets/d/1cuuMHuz6yQycAc8N5BWwKXoorITwTeCxbcnyONn9eAo)

---

## SDLC Gate Checklist

Before creating a UAT, verify the implementation has passed through each SDLC phase:

| # | Phase | Gate check |
|---|-------|-----------|
| 1 | **Understand It** | Has the PRD been created by Product? (Required for all P0s, P1s, and P2s > 4MW) |
| 2 | **Gate 1** | Has the gate check been completed to move into Think It? (Critical for P2s — intake process with Finance. P0/P1 bets may defer to Gate 2.) |
| 3 | **Think It** | Have the RFC and HLD been drafted, signed off internally, and linked in the PRD? |
| 4 | **HLD shared** | Has the HLD been shared with stakeholders via Jira comment + Slack ping in the project channel? |
| 5 | **Gate 2** | Has the gate check been completed to confirm alignment on the solution before Build It? |
| 6 | **Test Plan** | Has a Test Plan been drafted, added to the PRD, shared via Jira comment + Slack ping, and signed off by stakeholders? |
| 7 | **UAT** | Has a UAT been created, shared via Jira comment + Slack ping, and shared with stakeholders? |

---

## Test Plan Structure

The test plan is the **first tab** of the UAT spreadsheet. It defines what will be tested before the actual validation work begins.

### Planning questions

Think through these questions before writing test plan items:

1. What will this UAT cover? (Input Data Changes, Calculator Changes, UI Changes, Reporting Changes, MEC Check Changes) — each category should have its own section
2. How many month(s) of data are we expected to generate?
3. How many payable and/or reporting run(s) are we expected to generate?
4. Which licensor(s) should we include in test calculation runs, and how should their contracts be configured?
5. For which licensor(s) should we be generating test files?
6. How many month(s) of impacted MEC checks should we generate test outputs for?
7. Does this implementation impact any key controls (MEC Checks or otherwise)? Have we run this by FinE Risks & Controls?
8. Could this change impact ingestion? Should you run a test NS ingestion to make sure there's no impact on the MEC process?
9. **Scenario testing** — clearly define the different scenarios to cover. Licensor/contract configurations, periods, reports, booking types (MEC/QEC). Scenarios should be suggested by FinE but formally signed off by TA/CA.

### Test plan item table

| # | UAT Category | Test Subject | UAT Item | Preparer | Approver | Status | Data Needed | Data Endpoints | Artifacts Needed | Artifacts Produced |
|---|-------------|-------------|----------|----------|----------|--------|-------------|---------------|-----------------|-------------------|
| 01 | Input Data | [Dataset name] | [What to validate] | [Squad] | [TA/CA] | Not Started | [Description of data needed] | [BQ table names] | [Prior artifacts to reference] | [UAT tabs produced] |
| 02 | Calculator | [Calculation name] | [What to validate] | | | Not Started | [Payable runs, scenarios] | | | |
| 03 | Reporting | [Report name] | [What to validate] | | | Not Started | [Cuttlefish datasets] | | | |
| 04 | MEC Checks | [Control name] | [What to validate] | | | Not Started | [Test files for MEC checks] | | | |
| 05 | Monitoring | [Counter/alert name] | [What to validate] | | | Not Started | | | | |
| 06 | Golden Tests | [Test name] | [What to validate] | | | Not Started | | | | |

**Status values:** Not Started, In Progress, Ready For Review, UAT Approved

**Sections:** Test plans often have multiple sections:
- **Initial Testing** — core validation items
- **Planned Future Testing** — items deferred to a later phase
- **Phase 2** — items dependent on Phase 2 delivery

### Test plan links

Include at the top of the test plan tab:

- Link to PRD
- Link to RFC/HLD
- FinE PoC(s): [names]
- Finance PoC(s): [names]

---

## UAT Summary Tab

Every UAT sheet **must** include a Summary tab with:

### Approval status

| Approver Name | Role | Approval Date | Approval Status | Comments |
|--------------|------|--------------|----------------|----------|
| [Name] | [TA/CA/Finance] | [Date] | [UAT Approved / Pending / Rejected] | [Any relevant comments] |

### Summary fields

| Field | Content |
|-------|---------|
| **Links** | Links to PRD (which should include the HLD and Test Plan), UAT Jira ticket |
| **Purpose** | What is the overall purpose of this UAT; what changes does this UAT cover specifically? |
| **Scope** | Month(s) tested, calculation and reporting run(s) used, dataset(s) tested (names and BQ partitions) |
| **Validations** | Summary of all validations performed within each tab and why |
| **Summary of Findings** | Summary of results from each validation test. Include visualizations if helpful. **Break key callouts into separate cells** so reviewers can comment on individual items. |
| **Explanation of Diffs** | If applicable, summarize differences uncovered, why they exist, and why they are acceptable. **Break into separate cells** for reviewer comments. |
| **List of Tables Used** | All data endpoints used in the validations |

---

## UAT Validation Tab Structure

Each validation tab follows this format:

### Scenario header (if applicable)

| Field | Content |
|-------|---------|
| **Scenario** | Scenario number (aligned with test plan) |
| **Scenario description** | Configuration used, periods, links to Bloom/Royalties Studio, tables used |

### Test structure

| Field | Content |
|-------|---------|
| **Test** | Name of test |
| **Test Description** | Brief description of what the test covers |
| **Expected** | Field names and expected values — validated by TA/RoyOps before UAT starts to ensure comprehensive coverage and aligned expectations |
| **Validation** | How the validation is performed. Summary of the query for non-technical stakeholders, including relevant filters. |
| **Notes** | Additional callouts about the outputs (if applicable) |

Then: **[QUERY OUTPUTS HERE]** — the actual SQL results proving the validation.

---

## UAT Type-Specific Guidance

### Data Sourcing UATs

1. **Summary tab** — outline all relevant changes:
   - New upstream data endpoints replacing existing ones? Names and test partitions?
   - New fields added to existing dataset? Field names and upstream source?
   - Do values in new fields match upstream? Any downstream dataset impacts?

2. **Prove upstream-only changes** — show that strictly the upstream dataset is changing and no downstream values are unexpectedly changing.
   - Don't use "No Results" as proof — create output showing X matches and Y diffs explicitly.

3. **Prove new fields are accurate** — show values match the upstream source.

4. **Prove no unexpected changes** — provide outputs showing relevant datasets are unimpacted, or explain expected differences.

5. **Run multiple months** if requested by stakeholders.

### Calculator UATs

1. **Summary tab** — outline changes and payable runs used:
   - What changed in the calculation?
   - Links to payable calculation runs in Royalties Studio
   - Calculator datasets used
   - Any unexpected results and why they make sense

2. **Recreate arithmetic in SQL** — take calculator inputs, apply the formula in SQL, prove outputs match.

3. **Prove math in the spreadsheet** — export calculator inputs for a few rows, apply formulas in Google Sheets to verify arithmetic works.

### Reporting UATs

1. **Summary tab** — outline changes and payable/reporting runs:
   - What changed in reporting?
   - Links to payable runs and reporting runs in Royalties Studio
   - Where test reporting outputs are stored
   - Which calculator datasets are upstreams of Cuttlefish datasets

2. **Prove Cuttlefish matches calculator** — show relevant fields/values from calculator and Cuttlefish datasets tie.

3. **Provide test files** — paste example test file (or excerpt) for Royalty Ops to verify formatting.

### MEC Checks / Controls

- If there's a new data source or changes to existing controls, document and communicate with FinE Risk team.
- Provide documentation of controls conversations as part of UAT handover.
- If applicable, provide test outputs of updated controls for Finance review.

---

## Monitoring & Alerting Tab

For pipeline/calculator UATs, include a monitoring tab documenting counters and alerting rules:

| Counter | Description | Value | Alerting |
|---------|-------------|-------|----------|
| [CounterName] | [What it measures] | [Value from test run] | [Alert condition, e.g., "pipeline fails if X != Y"] |

Include values from both the current UAT run and any prior baseline run for comparison.

> **Real example:** The Delta Calculation UAT tracked 15+ counters from the Pocket Calculator Extract and Delta Calculation pipelines, including record counts at each stage, with alerting rules like "pipeline will fail if InputBooked - DroppedBooked != OutputCalculationFacts."

---

## Golden Tests

For calculator/pipeline UATs, include golden tests — deterministic test cases with known inputs and expected outputs that exercise specific edge cases:

| Golden test | What it validates |
|-------------|------------------|
| Basic calculation | Happy-path delta calculation |
| Multi-period multi-licensor | Calculation across periods and licensors |
| Aggregated records (single) | Records aggregated to single top publisher per track |
| Aggregated records (multiple) | Records with multiple top publishers per track |
| Negative royalty pool | Behavior when pool is negative |
| Negative delta | Outputs when calculated delta is negative |
| Long tail fallback | Unmapped licensors use long-tail placeholder pool |
| Bookable filtering | Only configured licensor/periods included, negative aggregated amounts excluded |
| Cutoff date | Only response records before cutoff date used as inputs |

Golden tests have **Inputs** (synthetic data) and **Expected Outputs** defined in the spreadsheet, allowing automated regression testing.

---

## Helpful SQL Patterns

### Regression testing: field-by-field comparison

Compare a UAT table to a baseline table, field by field:

```sql
WITH baseline AS (
  SELECT * EXCEPT(field_that_needs_adjustment),
  -- adjustments: CAST to correct type(s), align date format
  FROM baseline_table
),
uat AS (
  SELECT * FROM uat_table
)
SELECT
  COUNT(*) count,
  -- Standard field comparison:
  IF(FARM_FINGERPRINT(FORMAT("%T", uat.field_1)) <>
     FARM_FINGERPRINT(FORMAT("%T", baseline.field_1)), 'Diff', 'Match') field_1,
  -- For type mismatches: CAST first
  IF(FARM_FINGERPRINT(FORMAT("%T", CAST(uat.field_2 AS STRING))) <>
     FARM_FINGERPRINT(FORMAT("%T", baseline.field_2)), 'Diff', 'Match') field_2,
  -- For nullable fields: COALESCE
  IF(FARM_FINGERPRINT(FORMAT("%T", COALESCE(uat.field_3, 'NULL'))) <>
     FARM_FINGERPRINT(FORMAT("%T", COALESCE(baseline.field_3, 'NULL'))), 'Diff', 'Match') field_3,
  -- For numeric fields with rounding:
  SUM(ABS(COALESCE(uat.amount_1, 0) - COALESCE(baseline.amount_1, 0))) amount_1
FROM baseline
FULL OUTER JOIN uat ON [join_key]
GROUP BY ALL
ORDER BY 1
```

**Always include expected record counts** to validate the join isn't expanding data:

```sql
SELECT 'baseline' AS table, COUNT(*) AS reference_count FROM baseline
UNION ALL
SELECT 'uat', COUNT(*) FROM uat
```

### Regression testing: full table JSON comparison

For full-row comparison using JSON serialization:

```sql
WITH new_table AS (
  SELECT id, TO_JSON_STRING(t, true) AS json_output
  FROM (SELECT * EXCEPT(field_to_exclude), field_to_reorder FROM TABLE ORDER BY id) AS t
),
old_table AS (
  SELECT id, TO_JSON_STRING(t, true) AS json_output
  FROM (SELECT * EXCEPT(field_to_reorder), field_to_reorder FROM TABLE ORDER BY id) AS t
)
SELECT
  COALESCE(n.id, o.id) AS id,
  CASE
    WHEN n.id IS NULL THEN 'missing_in_new'
    WHEN o.id IS NULL THEN 'new_row_only'
    WHEN n.json_output != o.json_output THEN 'mismatch'
    ELSE 'match'
  END AS comparison_result,
  n.json_output AS new_json,
  o.json_output AS old_json
FROM new_table n
FULL OUTER JOIN old_table o USING (id)
```

---

## Key principles

- **Don't use "No Results" as proof** — always show explicit match/diff counts so reviewers can verify completeness.
- **Break key callouts into separate cells** — reviewers need to comment on individual findings, not a wall of text.
- **Expected values must be pre-validated** — TA/RoyOps should confirm expected values before the UAT starts, not after.
- **Each UAT category gets its own section** — don't mix Data Sourcing validations with Calculator validations in the same tab.
- **Share via Jira comment + Slack ping** — the UAT must be shared through the appropriate channels (comment on Jira ticket with Slack ping in the project channel).
