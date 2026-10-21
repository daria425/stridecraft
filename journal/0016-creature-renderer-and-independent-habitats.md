# ADR-0016: React Three Fiber renderer with independent creature habitats

**Date**: 2026-10-21
**Status**: accepted
**Deciders**: Daria, Codex

## Context

`CreatureSlot` needs to show the strider in a 3D environment behind the existing UI. Cetus's
first location is a flooded sanctuary. Other breeds may have distinct locations later, but
that is still undecided. This phase must leave the concurrently developed backend untouched.

## Decision

Use Three.js through React Three Fiber, with Drei for scene helpers. Separate model loading,
camera/lighting and habitat components. Optional `breedId` selects a presentation-only habitat
mapping: Cetus uses the sanctuary; other breeds use a neutral stage. The dev studio can
override the environment. Keep the existing API-provided `modelUrl` interface and ADR-0013's
asset ownership. The floor engraving belongs in 3D so perspective and occlusion agree.

Dev-only Vite middleware serves the two existing Cetus GLBs at explicit preview URLs, without
exposing the rest of the repo or bundling model files in production. Dashboard/adoption
sandboxes use the textured export. Production still waits for the backend owner to set the
existing breed model path to `breeds/cetus/cetus-texture.glb`; no server files change here.

## Alternatives considered

- **Imperative Three.js:** direct control, but duplicates renderer lifecycle and sizing work
  already managed by React Three Fiber.
- **One habitat coupled to the loader:** simpler initially, but makes future breed locations
  harder to add. A separate component preserves the option without committing to more habitats.
- **Server environment metadata now:** centralizes presentation but changes the contract before
  location requirements are settled. Revisit if habitats become authored content.

## Consequences

- One renderer serves the studio, adoption and dashboard; scenery can change independently.
- The 3D bundle is lazy-loaded. Rendering caps pixel density, pauses continuous frames in hidden
  tabs, respects reduced motion, and keeps the location visible on a model failure.
- `cetus-texture.glb` has embedded base-colour, metallic/roughness and normal images;
  `cetus-model.glb` is untextured. Both are static, without skeletons or animation clips.
  Rigging and an idle animation remain asset work; GLB export alone does not provide them.
- Production model selection stays backend-owned. The real Cetus asset is available in dev
  previews without changing backend content. Actual device GPU performance still needs review.
- New working notes under `docs/` are local/ignored; lasting decisions belong in `journal/`.
