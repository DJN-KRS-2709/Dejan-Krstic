---
name: agent-instructions-review
description: "Review and, when asked, rewrite an AI agent's system prompt or instructions against what its tools and runtime can really do: verified API paths and field names, tool budgets, iteration limits, memory between turns, credentials scope and time handling. Findings first, rewrite second. Use when improving a bot's instructions, auditing an agent for a client, or asking 'why does this agent waste calls / hallucinate fields / take the slow path'."
user_invocable: true
argument-hint: "[path to prompt or pasted prompt] [agent runtime or repo]"
---

# Agent Instructions Review

Most broken agents are not broken by the model. They are broken by instructions that describe tools, fields and limits that do not match reality. This skill checks the instructions against the real system and fixes the gap.

Answer in the user's language. Do not deploy, save or roll out a changed prompt unless the user explicitly asks.

## Workflow

```
- [ ] 1. Load the real prompt and the runtime facts
- [ ] 2. List every system and tool the prompt claims to use
- [ ] 3. Verify names, paths and limits against the live tools (never trust the prompt)
- [ ] 4. Score the problems (see the attack list)
- [ ] 5. Report findings first; rewrite only if useful or requested
- [ ] 6. Record durable facts you proved, in this skill's notes section or the agent's own docs
```

## Step 1: Load the real thing

- Use the prompt the user pasted, or read it from where it actually lives (a repo file, a config store, an environment variable, an agent platform's settings page). Prompts often are not in git; find the source of truth and say where it was.
- Never print secrets, connection strings or tokens while loading.
- Collect runtime facts: model, tool allowlist, max iterations or tool calls per turn, size limits on the prompt, and what persists between turns. Many runtimes start a fresh agent per request and keep only the text of earlier turns; tool results are gone. Any instruction like "you already loaded X earlier in this conversation" is then false.

## Step 2: Attack list (strongest first)

1. **False claims about tools** that push the agent onto a slow path, for example "there is no endpoint for X" when there is one. Verify, then correct.
2. **Discovery through the wrong resource.** Using a list endpoint as if it were sorted by recency when the sort is ignored; inventing nested endpoints that do not exist; creating objects (segments, filters, saved searches) just to read data. Time windows belong where the API actually supports them.
3. **Schema tourism.** Calling describe or schema tools before every action. Those payloads are large and burn budget. Put the needed paths and field names in the prompt; check auth only when a call fails.
4. **Wrong field paths.** Instructions that read top level fields which actually sit nested (or the reverse). Specify exact paths and project only the fields needed.
5. **Display labels instead of stored values.** The UI says "Temporarily excluded", the data stores a segment id or an enum value. Use the stored value.
6. **Missing scope identifiers.** If the credential can see more than one workspace, account or project, the prompt must name the one to use on every call. Isolation in the prompt is not isolation in the credential; flag it.
7. **No join key, or ranking by the wrong field.** Follow-up calls need the stable id. A high score with no recent activity is rarely what "important right now" means.
8. **Clock fiction.** Models do not know the current time. Relative time must come from timestamps in the data (and the right one: event time, not ingest time), or from a tool that returns the current time.
9. **Imaginary interpreter.** If the agent has no code execution, the prompt must say so plainly, or the model may emit shell or Python as if it were a tool. Suggested line: "You cannot run code. Do not output code as a tool call. Work values out yourself or get them from one of your listed tools."

Keep what is good (ranking logic, tone, output format, eligibility rules). Usually only the search path needs rewriting.

## Step 3: Verify before rewriting

- Do not guess field, attribute, event or endpoint names. Make small read only calls to confirm them.
- Ask for shape, not people: project keys and names only, never full records. Never copy personal data (emails, phones, ids tied to people) into the report or into this skill.
- Use tight time windows and small limits.
- Note any limit you discover (window size, page size, rate limits) with the call that proved it.

## Step 4: Output

1. **Keep:** what already works and should stay.
2. **Wrong or expensive:** each claim in the prompt next to the verified reality, ordered by impact.
3. **New version of the prompt**, fenced and paste ready, only if requested or clearly useful.
4. **Fixes the prompt cannot make:** runtime or credential issues (credential sees too much, allowlist still includes heavy tools, prompt size near the limit).

## Step 5: Keep facts current

When a call proves a durable fact (a correct path, a field location, a limit), record it in the agent's docs or in a notes section of this skill in the same session. Replace wrong entries instead of keeping both. Never record personal data.

## Anti-patterns in your own rewrite

- Sending the agent back to schema tools "just in case".
- Telling it to create objects in the system to answer a read question.
- Inventing a hard call limit that the runtime does not enforce, without stating the real maximum. A planned path of a handful of calls is enough.
- Letting the prompt grow past the runtime's size budget (check what else shares that budget, such as tool lists and server configs).
- Dropping the "cannot run code" line when the agent has no interpreter.

## Notes (durable facts)

Add verified facts here as `system | fact | how it was verified | date`. Keep it free of personal data and of any client or employer specifics; those belong in that project's private docs.
