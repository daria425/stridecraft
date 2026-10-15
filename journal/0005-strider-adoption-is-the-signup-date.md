# ADR-0005: Strider adoption is the sign-up date

**Date**: 2026-10-13
**Status**: accepted
**Deciders**: Daria, Claude

## Context

ADR-0003 counts only runs after "sign-up" and asks for a `created_at` on the user. But the strider is
its own creature that grows from training alongside you, and onboarding is: no strider yet, so pick
one, then start. Logging in with Strava and adopting a strider can be different moments.

## Decision

The counting date is `adopted_at` on the strider, set when the user adopts it by picking a breed and a name. The user row
holds only identity and a cached profile (username, name, picture URL). Adoption triggers a fetch of the
42 days before it, stored as baseline runs with no gains. Onboarding checks "has a strider?" and
redirects to strider adoption if not. This supersedes the "`created_at` on the user" wording in
ADR-0003 and CLAUDE.md.

## Alternatives Considered

### Alternative 1: `created_at` on the user (Strava login date)

- **Pros**: Simple; one fewer table.
- **Cons**: Runs between login and picking a strider would count for a strider that did not exist yet.
- **Why not**: The strider is what grows, so its adoption is the start.

### Alternative 2: Count from Strava account creation

- **Pros**: Needs no date of our own.
- **Cons**: Would let years of history count.
- **Why not**: Contradicts "the strider is not you" (ADR-0003).

## Consequences

### Positive

- One clear date, and a standard onboarding gate.

### Negative

- The strider needs its own table (user, breed, name, `adopted_at`, unique per user).
- The adoption UI is a later phase, so for now these values are passed in via the CLI.

### Risks

- A user could adopt a strider long after logging in; runs in between are baseline only. That is
  intended, but worth remembering when it looks like "missing" progress.
