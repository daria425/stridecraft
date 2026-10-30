# ADR-0019: A profile page, and resetting a profile is a real feature

**Date**: 2026-10-30
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The only way to start over (a fresh strider, fresh stats and journey) was `DELETE /me/strider`, a dev-only
tool behind `DEV_TOOLS=1`, or nuking the database. Players need it too: it is how they choose a new strider.
There was also no page that showed the strider and its progress in one place.

## Decision

**`/profile`** shows the trainer's name, the strider in a gilt card with its name, a stats table, and the
current leg with the last encounter. A "View profile" link sits in the dashboard bar.

**Reset is a product endpoint.** `DELETE /me/strider` moved from the dev router to `me`, always registered.
It deletes the strider (and so its waypoint spacing), journey events, runs, run gains and the sync time;
the user and their Strava login stay. The frontend confirms first ("This resets all voyage progress. Are
you sure you want to continue?"), calls it, and invalidates `me`: `strider` is then `null` and the existing
gate sends the user to adoption. No special redirect.

**`GET /me/profile`** returns totals over runs *counted since adoption* only (runs with gains): run count,
training runs, voyage distance, elevation gain. Earlier runs are baseline and never shown as totals, in line
with ADR-0005; Strava already shows lifetime numbers.

**A breed `icon`** (a still image under `assets/`, served as `icon_url` on `GET /breeds`) is used for the
profile portrait. Breeds without one fall back to the live creature renderer.

## Alternatives Considered

- **Capture the 3D canvas to PNG in code:** fiddly, and the author can choose a better angle by hand.
- **Keep reset dev-only:** players could never pick a different strider.

## Consequences

- Reset is destructive and cannot be undone; the confirm dialog is the only guard.
- A reset during a running import returns 409 until it finishes.
- Personal bests are not on the profile: best efforts exist for only the newest 50 runs.
