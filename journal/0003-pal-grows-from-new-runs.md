# ADR-0003: The pal grows only from post-sign-up runs; stats never decay

> **Terminology note:** "pal" in this ADR is now called a **strider** (ADR-0007). The text is left as written.

**Date**: 2026-10-13
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The first plan made Endurance, Hills and Consistency a rolling 6-week window of the user's real
performance that decayed, and let users override the training flag in the app. ADR-0002 already
made Speed a never-decaying running total. The product idea is that the pal is its own creature
(as in Pokemon or Palworld) and grows because you train together. Checking whether Strava synced
and whether the pal shrank would be too high-touch for the user.

## Decision

All four stats are running totals that start at the pal's own base values and never decay. Only
runs after the user's sign-up date add to any stat. Earlier runs only supply the baseline, such as
the 6-week average pace for Speed. The training flag comes only from Strava (Race or Workout),
with no in-app override. Consistency is rewarded by growing the Consistency stat and by unlocking
skills, not by penalising gaps.

## Alternatives Considered

### Alternative 1: Rolling window with decay for Endurance, Hills and Consistency

- **Pros**: Stats reflect current form; stopping training has a visible effect.
- **Cons**: Punishes breaks and illness; pushes users to check the app and whether Strava synced.
- **Why not**: It conflicts with the effortless-UX principle.

### Alternative 2: Pre-sign-up runs count toward the stats

- **Pros**: The pal's stats are meaningful on day one.
- **Cons**: The pal would mirror the user instead of being its own creature.
- **Why not**: "The pal is not you."

### Alternative 3: In-app training-run toggle with override

- **Pros**: Fixes runs the user forgot to tag in Strava.
- **Cons**: Extra logging in the app, and it was only needed to compensate for Speed decay.
- **Why not**: Every run already adds to Speed, so an untagged run loses little.

## Consequences

### Positive

- Simple model: a stat is a base plus the sum of per-run contributions, with nothing to recompute
  on a sliding window.
- No manual logging; breaks never hurt the pal.

### Negative

- Stats only grow, so they stop reflecting current form, and grinding is accepted.
- Per-run contributions depend on earlier runs, so they should be stored when the run is first
  processed. This needs persistence (a sign-up date and a stored contribution per run). The
  sign-up date is `adopted_at` on the pal, not a `created_at` on the user (ADR-0005; storage in
  ADR-0006).
- Needs a per-run contribution rule for each of Endurance, Hills and Consistency, and the
  constants are not decided yet.
- Supersedes the decay parts of CLAUDE.md; refines ADR-0002.

### Risks

- With no decay or cap, stats could grow without limit, so we may need a cap or diminishing
  returns; to be tuned with real numbers.
