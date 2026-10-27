# ADR-0017: An endless journey: authored legs rolled in turn, filled with random encounters

**Date**: 2026-10-25
**Status**: accepted
**Deciders**: Daria, Claude

## Context

ADR-0015 proposed a journey of authored waypoints at fixed kilometre marks, ending in a boss. Working
through the first build showed two problems. A finite road is a dead end: at a 50 km spacing six
waypoints is about 300 km, a couple of months of running. And writing a whole new journey every time
the old one ends is a lot of pressure for a side game people only want to run alongside. Runners also
differ a lot in weekly distance, so one fixed spacing suits few of them. Prior art that never dead-ends
(Zombies, Run!'s repeatable runs, roguelike event pools such as Slay the Spire and FTL, Fallen London's
"storylets") pairs a small authored spine with a large pool of tagged scenes drawn at random.

## Decision

The journey is endless. A **journey** is a set of **legs** (regions with tags), each a fixed number of
waypoints ending in an authored **landmark**. The road starts in the first leg; when a landmark is
crossed the next leg is rolled from the others (the same one again only if it is the only leg), so the
road loops without end and every leg's tags get their turn. A **waypoint** sits every `waypoint_spacing_km`, a number each user chooses once at adoption (50 to 1000,
default 50). Crossing one rolls a scene: a landmark, or an **encounter** (a template with `{slots}`,
tags and a weight) whose tags overlap the leg's, not repeated within the last few. The scene's text is
stored on the crossing event and never rewritten, as is the leg rolled at a landmark. Distance is derived
from the runs; only crossings are stored, with their place in the leg. Encounter variables are flavour only: no numbers or targets, which belong to quests and challenges.

## Alternatives Considered

### Alternative 1: A finite journey with fixed km marks (ADR-0015 as written)

- **Pros**: Simple, fully authored, a clear ending.
- **Cons**: A dead end after weeks; one pace for every runner; a new journey must be written to continue.
- **Why not**: The side-game feel needs a road that just keeps going.

### Alternative 1b: One open-ended final leg

- **Pros**: Simple; the next leg follows from the waypoint number alone, nothing extra to store.
- **Cons**: After the authored legs a runner is stuck with one leg's tags and sees a small fraction of
  the encounters for ever.
- **Why not**: Found while building: rolling the next leg keeps all the content in play.

### Alternative 2: Chapters that auto-continue

- **Pros**: Every chapter is fully authored.
- **Cons**: Needs a new chapter written before each user finishes the last; an "uncharted" gap otherwise.
- **Why not**: The same authoring pressure, only later.

### Alternative 3: Replay laps of the same road

- **Pros**: No extra writing.
- **Cons**: The same few scenes repeat and go stale.
- **Why not**: Random pools give variety at the same cost per scene.

### Alternative 4: Pure random scenes, no authored spine

- **Pros**: Smallest engine.
- **Cons**: No sense of place or arrival, which is the NyxQuest-like feel the game is after.
- **Why not**: Legs and landmarks stay as the thin authored spine.

### Alternative 5: AI generates scenes at runtime

- **Pros**: Unlimited variety.
- **Cons**: Lore drift, cost, non-determinism; ADR-0015 already decided AI tailors rather than authors.
- **Why not**: Not decided against for good: AI-written encounter templates, reviewed and saved as YAML,
  fit this design unchanged. Runtime generation does not. Left for a later ADR.

## Consequences

### Positive

- No dead end; new fun content is one more YAML file, joining every leg that shares a tag.
- Each runner sets their own pace through the same story.
- Quests later attach as an optional field on an encounter or landmark without reshaping the journey.
- Distance stays derived (as stats are), so it cannot drift from the runs.

### Negative

- The spacing is a per-user setting the pace of the story depends on; a poor choice means too many
  or too few scenes. It is fixed at adoption for now.
- With few legs the same fixed landmarks come round often (two legs: every 12 waypoints); more legs fix it.
- Random scenes feel generic unless the pool is large and well written (placeholder content only today).
- Which leg a strider is in can no longer be derived from the waypoint number (it was rolled), so it is
  stored on the events. New columns and table, so the database is rebuilt (ADR-0006).

### Risks

- A late upload or retagged run does not change crossings already recorded, the same known limit as gains.
- Spacing is validated in the server (`services/adoption.py`) and mirrored in the adoption page, so
  the two can drift; the server is the authority.
