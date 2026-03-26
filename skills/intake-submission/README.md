# Intake Submission Skill

Submit a bet to the **FinE/Finance: Monthly Intake Review** document for discussion at the next intake meeting.

## What It Does

This skill adds a row to the New Intake table in the [FinE/Finance: Monthly Intake Review document](https://docs.google.com/document/d/1ZptcAu79FXTDUM1RJMgTRnxFlDEZE8HGmlM-_uVPRrY/edit).

The intake meeting brings together L2 sponsors to align on:
- Purpose and scope of new initiatives
- Finance cross-team dependencies
- Strategic priority and hard deadlines
- Required participants

## Usage

```bash
/submit-intake
```

The skill will prompt you for:

1. **Finance Area** (required) — The FinE area your bet belongs to (e.g., "Royalties", "Tax", "RTR")
2. **Finance Sponsor** (required) — The finance executive sponsoring this work (email)
3. **Tech Sponsor** — The engineering lead sponsoring this work (email)
4. **Bet Name** (required) — Clear, concise name of your bet
5. **Pitch Link** — Link to your bet's PRD, Groove initiative, or other documentation

## Before You Submit

- Your bet should have a **problem frame** and **hypothesis** written
- You should have identified your **Finance Sponsor** — ask your FinE lead if unsure
- The document is visible to all stakeholders, so information should be polished
- **Do not submit without confirming key details** — you'll be prompted to review before adding the row

## How It Works

1. **Finds the next intake meeting** — Scans the document for the next scheduled intake table (by date heading like "## Mar 9, 2026")
2. **Checks for past tables** — Will not add rows to intake meetings that have already occurred
3. **Alerts if missing** — If no table exists for the next meeting yet, alerts you and suggests contacting your FinE lead
4. **Collects your bet info** — Gathers area, sponsors, bet name, and pitch link
5. **Confirms before submitting** — Shows you all details for final review before adding the row

## Important Notes

- Each monthly intake meeting has its own **dated table** (e.g., "## Feb 9, 2026", "## Mar 9, 2026")
- This skill will **only add rows to current/future intake meetings**, not past ones
- The intake document is shared with L2 sponsors and leadership
- After submission, your Finance Sponsor will use this data to prepare for the intake discussion
- You can update the row manually afterward if details change

## Related Resources

- [FinE Intake Document](https://docs.google.com/document/d/1ZptcAu79FXTDUM1RJMgTRnxFlDEZE8HGmlM-_uVPRrY/edit)
- [PM File System — Bet Structure](./CLAUDE.md)
- [FinE Domain Scaffolding](./docs/domain-scaffolding.md)
