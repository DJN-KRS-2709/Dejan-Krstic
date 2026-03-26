# Scaffold Skill — Rehearsal Notes

> **This file is a companion to `SKILL.md`.** It contains lessons learned from 4 rehearsal cycles across 3 real skill builds (record-session, review-recording, engineer-impact-mirror) and 1 fresh-agent A/B test. Read relevant sections when improving the new-skill process itself.

## Why not auto-generate the full skill?

The scaffold creates structure, not logic. The skill's actual steps, MCP calls, and classification tables require domain knowledge that only the skill author has. The scaffold eliminates boilerplate so the author focuses on the interesting parts.

## Trigger phrase quality matters

Poor triggers cause skills to fire on the wrong prompt or not fire when they should. Include both formal and informal phrasings. After the first few uses, review whether the skill is being triggered correctly and adjust.

## Skill location must be asked, not assumed (cycle 1, Mar 2026)

When building record-session, the master session placed it in `skills/` (universal) instead of `plugins/rehearsal-room/` (methodology). A temporary training skill doesn't belong with universal skills. The new-skill process should explicitly ask: "Where does this skill live?" with guidance:
- `skills/` for permanent skills any team would use
- `plugins/rehearsal-room/` for methodology skills (improving, saving, auditing)
- Consider lifespan: temporary skills default to the plugin, permanent to universal

This is an unauthorized delegation violation: the AI decided the location was "obvious" without asking.

## Fresh-session A/B test revealed creative gap (cycle 1, Mar 2026)

Two fresh agents built record-session and review-recording from the same inputs using the new-skill process. Compared to the master session's versions:

**What fresh sessions got right (~85%):** Structure, conventions, frontmatter, Decision authority, checkpoint mechanism, CORRECTION tagging, reviewed-status tracking, all required sections.

**What fresh sessions missed (~15%):** Narrative layer (documentary crew concept), root-cause depth in deduplication, connections to other skills and migration paths, systemic thinking about how the skill fits the broader methodology.

**What fresh sessions did BETTER (steal these):**
1. `action` parameter in agent input contract for agent-friendliness
2. Explicit "Not for regular usage-mode sessions" in When to run section
3. Handle zero-corrections case (mark reviewed with note instead of silently skipping)
4. Dry-run mode for review-recording (preview corrections before committing to apply)

## Decision authority is now a required section (cycle 1)

CLAUDE.md authoring rules require a Decision authority section. The template in Step 3 includes this. Both fresh agents included it because they read CLAUDE.md.

## The output template is a contract

Once other skills depend on this skill's output format, changing it is a breaking change. Design the output format carefully in the scaffold phase.

## Prompting for patterns produces better v1s (cycle 1)

The original scaffold asked "what's the core logic?" but didn't prompt for specific patterns (filtering, calculation, cross-referencing). Prompting for these patterns explicitly produces a more complete first version.

## Edge case seeding vs rehearsal discovery (cycle 1)

Obvious edge cases (missing data, partial matches, timezone issues) waste a rehearsal cycle if they're predictable. Seed the obvious ones; let rehearsal discover the subtle ones.

## Dry-run behavior should be a scaffold default (cycle 1)

Every skill supports dry-run mode. Adding it as a scaffold default means every new skill handles it from v1.

## "Analyze before designing" is the highest-leverage step (cycle 2, from review-pr)

Building review-pr, the initial design assumed all PRs need the same treatment. Looking at 80+ real PRs revealed 5 distinct quality tiers that each need different handling. Step 0 front-loads this analysis.

## "Validate design against data" catches the biggest mistakes early (cycle 2, from review-pr)

The user asked "how does your example match the real world data?" after seeing the initial output. This single question revealed: the format didn't match reality, Slack was a missing data source, and different PR types needed different treatment. Step 2.5 formalizes this.

## Multi-mode skills need early identification (cycle 2, from review-pr)

review-pr has 3 modes that share data gathering but diverge on output. Asking "does this skill have different modes?" early prevents architectural rework.

## Input classification drives per-type behavior (cycle 2, from review-pr)

The 5-era classification is the core of review-pr's design. Asking "are there different types of inputs?" in Step 1 surfaces this before building.

## Subagent architecture emerges from context pressure (cycle 2, from review-pr)

review-pr uses a subagent for code review because holding the full diff + Jira context + Slack threads in one context is impractical. Asking "should part of this be delegated?" surfaces this earlier.

## Data sources are discovered, not planned (cycle 2, from review-pr)

review-pr was designed with Jira + GHE. Slack, PR comments, and `.claude/plans/` all emerged during testing. The initial MCP list is always incomplete.

## Simulated rehearsal vs real-world building: 40% overlap (cycle 3, from engineer-impact-mirror)

Simulation found 5 findings. Real usage confirmed 3.5 and found 5 more the simulation missed.

**Simulation catches well:** Structural gaps, missing questions, consistency issues.

**Simulation CANNOT catch:** Domain knowledge requirements (evolving frameworks), layered knowledge architecture (Spotify-wide vs FinE vs team), search strategy corrections, data drift in real output, interaction design ("let the skill ask me directly").

Simulated rehearsal is a useful pre-check (~40% of issues) but never replaces building with a real user against real data.

## "Let the skill ask me directly" (cycle 3, from engineer-impact-mirror)

The AI pre-answered Step 1 questions instead of letting the user experience the skill. The user pushed back. The questions ARE the product. Always run them with the user, even when you think you know the answers.

## Framework-dependent skills are a new category (cycle 3, from engineer-impact-mirror)

Most skills are data-dependent: they query systems and process what they find. engineer-impact-mirror revealed a new category: framework-dependent skills that interpret data through an evolving external framework (Performance@Spotify). The framework changes HOW data is interpreted, not just WHAT data is gathered.

This applies to most SDLC-related skills in the repo. Any skill that references gate definitions, delivery phases, epic classification rules, or planning methodology depends on a framework that can change. The FinE SDLC reference is a static snapshot of a living process.

Added "Framework dependency" as a common pattern prompt in Step 2. Skills that depend on evolving frameworks need a refresh step that checks for updates on every run.

## Human vision shaped the architecture, not corrections (cycle 3)

Building engineer-impact-mirror, two user corrections reshaped the entire knowledge architecture:
1. "Performance@Spotify is Spotify-wide, Joakim's doc is FinE-specific" (layer separation)
2. "Don't filter to Spotify-wide before searching" (search broadly, classify after)

These weren't corrections to what the AI did wrong. They were the user's VISION for what the skill should be. The signal hierarchy's highest level (human intent) shaped the architecture. Data and dry-runs refine it. But the architecture comes from the human.

## Step 2.5 preview is worth more than all Step 1 questions combined (cycle 3)

Two corrections during the Kevin preview (date drift, "be an expert in Performance@Spotify") were worth more than all 15 Step 1 design questions. The abstract design conversation produced a reasonable skill. The concrete preview against real data produced a much better one. This is the strongest evidence yet for "do not skip Step 2.5."
