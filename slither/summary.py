from datetime import datetime, timedelta
from sqlalchemy import func
from . import domain_model


class Summary(object):
    def __init__(self, database):
        self.database = database

    def summarize(self, sport=None):
        raise NotImplementedError("Base class")

    def _summary_entry(self, end, sport, start):
        activities = self.database.list_activities_between(start, end)
        summary = self._summarize_activities(activities, sport)
        summary["start"] = start
        summary["end"] = end
        return summary

    def _start_of_first_activity(self):
        q = self.database.session.query(
            domain_model.Activity, func.min(domain_model.Activity.start_time))
        return q.first()[1]

    def _start_of_last_activity(self):
        q = self.database.session.query(
            domain_model.Activity, func.max(domain_model.Activity.start_time))
        return q.first()[1]

    def _summarize_activities(self, activities, sport):
        distance = 0.0
        time = 0.0
        n_activities = 0
        for activity in activities:
            if sport is None or activity.sport == sport:
                if activity.distance is not None:
                    distance += activity.distance
                if activity.time is not None:
                    time += activity.time
                n_activities += 1
        return {"distance": distance,
                "time": time,
                "n_activities": n_activities}


class WeekSummary(Summary):
    def summarize(self, sport=None):
        start = self._start_of_last_activity()
        start = datetime(year=start.year, month=start.month, day=start.day)
        start = start - timedelta(days=start.weekday())
        earliest = self._start_of_first_activity()

        summaries = []
        while True:
            end = start + timedelta(days=7)
            if end < earliest:
                break
            summary = self._summary_entry(end, sport, start)
            summaries.append(summary)
            start = start - timedelta(days=7)
        return summaries


class MonthSummary(Summary):
    def summarize(self, sport=None):
        latest = self._start_of_last_activity()
        earliest = self._start_of_first_activity()

        year = latest.year
        month = latest.month + 1
        end = datetime(year=year, month=month, day=1)
        summaries = []
        while True:
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            start = datetime(year=year, month=month, day=1)
            if start < earliest:
                break
            summary = self._summary_entry(end, sport, start)
            summaries.append(summary)
            end = start
        return summaries


class YearSummary(Summary):
    def summarize(self, sport=None):
        latest = self._start_of_last_activity()
        earliest = self._start_of_first_activity()

        i = 0
        summaries = []
        while True:
            start = datetime(year=latest.year - i, month=1, day=1)
            end = datetime(year=latest.year - i + 1, month=1, day=1)
            if end < earliest:
                break
            summary = self._summary_entry(end, sport, start)
            summaries.append(summary)
            i += 1
        return summaries