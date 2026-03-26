---
name: respond-to-comments
description: >
  This skill should be used when the user asks to "respond to doc comments",
  "reply to comments in a Google Doc", "review doc comments", "triage document comments",
  "summarize Google Doc comments", "draft replies to doc comments",
  or mentions responding to feedback in a Google Doc.
user_invocable: true
---

## Prerequisites

Before running this skill, verify the following are available:

1. **GDrive MCP server**: The `mcp__claude_ai_GDrive_MCP` server must be configured and accessible. Verify by checking that tools like `mcp__claude_ai_GDrive_MCP__list_document_comments` are available. If not configured, add the GDrive MCP server to your Claude Code MCP settings.

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Respond to Google Doc Comments

Summarize, triage, and draft replies for open comments on a Google Doc.

## Workflow

### 1. Identify the Document

Obtain the Google Doc file ID from the user. Accept any of these formats:
- Full URL: `https://docs.google.com/document/d/{fileId}/edit`
- Just the file ID string

Extract the file ID from URLs by parsing the path segment between `/d/` and the next `/`.

If no document is provided, ask the user via AskUserQuestion.

### 2. Gather Context

Fetch the document content and comments in parallel:

- **Comments**: Use `mcp__claude_ai_GDrive_MCP__list_document_comments` with the file ID to retrieve all open comments and their reply threads.
- **Document structure**: Use `mcp__claude_ai_GDrive_MCP__get_document_structure` to understand the document layout. Then fetch relevant sections as needed for context around comments.

### 3. Summarize & Triage

Present a summary table of all open comments, organized by priority:

| Priority | Commenter | Comment (truncated) | Section | Action Needed |
|----------|-----------|---------------------|---------|---------------|
| High     | ...       | ...                 | ...     | ...           |
| Medium   | ...       | ...                 | ...     | ...           |
| Low      | ...       | ...                 | ...     | ...           |

**Priority classification:**

- **High**: Questions requiring a decision, blockers, requests for significant changes, unresolved disagreements
- **Medium**: Suggestions for improvement, clarifying questions, style/tone feedback
- **Low**: Minor edits (typos, formatting), acknowledgments, resolved-but-open threads, FYI comments

**Action needed categories:**
- `Reply` — commenter asked a question or made a suggestion needing a response
- `Revise` — comment requests a content change in the doc
- `Acknowledge` — comment is informational, just needs a brief acknowledgment
- `Resolve` — comment appears already addressed, can likely be resolved

### 4. Draft Replies

After presenting the summary, draft a reply for each comment that needs one (`Reply`, `Revise`, or `Acknowledge` actions).

**Drafting guidelines:**

- Match the tone and formality of the original commenter
- Be concise — one to three sentences per reply
- For suggestions: acknowledge the feedback, state whether it will be incorporated, and explain briefly if not
- For questions: answer directly, referencing the relevant section of the doc
- For revision requests: confirm the change will be made or explain an alternative approach
- For acknowledgments: keep it brief ("Thanks, good catch!" or "Noted, will update.")

**Output format for each drafted reply:**

```
**Comment by [Name]** (Section: [section name])
> [Original comment text]

**Suggested reply:**
[Draft reply text]

**Action:** [Reply | Revise | Acknowledge | Resolve]
```

### 5. User Review

After presenting all drafted replies, ask the user which replies to send, modify, or skip. Do NOT post any replies without explicit user approval.

Present options via AskUserQuestion:
- Send all drafts as-is
- Review and edit individually
- Skip (just use the summary)

## Notes

- This skill is read-only by default — it never posts replies without user confirmation
- For documents with many comments (50+), use pagination via `pageToken` in the comments API
- When the document is long, prefer `get_document_structure` + `get_document_section` over reading the entire document
- If a comment thread has multiple replies, summarize the thread state (e.g., "3-reply thread, last from [Name], awaiting response")

## Additional Resources

### Reference Files

- **`references/reply-patterns.md`** — Common reply patterns and templates for different comment types
