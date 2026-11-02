from app.uptime import uptime_seconds


def test_counts_whole_seconds_since_start():
    assert uptime_seconds(now=lambda: 130.9, started_at=10.0) == 120


def test_never_goes_below_zero():
    assert uptime_seconds(now=lambda: 5.0, started_at=10.0) == 0


def test_uses_the_real_clock_by_default():
    assert uptime_seconds() >= 0
