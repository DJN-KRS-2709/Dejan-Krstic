<!--
  Template source: FinE SDLC Guidance — Test Plan requirements (no standalone Google Doc template)
  Derived from: Build It step 3 in SDLC Guidance V1 and PRD Template test plan section
  Last synced: 2026-03-19
  Sync policy: This template is derived from SDLC guidance, not a standalone Google Doc.
               Review against the SDLC Guidance doc periodically for changes.
-->

# Test Plan: [Initiative Title]

> **PRD:** [Link to PRD](./prd.md)
> **HLD:** [Link to HLD](./hld.md)
> **Author:** [EM / Engineer name]
> **Last updated:** YYYY-MM-DD
> **Status:** [Draft / In Review / Active / Complete]

---

## Scope

What is being tested and what is out of scope.

**In scope:**
- [Feature / component 1]

**Out of scope:**
- [Item excluded and why]

---

## Acceptance Criteria → Test Mapping

| AC ID | Acceptance Criteria | Test Type | Test Description | Status |
|-------|-------------------|-----------|-----------------|--------|
| FR-01 | [From PRD] | Unit / Integration / E2E / UAT | | |

---

## Test Types

### Unit Tests

- **Owner:** Engineers
- **Framework:** [e.g., ScalaTest, pytest]
- **Coverage target:** [e.g., critical paths]

### Integration Tests

- **Owner:** Engineers
- **Environment:** [Test environment details]
- **Data needs:** [Test data requirements]

### End-to-End Tests

- **Owner:** Engineers
- **Environment:** [Test environment details]
- **Data needs:** [Test data requirements]

### Regression Tests

- **Owner:** Engineers
- **Scope:** [What existing functionality to validate]

### UAT (User Acceptance Testing)

- **Owner:** [Finance stakeholder name(s)]
- **FinE support:** [Engineer name(s)] — [estimated MW for support]
- **Scope:** [What Finance will validate]
- **Data needs:** [Test data requirements]
- **Timeline:** [Start date → End date]
- **Sign-off criteria:** [What constitutes UAT pass]
- **UAT spreadsheet:** [Link to Google Sheet — created from UAT template]

> Note: Finance UAT time is coordinated but not counted in FinE MW estimates. Tag UAT stories with `UAT` label.
>
> **UAT structure:** UATs are created as **Google Sheets** (not Google Docs or markdown) because they contain SQL query outputs, data comparisons, and tabular validation evidence. See `sheet-music/fine/templates/uat.md` for the full UAT structure including test plan tab, summary tab, validation tabs, golden tests, and SQL patterns. Use the [Framework - Test Plan/UAT Formats](https://docs.google.com/spreadsheets/d/1h47QNVMgJHiORuJZBK2rbTDWGrA5RhJfF93dAefzWbs) Google Sheet as the starting template.

---

## Test Environments

| Environment | Purpose | Access | Data |
|-------------|---------|--------|------|
| | | | |

---

## Timeline & Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| Test plan approved | | | |
| Unit/integration tests complete | | | |
| E2E tests complete | | | |
| UAT start | | | |
| UAT sign-off | | | |

---

## Test Artifacts

| Artifact | Format | Location | Owner |
|----------|--------|----------|-------|
| Test results | | | |
| UAT evidence | | | |
| Variance analysis | | | |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| | | |
