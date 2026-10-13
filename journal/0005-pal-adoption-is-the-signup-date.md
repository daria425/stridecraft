# ADR-0005: Pal adoption is the sign-up date

**Date**: 2026-10-13
**Status**: accepted
**Deciders**: Daria, Claude

## Context

ADR-0003 counts only runs after "sign-up" and asks for a `created_at` on the user. But the pal is
its own creature that grows from training alongside you, and onboarding is: no pal yet, so pick
one, then start. Logging in with Strava and adopting a pal can be different moments.

## Decision

The counting date is `adopted_at` on the pal, set when the user picks a fighter. The user row holds
only identity and a cached profile (username, name, picture URL). Adoption triggers a fetch of the
42 days before it, stored as baseline runs with no gains. Onboarding checks "has a pal?" and
redirects to fighter selection if not. This supersedes the "`created_at` on the user" wording in
ADR-0003 and CLAUDE.md.

## Alternatives Considered

### Alternative 1: `created_at` on the user (Strava login date)

- **Pros**: Simple; one fewer table.
- **Cons**: Runs between login and picking a pal would count for a pal that did not exist yet.
- **Why not**: The pal is what grows, so its adoption is the start.

### Alternative 2: Count from Strava account creation

- **Pros**: Needs no date of our own.
- **Cons**: Would let years of history count.
- **Why not**: Contradicts "the pal is not you" (ADR-0003).

## Consequences

### Positive

- One clear date, and a standard onboarding gate.

### Negative

- The pal needs its own table (user, fighter, `adopted_at`, unique per user).
- The fighter-selection UI is a later phase, so for now these values are passed in via the CLI.

### Risks

- A user could adopt a pal long after logging in; runs in between are baseline only. That is
  intended, but worth remembering when it looks like "missing" progress.
