from datetime import UTC, datetime, timedelta

import pytest

from stridecraft.models import Run
from stridecraft.stats.stats_calculator import (
    ConsistencyCalculator,
    EnduranceCalculator,
    HillsCalculator,
    SpeedCalculator,
    StatConverter,
    Stats,
)

SIGNUP = datetime(2026, 1, 1, tzinfo=UTC)


def make_run(
    days_after_signup: float,
    km: float = 10,
    pace_min_per_km: float = 6,
    elevation: float = 0,
    training: bool = False,
    source_id: str | None = None,
) -> Run:
    start = SIGNUP + timedelta(days=days_after_signup)
    return Run(
        user_id=1,
        source="strava",
        source_id=source_id or str(start.timestamp()),
        start_time=start,
        distance_m=km * 1000,
        moving_time_s=int(km * pace_min_per_km * 60),
        elevation_gain_m=elevation,
        is_training=training,
    )


# Tests assert relationships (faster gains more than slower), never the tuned constants, so
# changing a constant in stats_calculator.py should not break them.


def test_first_run_and_slower_run_both_get_only_the_base_add():
    first = SpeedCalculator().gain(make_run(10), [])
    slower = SpeedCalculator().gain(
        make_run(5, pace_min_per_km=6), [make_run(1, pace_min_per_km=5)]
    )
    assert first > 0
    assert slower == pytest.approx(first)


def test_faster_pace_and_training_tag_each_add_on_top_of_the_base():
    history = [make_run(1, pace_min_per_km=6)]
    base = SpeedCalculator().gain(make_run(5, pace_min_per_km=6), history)
    faster = SpeedCalculator().gain(make_run(5, pace_min_per_km=5.4), history)
    much_faster = SpeedCalculator().gain(make_run(5, pace_min_per_km=4.8), history)
    tagged = SpeedCalculator().gain(make_run(5, pace_min_per_km=6, training=True), history)
    both = SpeedCalculator().gain(make_run(5, pace_min_per_km=5.4, training=True), history)
    assert base < faster < much_faster
    assert base < tagged
    assert both > faster
    assert both > tagged


def test_speed_baseline_ignores_runs_older_than_the_window():
    stale_fast = [make_run(-100, pace_min_per_km=3)]
    run = make_run(10, pace_min_per_km=6)
    assert SpeedCalculator().gain(run, stale_fast) == pytest.approx(SpeedCalculator().gain(run, []))


def test_zero_distance_and_zero_time_runs_do_not_crash():
    empty = make_run(5, km=0)
    history = [make_run(1)]
    assert SpeedCalculator().gain(empty, history) == pytest.approx(
        SpeedCalculator().gain(empty, [])
    )
    assert EnduranceCalculator().gain(empty, history) == 0


def test_endurance_pays_extra_per_km_only_for_a_new_longest_run():
    history = [make_run(1, km=10)]
    calculator = EnduranceCalculator()
    shorter = calculator.gain(make_run(5, km=8), history) / 8
    same_as_longest = calculator.gain(make_run(5, km=10), history) / 10
    longer = calculator.gain(make_run(5, km=12), history) / 12
    assert shorter == pytest.approx(same_as_longest)
    assert longer > same_as_longest


def test_hills_gain_scales_with_elevation():
    calculator = HillsCalculator()
    flat, hilly, hillier = (calculator.gain(make_run(5, elevation=m), []) for m in (0, 100, 200))
    assert flat == 0
    assert hillier == pytest.approx(2 * hilly)
    assert hilly > 0


def test_consistency_pays_on_third_run_of_the_week_only():
    calculator = ConsistencyCalculator(SIGNUP)
    week = [make_run(0), make_run(1), make_run(2), make_run(3)]  # Thu 1 Jan to Sun 4 Jan
    gains = [calculator.gain(run, week[:i]) for i, run in enumerate(week)]
    assert [g > 0 for g in gains] == [False, False, True, False]


def test_consistency_streak_grows_then_resets_without_taking_anything_away():
    calculator = ConsistencyCalculator(SIGNUP)
    # Weeks start Monday; SIGNUP is a Thursday, so week 1 is partial. Use full weeks from Mon 5 Jan.
    runs = [make_run(4 + 7 * week + d) for week in (0, 1) for d in (0, 1, 2)]
    first_good_week = calculator.gain(runs[2], runs[:2])
    second_good_week = calculator.gain(runs[5], runs[:5])
    assert second_good_week > first_good_week > 0

    gap_week = [make_run(4 + 7 * 3 + d) for d in (0, 1, 2)]  # week 3 was skipped entirely
    after_gap = calculator.gain(gap_week[2], [*runs, *gap_week[:2]])
    assert after_gap == pytest.approx(first_good_week)


def test_converter_ignores_pre_signup_runs_but_uses_them_as_baseline():
    before = make_run(-10, pace_min_per_km=6, elevation=500, source_id="old")
    after = make_run(1, pace_min_per_km=5.4, source_id="new")
    result = StatConverter().convert([after, before], SIGNUP)  # input order doesn't matter
    without_baseline = StatConverter().convert([after], SIGNUP)
    assert [g.source_id for g in result.gains] == ["new"]
    assert result.stats.hills == Stats().hills  # the old run's 500 m did not count
    assert result.stats.speed > without_baseline.stats.speed  # but it set the pace to beat


# --- Scenario tests: sign up, log new runs, watch the pal grow --------------------------------
# History used below: 6 weeks before sign-up, 3 runs a week, 10 km at 6:00/km (3600 s each).


def history_before_signup() -> list[Run]:
    return [make_run(-42 + 7 * week + d, pace_min_per_km=6) for week in range(6) for d in (0, 2, 4)]


def month_of_runs() -> list[Run]:
    """4 weeks after sign-up, Mon/Wed/Fri each week. All 10 km, 6:00/km, 100 m climbing,
    except the very last run: a faster (5:30/km) Workout."""
    runs = []
    for week in range(4):
        for day in (0, 2, 4):
            monday = 4  # sign-up is a Thursday, so day 4 is the first full week's Monday
            runs.append(make_run(monday + 7 * week + day, pace_min_per_km=6, elevation=100))
    last = runs[-1]
    runs[-1] = make_run(
        (last.start_time - SIGNUP).days, pace_min_per_km=5.5, elevation=100, training=True
    )
    return runs


def test_signing_up_with_existing_history_leaves_the_pal_at_base():
    result = StatConverter().convert(history_before_signup(), SIGNUP)
    assert result.stats == Stats()
    assert result.gains == []


def test_a_runs_gains_do_not_change_when_later_runs_are_logged():
    # This is what lets us store each run's gains once and never recompute them.
    runs = [*history_before_signup(), *month_of_runs()]
    earlier = StatConverter().convert(runs[:-4], SIGNUP).gains
    later = StatConverter().convert(runs, SIGNUP).gains
    assert later[: len(earlier)] == earlier


def test_no_run_ever_takes_anything_away_from_the_pal():
    slow_day = make_run(30, pace_min_per_km=9, km=2)  # far slower and shorter than usual
    runs = [*history_before_signup(), *month_of_runs(), slow_day]
    result = StatConverter().convert(runs, SIGNUP)
    for gain in result.gains:
        assert min(gain.speed, gain.endurance, gain.hills, gain.consistency) >= 0
    assert result.stats.speed >= Stats().speed
