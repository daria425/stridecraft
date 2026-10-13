## Project: Stridecraft

Gamify real runs into a Palworld/Pokemon/WoW/Ark-inspired RPG for **intermediate runners**: progression comes from performance, PBs, volume, elevation and streaks, not "you ran today". Decisions below come from a planning session.

### Scope & stack

- **Audience:** just the author first. Keep a `user_id` in the schema so multi-user later isn't a rewrite.
- **Data source:** Strava API (OAuth + webhook/sync). Model a generic `Run` so other sources can plug in later.
- **Stack:** Python (FastAPI) server in `server/`, web frontend in `web/`.
- **Content is data, not code:** skills, quests, bosses and outfits live in data files (author adds new ones over time).

### Character

- Pick one fighter ("pal") once at the start from a **pre-generated set (~4-6) of AI-generated designs**, shipped as static assets. Outfits are pre-made variants.
- All fighters start with **identical stats**; the difference is looks only. Training makes them diverge (fast, enduring, hilly...).
- **No character level / XP.**
- **The pal is not you** (Pokemon/Palworld principle): a caught pal has its own powers and is unrelated to the trainer's skill. It gets stronger by training alongside you. So every stat starts from the pal's own base values, and **only runs after the user's sign-up date count** toward any stat. Runs before sign-up only serve as the baseline (e.g. the 6-week average pace for Speed). Needs a `created_at` on the user once persistence exists.
- **Effortless UX:** the user just runs and logs in Strava; the app asks for no extra logging.

### Stats

- Four stats: **Speed, Endurance, Hills, Consistency**.
- **Endurance, Hills and Consistency** are a **rolling window of recent performance** (~6 weeks, tune later) counted from runs after sign-up only, so they can fall back if you stop training. Revisit a hybrid (points capped by performance) if stats feel flat in practice. Exact base values, how the window combines with the pal's base, and decay are still open.
- **Speed is different** (journal/0002): a **running total that never decays**, starting at 10. Every run adds a small base amount (~0.002), plus a pace bonus when its average pace beats the average pace of the previous 6 weeks; training-flagged runs get an additional bonus. Grinding is accepted. No best efforts or splits are needed for Speed.
- **PBs** are whatever Strava reports as `pr_rank` on `best_efforts` (journal/0001, 0002); treadmill runs have none, which is accepted.
- **Endurance:** weekly km + longest run. **Hills:** weekly elevation gain (per km). **Consistency:** runs per week held over the window. Each normalised to a 0-100 scale against the user's own history (revisit fixed benchmarks if that proves confusing).
- Exact formulas are decided per-phase; keep the maths simple and unit-tested.

### Training runs

- A run is a **training run** only if Strava tags it Race or Workout. **No in-app toggle or override**: if the user forgot to tag it in Strava, that's on them (every run still adds to Speed, so nothing is lost).
- **Training run:** gets an **additional Speed bonus** on top of the base add and pace bonus every run gets (size TBD), and counts toward the other stats.
- **Any other run (easy):** still adds to Speed (base add, plus the pace bonus if it was faster than the 6-week average) and feeds **Endurance and Consistency**. Speed never decays, so easy runs can't hurt the character (70-80% of runs should be easy).

### Permanent progression (never decays)

- **Skills (collection):** unlocked once, kept forever. Equipped into **limited slots** (Palworld passive-style loadout; slot count and tiers/trade-offs TBD). Skills affect **boss fights only**.
- **Quest log / trophies:** permanent record of quests done and bosses beaten.
- **Skill unlock triggers (v1):** PB-based (e.g. 2 PBs in a week), volume/elevation milestones (e.g. 50 km week), consistency/streaks.
- **Deferred:** pacing/split-based triggers (negative splits, even splits).

### Quests, bosses, outfits

- **Quests:** fixed, hand-authored (author adds them as ideas come). Finishing quests and beating bosses grants skills and outfits.
- **Boss fights:** **auto-battle you watch**. Outcome is simulated from the trained pal's stats + equipped skills; the player's decisions are training and loadout beforehand.
- **Deferred:** the stat to combat-attribute mapping, and boss/skill balance, decided when the battle phase starts.

### Open / not yet decided

- Skill slot count, skill tiers and negative trade-offs.
- Exact window length, normalisation and decay maths for Endurance/Hills/Consistency; Speed constants (base add, pace-bonus `k`, training bonus size) and whether Speed is capped.
- Combat formulas and boss design.
- Build order / phases (needed before the "plan mode per phase" workflow above applies), testing bar per phase, deployment and hosting.

## How we work together

This is a collaboration, not a hand-the-keys-over build. Specifically:

- **Plan mode per phase.** Before starting each phase in the Build order below, propose a short approach (what files, what interfaces, what's deliberately deferred) and wait for a go-ahead. Small decisions _within_ an agreed phase don't need a check-in.
- **Don't silently re-scope.** If a phase turns out to need something not in this file (a new dependency, a schema change, a reordering), surface it and get agreement before running with it — don't just decide and proceed. -**Do not silently make changes** Other than obviou fixes such as typos, get verification first. You don't know is it a bug or a feature. -**Document decisions where relevant** - Use architecture-decision-skill when we decide on smth important such that journal/ dir will contain everything important and as the single source of truth. This file should reference it but remain as a moe general overview.
- **Testing bar is decided per-phase**, not fixed upfront.
- This doc reflects real decisions made in a planning session, not aspirations. If something here turns out to be wrong once we're building, fix the doc, don't quietly diverge from it.
  -I change decisions and pivot a lot so always check this doc at the beginning of a session as well as presence of and contents of journal/ dir to get latest project state. -**Code as the source of truth**. Contents of this file should match what is actually going on in the repo, not the other way around. We should not do something in a stupid way just because 'CLAUDE.md' or 'AGENTS.md' said so, if there is a better way it may just mean we overlooked it initially!

  ## Linting & code style (needs setup)

- **Tool:** [ruff](https://docs.astral.sh/ruff/) for both linting and formatting (`server/pyproject.toml`) — one tool, no separate black/isort/flake8.
- **Rules enabled:** pyflakes (`F`), pycodestyle (`E`/`W`), import sorting (`I`), pyupgrade (`UP`), bugbear (`B`), mccabe complexity (`C90`).
- **Max complexity: 10** (`mccabe.max-complexity`). If a function trips this, that's a signal to split it, not to raise the limit — raise it only with a specific reason, not to make a violation go away.
- **Line length: 100.** Double quotes.
- **Enforced via pre-commit hook** (`.pre-commit-config.yaml`, scoped to `server/`): `ruff check --fix` then `ruff format` run automatically on every commit. Installed once via `uv tool install pre-commit && pre-commit install`; after that it's automatic — don't reach for `--no-verify` to skip it.
- Run manually any time: `cd server && uv run ruff check . && uv run ruff format .`
- The `/web` frontend (later phase) gets its own eslint + prettier config when that phase starts — not set up yet since there's no frontend code.
- No type checker yet (mypy) — revisit if untyped bugs actually start costing time.
- Be pragmatic but functions should have clear names and do one thing, thats basic code quality
- Don't prefix functions with \_, no reason, I just do not like it.
- I prefer OOP where possible as I find that is a clearer way to keep everything scoped and organized but no need to force it
- No testing for the sake of testing, tests should verify the app works and validate edge case behavior rather than that the function which returns a string indeed returns a string
- Shared functions should be grouped (for example in a dedicated utils/ module, grouped by theme)
