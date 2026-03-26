---
name: launch-checklist
description: "Generate a customized pre-launch checklist for a bet or feature — covers eng readiness, legal, privacy, data, comms, experimentation, and rollback planning"
user_invocable: true
argument-hint: "[path/to/bet or feature name]"
---

# Launch Checklist Generator

Generate a comprehensive, customized pre-launch checklist based on the bet or feature being launched.

---

## Step 1: Identify the Launch

If `$ARGUMENTS` is provided, use it as the bet directory path or feature name.

Otherwise:
1. Check the current directory for bet artifacts (`hypothesis.md`, `prd.md`, `status.md`, `problem_frame.md`)
2. If none found, check for a `domains/` directory and list available bets
3. If still ambiguous, ask the user: *"What are you launching? Provide a bet path, feature name, or brief description."*

## Step 2: Gather Context

Read any available bet artifacts to understand:
- **What** is being launched (feature scope, user impact)
- **Who** is affected (internal users, external users, partners, markets)
- **How** it's being rolled out (experiment, phased rollout, big-bang, dark launch)
- **Where** it lives (backend service, client app, web, API)

If key context is missing, ask the user up to 3 clarifying questions using AskUserQuestion. Focus on:
1. Launch type (experiment / phased rollout / full launch / internal-only)
2. User-facing or backend-only
3. Any known compliance or data concerns

## Step 3: Select Applicable Checklist Sections

Based on the context gathered, include **only the sections that apply**. Do not include sections that are clearly irrelevant (e.g., skip "Mobile Client" for a backend-only service).

### Available Sections

#### Engineering Readiness
- [ ] All code merged and deployed to staging
- [ ] Load testing completed for expected traffic
- [ ] Monitoring and alerting configured (dashboards, PagerDuty)
- [ ] Runbook created or updated for on-call
- [ ] Feature flags in place for kill-switch capability
- [ ] Database migrations applied and verified
- [ ] API versioning or backward compatibility confirmed
- [ ] Dependencies notified of launch timeline

#### Experimentation & Rollout
- [ ] Experiment configured in experimentation platform
- [ ] Control and treatment groups defined
- [ ] Success metrics and guardrail metrics identified
- [ ] Rollout percentage and ramp schedule agreed
- [ ] Holdback group defined (if applicable)
- [ ] Statistical power calculation completed

#### Data & Analytics
- [ ] Event logging implemented and validated
- [ ] Dashboard created for launch metrics
- [ ] Data pipeline confirmed for new events
- [ ] Metric definitions aligned with hypothesis
- [ ] Anomaly detection configured for key metrics

#### Privacy & Legal
- [ ] Privacy review completed (if handling new user data)
- [ ] Data processing agreement updated (if new data flows)
- [ ] Cookie/consent requirements reviewed
- [ ] GDPR/CCPA compliance verified for new data collection
- [ ] Terms of service update needed? (confirmed with legal)

#### Security
- [ ] Security review completed (if new attack surface)
- [ ] Authentication and authorization verified
- [ ] Input validation and sanitization in place
- [ ] Secrets and credentials stored securely (no hardcoded values)

#### Communications & Stakeholders
- [ ] Stakeholders briefed on launch plan and timeline
- [ ] Customer support team informed and prepared
- [ ] Internal comms sent (Slack, email, all-hands)
- [ ] External comms prepared (blog post, changelog, in-app notification)
- [ ] Partner teams notified (if cross-team dependency)

#### Rollback Plan
- [ ] Rollback procedure documented
- [ ] Feature flag kill-switch tested
- [ ] Database rollback plan confirmed (if migrations involved)
- [ ] Rollback owner and escalation path identified
- [ ] Rollback criteria defined (what triggers a rollback)

#### Mobile Client (if applicable)
- [ ] App store submission timeline confirmed
- [ ] Minimum app version requirement set
- [ ] Force-update strategy decided (if needed)
- [ ] Client-side feature flag validated on device

#### Documentation
- [ ] Internal documentation updated (Backstage, Confluence, etc.)
- [ ] API documentation updated (if public API changes)
- [ ] Architecture diagrams updated

## Step 4: Output the Checklist

Present the checklist in this format:

```
## Launch Checklist: [Feature/Bet Name]

**Launch type:** [experiment / phased rollout / full launch / internal-only]
**Target date:** [from context or "TBD"]
**Owner:** [from context or "TBD"]

---

[Include only applicable sections with checkboxes as above]

---

### Launch Confidence

Before proceeding, rate your confidence:
- [ ] 🟢 **Go** — all critical items checked, risks mitigated
- [ ] 🟡 **Conditional Go** — minor items outstanding, launch with known risks
- [ ] 🔴 **No-Go** — critical blockers remain

### Notes
[Space for any launch-specific notes or open questions]
```

## Step 5: Offer Next Steps

After presenting the checklist, ask:

> *"Would you like me to:*
> *1. Save this checklist to a file in your bet directory*
> *2. Identify which items are already done based on your artifacts*
> *3. Focus on a specific section in more detail?"*

If the user asks to save, write it to `{bet_directory}/launch-checklist.md` or `launch-checklist.md` in the current directory.
