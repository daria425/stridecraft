# How runs flow into pal stats

Plain-language reference. Reasoning lives in `journal/` (ADR-0003, 0005, 0006); the maths in
`docs/stats.md`.

## Onboarding

```
open app -> user has a pal?
              |- yes -> dashboard
              '- no  -> pick a fighter (one time)
                         |- create pal: fighter, adopted_at = now
                         |- fetch Strava runs from (adopted_at - 42 days) to now
                         '- store them all in `runs`
                              before adopted_at -> baseline only, no gains
                              after adopted_at  -> processed like any synced run
```

## What a run is worth

Gains are computed once, the first time a run is seen, from the run itself (distance, time,
elevation, Race/Workout tag) and the stored runs before it (the previous 42 days for the Speed and
Endurance baselines; run counts per week since adoption for the Consistency streak). The four
numbers are saved in `run_gains` and never recomputed.

## Stats

```
stat = pal base value + SUM of that column over run_gains
```

Nothing stores "current stats". Gains are never negative, so stats only go up. The model is
additive; a run's gain depends on earlier runs only through the baseline and the streak.

## Sync

1. List Strava summaries since `last_synced_at` minus a day of overlap.
2. Skip runs already stored (unique on user, source, source id).
3. Fetch details only for new runs (saves rate limit, gives best efforts).
4. Sort by start time; for each run compute gains against stored runs plus earlier runs in the
   batch, and insert the run and its gains in one transaction.
5. Re-running a sync changes nothing.

A run starting before `adopted_at` is baseline even if uploaded later.

## Known limits

- Gains are frozen: retagging, editing or deleting a run in Strava after sync changes nothing.
- A late upload with an old start time does not change gains already stored for later runs.
- Schema changes use wipe-and-rebuild (re-fetch from Strava, recompute), not migrations.
