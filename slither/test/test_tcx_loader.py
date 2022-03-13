import os
from datetime import datetime
from slither.loader import TcxLoader
from nose.tools import assert_equal, assert_in


def test_load_tracked_activity():
    with open(os.path.join("test_data", "running.tcx")) as f:
        tcx_content = f.read()
    loader = TcxLoader(tcx_content)

    activity = loader.load()
    assert_equal(activity.sport, "running")
    assert_equal(
        activity.start_time,
        datetime(year=2016, month=12, day=11, hour=10, minute=54, second=30))
    assert_equal(activity.distance, 2200)
    assert_equal(activity.time, 750)
    assert_equal(activity.heartrate, 154)
    assert_equal(activity.calories, 0)
    paths = activity.get_path()

    assert_in("timestamps", paths)
    assert_in("coords", paths)
    assert_in("altitudes", paths)
    assert_in("heartrates", paths)
    assert_in("velocities", paths)
    assert_equal(len(paths["timestamps"]), 750)
