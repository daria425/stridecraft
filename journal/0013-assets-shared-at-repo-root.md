# ADR-0013: Binary assets live in a repo-root `assets/`, served by URL

**Date**: 2026-10-16
**Status**: accepted
**Deciders**: Daria, Claude

## Context

The frontend is about to exist and needs the game's binary assets (3D models, later portraits and
icons). ADR-0008 put binary assets in `server/static/`, but nothing served them. The question was
whether content should move so the frontend and server share one source and do not drift. The
YAML is a few KB and already reaches the frontend through `GET /breeds`; the models are
megabytes and are the only content that affects load time.

## Decision

YAML definitions stay in `server/content/`: the server validates them and the API is the only way
the frontend reads them, so there is one source and the generated OpenAPI types catch schema
drift. Binary assets move to `assets/` at the repo root (e.g. `assets/breeds/cetus.glb`).
`Breed.model` stays a path relative to `assets/`; the API returns `model_url`, built from
`ASSET_BASE_URL` (default: this API's `/assets` mount, for dev). In production `ASSET_BASE_URL`
can point at a CDN or static host with long-cache headers and nothing else changes.

## Alternatives Considered

### Alternative 1: Keep assets in `server/static/`

- **Pros**: Nothing moves.
- **Cons**: Assets are tied to the Python process and its deployment.
- **Why not**: Models are the heavy part and should be CDN-able.

### Alternative 2: Move YAML and assets to a repo-root `content/`

- **Pros**: Author edits a definition and its art side by side; the frontend can import both.
- **Cons**: Raw YAML in the frontend invites parsing it there and drifting from the validator;
  supersedes ADR-0008 and touches packaging and tests.
- **Why not**: Saves one tiny request on the adopt page and costs the single source.

## Consequences

### Positive

- The frontend only ever sees URLs; moving assets to a CDN is an env var.
- Content validation and rules stay in one place.

### Negative

- Definition and art are in different directories (the YAML names the asset path).
- `assets/` is not part of the server wheel (the packaging item for `server/content/` is still open).

### Risks

- Large binaries in git; revisit (Git LFS or external storage) when the first real models land.
