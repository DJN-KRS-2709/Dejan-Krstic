# Enforcement Reference: Rationalization Patterns for Brief Verification

Apply when the PM resists verification or dismisses drift findings. Intervene immediately with the specified counter.

---

## Rationalization Patterns

| Rationalization | Counter |
|---|---|
| "I just created these, they're correct" | "Just created != verified. Read the artifact and compare. 60 seconds." |
| "The Jira ticket is close enough" | "'Close enough' = 'slightly wrong.' Engineers build what the ticket says, not what you intended." |
| "The brief changed since I created artifacts" | "Then artifacts are stale. Update them or note the drift explicitly." |
| "It's a minor wording difference" | "Minor wording differences in problem statements become major scope differences in implementation." |
| "Stakeholders don't read Jira descriptions" | "Engineers do. The description matters." |
| "Verification is overkill" | "The verification takes 60 seconds. The rework from missed drift takes weeks." |

---

## Red Flags

| Red Flag | Action |
|---|---|
| PM skips verification after changes | "Artifacts were modified since the brief was written. Verify before claiming alignment." |
| Dismissing drift as cosmetic | "If it's cosmetic, the fix takes 30 seconds. If it's not, you just caught a real problem." |
| "We'll fix it when engineers ask" | "Engineers won't ask. They'll build what the ticket says and discover the mismatch in QA." |
