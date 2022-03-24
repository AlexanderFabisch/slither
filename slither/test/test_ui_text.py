import datetime
from slither.core.ui_text import d
from nose.tools import assert_equal


def test_display_date():
    s = d.display_date(datetime.datetime(year=2020, month=3, day=2))
    assert_equal(s, "03/02/20")


def test_display_datetime():
    s = d.display_datetime(
        datetime.datetime(year=2020, month=3, day=2,
                          hour=10, minute=30, second=40))
    assert_equal(s, "2020/03/02 10:30 Mon")


def test_display_sport():
    s = d.display_sport("swimming")
    assert_equal(s, "Swimming")

    s = d.display_sport("running")
    assert_equal(s, "Running")

    s = d.display_sport("racecycling")
    assert_equal(s, "Bicycle Racing")

    s = d.display_sport("cycling")
    assert_equal(s, "Cycling")

    s = d.display_sport("other")
    assert_equal(s, "Other")


def test_display_distance():
    s = d.display_distance(0.0)
    assert_equal(s, "-")

    s = d.display_distance(1000.0)
    assert_equal(s, "1 km")

    s = d.display_distance(1234.0)
    assert_equal(s, "1234 m")

    s = d.display_distance(2345.0)
    assert_equal(s, "2.35 km")


def test_display_time():
    s = d.display_time(0.0)
    assert_equal(s, "-")

    s = d.display_time(None)
    assert_equal(s, "NA")

    s = d.display_time(float("nan"))
    assert_equal(s, "NA")

    s = d.display_time(58.52)
    assert_equal(s, "58.52 s")

    s = d.display_time(3652)
    assert_equal(s, "01:00:52 h")


def test_display_calories():
    s = d.display_calories(0.0)
    assert_equal(s, "-")

    s = d.display_calories(30)
    assert_equal(s, "30 kCal")


def test_display_heartrate():
    s = d.display_heartrate(0.0)
    assert_equal(s, "-")

    s = d.display_heartrate(60)
    assert_equal(s, "60 bpm")
