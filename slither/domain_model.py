import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from collections import deque
import numpy as np

from .config import config
from .ui_text import appropriate_partition, d


Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    sport = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    distance = sqlalchemy.Column(sqlalchemy.Float)
    time = sqlalchemy.Column(sqlalchemy.Float)
    calories = sqlalchemy.Column(sqlalchemy.Float)
    heartrate = sqlalchemy.Column(sqlalchemy.Float)
    filetype = sqlalchemy.Column(sqlalchemy.String, default="tcx")
    has_path = sqlalchemy.Column(sqlalchemy.Boolean)
    trackpoints = relationship("Trackpoint")

    def set_path(self, timestamps, coords, altitudes, heartrates, velocities):
        assert len(timestamps) == len(coords), "%d != %d" % (
            len(timestamps), len(coords))
        assert len(timestamps) == len(altitudes), "%d != %d" % (
            len(timestamps), len(altitudes))
        assert len(timestamps) == len(heartrates), "%d != %d" % (
            len(timestamps), len(heartrates))
        assert len(timestamps) == len(velocities), "%d != %d" % (
            len(timestamps), len(velocities))

        self.trackpoints = [
            Trackpoint(timestamp=t, latitude=p[0], longitude=p[1], altitude=a,
                       heartrate=h, velocity=v)
            for t, p, a, h, v in zip(timestamps, coords, altitudes, heartrates,
                                     velocities)]

    def get_filename(self):
        start_time_str = self.start_time.strftime("%Y%m%d_%H%M%S")
        return "%s_%s.tcx" % (self.sport, start_time_str)

    def get_path(self):
        if hasattr(self, "path"):
            return self.path
        elif self.has_path:
            self.path = {
                "timestamps": np.array([t.timestamp for t in self.trackpoints],
                                       dtype=np.float),
                "coords": np.array([(t.latitude, t.longitude)
                                    for t in self.trackpoints], dtype=np.float),
                "altitudes": np.array([t.altitude for t in self.trackpoints],
                                      dtype=np.float),
                "heartrates": np.array([t.heartrate for t in self.trackpoints],
                                       dtype=np.float),
                "velocities": np.array([t.velocity for t in self.trackpoints],
                                       dtype=np.float)
            }
            return self.path
        else:
            return None

    def get_paces(self):  # TODO move data processing to separate module
        path = self.get_path()
        velocities = path["velocities"][1:]
        timestamps = path["timestamps"]
        delta_t = np.diff(timestamps)

        max_velocity = config["max_velocity"].get(
            self.sport, config["max_velocity"]["default"])
        valid_velocities = np.where(velocities <= max_velocity)
        velocities = velocities[valid_velocities]
        delta_t = delta_t[valid_velocities]

        dist = np.cumsum(velocities * delta_t)
        split_distance = appropriate_partition(dist[-1])

        pdt = config["pace_distance_table"]
        pace_distance = pdt.get(self.sport, pdt["other"])

        paces = []
        last_t = 0
        for threshold in range(split_distance, int(dist[-1]), split_distance):
            t = np.argmax(dist >= threshold)
            split_time = timestamps[t] - timestamps[last_t]
            pace = split_time / split_distance * pace_distance
            paces.append((threshold, pace))
            last_t = t
        return paces

    def compute_records(self, distance):
        record = self._check_metadata(distance)
        if self.has_path:
            record = min((record, self._check_path(distance)))
        return Record(sport=self.sport, distance=distance, time=record,
                      activity_id=self.id)

    def _check_metadata(self, distance):
        if self.distance >= distance:
            ratio = self.distance / distance
            return self.time / ratio
        else:
            return float("inf")

    def _check_path(self, distance):
        queue_dist = 0.0
        queue_time = 0.0
        dqueue = deque()
        tqueue = deque()

        v = self.get_path()["velocities"][1:]
        dt = np.diff(self.get_path()["timestamps"])
        record = float("inf")

        for t in range(len(v)):
            if np.isnan(v[t]):
                queue_dist = 0.0
                queue_time = 0.0
                dqueue.clear()
                tqueue.clear()
                continue
            if v[t] > config["max_velocity"][self.sport]:
                continue
            dist = v[t] * dt[t]
            dqueue.appendleft(dist)
            tqueue.appendleft(dt[t])
            queue_dist += dist
            queue_time += dt[t]
            while queue_dist > distance:
                if queue_time < record:
                    record = queue_time
                dist = dqueue.pop()
                time = tqueue.pop()
                queue_dist -= dist
                queue_time -= time

        return record

    def generate_distance_markers(self):
        path = self.get_path()
        timestamps = path["timestamps"]
        velocities = path["velocities"]
        valid_velocities = np.isfinite(velocities)
        timestamps = timestamps[valid_velocities]
        velocities = velocities[valid_velocities]

        delta_t = np.diff(timestamps)
        dist = np.cumsum(velocities[1:] * delta_t)

        marker_dist = appropriate_partition(dist[-1])

        marker_indices = {}
        for threshold in np.arange(marker_dist, int(dist[-1]), marker_dist):
            label = d.display_distance(threshold)
            marker_indices[label] = np.argmax(dist >= threshold)

        return marker_indices


class Trackpoint(Base):
    __tablename__ = "trackpoints"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    activity_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("activities.id"))
    timestamp = sqlalchemy.Column(sqlalchemy.Float)
    latitude = sqlalchemy.Column(sqlalchemy.Float)
    longitude = sqlalchemy.Column(sqlalchemy.Float)
    altitude = sqlalchemy.Column(sqlalchemy.Float)
    heartrate = sqlalchemy.Column(sqlalchemy.Float)
    velocity = sqlalchemy.Column(sqlalchemy.Float)


class Record(Base):
    __tablename__ = "records"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    sport = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    distance = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    time = sqlalchemy.Column(sqlalchemy.Float)
    activity_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("activities.id"))

    activity = relationship("Activity", foreign_keys=[activity_id])


def init_database(session):
    records = [
        Record(sport=sport, distance=distance, time=float("inf"))
        for sport, distances in config["records"].items()
        for distance in distances
    ]
    session.add_all(records)
    session.commit()
