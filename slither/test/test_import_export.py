from slither.io.tcx_loader import TcxLoader
from slither.export import TcxExport
from nose.tools import assert_equal, assert_almost_equal


def test_import_export():
    filename = "test_data/running.tcx"
    loader = TcxLoader(open(filename, "r").read())
    a1 = loader.load()
    exporter = TcxExport()
    tmp = exporter.dumps(a1)
    loader = TcxLoader(tmp)
    a2 = loader.load()
    assert_equal(a1.calories, a2.calories)
    assert_equal(a1.heartrate, a2.heartrate)
    assert_equal(a1.distance, a2.distance)
    for t1, t2 in zip(a1.trackpoints, a2.trackpoints):
        assert_almost_equal(t1.timestamp, t2.timestamp)
        assert_almost_equal(t1.latitude, t2.latitude)
        assert_almost_equal(t1.longitude, t2.longitude)
        assert_almost_equal(t1.altitude, t2.altitude)
        assert_almost_equal(t1.heartrate, t2.heartrate)
        assert_almost_equal(t1.velocity, t2.velocity, places=4)
