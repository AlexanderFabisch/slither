import os
import tempfile
from datetime import datetime
from slither.database import Database
from slither.domain_model import Activity
from nose.tools import assert_true, assert_false, assert_equal


def test_intialization():
    filename = tempfile.mktemp(prefix="db", suffix=".sqlite")
    assert_false(os.path.exists(filename))
    Database(db_filename=filename)
    assert_true(os.path.exists(filename))


def test_add_activity():
    filename = tempfile.mktemp(prefix="db", suffix=".sqlite")
    db = Database(db_filename=filename)
    activity = Activity(
        start_time=datetime(year=2000, month=10, day=10),
        sport="swimming")
    db.session.add(activity)
    db.session.commit()

    activities = db.list_activities_between(
        datetime(year=2000, month=10, day=5),
        datetime(year=2000, month=10, day=15))
    assert_equal(len(activities), 1)

    activities = db.list_activities_between(
        datetime(year=2000, month=10, day=15),
        datetime(year=2000, month=10, day=25))
    assert_equal(len(activities), 0)

