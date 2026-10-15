# How a run becomes strider stats

Plain-language reference for the maths. Decisions and reasoning live in `journal/`
(ADR-0002, ADR-0003); this file is the "what exactly happens" version, with examples.
**All constants are first guesses**; tune them after seeing real numbers.

## The big picture

- Four stats: **Speed, Endurance, Hills, Consistency**.
- Each is a running total: **base value + sum of per-run additions**. It never goes down.
- Only runs **after the user signed up** add anything. Earlier runs are only used as a baseline
  (the 6-week average pace and longest run).
- **Every run counts toward every stat**, easy or not. A run tagged Race or Workout in Strava is a
  *training run*, which earns one extra thing: a Speed bonus. Nothing else differs.
- Each run's additions are worked out once, when the run is first processed, then stored (frozen;
  see `docs/data-flow.md`).

"Previous 6 weeks" always means the 42 days before that run's start time.

## Speed (starts at 10)

A run adds up to three pieces:

| Piece | Formula | Constant |
|---|---|---|
| Base add (every run) | flat `BASE_ADD` | 0.002 |
| Pace bonus (only if faster than usual) | `PACE_K * max(0, run_speed / avg_speed - 1)` | `PACE_K` = 0.1 |
| Training bonus (Race/Workout only) | flat `TRAINING_BONUS` | 0.004 |

- `run_speed` = distance / moving time of this run.
- `avg_speed` = total distance / total moving time of all runs in the previous 6 weeks.
- `run_speed / avg_speed - 1` is "how much faster than usual", as a fraction (0.10 = 10% faster).
  If the run is slower, `max(0, ...)` makes the bonus 0, never negative.
- No earlier runs in the 6 weeks means no pace bonus.
- Run length doesn't matter for Speed: a 1 km jog earns the same base add as a 20 km run.

Examples (6-week average pace is 5:30/km):

| Run | Calculation | Speed added |
|---|---|---|
| Easy, 5:45/km | 0.002 + 0 | 0.002 |
| Easy, about 5:00/km (10% faster) | 0.002 + 0.1 * 0.10 | 0.012 |
| Tempo workout, about 5:00/km | 0.002 + 0.010 + 0.004 | 0.016 |

## Endurance (base 10)

| Piece | Formula | Constant |
|---|---|---|
| Distance | `KM_ADD * km` | `KM_ADD` = 0.001 |
| Long-run bonus (only if it's your longest in 6 weeks) | `LONG_RUN_K * (km / longest_km - 1)` | `LONG_RUN_K` = 0.1 |

`longest_km` is the longest run in the previous 6 weeks. A 10 km run gives 0.01. Running 12 km
when your longest was 10 gives 0.012 + 0.1 * 0.2 = 0.032. No earlier runs means no long-run bonus.

## Hills (base 10)

`METRES_ADD * elevation_gain_m`, with `METRES_ADD` = 0.0001. 100 m of climbing gives 0.01.

## Consistency (base 10)

- Count runs per calendar week (Monday to Sunday).
- The moment a week reaches `WEEKLY_RUN_GOAL` runs (3), award `STREAK_ADD * streak`.
- `streak` = number of consecutive weeks, including this one, that reached the goal, capped at
  `MAX_STREAK` (10). `STREAK_ADD` = 0.01.
- Missing a week resets the streak counter to 0 but the stat keeps what it had. Nothing is taken
  away.
- Example: hit 3 runs in 4 weeks in a row, and the 4th week's goal run adds 0.04.

## Not decided yet

- Whether any stat gets a cap or diminishing returns.
- Whether the strider's base values differ per stat (all 10 for now).
- Skills that reward consistency (to be designed with the skills phase).
