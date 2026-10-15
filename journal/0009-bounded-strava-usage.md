# ADR-0009: Stats come from the activity list; Strava usage is bounded

**Date**: 2026-10-15
**Status**: accepted
**Deciders**: Daria, Claude

## Context

ADR-0001 fetched a detail call per run for best efforts, because Speed was then going to use them.
ADR-0002 dropped that, so stats need only what the activity list already has. Detail calls are the
main cost against Strava's default limit (100 requests per 15 minutes, 1,000 per day), and a long
backlog could never finish. A user may be away for years before checking in, and that is not
their fault. Strava does not document the order activities come back in.

## Decision

All gains come from the list data. Only the newest 50 GPS runs from adoption on get a detail call
for best efforts; a 429 on a detail call degrades to storing the run without them. Listing goes
through 90-day windows (`before`/`after`), newest first, so nothing relies on Strava's order, and is
bounded to 25 pages (5,000 activities) per sync. Beyond that the oldest windows are dropped whole,
never half a window, and `SyncResult.truncated` is set. A sync does not fail for having too much
history.

## Alternatives Considered

### Alternative 1: A detail call for every run

- **Pros**: Every run has best efforts.
- **Cons**: Any backlog over about 95 runs fails against the rate limit and can never complete.
- **Why not**: Stats do not need best efforts.

### Alternative 2: Resumable partial syncs

- **Pros**: Nothing is lost.
- **Cons**: More machinery (a cursor, a partial state) and a "come back later" experience.
- **Why not**: It was built, then rejected as too complicated once detail calls were capped.

### Alternative 3: Fail when there is too much history

- **Pros**: Simple.
- **Cons**: Blames the user for something they cannot fix.
- **Why not**: The app should cope, and at most mention it.

### Alternative 4: A plain page cap on a single listing

- **Pros**: Simplest bound.
- **Cons**: With an undocumented order it keeps an arbitrary subset, possibly the oldest.
- **Why not**: Windows give a deterministic "newest kept" whatever the order.

## Consequences

### Positive

- A sync always finishes in one pass. A two-year absence is about a dozen list requests.
- Supersedes the detail-call part of ADR-0001.

### Negative

- Someone with more than 5,000 activities since the last sync loses their oldest runs for good,
  as the sync cursor moves on.
- Runs stored without best efforts are never upgraded, so PB skills only see recent runs.
- Gains maths rescans history per run (quadratic): fine for thousands of runs, slow beyond.

### Risks

- The constants (50, 25 pages, 90 days) are first guesses; Strava's limits may differ for the
  author's app, so check them in Strava's API settings.
