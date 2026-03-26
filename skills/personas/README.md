# Personas Plugin

Build, refresh, and simulate stakeholder personas from 6 data sources with role-adaptive weighting.

## Usage

```
/persona <name>              # Simulate from existing persona
/persona --build <Name>      # Full build from scratch
/persona <name> --refresh    # Incremental refresh + simulate
/persona --list              # List personas with refresh dates
```

Also auto-invoked by conversational triggers like:
- "What would Craig think of this?"
- "Run this by Nate"
- "How would Shameka react?"

## How It Works

1. **Build** researches a person via 6 sources with role-adaptive depth:
   - **Bandmanager** — org position, reporting chain, groups
   - **Slack** — communication style, objections, feedback patterns
   - **Google Drive** — docs they own, writing style, priorities
   - **GHE** — PR review style, technical standards, collaboration patterns
   - **Auto-Memory** — user's private observations and relationship notes
   - **Groove** — strategic priorities, status communication, cross-org work
2. **Role detection** classifies the person (engineer, PM/leader, other) and adjusts source depth — engineers get deep GHE analysis, PMs get deep Groove and Drive analysis
3. **Personas** are stored encrypted at `~/.claude/personas/` — per-user, never committed
4. **Simulate** decrypts a persona into session memory and simulates the stakeholder's perspective
5. **Refresh** incrementally updates a persona with data since the last refresh date, including new sources

## Prerequisites

- `openssl` and `security` (macOS Keychain) — for encryption
- **Required:** Slack, Bandmanager, and Google Drive MCP integrations — for build/refresh
- **Optional:** GHE and Groove MCP integrations — role-adaptive (GHE is primary for engineers, Groove is deep for PMs/leaders)
- Auto-Memory requires no integration (reads local files)
- Simulation from an existing persona requires no integrations

## Crypto Script

All encryption/decryption is handled by `bin/persona-crypto.sh`, which pins every crypto parameter as a readonly constant. This eliminates decryption failures caused by LLM-generated parameter variation.

```bash
persona-crypto.sh encrypt <name>    # base64 transfer file → .enc
persona-crypto.sh decrypt <name>    # .enc → stdout
persona-crypto.sh keygen            # generate + store key (idempotent)
persona-crypto.sh keycheck          # verify key exists
persona-crypto.sh verify <name>     # test decrypt, diagnose failures
persona-crypto.sh migrate <name>    # re-encrypt with canonical params
persona-crypto.sh migrate-all       # migrate all personas
```

If decryption fails after an update, run `verify` to diagnose the mismatch, then `migrate` to fix it.

## Privacy

- Persona files are encrypted at rest with a per-user key in macOS Keychain
- No plaintext persona files are ever written to disk
- Persona contents are never displayed to the user
- Files live outside any git repository (`~/.claude/personas/`)
- Auto-memory observations are attributed as user interpretations, never as direct quotes
