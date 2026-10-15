# ADR-0012: FastAPI REST API, "log in with Strava" via Authlib and a session cookie

**Date**: 2026-10-15
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The CLI was single-user glue (one `tokens.json`, `UserRepository.first()`). The product is a web
app with an onboarding flow: log in, get a user, adopt a strider if there is none, import runs.
Strava is the only identity we need, and we also need each user's Strava tokens to read their
runs. Daria wants to touch auth as little as possible and not hand-roll any of it.

## Decision

Add a FastAPI app (`stridecraft/api/`) with a generated OpenAPI spec (`/docs`, `/openapi.json`).
Login is Authlib's Strava OAuth flow plus Starlette's signed-cookie `SessionMiddleware`; there is
no password, JWT or account system. Strava tokens are stored per user in the database,
encrypted with Fernet (key from `TOKEN_ENCRYPTION_KEY`). Routes are owner-scoped under `/me`
(no ids in URLs), the user is created-or-fetched in the OAuth callback, and `GET /me` returns the
user with `strider: null` until they adopt, which is the frontend's cue to redirect. Adopting
imports runs in a background task; `GET /me/sync` reports progress. Imports run one at a time
app-wide because Strava's rate limit is per app. The CLI stays as a single-user dev util.

## Alternatives Considered

### Alternative 1: Auth0 / Clerk in front of Strava

- **Pros**: Email/password, other social logins, MFA for free.
- **Cons**: A second user store and an extra hop, and we would still run Strava OAuth ourselves
  to get API tokens.
- **Why not**: Strava is the identity; nothing is removed from our side. Revisit if non-Strava
  login is wanted; the change would be confined to `routers/auth.py` and `deps.current_user`.

### Alternative 2: JWT bearer tokens

- **Pros**: Easier for non-browser clients.
- **Cons**: The frontend must store the token; harder to revoke.
- **Why not**: Only a same-site web frontend exists; a cookie is less code.

### Alternative 3: Import synchronously inside `POST /me/strider`

- **Pros**: No status model.
- **Cons**: Tens of seconds per request; proxy timeouts.
- **Why not**: Background task plus a status endpoint.

## Consequences

### Positive

- The whole onboarding flow is five calls and is documented by the generated spec.
- Users are isolated by construction: every route reads the user from the session.

### Negative

- Import status is in memory (one process); a restart resets it to idle (the next sync catches
  up, since imports are idempotent).
- New Strava apps are limited to one athlete until Strava raises the capacity, so other users
  cannot log in until Daria requests that.
- Weeks are still Monday-start in UTC, so Consistency is slightly off for runners in other time
  zones. Not fixed here.
- Deleting a user's data when they revoke Strava access is not built (webhook phase).

### Risks

- Losing `TOKEN_ENCRYPTION_KEY` makes stored tokens unreadable; users would have to log in
  again (nothing else is lost). There is no key rotation yet.
