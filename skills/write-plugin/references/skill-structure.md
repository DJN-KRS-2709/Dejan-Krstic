# Required SKILL.md Structure

Every pm-os plugin SKILL.md must follow this structure. Missing sections = incomplete skill.

---

## Required Sections

### 1. Frontmatter (YAML)

```yaml
---
name: <skill-name>
description: "<Triggering conditions, not feature list. Claude reads this to decide whether to invoke.>"
user_invocable: true
argument-hint: "<argument pattern>"
---
```

**Description rules:**
- Start with "Use when..."
- Describe the PM's situation, not the skill's capabilities
- Include auto-invoke triggers: "Auto-invoke when user says..."
- Keep under 200 characters

### 2. Title and Role

```markdown
# [Skill Name] Skill

You are a **[role]**. Your job is to [one sentence purpose].
```

### 3. Core Rule (HARD GATE)

```markdown
## Core Rule (HARD GATE)

**[SINGLE RULE IN CAPS.]**

[Explanation of what is blocked until the gate is passed.]
```

Every skill needs exactly one hard gate. This is the single rule that prevents the core failure the skill exists to address.

### 4. Anti-Patterns Reference

```markdown
Read `references/enforcement.md` for the full rationalization table. Apply throughout.
```

### 5. Steps (Numbered)

```markdown
## Step N: [Name]

[Instructions. One action per step. Atomic and verifiable.]

### GATE N: [Gate condition]

[What must be true before proceeding.]
```

**Step rules:**
- One primary action per step
- Questions asked one at a time, never bundled
- Gates at every analysis-to-action transition
- Domain validation always in Step 0

### 6. Behavioral Rules (Numbered list)

```markdown
## Behavioral Rules

1. **[Rule name].** [Explanation.]
```

Minimum 5 rules. Must include: one-question-at-a-time, never skip steps, enforce enforcement reference.

### 7. Arguments

```markdown
## Arguments

- `<arg>` -- Description. Required/Optional.
```

### 8. Example Usage

```markdown
## Example Usage

\`\`\`
/skill-name argument1 --flag value
\`\`\`
```

---

## Required Reference Files

| File | Purpose |
|---|---|
| `references/enforcement.md` | Rationalization table (minimum 5 rows) + red flags |
| Additional references | Domain-specific patterns, templates, shared gates |

---

## Style Rules

- No em-dashes. Use commas, colons, or restructure.
- Tables over paragraphs for structured data.
- Exact output templates where applicable.
- Domain validation boilerplate: allowlist, traversal rejection, regex check, quote arguments.
