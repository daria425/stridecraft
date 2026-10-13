from stridecraft.models import Run

BASE = {
    "id": 123,
    "start_date": "2026-09-01T06:30:00Z",
    "distance": 10000.0,
    "moving_time": 3000,
    "total_elevation_gain": 85.5,
}


def test_maps_activity_with_best_efforts_and_pr_rank():
    payload = {
        **BASE,
        "best_efforts": [
            {"name": "5k", "distance": 5000, "elapsed_time": 1450, "pr_rank": 1},
            {"name": "1k", "distance": 1000, "elapsed_time": 270, "pr_rank": None},
        ],
    }
    run = Run.from_strava(payload, user_id=7)
    assert run.source_id == "123"
    assert run.start_time.utcoffset().total_seconds() == 0
    assert [(e.name, e.pr_rank) for e in run.best_efforts] == [("5k", 1), ("1k", None)]


def test_missing_optional_fields_do_not_crash():
    run = Run.from_strava({**BASE, "best_efforts": None}, user_id=7)
    assert run.best_efforts == []
    run = Run.from_strava({k: v for k, v in BASE.items() if k != "total_elevation_gain"}, 7)
    assert run.elevation_gain_m == 0.0


def test_is_training_only_for_race_and_workout():
    flags = {
        wt: Run.from_strava({**BASE, "workout_type": wt}, 7).is_training for wt in (0, 1, 2, 3)
    }
    assert flags == {0: False, 1: True, 2: False, 3: True}
    assert Run.from_strava(BASE, 7).is_training is False
