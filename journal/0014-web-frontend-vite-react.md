# ADR-0014: Vite + React SPA; sync on open and tab focus until the webhook

**Date**: 2026-10-16
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The API (ADR-0012) needs a web frontend before progression features. The first pass is structure
only: login, adoption (with an easily iterated creature picker) and a dashboard, with a square
where the 3D strider will go. Nothing syncs automatically today: imports run on adoption and on
`POST /me/sync`. Strava cannot push to the browser; only the server can learn of a run, by
polling Strava or by webhook.

## Decision

`web/` is a Vite + React + TypeScript SPA using react-router and TanStack Query, with types
generated from the API's OpenAPI spec (`openapi-typescript` + `openapi-fetch`, `npm run gen:api`).
Visuals are deferred: the first pass is unstyled with design tokens in one CSS file, and a
PRODUCT.md / DESIGN.md will drive the design pass. Until the webhook phase the dashboard syncs
by itself when it opens and when the tab regains focus, if the last sync is older than 10
minutes; there is no sync button. Stats do not depend on sync timing (gains are computed oldest
first against stored runs, with a 7-day look-back), so this loses nothing but freshness.

## Alternatives Considered

### Alternative 1: Server-side stale check inside `GET /me`

- **Pros**: Frontend only polls.
- **Cons**: A read endpoint with a side effect; changes API behaviour.
- **Why not**: The hook is small and the webhook replaces it.

### Alternative 2: Webhook now

- **Pros**: Fresh data with the app closed; needed anyway for delete-on-deauth.
- **Cons**: Needs a public URL and subscription management; not needed for one user.
- **Why not**: Deferred to its own phase. It would not refresh an open page by itself either:
  the page would still need to poll.

## Consequences

### Positive

- The full loop (login, adopt, import, stats) works in a browser with no backend changes beyond
  ADR-0013.
- The picker (`BreedPicker`), the 3D slot (`CreatureSlot`) and the tokens are each one file.

### Negative

- A run edited in Strava after it was synced (retagged Race/Workout) is not picked up; only a
  webhook update event could do that.
- TypeScript is pinned to 5.9 because `openapi-typescript` does not support 6 yet.

### Risks

- Generated `schema.d.ts` is committed; it must be regenerated when the API changes.
