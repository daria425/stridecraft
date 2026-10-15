# ADR-0006: SQLite, SQLAlchemy, frozen gains; rebuild instead of migrations

**Date**: 2026-10-13
**Status**: accepted
**Deciders**: Daria, Claude

## Context

ADR-0003 requires per-run gains stored at first processing. The schema will change often while we
are testing, and only the author's data exists. Runs and gains are derivable from Strava plus
`adopted_at`. Strava's rate limit (about 100 calls per 15 minutes) makes repeat detail calls
costly, so sync must avoid them.

## Decision

- SQLite via SQLAlchemy 2.0, tables created with `create_all()`, no Alembic yet.
- Tables: `users` (identity and profile cache), `striders` (user, breed, name, `adopted_at`), `runs` (a
  slim copy of the `Run` fields, unique on user, source and source id, best efforts as JSON),
  `run_gains` (one row per post-adoption run, frozen).
- A run with no `run_gains` row is a baseline run. Strider stats are the strider's base values plus the sum
  of `run_gains`; no stats row is stored.
- Schema changes mean deleting the DB file and running a `rebuild` command: re-fetch from Strava,
  re-apply `adopted_at`, breed and name (passed as arguments), recompute gains with the current
  formulas.
- Sync lists Strava summaries since `last_synced_at` minus 7 days (so a late-uploaded run is
  still caught) and skips runs already stored. It processes them oldest first, committing each run
  with its gains, so re-running a sync changes nothing. Gains come from the list data alone; best
  efforts (one detail request each) are fetched for only the newest runs, and listing is bounded,
  both to stay within Strava's rate limit (see ADR-0009).
- Tokens stay in `tokens.json` for now.

## Alternatives Considered

### Alternative 1: Alembic from day one

- **Pros**: Safe for real data.
- **Cons**: SQLite's limited `ALTER TABLE` makes it clunky; slows iteration.
- **Why not**: Revisit when anyone else's data exists.

### Alternative 2: Plain `sqlite3`

- **Pros**: One less dependency.
- **Cons**: Hand-written SQL and tied to SQLite.
- **Why not**: SQLAlchemy keeps a later Postgres move cheap.

### Alternative 3: Postgres now

- **Pros**: Production-like.
- **Cons**: More setup; hosting is undecided.
- **Why not**: Not needed for a single-user start.

### Alternative 4: Recompute gains on every read

- **Pros**: No gains table.
- **Cons**: Stats would shift whenever constants are retuned.
- **Why not**: Contradicts "computed once" (ADR-0003).

## Consequences

### Positive

- Schema changes are cheap, and stats cannot drift because they are derived.
- Once a run is processed, its contribution never needs Strava again. We still keep runs as the
  42-day baseline and for the streak history.

### Negative

- Gains are frozen: a Race/Workout retag, edit or delete in Strava after sync changes nothing, and
  a late-uploaded old run does not alter later runs' gains.
- Rebuild depends on Strava history still being there, and on `adopted_at`, breed and name being
  supplied again.
- Plaintext tokens and no migrations are fine for one user but must change before others sign up.

### Risks

- Rebuild recomputes with current formulas, so rebuilt gains can differ from the frozen ones.
  Accepted while testing; stop rebuilding once the numbers matter.
