"""Turns runs into pal stats. Formulas and worked examples: docs/stats.md.

NOTE: Claude structured this file unusually on purpose. Every tuning constant is an ALL_CAPS
name defined INSIDE the function that uses it (not at module level or in config.py), so each
formula can be read top to bottom in one place. Daria finds the maths hard to follow otherwise
and would lose the plot. Keep it this way.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from stridecraft.config import STATS_WINDOW_DAYS
from stridecraft.models import Run


@dataclass(frozen=True)
class Stats:
    # Defaults are the pal's starting values: Stats() is a brand new pal.
    speed: float = 10.0
    endurance: float = 10.0
    hills: float = 10.0
    consistency: float = 10.0

    def plus(self, gains: "RunGains") -> "Stats":
        return Stats(
            self.speed + gains.speed,
            self.endurance + gains.endurance,
            self.hills + gains.hills,
            self.consistency + gains.consistency,
        )


@dataclass(frozen=True)
class RunGains:
    """What one run added to each stat (to be stored when persistence exists)."""

    source_id: str
    speed: float
    endurance: float
    hills: float
    consistency: float


@dataclass(frozen=True)
class Conversion:
    stats: Stats
    gains: list[RunGains]


def baseline_runs(run: Run, history: list[Run]) -> list[Run]:
    """Runs in the STATS_WINDOW_DAYS before `run` started (before sign-up is fine)."""
    window_start = run.start_time - timedelta(days=STATS_WINDOW_DAYS)
    return [r for r in history if window_start <= r.start_time < run.start_time]


def average_speed(runs: list[Run]) -> float | None:
    """Total distance / total moving time in m/s, or None if there is nothing to average."""
    total_time = sum(r.moving_time_s for r in runs)
    if total_time == 0:
        return None
    return sum(r.distance_m for r in runs) / total_time


class SpeedCalculator:
    def gain(self, run: Run, history: list[Run]) -> float:
        BASE_ADD = 0.002  # every run
        PACE_K = 0.1  # points per 100% faster than the 6-week average (10% faster = 0.01)
        TRAINING_BONUS = 0.004  # flat extra for Race/Workout runs

        gain = BASE_ADD
        average = average_speed(baseline_runs(run, history))
        if average and run.moving_time_s:
            run_speed = run.distance_m / run.moving_time_s
            gain += PACE_K * max(0.0, run_speed / average - 1)
        if run.is_training:
            gain += TRAINING_BONUS
        return gain


class EnduranceCalculator:
    def gain(self, run: Run, history: list[Run]) -> float:
        KM_ADD = 0.001  # per km (10 km = 0.01)
        LONG_RUN_K = 0.1  # points per 100% longer than your longest run of the last 6 weeks

        km = run.distance_m / 1000
        gain = KM_ADD * km
        longest_km = max((r.distance_m for r in baseline_runs(run, history)), default=0) / 1000
        if longest_km and km > longest_km:
            gain += LONG_RUN_K * (km / longest_km - 1)
        return gain


class HillsCalculator:
    def gain(self, run: Run, history: list[Run]) -> float:
        METRES_ADD = 0.0001  # per metre climbed (100 m = 0.01)
        return METRES_ADD * run.elevation_gain_m


class ConsistencyCalculator:
    def __init__(self, signup_date: datetime):
        self.signup_date = signup_date

    def gain(self, run: Run, history: list[Run]) -> float:
        WEEKLY_RUN_GOAL = 3  # runs in a calendar week that count as a "good week"
        STREAK_ADD = 0.01  # points per week of streak, paid when the goal is reached
        MAX_STREAK = 10

        weekly_runs = self.runs_per_week([*history, run])
        this_week = week_start(run.start_time)
        if weekly_runs[this_week] != WEEKLY_RUN_GOAL:
            return 0.0

        streak = 1
        previous = this_week - timedelta(weeks=1)
        while weekly_runs[previous] >= WEEKLY_RUN_GOAL and streak < MAX_STREAK:
            streak += 1
            previous -= timedelta(weeks=1)
        return STREAK_ADD * streak

    def runs_per_week(self, runs: list[Run]) -> Counter[date]:
        """Runs per Monday-start week, counting only runs from sign-up onwards."""
        return Counter(week_start(r.start_time) for r in runs if r.start_time >= self.signup_date)


def week_start(moment: datetime) -> date:
    return (moment - timedelta(days=moment.weekday())).date()


class StatConverter:
    """The single entry point: runs in, pal stats (and per-run gains) out."""

    def convert(self, runs: list[Run], signup_date: datetime) -> Conversion:
        speed, endurance, hills = SpeedCalculator(), EnduranceCalculator(), HillsCalculator()
        consistency = ConsistencyCalculator(signup_date)

        ordered = sorted(runs, key=lambda r: r.start_time)
        stats = Stats()
        gains: list[RunGains] = []
        for index, run in enumerate(ordered):
            if run.start_time < signup_date:
                continue
            history = ordered[:index]
            run_gains = RunGains(
                source_id=run.source_id,
                speed=speed.gain(run, history),
                endurance=endurance.gain(run, history),
                hills=hills.gain(run, history),
                consistency=consistency.gain(run, history),
            )
            stats = stats.plus(run_gains)
            gains.append(run_gains)
        return Conversion(stats, gains)
