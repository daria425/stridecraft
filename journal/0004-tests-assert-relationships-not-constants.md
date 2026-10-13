# ADR-0004: Stat tests assert relationships, not tuned constants

**Date**: 2026-10-13
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The stats calculator had 15 tests. Several re-implemented the formula with the constants copied
in (for example `0.002 + 0.1 * (6 / 5.4 - 1) + 0.004`), and a pair of scenario tests added up
expected totals for a month of runs. The constants in `docs/stats.md` are first guesses to be
tuned against real data, so each retune would break about 4-5 tests at once. Those tests only
proved the code equals itself. Updating them forever, or living with failing tests, would defeat
the point of having tests.

## Decision

Stat tests assert relationships and rules, never the value of a tuned constant: faster gains more
than slower, a training tag adds on top of the base, 200 m climbs twice what 100 m does, a second
good week pays more than the first, no gain is negative. Exact worked numbers live in
`docs/stats.md`, not in tests.

## Alternatives Considered

### Alternative 1: Keep exact-number tests and update them on every retune

- **Pros**: Catches any accidental change to a formula or constant.
- **Cons**: Constant churn is expected, so the updates become busywork or the tests get ignored.
- **Why not**: A test that fails on every intentional change carries no signal.

### Alternative 2: Import the constants into the tests

- **Pros**: Tests would follow tuning automatically.
- **Cons**: The constants are deliberately local to each function (see the note at the top of
  `stats_calculator.py`), and the expected value would just mirror the implementation.
- **Why not**: It breaks the project convention and still tests the formula against itself.

## Consequences

### Positive

- Retuning constants should not break any test; failures mean a rule or relationship changed.
- 23 tests became 20. Removed or rewritten: the formula-mirroring scenario tests, the
  empty-input test (covered by the sign-up test) and the "stats never drop" test (replaced by a
  direct check that no gain is negative).

### Negative

- An accidental constant change (say `PACE_K` 0.1 to 0.01) is no longer caught by a test; only
  `docs/stats.md` and review catch it.
- Relative assertions are slightly less obvious to read than a literal expected number.

### Risks

- A relationship test could pass for the wrong reason. Mitigation: keep each to one clear rule,
  and add a case when a real bug slips through.
