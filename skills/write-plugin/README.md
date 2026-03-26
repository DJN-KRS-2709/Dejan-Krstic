# write-plugin

Author new pm-os plugins using TDD-for-skills methodology. **Failure first, skill second.**

## What It Does

Seven-step guided process that takes an observed agent failure and produces a complete pm-os plugin. Follows TDD-for-skills: define the anti-pattern (RED), design the skill to prevent it (GREEN), close loopholes (REFACTOR).

No skill without 3 failure examples. No publication without quality checklist.

## Usage

```
/write-plugin tradeoff-enforcer --from-observation "agent skips tradeoff analysis"
/write-plugin meeting-prep --category productivity
/write-plugin metric-validator --from-observation "agent accepts vague metrics"
```

Auto-invokes when you say: "create a plugin", "new skill", "I need a slash command for".

## The Seven Steps (TDD-for-Skills)

1. **Understand** the need from an observed failure
2. **RED: Define anti-pattern** with 3 failure examples (hard gate: 3 required)
3. **Build rationalization table** (how the agent would justify the failure)
4. **GREEN: Design the skill** (frontmatter, hard gate, steps, output template)
5. **REFACTOR: Close loopholes** (test skill against rationalization table, hard gate: all covered)
6. **Generate plugin skeleton** (plugin.json, SKILL.md, enforcement.md, README.md)
7. **Quality check** against plugin-quality-checklist.md

## Hard Gates

- **3 failure examples required.** Before any skill design begins.
- **All rationalizations covered.** Every row in the rationalization table must map to a step, gate, or rule.
- **Quality checklist passes.** All items must pass before publication.

## Reference Files

- `references/enforcement.md` -- Rationalization patterns for plugin authoring
- `references/skill-structure.md` -- Required SKILL.md format and sections
- `references/plugin-quality-checklist.md` -- Mandatory quality gate before publishing

## Output

A complete plugin directory:
```
plugins/<name>/
  .claude-plugin/plugin.json
  README.md
  skills/<name>/
    SKILL.md
    references/
      enforcement.md
      [additional references]
```

## Category

`development`
