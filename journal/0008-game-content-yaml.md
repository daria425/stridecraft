# ADR-0008: Game content is YAML files, validated by pydantic

**Date**: 2026-10-15
**Status**: accepted
**Deciders**: Daria, Claude

## Context

Breeds, and later skills, quests, bosses and outfits, are invented content that will grow and has
to stay consistent. A breed is more than a string, and authored content should not live in the
database.

## Decision

Definitions live as one YAML file per entity at `server/content/<kind>/<id>.yaml`, and the
filename is the id. Pydantic models validate them strictly at load, and a `Content` registry holds
them in memory. The database stores only ids, as plain strings with no foreign key, validated
against the registry at adoption. Binary assets (3D models) stay in `server/static/` and are
referenced by path. Behaviour stays in code; data only parametrises it.

## Alternatives Considered

### Alternative 1: JSON files

- **Pros**: No new parser dependency.
- **Cons**: No comments, noisy to hand-edit.
- **Why not**: The author edits this content by hand and wants notes beside it.

### Alternative 2: TOML

- **Pros**: Comments, strict typing.
- **Cons**: Awkward for nested lists and tables.
- **Why not**: Skills and bosses will be nested.

### Alternative 3: Content in database tables

- **Pros**: Queryable.
- **Cons**: Needs migrations, loses code review and diffs.
- **Why not**: Content ships with the code and changes by commit.

### Alternative 4: One file per kind

- **Pros**: Fewer files.
- **Cons**: Long scrolls and noisy diffs.
- **Why not**: One file per entity is easier to read and to add to.

### Alternative 5: Dataclasses with hand-written validation

- **Pros**: Nothing new to learn.
- **Cons**: Validation code is written per kind.
- **Why not**: Pydantic comes with FastAPI anyway.

## Consequences

### Positive

- Adding content is adding a file, and bad content fails loudly at load and in CI.
- Breed (and later anything else) can grow beyond a string without a schema change.

### Negative

- Ids are permanent: renaming one breaks stored references.
- YAML's implicit typing (bare `no` becomes `False`) is covered only by strict validation.
- `server/content/` is outside the Python package, so it must be packaged for deployment.

### Risks

- Cross-references (a quest reward naming a skill that does not exist) are not checked yet; add
  the check when two content kinds reference each other.
