# Architecture Decision Records

| ADR                                | Title                                         | Status   | Date       |
| ---------------------------------- | --------------------------------------------- | -------- | ---------- |
| [0001](0001-strava-fetch-window.md) | Strava fetch: 42-day window, detail calls for best efforts | partly superseded by 0009 | 2026-10-12 |
| [0002](0002-speed-running-total.md) | Speed is a running total: base add plus pace bonus | accepted | 2026-10-12 |
| [0003](0003-pal-grows-from-new-runs.md) | The pal grows only from post-sign-up runs; stats never decay | accepted | 2026-10-13 |
| [0004](0004-tests-assert-relationships-not-constants.md) | Stat tests assert relationships, not tuned constants | accepted | 2026-10-13 |
| [0005](0005-strider-adoption-is-the-signup-date.md) | Strider adoption is the sign-up date | accepted | 2026-10-13 |
| [0006](0006-sqlite-frozen-gains-rebuild.md) | SQLite, SQLAlchemy, frozen gains; rebuild instead of migrations | accepted | 2026-10-13 |
| [0007](0007-striders-breeds-and-names.md) | Pals become striders, with a breed and a name | accepted | 2026-10-15 |
| [0008](0008-game-content-yaml.md) | Game content is YAML files, validated by pydantic | accepted | 2026-10-15 |
| [0009](0009-bounded-strava-usage.md) | Stats come from the activity list; Strava usage is bounded | accepted | 2026-10-15 |
| [0010](0010-typed-errors-handled-at-the-top.md) | Expected errors are typed, UI-neutral, and caught at the top level | accepted | 2026-10-15 |
| [0011](0011-scale-stat-constants-uniformly.md) | Scale all stat constants x20, uniformly | accepted | 2026-10-15 |
| [0012](0012-rest-api-strava-login.md) | FastAPI REST API, "log in with Strava" via Authlib and a session cookie | accepted | 2026-10-15 |
| [0013](0013-assets-shared-at-repo-root.md) | Binary assets live in a repo-root `assets/`, served by URL | accepted | 2026-10-16 |
| [0014](0014-web-frontend-vite-react.md) | Vite + React SPA; sync on open and tab focus until the webhook | accepted | 2026-10-16 |
| [0015](0015-journey-quests-and-tailored-challenges.md) | Journey carried by distance, authored quests, AI-tailored challenges | partly superseded by 0017 | 2026-10-20 |
| [0016](0016-creature-renderer-and-independent-habitats.md) | React Three Fiber renderer with independent creature habitats | accepted | 2026-10-21 |
| [0017](0017-endless-journey-from-encounter-pools.md) | Endless journey: authored legs rolled in turn, filled with random encounters | accepted | 2026-10-25 |
| [0018](0018-journey-level-maps-and-arrival-banner.md) | A 3D voyage map, a once-only arrival banner, a dev endpoint to cross waypoints | accepted | 2026-10-27 |
