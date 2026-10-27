# How runs flow into strider stats

Plain-language reference. Reasoning lives in `journal/` (ADR-0003, 0005, 0006); the maths in
`docs/stats.md`.

## Onboarding

```
GET /auth/strava/login -> Strava -> GET /auth/strava/callback
   |- user created or fetched by Strava athlete id, tokens stored encrypted, cookie set
   '- redirect to the frontend
GET /me -> strider?
   |- yes -> dashboard
   '- null -> adoption page: GET /breeds, GET /names/random
                POST /me/strider {breed, name}
                |- create strider: adopted_at = now
                '- background import (GET /me/sync shows progress):
                     fetch Strava runs from (adopted_at - 42 days) to now
                     before adopted_at -> baseline only, no gains
                     after adopted_at  -> processed like any synced run
```

The dashboard also starts an import when it opens or the tab regains focus and the last one is
over 10 minutes old (journal/0014); no button, until a webhook exists.

Imports run one at a time across all users, because Strava's rate limits belong to the app.

## What a run is worth

Gains are computed once, the first time a run is seen, from the run itself (distance, time,
elevation, Race/Workout tag) and the stored runs before it (the previous 42 days for the Speed and
Endurance baselines; run counts per week since adoption for the Consistency streak). The four
numbers are saved in `run_gains` and never recomputed.

## Stats

```
stat = strider base value + SUM of that column over run_gains
```

Nothing stores "current stats". Gains are never negative, so stats only go up. The model is
additive; a run's gain depends on earlier runs only through the baseline and the streak.

## Sync

1. List Strava summaries since `last_synced_at` minus 7 days (so late uploads are caught), in
   90-day windows, newest first. Strava does not document its result order, so we never rely on it.
   The list alone has what every stat needs (distance, time, elevation, Race/Workout tag). A user
   away for two years is about a dozen requests. Each sync lists at most 25 pages (5,000
   activities); beyond that the oldest windows are dropped whole (never half a window) and the
   result is flagged `truncated`, so the app can mention it. The sync does not fail.
2. Skip runs already stored (unique on user, source, source id).
3. Sort the new runs oldest first. For each, compute gains against stored runs plus the earlier
   runs just processed, and commit the run and its gains in one transaction. Baseline runs
   (before adoption) are stored without gains.
4. A run after adoption also moves the strider along the journey (ADR-0017), in the same
   transaction as its gains: the total distance of all runs with gains is compared with the
   strider's next waypoint (the last crossing's threshold plus its `waypoint_spacing_km`). Each
   waypoint reached is turned into a scene (the leg's landmark, or a random encounter that fits the
   leg and was not shown lately) and stored with its text. Crossing a landmark also rolls which leg
   comes next. Distance is never stored, only these crossings.
5. Best efforts (for PBs) need one detail request per run, and Strava allows about 100 requests
   per 15 minutes. So only the newest 50 GPS runs from adoption on get the detail call; the rest
   are stored without best efforts. If Strava still answers 429, the sync carries on without
   details: stats never depend on them.
6. Re-running a sync changes nothing.

A run starting before `adopted_at` is baseline even if uploaded later.

## Known limits

- Gains and journey crossings are frozen: retagging, editing or deleting a run in Strava after
  sync changes nothing.
- A late upload with an old start time does not change gains already stored for later runs.
- A run that shows up in Strava with a start time more than 7 days before the previous sync is
  never fetched until a rebuild.
- A truncated sync never imports the dropped (oldest) runs later, as the sync cursor moves on.
- Runs stored without best efforts are not upgraded later, so they can't trigger PB skills.
- Gains cost grows with the square of the run count (each run rescans history): fine for
  thousands of runs, slow beyond that.
- Schema changes use wipe-and-rebuild (re-fetch from Strava, recompute), not migrations.
