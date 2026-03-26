# FTI-Groove Two-Way Validator Skill

A Claude Code skill that validates bidirectional sync between Jira FTI tickets and Groove Initiatives/DoDs.

## Quick Start

**Via Claude Code:**
```
Validate FTI-Groove sync for user@spotify.com
```

**Via CLI:**
```bash
node fti-groove-validator.skill.js --email user@spotify.com
node run-fti-groove-validator.js --email user@spotify.com --include-done
```

## What It Does

Finds orphaned items in both directions:
- **Jira Orphans**: FTI tickets missing Groove Initiative/DoD linkage
- **Groove Orphans**: Groove DoDs without corresponding FTI tickets

## Files in This Directory

| File | Purpose |
|------|---------|
| `fti-groove-validator.skill.js` | Main skill (self-contained, portable) |
| `run-fti-groove-validator.js` | Wrapper showing Claude Code integration |
| `fti-groove-validator.README.md` | Detailed user guide |
| `SKILL_SUMMARY.md` | Quick reference summary |
| `SKILL_INTEGRATION_GUIDE.md` | How to port to pm-os/workspace |
| `DEMO_EXECUTION.md` | Example execution walkthrough |
| `README.md` | This file |

## Documentation

Start here:
1. **SKILL_SUMMARY.md** - Quick overview and key features
2. **fti-groove-validator.README.md** - Complete user guide
3. **SKILL_INTEGRATION_GUIDE.md** - Porting to pm-os/workspace
4. **DEMO_EXECUTION.md** - See example output

## Prerequisites

- Node.js ≥14
- acli (Atlassian CLI) - `brew install acli`
- Claude Code with Groove MCP (for Groove queries)

## Installation

### Option 1: Use in Current Location
```bash
cd /Users/taylormendel/spotify-workspace/fti-groove-validator
node fti-groove-validator.skill.js --email your@spotify.com
```

### Option 2: Copy to pm-os/workspace
```bash
# Copy entire directory
cp -r fti-groove-validator /path/to/pm-os/workspace/skills/

# Or just copy the main skill file
cp fti-groove-validator.skill.js /path/to/pm-os/workspace/skills/
```

## Configuration

Verify Jira custom field IDs in `fti-groove-validator.skill.js` (lines 33-37):

```javascript
const JIRA_CUSTOM_FIELDS = {
  grooveInitiativeId: 'customfield_13283',
  grooveDodId: 'customfield_13281'
};
```

To find correct IDs:
1. Open any FTI ticket in Jira
2. Click "..." → "View in JSON"
3. Search for "Groove Initiative" and "Groove DOD"
4. Update if needed

## Example Output

```
================================================================================
FTI ↔ Groove Validation Report
Owner: taylorm@spotify.com
================================================================================

📋 JIRA TICKETS MISSING GROOVE LINKAGE
✓ All Jira tickets are properly linked to Groove!

--------------------------------------------------------------------------------

🎯 GROOVE DoDs MISSING JIRA TICKETS

1. DOD-5459 - Holistic Assessment of Data Landscape
   Initiative: P0: The Data Quest (INIT-862)
   Status: IN_PLANNING
   Owner: Taylor Mendel
   https://spotify.groove.work/dods/DOD-5459

Total: 5 orphaned Groove DoD(s)

================================================================================

⚠️  Found 5 orphaned item(s) requiring attention.
```

## Features

✅ Self-contained (no npm dependencies)
✅ Portable (single file works anywhere)
✅ Two-way validation (Jira ↔ Groove)
✅ Colored CLI output with clickable links
✅ Works with or without Claude Code MCP
✅ Optional --include-done flag

## Support

For issues or questions:
- Check the detailed guides in this directory
- Verify Jira custom field IDs match your instance
- Test acli connectivity: `acli jira auth verify`
- Ensure Groove MCP server is configured in Claude Code

## License

Internal Spotify use only.
