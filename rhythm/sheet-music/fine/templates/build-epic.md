# Build It Epic Description Template

> Source: [Google Drive](https://drive.google.com/file/d/10xiUiTdvJtfrayzByv7IZwVUlt-cXocT/view)
>
> Use this template for all Build It epic descriptions in OTTR.
> Skills that create epics should populate as many fields as possible from the initiative context, HLD, and PRD.

---

## Epic Overview: What and Why
**Summary:**
*Provide a short explanation of what this epic is and why it is needed.*
*(Example: This epic enables royalty data sourcing for Music Pro to support accurate revenue calculations.)*

**The "Why" (Hypothesis):**
*We believe that by [doing this work], we will [achieve this outcome].*

## Value Proposition
**Who benefits?**
*[List squads, stakeholders, or end-users]*

**Value Delivered:**
*Articulate the specific functional or user value this epic delivers. It must be a distinct, standalone piece of value.*

### Concrete Outputs & Definition of Done
*List the tangible deliverables of this Epic and the specific criteria that define them as "Done".*

| Concrete Output | Definition of Done (Completion Criteria) |
| :--- | :--- |
| *Example: Data Ingestion Service* | *Service deployed to Prod; Unit tests >80%; Integration tests passed.* |
| *Example: Admin UI Dashboard* | *UI matches Figma specs; Accessibility audit passed; UAT signed off.* |
| *[Output Name]* | *[Criteria]* |

## Planning & Estimation
Set the following values in the dedicated Jira fields on this issue:
*   **Assignee:** [Workstream Lead](https://docs.google.com/document/d/1Sqg_KxQGE8Aoq4PI2aKDSmRBoQwWxCS7fFEPFqtQTME/edit?usp=sharing)
*   **Start Date:** Set to Target Start.
*   **Due Date:** Set to Target End.
*   **Priority:** Set to the appropriate P# (e.g. P0, P1, P2)
*   **Original Estimate:** Enter estimate of effort in **weeks** (e.g., "4w"). This is not the calendar estimate; that is reflected in the start and end dates.
*   **Delivery Stage:** Select from `Understand-It`, `Think-It`, `Build-It`. Don't use `Ship-It` or `Tweak-It` for now.
*   **Fix versions:** Select all the Release Versions that apply. (e.g. `US Direct Deals Phase 1` AND `Spring 2026 Cycle`) If none apply, create a new Release and select it here.
*   **Component:** Set to the appropriate process tower.
*   **Tags:** Add the following tags: Product Area (i.e. `PTP_MusicPublishing`), P# (e.g. `P0` or `P1`), Delivery stage (e.g. `Build-It`, `Think-It`), and add `UAT` if the epic contains a UAT ticket for stakeholders. Add `shared-epic` if multiple squads contribute. Add `RACM` if applicable.

## Traceability & Documentation
**Parent DoD:** [Link to the Parent Initiative/DoD this Epic contributes to]
**Key Documents:**
*   [Link to PRD]
*   [Link to HLD / Technical Design]
*   [Link to RFC]

## Dependencies & Risks
*   **Dependencies:** [List external squads or technical prerequisites]
*   **Initial Risks:** [List known risks regarding scope, timeline, or complexity]

---

### Standard Operating Procedures (FinE Guidelines)
**Updates:** For "In Progress" Epics, updates must be posted as comments at the end of every sprint using the format below.

**(Copy/Paste for Sprint Update Comments):**

**Sprint Summary**
- **Progress this sprint:**
    - Be objective and specific.
    - Include links to documents, meeting notes, and outcomes.
    - Mention delays explicitly with revised timelines.
- **Plans for next sprint:**
    - Specify actionable next steps with clear dates.
    - Avoid vague terms like "next sprint" or "soon."
- **Key Callouts:**
    - **Risks**: *<concise description of ongoing risks, remove this bullet if none>*
    - **Date Changes**: *<concise explanation of why dates change, remove this bullet if none>*
    - **Scope Changes**: *<concise description of any scope changes discovered this sprint, remove this bullet if none>*
    - **Others**: *<concise description of any other callouts, remove this bullet if none>*
