# Verification Gate: Fresh Evidence Before Claims

Shared pattern consumed by write-brief and execute-brief. Apply at every analysis-to-output transition.

---

## Core Rule

**NO CLAIM WITHOUT FRESH EVIDENCE FROM THE SOURCE FILE.**

Before generating any output that references a source file (problem frame, status.md, decision log, brief), you must re-read that file from disk. Memory of previous reads is not sufficient.

---

## 5-Step Gate

1. **Identify source file.** What file does your output depend on? Name it explicitly.
2. **Read from disk.** Use the Read tool. Not your memory. Not "what was discussed earlier."
3. **Check match.** Does the file content match what you are about to claim? Compare key fields: problem statement, metrics, recommendations, status.
4. **If mismatch: STOP.** Surface the discrepancy to the user. Do not silently reconcile. Do not pick one version.
5. **If match: proceed with citation.** Reference the file path and the specific section you verified.

---

## Red Flags (Block These)

| Pattern | Why It Fails |
|---|---|
| "Based on what was discussed earlier..." | Discussion != file content. Files change. Read the file. |
| "The problem frame says..." (without reading it) | You are quoting memory, not the file. Read it. |
| "Should be consistent with..." | "Should be" is a guess. Verify or flag. |
| Generating output without reading inputs | Output without verification is fabrication with extra steps. |

---

## Anti-Rationalizations

| Rationalization | Counter |
|---|---|
| "I just read it" | Files change between reads. Re-read before output generation. |
| "The user told me what it says" | Verbal != file content. The file is the source of truth. Read it. |
| "It's a minor detail" | Minor mismatches in problem statements become major scope differences in implementation. Verify. |
