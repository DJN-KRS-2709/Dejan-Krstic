# User Story Description Template

> Source: [Google Drive](https://drive.google.com/file/d/18qaq5uv034kGfW9dAI7Tc0_G5knpEiYq/view)
>
> Use this template for all story and task descriptions in Jira (OTTR and FTI).
> Skills that create stories should populate as many fields as possible from the epic context, HLD, and PRD.

---

## Story Summary (tl;dr)
**As a** [role/persona],
**I want** [feature/action],
**So that** [benefit/value].

## Acceptance Criteria (Confirmation)
*Specific conditions that must be met for this story to be marked "Done".*

*   [ ] **Scenario 1:** Given [context], When [action], Then [result].
*   [ ] **Scenario 2:** Handle error state if [condition] occurs.
*   [ ] **UI/UX:** Implementation matches linked designs.
*   [ ] **NFR:** Meets performance/security standards (e.g., load time < 2s).

## Implementation Details & Context
*   **Design Links:** [Figma/Mockups]
*   **Tech Notes:**
    *   *API endpoints to modify:*
    *   *DB Schema changes:*
*   **Dependencies:** [Link to blocking issues or dependent stories]

## Planning & Metadata
Set the following values in the dedicated Jira fields:
*   **Story Points:** Estimate effort (FinE guideline: Stories should be 1-10 days of work).
*   **Parent:** Assign to the appropriate epic. All unplanned work gets assigned to the current KTLO epic and tagged as BAU or KTLO.
*   **Start Date:** Assign a target start date to the ticket. Should match when the story is first moved into `In Progress`.
*   **Due Date:** Assign a target end date for the ticket.
*   **Tags:** Add the `UAT` tag if this is a UAT task. All unplanned work needs a tag for either `BAU` or `KTLO`.
