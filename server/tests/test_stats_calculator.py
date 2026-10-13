from datetime import UTC, datetime, timedelta

import pytest

from stridecraft.models import Run
from stridecraft.stats.stats_calculator import (
    ConsistencyCalculator,
    EnduranceCalculator,
    SpeedCalculator,
    StatConverter,
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


def test_speed_first_run_has_no_pace_bonus():
    assert SpeedCalculator().gain(make_run(10), []) == pytest.approx(0.002)


def test_speed_slower_run_gets_only_the_base_add():
    history = [make_run(1, pace_min_per_km=5)]
    assert SpeedCalculator().gain(make_run(5, pace_min_per_km=6), history) == pytest.approx(0.002)


def test_speed_faster_run_and_training_bonus_stack():
    history = [make_run(1, pace_min_per_km=6)]
    faster = make_run(5, pace_min_per_km=5.4, training=True)  # 6/5.4 = 11.1% faster
    expected = 0.002 + 0.1 * (6 / 5.4 - 1) + 0.004
    assert SpeedCalculator().gain(faster, history) == pytest.approx(expected)


def test_speed_baseline_ignores_runs_older_than_the_window():
    stale_fast = [make_run(-100, pace_min_per_km=3)]
    assert SpeedCalculator().gain(make_run(10, pace_min_per_km=6), stale_fast) == pytest.approx(
        0.002
    )


def test_zero_distance_and_zero_time_runs_do_not_crash():
    empty = make_run(5, km=0)
    history = [make_run(1)]
    assert SpeedCalculator().gain(empty, history) == pytest.approx(0.002)
    assert EnduranceCalculator().gain(empty, history) == 0


def test_endurance_long_run_bonus_only_when_longest_in_window():
    history = [make_run(1, km=10)]
    assert EnduranceCalculator().gain(make_run(5, km=8), history) == pytest.approx(0.008)
    assert EnduranceCalculator().gain(make_run(5, km=12), history) == pytest.approx(
        0.012 + 0.1 * 0.2
    )


def test_consistency_pays_on_third_run_of_the_week_only():
    calculator = ConsistencyCalculator(SIGNUP)
    week = [make_run(0), make_run(1), make_run(2), make_run(3)]  # Thu 1 Jan to Sun 4 Jan
    gains = [calculator.gain(run, week[:i]) for i, run in enumerate(week)]
    assert gains == [0, 0, pytest.approx(0.01), 0]


def test_consistency_streak_grows_then_resets_without_taking_anything_away():
    calculator = ConsistencyCalculator(SIGNUP)
    # Weeks start Monday; SIGNUP is a Thursday, so week 1 is partial. Use full weeks from Mon 5 Jan.
    runs = [make_run(4 + 7 * week + d) for week in (0, 1) for d in (0, 1, 2)]
    assert calculator.gain(runs[2], runs[:2]) == pytest.approx(0.01)
    assert calculator.gain(runs[5], runs[:5]) == pytest.approx(0.02)  # second good week

    skipped_week = make_run(4 + 7 * 3)  # two weeks later, a fresh week
    after_gap = [skipped_week, make_run(4 + 7 * 3 + 1), make_run(4 + 7 * 3 + 2)]
    assert calculator.gain(after_gap[2], [*runs, *after_gap[:2]]) == pytest.approx(0.01)


def test_converter_ignores_pre_signup_runs_but_uses_them_as_baseline():
    before = make_run(-10, pace_min_per_km=6, elevation=500, source_id="old")
    after = make_run(1, pace_min_per_km=5.4, source_id="new")
    result = StatConverter().convert([after, before], SIGNUP)  # input order doesn't matter
    assert [g.source_id for g in result.gains] == ["new"]
    assert result.stats.hills == 10  # the old run's 500 m did not count
    assert result.stats.speed == pytest.approx(10 + 0.002 + 0.1 * (6 / 5.4 - 1))


def test_converter_with_no_runs_returns_starting_stats():
    result = StatConverter().convert([], SIGNUP)
    assert (result.stats.speed, result.stats.consistency) == (10, 10)
    assert result.gains == []
