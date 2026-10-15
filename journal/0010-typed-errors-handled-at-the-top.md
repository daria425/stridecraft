# ADR-0010: Expected errors are typed, UI-neutral, and caught at the top level

**Date**: 2026-10-15
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The first sync code raised plain exceptions with CLI hints in the message ("run `adopt`", "use a
later --adopted-at"). The CLI is temporary and the real caller will be an API route returning a
message to a frontend, where those hints are meaningless or wrong.

## Decision

All expected failures subclass `StridecraftError` in `stridecraft/errors.py` (`StravaError`,
`RateLimitError`, `NotAuthorizedError`, `NoStriderError`, `AdoptionError`) with plain-English
messages that never mention commands or flags. Services raise them. The top level (the CLI now,
the API route later) catches the base class and decides status codes and wording, for example
`NotAuthorizedError` means "reconnect Strava". Unexpected exceptions are not wrapped.

## Alternatives Considered

### Alternative 1: Built-in exceptions with a hint in the message

- **Pros**: Nothing to define.
- **Cons**: The hint is wrong for an API; callers must parse messages to tell cases apart.
- **Why not**: Meant for one caller only.

### Alternative 2: Exception classes per module with no common base

- **Pros**: Each lives next to its code.
- **Cons**: A route needs a long except list and a new error is easy to forget.
- **Why not**: One module and one base class is the single place to map.

## Consequences

### Positive

- One place for the API to map errors to responses.
- A revoked or expired Strava login (likely after a long absence) is a typed case the frontend
  can turn into "reconnect Strava".

### Negative

- A new expected failure must be added as a type, not raised ad hoc.

### Risks

- Mapping gaps: an unmapped expected error would surface as a 500 until it is handled.
