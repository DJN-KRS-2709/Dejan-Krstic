# Pitch Deck Builder Skill

Generate a professional pitch deck for your bet following the **FinE Unified Intake format**.

## What It Does

This skill creates a Google Slides presentation from your bet's documentation files, following the standard pitch structure used for FinE intake meetings:

1. **Cover Slide** — Bet name, sponsors, overview
2. **Executive Summary** — Clear problem statement and context
3. **Sponsors & Stakeholders** — Finance sponsor, FinE sponsor, enterprise process(es)
4. **Timeline** — Member weeks and delivery schedule (if known)
5. **Impact Assessment** — Regulatory, operational, reputational, and business continuity risks
6. **Definition of Done** — Clear success criteria and acceptance conditions
7. **Evidence & Metrics** — Supporting data, research, and key metrics
8. **Dependencies & Risks** — Known blockers and cross-team dependencies

## Usage

```bash
/pitch-deck --bet-path domains/royalties/music-label-uplifts
```

Or let the skill prompt you for the bet directory:

```bash
/pitch-deck
```

**Options:**
- `--bet-path PATH` — Path to your bet directory (e.g., `domains/domain-name/bet-name`)
- `--title TITLE` — Override the bet name for the presentation title
- `--open` — Automatically open the created presentation in your browser

## How It Works

1. **Reads your bet files** — Extracts content from:
   - `problem_frame.md` — Problem statement and context
   - `hypothesis.md` — Assumptions, expected outcomes, success criteria
   - `evidence.md` — Supporting evidence, metrics, research
   - `prd.md` — Goals, non-goals, constraints
   - `status.md` — Current status, timeline, blockers

2. **Builds the narrative** — Synthesizes your documentation into a clear, compelling story

3. **Creates Google Slides** — Generates a new presentation in your Google Drive with:
   - Professional FinE-aligned template
   - All slides pre-populated with your content
   - Proper formatting and branding

4. **Saves the link** — Updates your bet's `status.md` with the presentation URL

## Before You Run

Your bet should have:
- ✅ `problem_frame.md` — Clear problem statement
- ✅ `hypothesis.md` — Testable hypothesis with success criteria
- ✅ `status.md` — Identified sponsors and current status
- Optional: `evidence.md`, `prd.md` for additional content

## Slide Structure (FinE Unified Intake Format)

| Slide | Content | Source |
|-------|---------|--------|
| 1 | **Cover** — Bet name, subtitle, sponsors | Status & hypothesis |
| 2 | **Executive Summary** — Problem statement, why it matters now | Problem frame |
| 3 | **Sponsors & Stakeholders** | Status file |
| 4 | **Timeline** — Member weeks, delivery milestones | Status & PRD |
| 5+ | **Impact Assessment** — Risks by category (regulatory, operational, etc.) | Problem frame & evidence |
| 6+ | **Definition of Done** — Success criteria | Hypothesis |
| 7+ | **Evidence & Metrics** — Data supporting the bet | Evidence file |
| 8+ | **Dependencies & Risks** — Known blockers | PRD & status |

## Example

After running:
```bash
/pitch-deck --bet-path domains/adjustments/self-serve-adjustments --open
```

You get:
- A new Google Slides presentation titled "Self-Serve Adjustments - Pitch Deck"
- All 8-10 slides populated with your bet content
- Presentation automatically opened in your browser
- Link saved to your bet's `status.md` file

## Notes

- Presentations are created in your FinE PM Drive folder
- You can customize colors, fonts, and layout after generation
- The skill respects the existing narrative in your bet files
- Use `--title` to override the deck name if needed

## Related Resources

- [FinE Pitch Example](https://docs.google.com/presentation/d/1XWzu6QM5gfQlswXkFPRRza8SH8qXvQUp1igr8hywNdE/) (Mexico tax compliance)
- [PM File System — Bet Structure](./CLAUDE.md)
- [Intake Submission Skill](/submit-intake)
