# ADR-0018: A 3D voyage map, a once-only arrival banner, and a dev endpoint to cross waypoints

**Date**: 2026-10-27
**Status**: accepted
**Deciders**: Daria, Claude

## Context

ADR-0017 built the journey in the backend with no UI. The flow needs designing: how a crossing is shown
the moment the user arrives, and what the road looks like. Encounter text is still being written, so
the UI had to be buildable and iterable without real runs.

## Decision

**One 3D map, the voyage.** `/voyage` draws the *current leg's* road (the start, then the leg's waypoints,
the last being the landmark) on a floating Greek isle in React Three Fiber, with slow clouds drifting
around and beneath it. It is reached from a top menu with two entries, Strider and Voyage, on the dashboard
and on the map. Everything is procedural primitives, so there are no new asset files; the strider token is
the real breed model. Three variants were built first (the isle, a desert of ruins, Aegean cliffs); the
isle was kept and the others, with the scenery only they used, were removed. The scene code is split so
another map can be added by writing terrain and scenery only (`maps/MapCanvas`, `RoadLayer`, `road`).

**The map's data is `GET /me/journey`.** Two additive fields, `leg_length` and `leg_waypoint`, say how
long the leg is and which stop is next, so the client never infers them. `buildLegMap` (pure, tested)
turns it into stops.

**Arrival banner.** A crossing is "new" until the user has been shown it. This is stored on the server,
as `striders.journey_seen_waypoint` (the highest crossing shown), so it appears once on every device;
`POST /me/journey/seen` moves it forward only and never past the newest crossing. `JourneyArrivals`
shows unseen crossings oldest first (title and text from the YAML, "Waypoint N" or "Landmark reached"),
one dismissal each, on the dashboard and the map. Until dismissed, a stop stays unrevealed on the map (no
spoiler) and the strider waits at the last stop seen; dismissing makes it walk there.

**Dev endpoint** (`DEV_TOOLS=1`): `POST /me/journey/advance?waypoints=N` stores a made-up run of exactly
the distance to the next waypoint with an all-zero gains row, then calls `JourneyService.record()` like a
sync would. So the scene is genuinely rolled and frozen, distance and crossings stay consistent, no stat
moves, and `StriderReset` removes the run with the rest. Reload to see the banner.

## Alternatives considered

- **Seen state in the browser (localStorage):** no schema change, but per device, so it would replay.
- **Writing a `JourneyEvent` directly in the dev endpoint:** simpler, but distance and crossings would
  disagree, against ADR-0017's "distance is derived".
- **Painted 2D or SVG maps:** lighter, but less like the 3D references. Three.js is already a dependency.
- **Keeping several map styles in the menu:** useful to compare, but the menu is for the game, not for
  design previews. The ruins and cliffs scenes can be recovered from git history if wanted.

## Consequences

- A new column on `striders`: the database must be rebuilt (ADR-0006).
- The dev run has `source = "dev"`, a made-up distance and pace, and counts in the six-week pace
  baseline until reset. Fine for development; do not use it against real data you want to keep.
- Terrain is generated at load and cached by `useMemo`. Frame rate on a real GPU is unchecked.
- The strider's facing while walking assumes a model forward axis (`MODEL_FORWARD_OFFSET` in
  `RoadLayer.tsx`); revisit with the animation work from ADR-0016.
- Quests and trophies will attach to stops later (ADR-0017); the markers already carry the node.
