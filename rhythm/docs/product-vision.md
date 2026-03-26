# Product Vision: Three Products, One Rhythm

> Documented during session 29. Restructuring deferred to after Hack Days (Mar 26+).
> Current repos (rhythm, rehearsal-room) continue as-is until then.

## The Three Products

### 1. rhythm — "The Album"

**Audience:** FinE squads
**What it is:** Pre-built SDLC skills, plug and play. The genre is FinE's process.
**Current home:** rhythm (`skills/` + `plugins/rehearsal-room/`)

FinE squads clone this and get a working skill set immediately. The SDLC reference, templates, and ceremony flows are pre-configured. Team-specific data (`bands/fine/otter/bio/team.md`, `bands/fine/otter/discography/roadmap.md`) is replaced per squad.

### 2. rhythm-studio — "The Studio"

**Audience:** Any Spotify squad
**What it is:** Guided setup, bring your own process. Record your own album.
**Current home:** Parts of rhythm (`sheet-music/fine/sdlc-reference.md`, `sheet-music/fine/templates/`) + start-band's guided setup

Non-FinE squads use rhythm-studio to build their own skills repo from scratch. The guided setup asks about their process, tools, and cadence — then generates the structure. They write their own skills, their own ceremonies, their own sheet music.

### 3. rehearsal-room — "Where Bands Are Born"

**Audience:** Anyone wanting the methodology
**What it is:** The rehearsing loop, session workflow, scaffolding. Genre-agnostic.
**Current home:** rehearsal-room (6 skills: improve-skill, save-work, share-summary, join-band, new-instrument, room-check)

The Rehearsal Room provides the equipment: how to improve-skill (rehearse) a skill, how to save-work (save) a session, how to set up a studio (scaffold a repo). It doesn't know FinE's SDLC or any team's process — it knows how to BUILD process-encoding skills.

## How They Layer

```
rehearsal-room (methodology + tools)
  └── rhythm-studio (guided setup + templates)
        └── rhythm (pre-built FinE skills)
```

Each layer adds specificity:
- **rehearsal-room** is genre-agnostic — any team, any process, any tools
- **rhythm-studio** adds structure — guided setup, cadence detection, MCP wiring
- **rhythm** adds FinE's process — SDLC gates, Pulse reporting, Groove/Jira specifics

## Current → Future Mapping

| Current | Future product | What moves |
|---------|---------------|-----------|
| rhythm `plugins/` | **rhythm** | 24 FinE-universal skills |
| rhythm `sheet-music/fine/sdlc-reference.md`, `sheet-music/fine/templates/` | **rhythm-studio** | Reusable SDLC framework + templates |
| rhythm `bands/fine/otter/bio/team.md`, `bands/fine/otter/discography/roadmap.md` | stays local | Team-specific data, not a product |
| rehearsal-room `plugins/rehearsal-room-toolkit/` | **rehearsal-room** | 7 methodology skills |
| rehearsal-room `sheet-music/fine/templates/` | **rhythm-studio** | Scaffold templates (CLAUDE.md, team.md, etc.) |
| rehearsal-room `docs/case-studies/` | **rehearsal-room** | Evidence for the methodology |
| [rhythm-presentations](https://ghe.spotify.net/davidlalande/rhythm-presentations) repo | separate repo | Presentation materials, decks, image prompts |

## The Pitch for Each

- **rehearsal-room:** "Every band starts in a rehearsal room. Clone it and start rehearsing."
- **rhythm-studio:** "Your team has a rhythm. Here's the studio to record it."
- **rhythm:** "FinE's rhythm, encoded. Plug in and play."

## Timeline

- **Now (pre-Hack Days):** Document the vision (this file). Keep current repos working.
- **Hack Days (Mar 23-25):** Present using the musical vocabulary. Demo from current repos.
- **Post-Hack Days:** Restructure into three products based on adoption feedback.
- **If only 1 team adopts:** Keep rhythm + rehearsal-room (2 repos). rhythm-studio is premature.
- **If 3+ teams adopt:** Split into all three. rhythm-studio earns its existence.

## Open Questions

1. Should rehearsal-room be a plugin that installs INTO other repos, or a standalone repo you clone?
2. Does rhythm include the scaffold for new FinE squads, or does that live in rhythm-studio?
3. How do we handle the feedback loop (rhythm discoveries → rehearsal-room improvements) across 3 repos instead of 2?
