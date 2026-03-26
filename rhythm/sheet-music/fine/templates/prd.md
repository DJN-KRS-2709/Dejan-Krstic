<!--
  Template source: FinE PRD Template
  Google Doc: https://docs.google.com/document/d/1ZPD96pimAWH01GOXqy87GAV3ZYLvNyyPOtGGFmWD-yM/edit?tab=t.0
  Last synced: 2026-03-19
  Sync policy: Before using this template, skills should check if the upstream Google Doc
               has been modified since `last_synced`. If it has, flag to the user that the
               template may need updating. See sheet-music/fine/sdlc-reference.md for the artifact model.
-->

# 🎯 Summarize It

# [Initiative/DoD/Deliverable name]

> This can be at the Initiative level for single objective projects; at the DoD level for independent work streams within an initiative, or even at the Enterprise Process level if you don't have agency over the initiative or DoD.

---

**Created**: YYYY-MM-DD
**Last edited:** YYYY-MM-DD
**Link to FTI JIRA**: [FTI-XXX](https://spotify.atlassian.net/browse/FTI-XXX)
**Development Stage: Understand-It**

# Summary

Craft a short, powerful and clear statement that will help you align anyone who reads this on the goal and **desired outcome**.

# Stakeholders

| Role | People |
| :---- | :---- |
| **R**esponsible | \<FinE Eng\> \<FinE Product\> \<Finance GPO Delegate\> |
| **A**ccountable | \<Finance Sponsor\> \<FinE Sponsor\> |
| **C**onsulted | \<FinE SEM(s)\> \<FinE squad leads\> \<FinE EAs PAs Tech reps\> \<Impacted/Dependency squad leads\> \<Finance/FiDi reps\> |
| **I**nformed | \<Business Stakeholder(s)\> \<PgM/Bet PoC\> \<FinPop PgM\> |

---

# 🤔 Understand It

**Status: Open until \<date\>**

Determine if there's a problem worth solving, and frame it in a way that invites exploration. The goal is that stakeholders are aligned on what success looks like.

## Problem/Opportunity

Summary of the problem: It should consist of user, business, and technical problems. Talk about the opportunities related to these problems.

## Current State

Context about the initiative. User Journey to describe.

## Goals/Benefits

What is our desired outcome? What will the future look like when we launch this? How do we know they are successful?

## Metrics evaluation

Make sure you have an easy way to track your key metrics in order to understand what potential changes need to be made in order to continuously improve the product.

## Effort Estimate

What is the assumed effort based on the Understand-It Phase.

| Team | HL Description of Work Required | T-shirt size Effort Estimate |
| :---- | :---- | :---- |
| | | |

## Open questions — Understand It

| # | Question | Answer | POC | ETA for input |
| :---- | :---- | :---- | :---- | :---- |
| | | | | |

## Gate 1 Check

- [ ] RACI is complete and agreed upon by all sponsors
- [ ] Is this a Problem/Opportunity worth exploring
- [ ] Has clear goals and timelines
- [ ] FinE Eng Lead is assigned (responsible for several tasks during Think-It)
- [ ] Async review with RACI (above) for awareness

---

# 🔬 Think It

**Status: Open until \<date\>**

Research, develop and test hypotheses for potential solutions that meet success criteria. The goal is to have a solution chosen and a data-informed set of jobs to be done.

## Requirements

> Link to requirements spreadsheet OR list below.
> [Requirements template](https://docs.google.com/spreadsheets/d/1nahzXXDWYWnOYoxk-O_thiaYyj945A9Qv8bTD922bck/edit?gid=0#gid=0)

**Functional Requirements**
List of user interactions/interfaces, system behaviour, and any external integrations. Specific financial treatment, representation, or reporting needs. Compliance, regulatory & legal needs.

**Non-Functional Requirements**
Quality standards like performance, security, usability, timeliness, etc.

**Scope**
What is included, and more importantly, what is excluded from this project.

**Timing**
Key dependencies, milestones & release dates.

**Acceptance Criteria**

- **Outcome | Criteria**
  1 or more success criteria for each functional requirement
- **General Criteria**
  Success criteria for non-functional requirements

## High Level Design (HLD)

> Link to [HLD](./hld.md) or list below.
> [HLD Template](https://docs.google.com/document/d/1vk0FvGiOzL34uilBUPPaivrHDZFicVa0lNRXqP8-8FA/edit?tab=t.0#heading=h.8r9bpbo0iusx)

- What is the proposed solution?
- A brief description of the solution/approach, supported by system diagrams.
- Key changes
- Dependencies
- Impact
- Phases/Milestones
- Cost/Effort estimates
- Risks & Control impact (reviewed by RaaS rep)

Good to have:
- Data interfaces
- Money flow diagrams
- User Journey before and after
- Assumptions
- Specifics about what is not in scope

## Effort Estimate

What is the assumed effort based on the Think It Phase.

| Team | HL Description of Work Required | Member Week Effort Estimate |
| :---- | :---- | :---- |
| | | |

## High Level Timeline

> Insert Timeline link OR list below.

- Development and Integration: \<dates\>
- Testing and Quality Assurance: \<dates\>
- Launch: \<dates\>

## FinE Capability Map (if applicable)

What Enterprise Process does this initiative relate to? Fill out a scoping table based on which enterprise process is relevant to your initiative in [GLUE](https://www.appsheet.com/start/b67d6322-a7cf-48a4-8c66-939f87ee08c2?platform=desktop).

What are the system capabilities required to execute this initiative E2E? Do we have any [existing capabilities](https://docs.google.com/spreadsheets/d/1eVIO5tcvYSyDgtn2g8SvUjhWS-d6oULciyQadQKtayc/edit?gid=1185756575#gid=1185756575) that fulfill the need or can be modified to solve the problem?

## ROI & TCO

Based on the benefit and the effort, what is the return on investment for this initiative based on the Think-It analysis. Also what are there any Total Cost of Ownership considerations either quantifiable (e.g. ongoing Vendor/maintenance costs) or qualitative (e.g. this will add a dependency on another team into our development process and increase our speed to deploy new features).

## Resourcing & Priority

Review resourcing needs & timings from all dependencies. Include [re]prioritization in discussions with contributing squads & dependency (up|down stream) teams.

## Stakeholder Signoff

Review the Requirements, Acceptance Criteria and HLD with stakeholders for alignment before moving to build.

| Stakeholder | Name | Comments |
| :---- | :---- | :---- |
| Finance GPO/Delegate | | |
| FinE Director/SEM(s) | | |
| FinE EAs PAs Tech reps | | |
| \<Other\> | | |

## Open questions — Think It

| # | Question | Answer | Owner | Raiser | ETA for input |
| :---- | :---- | :---- | :---- | :---- | :---- |
| | | | | | |

## Gate 2 Check

- [ ] [Risk] Review HLD with RaaS for Risk Assessment & Control impact
- [ ] [Tech] Review of HLD with FinE Eng, FinE EA/PA & FinE Leads
- [ ] [Stakeholder] Review Product Requirements, AC & HLD plan with Business & Finance Stakeholders for alignment/sign-off

---

# 📠 Build It

**Status: Open until \<date\>**

Work toward creating a solution that fulfills the key jobs to be done. The goal is to have a solution that can be given to users.

## Execution Plan

Align on timelines, milestones & get resourcing commitments from all contributing squads. Create a more detailed milestone-based execution timeline.

> Insert Execution Plan doc link OR paste below.

## Delivery Breakdown

Breakdown the execution plan into milestone-based Epics & stories/tasks in JIRA (guidance in [FinE SDLC Central Guidance](https://docs.google.com/document/d/1a6Vlukg2cfGH7GbXzhq-5UBGZZssLsUMg3qPqxFpXKM/edit)).
Add dependencies, start/end dates & assign owner(s). Include considerations for additional discovery, testing (internal/UAT) and rollout.

> Add link(s) to JIRA DoDs/Epics & a 1-liner describing each.

## [Optional] RACM (Risk and Controls Matrix)

This is required for high risk and/or financially material projects esp those with control impact, and will be recommended by a RaaS rep.

> Insert RACM link.

## Test Plan

> Link to [Test Plan](./test-plan.md) OR list below.

Create a test plan that maps the outputs of each deliverable/milestone against the Acceptance Criteria, inclusive of the expectations on each contributing squad & stakeholders. This should cover:

1. Testing Timeline
2. Test environment & assumptions
3. Test targets — User workflows, UIs, Endpoints, Reports, etc
4. Test artifacts — format, granularity, variance thresholds & explanations
5. Scope of tests (positive/negative tests) that map back to the Acceptance Criteria
6. Roles & Responsibilities of each contributing squad & downstream consumers (Internal QA) and Stakeholders (for review or UAT if applicable)

## Launch & Support Plan

Create a Launch & Support plan documenting:

1. Launch Date
2. Coordinated dependencies (if any)
3. Pre|Post Launch checklist
4. Support/Monitoring plan (active/passive/escalations)
5. Rollback threshold & process

> Insert Launch & Support Plan link OR list below.

## Go/No-go

Create a Go/No-go checklist that contains all pre-requisites for launch & sign-off on sections for each Acceptance criteria item, Controls readiness, Launch & Support readiness.

> Insert Go/No-Go doc link OR list criteria below OR signoff on UAT ticket.

## Gate Check — Build It

- [ ] Review test outcomes (mapped back to AC doc) with team & internal stakeholders
- [ ] Go/No-go sign off from all contributing & dependency teams & stakeholders (Finance/Business if applicable)

---

# 🚀 Ship It

**Status: Open until \<date\>**

Give the solution to users, measure its effectiveness, and determine why it performed how it did. The goal is to learn.

## Launch Checklist

Coordinate & document state of each action item on the launch checklist & validate success/failure.

## Monitoring/Support

Ensure appropriate proactive monitoring & customer support mechanisms are kicked off during and post launch.

## Documentation

Update any system, user, or technical documentation repos.

## Release Notes

Make sure to cover the new features, enhancements, bug fixes, and any significant changes introduced in the latest software release.

## Feedback Collection

Focus on gathering insights about user experiences, pain points, feature preferences, and any issues they may have encountered to inform continuous improvement.

## Post-launch Evaluation

Pay attention to user engagement metrics, performance analytics, with the goal to compare the anticipated outcome with the actual results.

## Gate Check — Ship It

- [ ] Internal & Stakeholder comms on final status of launch

---

# 📝 Tweak It

**Status: Open until \<date\>**

Revise, refine, and rethink to produce better results. The goal is an updated version of the solution, or a revisitation of the problem.

## Improvement Requests

Create a new PRD using this template and link your current one as a reference point.

## Metrics evaluation

Make sure you have an easy way to track your key metrics in order to understand what potential changes need to be made in order to continuously improve the product.

---

# 📚 Appendix

Please add all documents you feel will be valuable to any user of this document.

> Reference examples from FinE:
> - [Capacity & Estimation guidance](https://docs.google.com/document/d/18ntwQ6Irrl76n1cDBovyVdhJyKsUEjPTaWyMgUOzk1I/edit?tab=t.0#heading=h.489jzschhyn0)
> - [PRD example: Content Buying on SAM](https://docs.google.com/document/d/1fLAudgZsZ5wbVS3-YgcEdjPDyAvThIuZeAE5qSmF_Gw/edit?tab=t.0)
> - [HLD example: Lyrics Royalties](https://docs.google.com/document/d/1xFWd8HCYiGE4mmHcJxyd3rQq3rUWnYuETwoTh2o7g8Y/edit?tab=t.0#heading=h.8r9bpbo0iusx)
> - [HLD example: Per User Revenue and Cost Sourcing](https://docs.google.com/document/d/1mfMytexSRpITcSy-a_SSQgZtYlER3DofoVwyoiJLQRw/edit?tab=t.0#heading=h.8r9bpbo0iusx)
> - [Test Plan example: RASP](https://docs.google.com/document/d/1Tz1vAZ3SpF7iG23FMdZCn6qSJsCvmPo5z-Z_XJt55No/edit?tab=t.0#heading=h.3pu9xbb00ubz)
> - [Go/No-Go example: RASP](https://docs.google.com/document/d/10VlOdcbqq1EbiJS6tQJHcWNQ_pYXb_FHfxwzS3__25Y/edit?tab=t.0#heading=h.k2vocvi7k585)
