# ADR-0001: Strava fetch: 42-day window, detail calls for best efforts

**Date**: 2026-10-12
**Status**: partly superseded by ADR-0009 (detail calls are now capped; the 42-day baseline window stays)
**Deciders**: Daria, Claude

## Context

Stats are a rolling window of recent performance (~6 weeks), and Speed needs best efforts per
distance band. Strava's activity list returns summaries only; `best_efforts` (1K, 5K, 10K, ...)
exist only on the single-activity detail endpoint, one API call per run. Strava rate limits are
100 requests per 15 minutes. The author has years of old logs that are irrelevant to the game.

## Decision

Fetch only runs from the last `STATS_WINDOW_DAYS` (42, one constant in `config.py`), then call
the detail endpoint for each of them to get `best_efforts`. Older history is not imported.

## Alternatives Considered

### Alternative 1: Import full history

- **Pros**: Complete record; PB and quest triggers could look back further.
- **Cons**: Hundreds of detail calls against the rate limit; old logs are irrelevant to stats.
- **Why not**: Strava's `pr_rank` on best efforts is computed against all-time history, so
  "this was a PB" triggers work without importing old runs.

### Alternative 2: Compute bests ourselves from streams/splits

- **Pros**: Works for any source and any distance.
- **Cons**: More API calls and our own best-segment maths to write and test.
- **Why not**: Strava already provides this; revisit if other sources are added.

## Consequences

### Positive

- Small, cheap sync (about 30 detail calls for 28 runs); window tunable in one place.

### Negative

- Anything needing history beyond the window (long streaks) cannot be derived from imported runs.

### Risks

- Treadmill runs (`trainer: true`) have no GPS and returned empty `best_efforts` in the author's
  data (12 of 28 runs), so they have no PB flags. Accepted: PBs only come from Strava's data
  (ADR-0002). The detail call could be skipped for them.
