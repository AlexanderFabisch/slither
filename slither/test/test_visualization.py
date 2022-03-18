from slither.loader import TcxLoader
from slither.core.visualization import make_map
from nose.tools import assert_equal, assert_in


def test_make_map():
    with open("test_data/running.tcx", "r") as f:
        loader = TcxLoader(f.read())
    activity = loader.load()
    map = make_map(activity.get_path())
    d = map.to_dict()
    assert_equal(d["name"], "Map")
    assert_in("openstreetmap", d["children"])
