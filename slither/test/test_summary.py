from datetime import datetime
from slither.service import Service
from nose.tools import assert_equal


def test_year_summary():
    service = Service(debug=True)
    service.new_activity({"start_time": datetime(year=2000, month=1, day=15),
                          "sport": "running",
                          "distance": 5.0,
                          "time": 3.0})
    service.new_activity({"start_time": datetime(year=2000, month=1, day=16),
                          "sport": "running",
                          "distance": 10.0,
                          "time": 6.0})
    try:
        summary = service.summarize_years(sport="running")
        assert_equal(len(summary), 1)
        assert_equal(summary[0]["n_activities"], 2)
        assert_equal(summary[0]["distance"], 15.0)
        assert_equal(summary[0]["time"], 9.0)
    finally:
        for a in service.list_activities():
            service.delete_activity(a)


def test_month_summary():
    service = Service(debug=True)
    service.new_activity({"start_time": datetime(year=2000, month=1, day=1),
                          "sport": "running",
                          "distance": 5.0,
                          "time": 3.0})
    service.new_activity({"start_time": datetime(year=2000, month=2, day=1),
                          "sport": "running",
                          "distance": 10.0,
                          "time": 6.0})
    try:
        summary = service.summarize_months(sport="running")
        assert_equal(len(summary), 2)
        assert_equal(summary[0]["n_activities"], 1)
        assert_equal(summary[0]["distance"], 10.0)
        assert_equal(summary[0]["time"], 6.0)
        assert_equal(summary[1]["n_activities"], 1)
        assert_equal(summary[1]["distance"], 5.0)
        assert_equal(summary[1]["time"], 3.0)
    finally:
        for a in service.list_activities():
            service.delete_activity(a)


def test_week_summary():
    service = Service(debug=True)
    service.new_activity({"start_time": datetime(year=2000, month=1, day=1),
                          "sport": "running",
                          "distance": 5.0,
                          "time": 3.0})
    service.new_activity({"start_time": datetime(year=2000, month=1, day=8),
                          "sport": "running",
                          "distance": 10.0,
                          "time": 6.0})
    try:
        summary = service.summarize_weeks(sport="running")
        assert_equal(len(summary), 2)
        assert_equal(summary[0]["n_activities"], 1)
        assert_equal(summary[0]["distance"], 10.0)
        assert_equal(summary[0]["time"], 6.0)
        assert_equal(summary[1]["n_activities"], 1)
        assert_equal(summary[1]["distance"], 5.0)
        assert_equal(summary[1]["time"], 3.0)
    finally:
        for a in service.list_activities():
            service.delete_activity(a)
