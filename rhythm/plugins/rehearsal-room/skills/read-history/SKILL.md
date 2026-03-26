---
name: read-history
alias: playback
role: cross-cutting
invokes: []
invoked-by: [improve-skill]
description: >
  Read the entire master tape transcript and build a comprehensive
  understanding of founding decisions, human corrections, and design
  rationale. Required before the first rehearsal cycle on any skill.
  Triggers: "read-history", "study the master tape", "read the founding session",
  "read the transcript", "understand the origins", "load master tape",
  "reflect", "deep reflection", "review everything"
---

# Study the Master Tape *(playback)*

Reads the entire master tape transcript in structured chunks, building a comprehensive understanding of how and why every skill, convention, and decision was made. This is the band listening to the original recording before rehearsing.

> **Design principle:** The master tape contains 612 user messages across 19,884 lines. Every major design decision, human correction, and methodology insight is in there. A new AI session reading only the skill files gets the WHAT. Reading the master tape gets the WHY.

## When to run

- **Before the first rehearsal cycle** on any skill — mandatory
- **Before reflect** — when doing a deep retrospective
- **When a new AI session starts** — to load the full founding context
- **When preparing presentations** — to mine for narrative moments and proof points

## Step 1: Decompress and validate

```bash
# Decompress if not cached
if [ ! -f /tmp/master-tape.jsonl ]; then
  gunzip -k bands/fine/otter/master-tape/master-tape.jsonl.gz -c > /tmp/master-tape.jsonl
  echo "Decompressed master tape"
else
  echo "Using cached master tape"
fi

# Validate
LINE_COUNT=$(wc -l < /tmp/master-tape.jsonl)
echo "Lines: $LINE_COUNT"
```

Expected: ~19,884 lines. If the file is missing or empty, flag and skip.

## Step 2: Build the index

Extract a lightweight index of all user messages with timestamps and topics:

```python
import json

messages = []
with open('/tmp/master-tape.jsonl') as f:
    for i, line in enumerate(f):
        try:
            msg = json.loads(line)
            if msg.get('type') == 'user':
                content = msg.get('message', {}).get('content', '')
                if isinstance(content, str) and len(content) > 10:
                    messages.append({
                        'line': i,
                        'text': content[:500],
                        'timestamp': msg.get('timestamp', '')
                    })
        except:
            pass

# Save index
with open('/tmp/master-tape-index.json', 'w') as f:
    json.dump(messages, f)
print(f"Indexed {len(messages)} user messages")
```

Expected: ~612 user messages.

## Step 3: Read in chunks

Read the full transcript in ~20 chunks of ~1000 lines. For each chunk, extract:

| What to extract | Tag | Example |
|----------------|-----|---------|
| Human decisions | `DECISION` | "I want to combine the retro and kickoff into one meeting" |
| Human corrections | `CORRECTION` | "I'm not sure I agree with #1" |
| Design rationale | `WHY` | "human judgment should have priority" |
| Skill-specific context | `SKILL:[name]` | Discussion about whos-available edge cases |
| Methodology evolution | `METHOD` | "the rehearsal methodology was refined through specific corrections" |
| Narrative moments | `NARRATIVE` | "the $3M Slack thread that was invisible in Jira" |
| User preferences | `PREFERENCE` | "lean and smart, not comprehensive documentation" |

**For each chunk:**

```bash
# Read lines N to N+1000
python3 -c "
with open('/tmp/master-tape.jsonl') as f:
    lines = f.readlines()[START:END]
for line in lines:
    # ... extract and tag
"
```

**Produce a chunk summary** (10-20 tagged items per chunk). Accumulate all chunk summaries.

## Step 4: Synthesize

After reading all chunks, produce a **Master Tape Understanding Document**:

```markdown
## Master Tape Understanding

### Founding decisions (chronological)
1. [DECISION] "encode our team's ways of working into skills we can automate" — the founding intent
2. [DECISION] Markdown-first artifact model — PRDs in repo, Google Docs generated
3. [DECISION] "make the right thing the easy thing" — core design principle
...

### Human corrections that changed architecture
1. [CORRECTION] "how does your example match real data?" → redesigned review-pr from 80+ real PRs
2. [CORRECTION] "start from intent, not data" → signal hierarchy: human > data > dry-runs
3. [CORRECTION] "use a subagent for the diff" → review-pr architecture change
...

### Per-skill founding context
#### whos-available
- Originally extracted from plan-sprint
- Rehearsed 3 cycles: holidays, temporary engineers, multi-sprint ranges
- Key correction: "ignore partial-day events"
...

### Methodology evolution
- Started as "build, dry-run, encode"
- Became: intent → validate with data → design with challenge → build → parallel test → encode
...

### User preferences
- Human-led, data-informed
- Lean and smart scaffolding
- "Film everything like a documentary crew"
- Skills should be interactive — ask, don't assume
...
```

## Step 5: Cache the understanding

Save the synthesis to `/tmp/master-tape-understanding.md` for other skills to reference during this session.

Log: `FINDING — Master tape read: [N] decisions, [M] corrections, [P] narrative moments extracted from [LINE_COUNT] lines.`

## Agent input contract

When called by improve-skill or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `skill_filter` | optional | all | Skill name to focus the read on |
| `mode` | optional | full | "full" (all chunks) or "targeted" (skill-specific only) |

In targeted mode: only read chunks that mention the specified skill. Faster but misses cross-cutting context.

### Decision authority
Decides autonomously:
- Chunk size and count : ~20 chunks of ~1000 lines each
- Extraction tags (DECISION, CORRECTION, WHY, SKILL, METHOD, NARRATIVE, PREFERENCE) : applied based on content analysis
- Chunk summary density : 10-20 tagged items per chunk
- Cache usage : skips re-reading if `/tmp/master-tape-understanding.md` exists and is recent
- Mode selection (full vs targeted) : full by default, targeted if `skill_filter` is provided
- Which chunks to skip in targeted mode : only reads chunks mentioning the target skill

Asks the user:
- Nothing — fully autonomous read-and-synthesize operation

### Success indicators

- [ ] All ~20 chunks read and summarized
- [ ] Master Tape Understanding Document produced
- [ ] Per-skill context extracted for skills mentioned in transcript
- [ ] Methodology evolution timeline captured
- [ ] Human corrections catalogued with their architectural impact

## Performance notes

- **Parallel:** Chunk reading can be parallelized (each chunk is independent)
- **Sequential:** Synthesis must wait for all chunks to complete
- **Cache:** Check `/tmp/master-tape-understanding.md` before re-reading — skip if recent
- **Skip:** In targeted mode, skip chunks that don't mention the target skill

## Rehearsal notes

> **Narrative moments:** The master tape IS the narrative. Every chunk will contain moments worth preserving.
>
> **Rehearsal notes are a floor, not a ceiling.**

### Why read the whole thing

The A/B test showed that rehearsal notes add strategic framing but not core accuracy. The master tape adds something neither provides: the human's reasoning process. Why did David push back on "start from data"? Why did he insist on musical aliases? Why does the guardrails convention exist? The answers are in the dialogue, not in any file.

### The founding corrections are the most valuable content

612 user messages. Many are "yes" or "commit." But ~50 are corrections that changed the architecture. These corrections encode David's judgment — the signal hierarchy says human judgment is the highest priority signal. The master tape IS that judgment, recorded.
