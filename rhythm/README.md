![rhythm♫](docs/images/readme-banner.png)

# Welcome to rhythm ♫!

Every band needs a rhythm. This is ours, encoded.

A shared recording studio where FinE squads lay down tracks. Each sprint is a recording session, each skill is an instrument, and the whole team plays together. The producer sets the tempo. The session musician plays along.

## Quick start

```bash
git clone git@ghe.spotify.net:davidlalande/rhythm.git
cd rhythm
claude
```

Then say: `join-band`

If you're on Otter Squad, you're already set up. For a new squad, `join-band` walks you through creating your band folder.

## How it works

```
You say:                Claude does:

Recording sessions (sprints):
"plan-session"          → plans the recording session (capacity, goals, risks)
"session-start"         → hits record, sprint begins
"session-wrap"          → wraps the session, review the takes
"listen-back"           → retro: listen to what was recorded, discuss

In the studio (daily):
"roll-call"             → who's in the studio today?
"tune-up"               → are all the instruments in shape?
"mix-notes"             → draft status updates for the producer (Pulse)
"warm-up"               → get ready for today's meetings
"review-take"           → review a PR, listen to a single take
"cue"                   → scan the horizon, any changes coming?

Making the album (initiative lifecycle):
"first-note"            → start discovery, the first note played
"demo-tape"             → is this ready for Gate 1?
"compose"               → write the technical design (HLD)
"green-light"           → Gate 2 passed, start recording
"score"                 → break the composition into parts (epics/stories)
"pre-master"            → pre-launch readiness check
"album-drop"            → release day, ship it

The Rehearsal Room (methodology):
"rehearse"              → test a skill against real data, make it better
"wrap"                  → save your work, review learnings, ship to master
"room-check"            → is the studio healthy?
```

Every skill has two names: a functional name (what it does) and a recording studio alias (what you say). Both work. Use whichever feels natural.

## The recording studio

```
rhythm/
├── skills/                    25 instruments (FinE-universal)
│   ├── plan-sprint/           (plan-session)     Full sprint planning
│   ├── start-sprint/          (session-start)    Kick off the sprint
│   ├── end-sprint/            (session-wrap)     Close the sprint
│   ├── run-retro/             (listen-back)      Sprint retrospective
│   ├── check-health/          (tune-up)          Epic SDLC compliance
│   ├── post-updates/          (mix-notes)        Status updates for Pulse
│   ├── whos-available/        (roll-call)        Team capacity
│   ├── prep-meetings/         (warm-up)          Meeting context
│   ├── review-pr/             (review-take)      PR review context
│   └── ...
│
├── plugins/
│   └── rehearsal-room/                9 methodology instruments
│       ├── improve-skill/     (rehearse)         Test + improve skills
│       ├── save-work/         (wrap)             Commit + review + ship
│       ├── check-repo/        (room-check)       Studio health audit
│       └── ...
│
├── sheet-music/               The rules (per area)
│   └── fine/                  FinE SDLC, templates, gate definitions
│
├── bands/                     Per-team folders
│   └── fine/otter/            Team data, roadmap, rehearsal notes, master tape
│
└── docs/                      Getting started, product vision
```

## The layers

Knowledge lives at the right level, like how a recording studio has house rules, genre conventions, and each band's own style:

| Layer | What's there | Analogy |
|-------|-------------|---------|
| **skills/** | Universal skill logic | The instruments, same for every band |
| **sheet-music/fine/** | FinE process rules and templates | The genre's theory book, all FinE bands follow the same progressions |
| **bands/fine/otter/** | Otter-specific data and rehearsal notes | The band's own style, learned from playing together |
| **plugins/rehearsal-room/** | The methodology for improving skills | The rehearsal space, where bands get tight |

When Claude plays an instrument for Otter:
1. Reads `skills/<name>/SKILL.md` (the universal instrument)
2. Reads `sheet-music/fine/rehearsal-notes/<name>.md` if it exists (FinE genre lessons)
3. Reads `bands/fine/otter/rehearsal-notes/<name>.md` if it exists (Otter's style)

## Full track listing

### Session instruments (25)

| Instrument | Alias | What it plays |
|------------|-------|--------------|
| `start-discovery` | *first-note* | Begin discovery, the first note played |
| `gate-1-review` | *demo-tape* | Is this demo ready for the label? (Gate 1) |
| `start-design` | *compose* | Write the arrangement (HLD) |
| `scan-horizon` | *cue* | Producer cues the band, what's changing? |
| `start-build` | *green-light* | Green light from the label, start recording (Gate 2) |
| `plan-work` | *score* | Write out all the parts for the musicians |
| `whos-available` | *roll-call* | Who's in the studio today? |
| `set-goals` | *tracklist* | Which tracks are we recording this session? |
| `forecast` | *studio-schedule* | The master calendar, which sessions produce which tracks |
| `check-health` | *tune-up* | Tune all the instruments before recording |
| `plan-sprint` | *plan-session* | Plan the recording session, who plays what, in what order |
| `create-sprint` | *prep-booth* | Set up the recording booth (Jira sprint) |
| `start-sprint` | *session-start* | Engineer hits record, session begins |
| `end-sprint` | *session-wrap* | Session wraps, review the takes |
| `run-retro` | *listen-back* | Listen to what was recorded, discuss what worked |
| `post-updates` | *mix-notes* | Notes on each track for the producer (Pulse) |
| `log-time` | *session-log* | Log studio time per track |
| `prep-demo` | *rough-mix* | Prepare the rough mix to play for stakeholders |
| `check-launch` | *pre-master* | Pre-mastering checks before the album ships |
| `ship-it` | *album-drop* | The album drops |
| `prep-meetings` | *warm-up* | Warm up before the session |
| `review-pr` | *review-take* | Review a single take for quality |
| `setup-team` | *join-band* | New member joins the band |
| `get-help` | *help* | What can I play? Discover available skills |
| `engineer-impact-mirror` | *highlight-reel* | Your impact, reflected back with evidence |

### Rehearsal Room instruments (9)

| Instrument | Alias | What it plays |
|------------|-------|--------------|
| `improve-skill` | *rehearse* | Rehearse until tight, test skills against real data |
| `save-work` | *wrap* | That's a wrap, commit, review, ship |
| `share-summary` | *liner-notes* | The album liner notes, session summary |
| `check-repo` | *room-check* | Check the studio, everything wired right? |
| `read-history` | *playback* | Play back the master tape, study the origins |
| `start-band` | *start-band* | Start a new band, create a team folder |
| `new-skill` | *new-instrument* | Craft a new instrument from scratch |
| `record-session` | *rolling-tape* | Record a training or demo session |
| `review-recording` | *playback-session* | Review recordings, extract corrections |

## The session workflow

Every time you're in the studio:

1. **Branch.** Claude creates `session/<you>/<date>-<topic>` automatically.
2. **Record.** Run skills, lay down tracks, make progress.
3. **Wrap.** Say `wrap` to commit, review learnings, and ship via PR.

Your takes go to master. Your bandmates hear the improvements next time they pull.

## The Rehearsal Room

The `plugins/rehearsal-room/` folder is where instruments get better. These skills teach you how to improve other skills:

- **rehearse**, test a skill against real data and encode what it learns
- **wrap**, save your session and check studio health
- **room-check**, audit the entire studio setup

The Rehearsal Room is also publishable as a standalone Claude Code marketplace plugin. Bands outside this studio can install just the methodology without the FinE instruments.

## For new bands

1. Clone this repo
2. Say `join-band`
3. It creates `bands/<your-band>/` with your roster, roadmap, and empty rehearsal notes
4. It detects the FinE sheet music and configures your instruments
5. Start playing. Start rehearsing. Your rehearsal notes accumulate from every session.

Your band's style makes the instruments smarter for everyone.

## Links

- [The Rehearsal Room](plugins/rehearsal-room/), the rehearsal methodology
- [FinE sheet music](sheet-music/fine/), SDLC rules and templates
- [Otter Squad](bands/fine/otter/), reference band
