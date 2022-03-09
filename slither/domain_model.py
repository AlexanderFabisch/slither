"""Domain model."""
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import numpy as np

from slither.core.analysis import fastest_part
from slither.core.config import config


Base = declarative_base()


class Activity(Base):
    """Activity."""
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

    def compute_records(self, distance):
        record = self._check_metadata(distance)
        if self.has_path:
            timestamps = self.get_path()["timestamps"]
            velocities = self.get_path()["velocities"]
            record = min((record, fastest_part(self.sport, timestamps, velocities, distance)))
        return Record(sport=self.sport, distance=distance, time=record,
                      activity_id=self.id)

    def _check_metadata(self, distance):
        if self.distance >= distance:
            ratio = self.distance / distance
            return self.time / ratio
        else:
            return float("inf")

    def __str__(self):
        return ("Activity(id=%s, sport=%s, start_time=%s, time=%f, ...)"
                % (self.id, self.sport, self.start_time, self.time))


class Trackpoint(Base):
    """Trackpoint."""
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
    """Record.

    A record is the fastest time for a given distance and sport.
    """
    __tablename__ = "records"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    sport = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    distance = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    time = sqlalchemy.Column(sqlalchemy.Float)
    valid = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
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
