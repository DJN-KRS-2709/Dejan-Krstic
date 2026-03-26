---
name: private
description: "Create a private document excluded from git tracking via .git/info/exclude"
argument-hint: "<path> [--dir]"
allowed-tools: ["Bash(mkdir:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(grep:*)", "Bash(tee:*)"]
---

# Private Document

Create a private file or directory that is excluded from git tracking using `.git/info/exclude` (per-clone, never shared, cannot be reverted by other users).

---

## Instructions

### 1. Parse Arguments

```
/private domains/booking/my-scratch-notes.md
/private domains/calculators/my-analysis/
/private scratch/ideas.md
/private --dir domains/booking/drafts
```

- `<path>` — Path to the file or directory to create (required). Relative to repo root.
- `--dir` — Create as a directory instead of a file.

If the path ends with `/`, treat it as a directory automatically.

If no arguments are provided, prompt the user for a path.

### 2. Determine Type

- If `--dir` flag is present OR path ends with `/`, create a directory
- Otherwise, create a file

### 3. Create the File or Directory

**For a directory:**
```bash
mkdir -p "<path>"
```

**For a file:**
```bash
mkdir -p "$(dirname '<path>')"
```

Then use the Write tool to create the file with a simple header:

```markdown
# Private Notes

> This file is excluded from git via .git/info/exclude and will not be committed.

---

```

### 4. Add to .git/info/exclude

First, check if the pattern already exists:

```bash
grep -qxF '<pattern>' .git/info/exclude
```

If it does NOT exist, append it:

```bash
echo '<pattern>' >> .git/info/exclude
```

**Pattern rules:**
- For a directory path like `domains/booking/drafts`, add `domains/booking/drafts/`
- For a file path like `domains/booking/notes.md`, add `domains/booking/notes.md`
- Always use the path relative to the repo root

Add a comment line above the pattern for context:

```bash
echo '' >> .git/info/exclude
echo '# Private: <short description based on path>' >> .git/info/exclude
echo '<pattern>' >> .git/info/exclude
```

### 5. Verify Exclusion

Run:

```bash
ls -la "<path>" 2>/dev/null && echo "Created successfully"
```

### 6. Confirm

Output:

```
Private document created: <path>

Excluded via: .git/info/exclude
Pattern: <pattern>

This file:
  - Will NOT appear in git status
  - Will NOT be committed or pushed
  - Is invisible to other clones
  - Survives any .gitignore changes

To see all your private exclusions:
  grep -v '^#' .git/info/exclude | grep -v '^$'
```

---

## Notes

- `.git/info/exclude` works identically to `.gitignore` but is per-clone and never tracked
- Patterns added here cannot be overwritten by other users or PR merges
- If the user wants a shared exclusion instead, suggest adding to `.gitignore` with the `_private/` convention
- The `_private/` directory convention is available anywhere in the tree for shared private space
