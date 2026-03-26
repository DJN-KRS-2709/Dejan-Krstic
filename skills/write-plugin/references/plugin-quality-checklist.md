# Plugin Quality Checklist

Run this checklist before publishing any pm-os plugin. Every item must pass.

---

## Structure

- [ ] `plugin.json` exists in `.claude-plugin/` with name, version, description, author, keywords
- [ ] `README.md` exists at plugin root with: What It Does, Usage, Steps summary, Hard Gates, Category
- [ ] `SKILL.md` exists in `skills/<name>/` with full frontmatter
- [ ] `references/enforcement.md` exists with rationalization table

## Frontmatter

- [ ] `name` matches directory name
- [ ] `description` starts with "Use when..." (triggering conditions, not features)
- [ ] `description` includes auto-invoke triggers
- [ ] `user_invocable: true` is set
- [ ] `argument-hint` is present

## Hard Gate

- [ ] Exactly one hard gate defined in Core Rule section
- [ ] Hard gate is a single, clear, enforceable rule
- [ ] Hard gate prevents the core failure the skill addresses

## Enforcement

- [ ] Rationalization table has at least 5 rows
- [ ] Each row has a specific rationalization and a specific counter
- [ ] Red flags section exists with at least 3 entries
- [ ] Counters are direct and actionable, not passive

## Steps

- [ ] Steps are numbered starting from 0 (context loading)
- [ ] Each step has one primary action
- [ ] Questions are asked one at a time (never bundled)
- [ ] Gates exist at analysis-to-action transitions
- [ ] Domain validation is in Step 0 (if applicable): allowlist, traversal, regex, quoting

## Behavioral Rules

- [ ] At least 5 behavioral rules
- [ ] Includes: one-question-at-a-time rule
- [ ] Includes: never skip steps rule
- [ ] Includes: enforce enforcement reference rule

## Output

- [ ] Exact output template defined (if skill produces an artifact)
- [ ] Template uses tables over paragraphs for structured data

## Style

- [ ] No em-dashes anywhere in the skill
- [ ] No frameworks beyond those defined in the skill
- [ ] Domain-specific jargon explained or avoided
