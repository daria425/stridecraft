# ADR-0007: Pals become striders, with a breed and a name

**Date**: 2026-10-15
**Status**: accepted
**Deciders**: Daria, Claude

## Context

"Pal" is Palworld's own concept, and the game should have its own identity. Earlier ADRs also
talked about a "fighter" chosen from a set of designs, which was loose wording for the same thing.
The creatures are drawn from Greek mythology (the first reference is Cetus) and will be 3D models.

## Decision

The user's creature is a **strider**. Each strider has a `breed` (a string key such as `"cetus"`,
one of the Greek-myth breeds) and a required `name`. All striders still start with identical
stats; the breed is looks only for now. At adoption the app suggests a random name from
`server/static/names_src.json` (a util picks one) and the user may edit it. The table holds
`id`, `user_id` (unique), `breed`, `name`, `adopted_at`. "Fighter" is no longer a term.

## Alternatives Considered

### Alternative 1: Keep "pal"

- **Pros**: No renaming.
- **Cons**: Palworld's term; weak identity for our own game.
- **Why not**: The author wants the game to stand on its own.

### Alternative 2: Nullable name

- **Pros**: Skips a step at adoption.
- **Cons**: Every screen needs a fallback.
- **Why not**: A suggested default makes a required name painless.

### Alternative 3: `species` instead of `breed`

- **Pros**: More familiar from Pokemon.
- **Cons**: All striders are one kind of creature, so these are varieties, not species.
- **Why not**: "Breed" fits better.

## Consequences

### Positive

- One consistent vocabulary (user, strider, breed, run).
- Breed can grow into a real concept later without a schema change if it stays a key into game
  data.

### Negative

- ADR-0002 and ADR-0003 still say "pal" in their text (marked with a note). ADR-0005 and 0006
  were rewritten in place because they were not yet pushed.
- Where breed definitions live is open (see the game-data discussion).

### Risks

- `breed` as a bare string can drift from the data it refers to; validate it against the game
  data at adoption.
