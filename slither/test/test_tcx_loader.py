import os
from slither.tcx_loader import TcxLoader
from nose.tools import assert_equal, assert_in


def test_load_tracked_activity():
    with open(os.path.join("test_data", "running.tcx")) as f:
        tcx_content = f.read()
    loader = TcxLoader(tcx_content)

    activity = loader.load()
    paths = activity.get_path()

    assert_in("timestamps", paths)
    assert_in("coords", paths)
    assert_in("altitudes", paths)
    assert_in("heartrates", paths)
    assert_in("velocities", paths)
    assert_equal(len(paths["timestamps"]), 750)
