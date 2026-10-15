# ADR-0011: Scale all stat constants x20, uniformly

**Date**: 2026-10-15
**Status**: accepted
**Deciders**: Daria, Claude

## Context

With the first-guess constants, a strider adopted in January (87 counted runs) ended at Speed
10.46, Endurance 10.97, Hills 10.53, Consistency 10.31, while one adopted in September (23
counted runs) sat between 10.15 and 10.27. Growth was proportional to training, but everything
is added onto a base of 10, so the whole spread was under one point (under 10% of the base) and
striders barely looked different. Endurance grows about twice as fast as the other stats,
because distance pays on every run.

## Decision

Multiply every gain constant by 20 (`BASE_ADD`, `PACE_K`, `TRAINING_BONUS`, `KM_ADD`,
`LONG_RUN_K`, `METRES_ADD`, `STREAK_ADD`). The base stays 10. Relative differences between
runs, stats and striders are unchanged; only their size against the base grows. Endurance
outgrowing the other stats is accepted as intended: humans are naturally better at stamina than
speed (see [persistence hunting](https://en.wikipedia.org/wiki/Persistence_hunting)), an ultra
runner should be ahead on Endurance, and a sprinter is fast without regular 20-milers.

## Alternatives Considered

### Alternative 1: Tune each stat separately so all four grow at similar rates

- **Pros**: Balanced stats for a typical runner.
- **Cons**: Needs a target for "balanced", and erases the stamina-over-speed character.
- **Why not**: Endurance leading is a feature for now. Revisit per stat if it becomes a problem.

### Alternative 2: Lower the base value instead of raising the constants

- **Pros**: Same effect on relative spread, constants stay small.
- **Cons**: Changes what a fresh strider looks like, and docs and content assume a base of 10.
- **Why not**: Scaling the constants is the smaller change.

## Consequences

### Positive

- Training history now visibly separates striders (the January run would land at roughly
  Speed 19, Endurance 29, Hills 20.5, Consistency 16).
- Tests assert relationships (ADR-0004), so none needed changing.

### Negative

- Already-stored `run_gains` are frozen at the old scale; existing databases need
  `reset` and a fresh `adopt` (ADR-0006).

### Risks

- 20 is still a guess. Retuning is a one-line change per constant, plus `docs/stats.md`.
