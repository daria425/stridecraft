# ADR-0015: A journey carried by distance, with authored quests and AI-tailored challenges

**Date**: 2026-10-20
**Status**: proposed
**Deciders**: Daria, Claude

## Context

The base app works end to end (Strava sync, frozen per-run gains, four stats, adoption, dashboard),
but a run only nudges four numbers. There is nothing to *do* between runs and nothing that
happens *because of* a run. The goal is a Temple Run feel: the core loop is "just keep running",
and along the way things happen (landmarks, obstacles, milestones). It must not become
"run 3 times this week".

Constraints from earlier decisions and from the code:

- **We only learn about a run after Strava syncs it** (ADR-0014; the webhook doesn't exist yet).
  Nothing can react live during a run. The moment the game "speaks" is the **post-run recap**
  (PRODUCT.md: the quick check right after a run).
- **Effortless and no guilt** (README, PRODUCT.md, ADR-0003): no extra logging, no penalties,
  nothing decays, missing a week never hurts.
- **Performance over presence**: pace, PBs, volume, elevation and streaks matter, not turning up.
- **Content is data, behaviour is code** (ADR-0008). Quests are hand-authored. Reward kinds
  (skills, outfits, bosses) don't exist yet, and PB data only exists for the newest 50 runs
  (docs/data-flow.md).
- Nothing stores "current state"; things are derived from runs plus frozen records (ADR-0006).
- AI should **tailor, not author**: the author keeps control of the story and the rules.

## Decision

Three layers, each with one job. Distance moves the strider along, authored quests give the story
beats, and tailored challenges give the performance goals.

```
JOURNEY  (spine, authored)     distance of every post-adoption run moves the strider along a route
  |- leg                       a region, ~4-6 weeks of running, ends in a boss (boss = later phase)
  |    '- waypoint at km X     landmark | quest | boss
  |
QUEST    (authored, fixed)     a story beat at a waypoint. No performance condition: reaching it is
  |                            the condition. Grants a trophy/story; some quests open a challenge slot.
  |
CHALLENGE (template + tailored) a short-lived, performance-based goal ("climb 180 m in one run this
                               week"). Authored template, tailored to this runner by a "picker".
```

### 1. The journey (what makes it Temple Run)

- **Position is derived**, like stats: `journey_km = SUM(distance of runs with a gains row)`.
  Nothing stores a "position". Every run, easy or hard, moves the strider (consistent with
  "every run counts").
- **Waypoints** sit at km offsets inside a leg, roughly one every 10-15 km, so an intermediate
  runner (about 25-40 km a week) crosses one every 2-3 runs. This is the pacing lever: frequent
  small beats, a bigger one at each leg's end. Numbers are first guesses.
- **The journey never blocks.** A waypoint can't be "failed" or hold the strider back; distance
  always carries on. The only gate is the leg-end boss, and a boss is passed by *preparation* (stats
  and loadout), not by an extra condition.
- When a sync processes a run and the running total crosses a waypoint, we **freeze a journey
  event** (`waypoint_crossed`, `quest_completed`, `challenge_offered`, ...), the same pattern as
  `run_gains`. The recap reads these events. Retuning content later never rewrites history.

### 2. Quests (authored, fixed)

Quests keep the existing rule "fixed, hand-authored". A quest is a story beat at a waypoint. It has
no performance condition, so it is never unfair or impossible for any runner. It grants a **trophy**
(permanent record) and, later, skills or outfits. A quest of kind `encounter` also **opens a
challenge slot** whose pool is themed for that leg ("a rockfall blocks the pass" opens a hills
challenge). This is how the story and the tailored goals stay connected.

### 3. Challenges (template + tailoring)

A challenge is a **template** (authored YAML) plus a **tier** and **concrete numbers** chosen for one
runner.

```yaml
# server/content/challenges/ridge_climb.yaml  (shape, not final)
name: Climb the Ridge
condition: single_run_elevation_m    # one of a small, fixed list implemented in code
baseline: avg_run_elevation_m        # what "normal for this runner" means for this condition
tiers: {easy: 1.3, stretch: 1.8, ambitious: 2.5}   # target = baseline x tier
clamp: {min: 60, max: 600}           # absolute floor and ceiling
window_days: 7
reward: {trophy: ridge_climber}
story: "{strider} eyes the ridge. Reach {target} m of climbing in a single run."  # fallback text
```

- **Conditions are a small, closed vocabulary in code** (ADR-0008: behaviour in code, data
  parametrises it). v1: single-run distance, single-run elevation, single-run pace vs. baseline,
  weekly distance, weekly run count, weekly elevation, weekly-run streak. **Deferred**: PB-based and
  split-based conditions (PB data is partial; ADR-0001/0009).
- **The code, not the AI, computes the target number** from the runner's baseline and the chosen
  tier, then clamps it. The AI picks *which* template and *which tier*.
- **Lifecycle (auto-offered, quiet expiry)**: challenges are offered, not accepted. An open
  challenge counts runs that start inside its window. When it is completed we freeze a
  `challenge_completed` event and grant the reward. When the window ends it **expires quietly**
  and is replaced. No penalty, no failure screen, no streak impact. The user may skip one (dismiss),
  which is not logged as a failure either.
- **Slots**: at most one quest-opened challenge plus up to two weekly side challenges open at once
  (first guess). Variety rule: don't offer the same template twice in a row.
- The concrete instance (template id, tier, numbers, story text, window) is **stored when offered
  and never rewritten**, so editing a template can't change a challenge someone is mid-way through.

### 4. Where the AI sits: a replaceable "picker"

```
sync -> RunnerProfile (numbers only) -> ChallengePicker -> picks -> validate -> store instances
                                           |- RuleBasedPicker   (default, no AI, always available)
                                           '- LlmPicker         (select + tune + narrate)
```

- **Input is aggregated numbers only**: 4-6 week average weekly km, longest run, average pace,
  runs per week, elevation per week, current streak, recent completions/skips per template, and the
  strider's name and breed. **No raw activities, GPS, titles or athlete identity leave the server.**
- **Output is structured** (pydantic): `[{template_id, tier, story}]`. Anything outside the
  eligible template list, an unknown tier or an over-long story is rejected.
- **The LLM may**: choose among eligible templates, choose a tier from the allowed ones, and write
  flavour text from facts we pass it (strider name, breed, leg theme, the target).
  **The LLM may not**: invent conditions, rewards or numbers, or give training or medical advice.
- **Safety guardrails live in code, whatever the AI says**: weekly-distance/elevation targets are
  capped at a small increase over the runner's recent average; no "ambitious" tier is offered after a
  long gap in runs; the copy never frames a miss as failure.
- **No AI means a working game.** `RuleBasedPicker` (rotate eligible templates, tier from recent
  completion rate, authored story text) ships first and is the fallback if the AI call fails or is
  not configured. The AI is an upgrade of one component, not a dependency of the feature.
- It is called **once per refresh** (weekly, or when a slot frees up), never per page view. Inputs and
  outputs are logged so we can see what it did.

### 5. Rewards and what they do not do

Challenges and quests grant **trophies** (the permanent quest log) now, and **skills and outfits**
once those content kinds exist. They **never change stats**: stats come only from runs (ADR-0003).
Because skill unlock triggers (PB, volume, streak) are the same kind of "condition on runs", the
condition vocabulary above is meant to be shared with skills later.

### 6. Terms (so docs and UI stay consistent)

| Term | Meaning |
|---|---|
| Journey / leg / waypoint | The authored route, its regions, and the points on it |
| Quest | Fixed, authored story beat at a waypoint (no performance condition) |
| Challenge | Short-lived, performance-based goal made from a template, tailored per runner |
| Picker | The component that decides which challenges a runner is offered |
| Recap | The post-run screen: km travelled, waypoints crossed, challenge progress, rewards |
| Trophy | Permanent record of a completed quest, challenge or boss |

### 7. Build order (each phase still gets its own plan check-in, per CLAUDE.md)

1. **Journey core, no challenges, no AI.** `journeys`/`legs` content kinds, derived position,
   waypoint crossing at sync, frozen `journey_events`, `GET /me/journey`. Testable on real runs at once.
2. **Quests and trophies.** Quest content, trophies, the first cross-reference check between
   content kinds (ADR-0008 flagged this risk).
3. **Challenge engine with `RuleBasedPicker`.** Templates, the condition evaluators, instances table,
   expiry, tier and clamp maths, unit tests for edge cases (late uploads, treadmill, a week with no runs,
   a run that completes two challenges).
4. **Frontend**: journey view, recap, challenge cards. Goes through the DESIGN.md design pass.
5. **`LlmPicker`**: structured-output call, guardrails, logging, fallback, and a few fixture profiles
   to eyeball the picks. Model and prompt are chosen at that phase.
6. **Skills, outfits and the first boss** plug into rewards and leg ends (own ADRs).

## Alternatives Considered

### Alternative 1: Quest board only

- **Pros**: Simplest to build; no route to author.
- **Cons**: No sense of continuous movement, so every run is just a checklist tick, which is the
  "run 3 times this week" shape.
- **Why not**: It misses the Temple Run feel that was the point.

### Alternative 2: Seasonal chapters

- **Pros**: Strong rhythm, natural fit for AI-written arcs.
- **Cons**: Creates calendar pull and "I missed the season", against the no-guilt principle.
- **Why not**: Legs are paced by distance rather than the calendar, so nothing is missed.

### Alternative 3: AI generates whole challenges and storylines

- **Pros**: Maximum variety and personalisation.
- **Cons**: Unbalanced or unsafe targets, inconsistent lore, cost and non-determinism, and it
  hands away the authored story that is half the product.
- **Why not**: Select + tune + narrate gets most of the felt personalisation with all the rules in code.

### Alternative 4: Narration-only AI over fixed challenges

- **Pros**: Safest and cheapest.
- **Cons**: Goals aren't actually tailored, so they're too easy for some runners and too hard for others.
- **Why not**: Tailoring the *goal* is the point. This remains our fallback behaviour.

### Alternative 5: Performance gates on journey waypoints

- **Pros**: More Temple Run "obstacle" tension.
- **Cons**: Fixed gates are unfair across runners, and a blocked journey is a punishment.
- **Why not**: Performance lives in tailored challenges; the journey only ever moves forward.

## Consequences

### Positive

- Every run visibly *does* something (distance, usually a waypoint), while performance still earns more.
- The AI is small, bounded and swappable, and the game works without it.
- Position, stats and events follow the project's existing pattern (derived values plus frozen events).
- Authoring is the same as today: add YAML files.

### Negative

- A lot of content to author before it feels rich (route, waypoint stories, templates).
- Distance-based movement rewards volume more than speed. Speed is rewarded through stats and
  challenges instead, so the journey alone will feel "grindy" to fast low-volume runners.
- New tables (`challenges`, `journey_events`), so the DB is rebuilt (ADR-0006).
- Weeks and windows use UTC until per-user time zones exist (already an open item).

### Risks

- A tailored challenge could push someone to overreach. Mitigated by clamps, increase caps and
  copy rules, but they need real thought in phase 3, not an afterthought.
- Fixed pacing numbers (km per waypoint, leg length) may feel wrong. They are data, so cheap to tune.
- LLM output quality and cost are unknown until phase 5. Mitigated by the fallback picker.
- Sending data to an LLM is a privacy surface. Mitigated by aggregates-only input; revisit before
  any other user signs up.

## Open questions for Daria

- How long should the first journey be, and is there a story per breed (Cetus starts on the Aethiopian coast)?
- Keep "quest" for authored beats and "challenge" for tailored ones, or different words?
- Slot counts and window lengths (first guesses above).
- Should a skipped challenge influence what the picker offers next?
- Does the recap replace the dashboard as the post-run landing, or sit beside it?
