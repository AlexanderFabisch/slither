import datetime
from slither.loader import FitLoader
from nose.tools import assert_equal, assert_true


def test_fit_loader():
    fit_loader = FitLoader(filename="test_data/running.fit")
    activity = fit_loader.load()
    assert_equal(activity.sport, "running")
    assert_equal(
        activity.start_time,
        datetime.datetime(
            year=2021, month=3, day=13, hour=12, minute=49, second=2))
    assert_equal(activity.time, 3087.19)
    assert_equal(activity.distance, 7864.22)
    assert_equal(activity.calories, 710)
    assert_equal(activity.filetype, "fit")
    assert_true(activity.has_path)
