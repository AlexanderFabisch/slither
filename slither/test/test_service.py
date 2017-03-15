from slither.service import Service
from nose.tools import assert_equal


def test_create_and_delete():
    service = Service(debug=True)
    activities = service.list_activities()
    assert_equal(len(activities), 0)
    filename = "test_data/running.tcx"
    service.import_activity(open(filename, "r").read(), filename)
    activities = service.list_activities()
    assert_equal(len(activities), 1)
    service.delete_activity(activities[0])
    activities = service.list_activities()
    assert_equal(len(activities), 0)
