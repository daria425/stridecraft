# ADR-0002: Speed is a running total: base add plus pace bonus

**Date**: 2026-10-12
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The first plan derived Speed from best efforts or splits through a predictor-style formula over a
rolling 6-week window, so it decayed and only training-flagged runs counted. That needs per-run
detail calls, is empty for treadmill runs (no GPS, so no `best_efforts`), and mostly sits flat
for a runner who logs easy runs. The product idea is that training becomes the pal's power, and
any run should add something.

## Decision

Speed starts at 10 and never decays. Every run adds a small base amount (about 0.002). If the
run's average pace beats the average pace of the previous 6 weeks (total distance / total moving
time of earlier runs), it also earns a pace bonus, starting formula
`k * max(0, run_speed / avg_speed - 1)`. Training-flagged runs get an additional bonus (size TBD).
With no earlier runs there is no pace bonus. Grinding (many short runs) is accepted. PBs come from
Strava's `pr_rank` on `best_efforts` only.

## Alternatives Considered

### Alternative 1: Predictor score from best efforts (Riegel)

- **Pros**: Reflects real race fitness across distances.
- **Cons**: Empty for treadmill runs, needs a detail call per run, hard to explain.
- **Why not**: Too complex for the product idea.

### Alternative 2: Best lap or `splits_metric`

- **Pros**: Covers treadmill runs.
- **Cons**: Laps depend on watch settings; splits cover 1 km only and use fixed boundaries.
- **Why not**: Same complexity for a narrower signal.

### Alternative 3: Own best efforts from streams

- **Pros**: Any distance, treadmill included.
- **Cons**: Pause handling, interpolation, and an algorithm to write and maintain.
- **Why not**: More than the product needs.

### Alternative 4: Count `pr_count` as PBs

- **Pros**: Cheap.
- **Cons**: It tracks segment PRs (route-dependent), not distance PBs; 0 on treadmill.
- **Why not**: Does not measure performance.

## Consequences

### Positive

- Speed needs only distance and moving time, so treadmill runs count fully.
- Simple, easy to unit-test and explain.

### Negative

- Speed can be grown by running more; accepted.
- A run's contribution depends on earlier runs, so it should be stored when the run is first
  processed and not recalculated on every sync.
- Reverses three earlier CLAUDE.md decisions: Speed decay, "can't be grinded", and easy runs
  never touching Speed.

### Risks

- Constants (base add, `k`, training bonus) may feel wrong; tune after seeing real numbers.
