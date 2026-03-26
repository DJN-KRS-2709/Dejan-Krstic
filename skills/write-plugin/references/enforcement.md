# Enforcement Reference: Rationalization Patterns for Plugin Authoring

Apply when the PM tries to skip failure examples, bypass the rationalization table, or ship a skill without enforcement. Intervene immediately with the specified counter.

---

## Rationalization Patterns

| Rationalization | Counter |
|---|---|
| "The anti-pattern is obvious, skip failure examples" | "If obvious, write 3 examples in 2 minutes. If you can't, the skill will be vague." |
| "I'll add the rationalization table later" | "The rationalization table IS the test suite. Skill without it = code without tests." |
| "This skill is simple, doesn't need enforcement" | "Simple skills are the most likely to be skipped. Hard gate still required." |
| "The description should say what it does" | "Description = trigger, not feature list. Claude reads it to decide whether to invoke." |
| "I'll refine loopholes after user reports" | "Users won't report, they'll stop using the skill. Close loopholes now." |
| "Not every step needs a gate" | "Not every step, but every analysis-to-action transition does." |

---

## Red Flags

| Red Flag | Action |
|---|---|
| Skill description lists features instead of triggers | "Description tells Claude WHEN to invoke, not WHAT it does. Rewrite as triggering conditions." |
| No hard gate defined | HARD BLOCK. "Every skill needs at least one hard gate. What single rule prevents the core failure?" |
| Fewer than 3 failure examples | HARD BLOCK. "3 failures minimum. These are your test cases. Without them, the skill is untested." |
| Rationalization table has fewer than 5 rows | "Each row is a loophole closed. 5 is the minimum. What else would the agent say to skip this?" |
| Steps are not atomic | "Each step should do one thing and be independently verifiable. Break it down." |
