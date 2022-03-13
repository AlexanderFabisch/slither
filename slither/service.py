"""Slither service."""
import os
from datetime import timedelta
import sqlalchemy
from sqlalchemy import func
from . import domain_model
from .core.config import config
from .loader import Loader
from .io.tcx_export import TcxExport
from .database import Database
from .registry import Registry
from .summary import WeekSummary, MonthSummary, YearSummary
from .synchronization import Synchronizer


class Service:
    """Service of the slither application.

    Parameters
    ----------
    debug : bool, optional (default: False)
        Start service in debug mode. In that case data will be stored in a
        subfolder 'debug/'.

    db_filename : str, optional (default: 'db.sqlite')
        Name of the database file.

    datadir : str, optional (default: 'data')
        Subdirectory in which the activity files will be stored.

    remote : str, optional (default: None)
        URL to remote data repository.

    username : str, optional (default: None)
        Username for remote data repository.

    password : str, optional (default: None)
        Password for remote data repository.

    base_path : str, optional (default: None)
        Base path at which application data will be stored.
    """
    def __init__(self, debug=False, db_filename="db.sqlite", datadir="data",
                 remote=None, username=None, password=None, base_path=None):
        self.debug = debug
        self.db_filename = db_filename
        self.datadir = datadir
        self.remote = remote
        self.username = username
        self.password = password
        self.base_path = base_path

        temp_dir = self._setup_directories(debug, datadir)
        self.database = Database(os.path.join(temp_dir, db_filename))
        self.registry = Registry(temp_dir)

    def _setup_directories(self, debug, datadir):
        """Prepare files for application.

        Parameters
        ----------
        debug : bool
            Start service in debug mode. In that case data will be stored in a
            subfolder 'debug/'.

        datadir : str
            Subdirectory in which the activity files will be stored.

        Returns
        -------
        temp_dir : str
            Path to directory in which application data will be stored.
        """
        if self.base_path is None:
            if debug:
                temp_dir = os.path.expanduser(
                    os.path.join("~", ".slither", "debug"))
            else:
                temp_dir = os.path.expanduser(os.path.join("~", ".slither"))
        else:
            temp_dir = self.base_path
        config["temp_dir"] = temp_dir
        self.full_datadir = os.path.join(temp_dir, datadir)
        if not os.path.exists(self.full_datadir):
            os.makedirs(self.full_datadir)
        if not os.path.exists(os.path.join(temp_dir, "cache")):
            os.makedirs(os.path.join(temp_dir, "cache"))
        return temp_dir

    def clone(self):
        """Clone service.

        Returns
        -------
        service : Service
            Cloned service.
        """
        return Service(self.debug, self.db_filename, self.datadir,
                       self.remote, self.username, self.password,
                       self.base_path)

    def list_activities(self):
        """List all activities.

        Returns
        -------
        activities : list
            List of all activities.
        """
        q = self.database.session.query(domain_model.Activity)
        return q.order_by(sqlalchemy.desc(domain_model.Activity.start_time)
                          ).all()

    def list_activity_for_date(self, date):
        """List activities on a specific day.

        Parameters
        ----------
        date : datetime
            Day.

        Returns
        -------
        activities : list
            List of all activities on a specific day.
        """
        return self.database.list_activities_between(
            date, date + timedelta(days=1))

    def new_activity(self, metadata):
        """Add new activity.

        Deprecated. Use add_new_activity instead.

        Parameters
        ----------
        metadata : dict
            Activity metadata.

        Raises
        ------
        ValueError
            Insufficient metadata.
        """
        if "sport" not in metadata:
            raise ValueError("Sport is missing.")
        if "start_time" not in metadata:
            raise ValueError("Start time is missing.")

        activity = domain_model.Activity(**metadata)

        self._store_activity(activity)

    def update_activity(self, activity, metadata):
        """Update activity.

        Parameters
        ----------
        activity : Activity
            An activity that should be modified.

        metadata : dict
            New metadata.
        """
        self.registry.delete(activity.get_filename())
        self._delete_records_for(activity)
        self.database.session.flush()

        for k, v in metadata.items():
            setattr(activity, k, v)

        self._store_activity(activity)

    def _store_activity(self, activity):
        """Store an activity

        Parameters
        ----------
        activity : Activity
            An activity that should be stored.
        """
        self.database.session.add(activity)
        self.database.session.flush()

        self._add_records_for(activity)
        self.database.session.commit()

        tcx = TcxExport().dumps(activity)
        target_filename = os.path.join(
            self.full_datadir, activity.get_filename())
        self.registry.update(tcx, target_filename)

    def _add_records_for(self, activity):
        """Add records from an activity.

        Parameters
        ----------
        activity : Activity
            An activity from which the records should be stored.
        """
        distances = config["records"].get(activity.sport, [])
        for distance in distances:
            record = activity.compute_records(distance)
            self.database.session.add(record)

    def import_activity(self, file_content, filename=None, timestamp=None):
        """Import activity from a format that can be inferred automatically.

        Parameters
        ----------
        file_content : str
            Activity in a format like e.g. TCX

        filename : str, optional (default: None)
            Filename that can be used to infer the data format, e.g. "test.tcx"

        timestamp : float, optional (default: None)
            Timestamp of last update (in case this activity has been
            transferred from a remote data repository)
        """
        loader = Loader(filename)
        loader = loader.get_loader(file_content)

        activity = loader.load()

        self.add_new_activity(activity, timestamp)

    def add_new_activity(self, activity, timestamp=None):
        """Add new activity.

        Parameters
        ----------
        activity : Activity
            New activity.

        timestamp : float, optional (default: None)
            Timestamp of last update (in case this activity has been
            transferred from a remote data repository).

        Raises
        ------
        ValueError
            Activity exists already.

        IOError
            File cannot be stored in registry.
        """
        target_filename = os.path.join(
            self.full_datadir, activity.get_filename())
        if os.path.exists(target_filename):
            raise ValueError("File '%s' exists already" % target_filename)
        self.database.session.add(activity)
        self.database.session.flush()
        self._add_records_for(activity)
        self.database.session.commit()
        try:
            tcx = TcxExport().dumps(activity)
            self.registry.update(tcx, target_filename, timestamp)
        except:
            self.delete_activity(activity)
            raise IOError("File '%s' could not be written" % target_filename)

    def _get_record_distances(self, sport):
        q = self.database.session.query(domain_model.Record.distance)
        res = q.filter(domain_model.Record.sport == sport).distinct(
            domain_model.Record.distance).all()
        return [distance for distance, in res]

    def delete_activity(self, activity):
        """Delete activity.

        Parameters
        ----------
        activity : Activity
            An activity that should be deleted.
        """
        filename = os.path.join(self.full_datadir, activity.get_filename())
        self._delete_records_for(activity)
        self.database.session.delete(activity)
        self.database.session.commit()
        self.registry.delete(filename)

    def _delete_records_for(self, activity):
        for record in self._get_records_for_activity(activity):
            self.database.session.delete(record)

    def get_best_splits(self, activity):
        """Get best splits of an activity.

        Parameters
        ----------
        activity : Activity
            An activity from which splits should be extracted.
        """
        records = self._get_records_for_activity(activity)
        return [(record.distance, record.time) for record in records]

    def _get_records_for_activity(self, activity):
        q = self.database.session.query(domain_model.Record)
        records = q.filter(domain_model.Record.activity_id == activity.id
                           ).order_by(domain_model.Record.distance).all()
        return records

    def list_records(self):
        q = self.database.session.query(
            domain_model.Record, func.min(domain_model.Record.time))
        grouped = q.filter(domain_model.Record.valid).group_by(
            domain_model.Record.sport, domain_model.Record.distance)
        res = grouped.order_by(domain_model.Record.sport,
                               domain_model.Record.distance).all()
        return [record for record, _ in res]

    def summarize_weeks(self, sport=None):
        return WeekSummary(self.database).summarize(sport)

    def summarize_months(self, sport=None):
        return MonthSummary(self.database).summarize(sport)

    def summarize_years(self, sport=None):
        return YearSummary(self.database).summarize(sport)

    def invalidate_record(self, record):
        record.valid = False
        self.database.session.commit()

    def sync_to_server(self):
        Synchronizer(self, self.remote, self.username, self.password
                     ).sync_to_server()
