import datetime
from slither.service import Service
from slither.domain_model import Activity
from nose.tools import assert_equal, assert_raises


def test_add_and_delete_activity():
    service = Service(debug=True)
    activity = Activity(
        sport="running", start_time=datetime.datetime.now(), distance=0.0)
    service.add_new_activity(activity)
    activities = service.list_activities()
    assert_equal(len(activities), 1)
    service.delete_activity(activities[0])
    activities = service.list_activities()
    assert_equal(len(activities), 0)


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


def test_new_activity_failure():
    service = Service(debug=True)
    assert_raises(
        ValueError, service.new_activity,
        {"start_time": datetime.datetime.now(), "distance": 0.0})
    assert_raises(
        ValueError, service.new_activity,
        {"sport": "running", "distance": 0.0})


def test_add_and_update_activity():
    service = Service(debug=True)
    service.new_activity(
        {"sport": "running", "start_time": datetime.datetime.now(),
         "distance": 0.0})
    activities = service.list_activities()
    assert_equal(len(activities), 1)
    service.update_activity(
        activities[0],
        {"sport": "running", "start_time": datetime.datetime.now(),
         "distance": 1.0})
    assert_equal(activities[0].distance, 1.0)
    service.delete_activity(activities[0])
    activities = service.list_activities()
    assert_equal(len(activities), 0)


def test_clone():
    service = Service(debug=True)
    service.new_activity(
        {"sport": "running", "start_time": datetime.datetime.now(),
         "distance": 0.0})
    activities = service.list_activities()
    assert_equal(len(activities), 1)
    cloned_service = service.clone()
    service.delete_activity(activities[0])
    activities = service.list_activities()
    assert_equal(len(activities), 0)
    activities = cloned_service.list_activities()
    assert_equal(len(activities), 0)
