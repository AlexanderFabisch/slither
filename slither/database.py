"""Database interface."""
import os
import sqlalchemy
from . import domain_model
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self._setup_database()

    def _setup_database(self):
        self.engine = sqlalchemy.create_engine("sqlite:///" + self.db_filename)
        initialized = os.path.exists(self.db_filename)
        if not initialized:
            domain_model.Base.metadata.create_all(bind=self.engine)

        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()
        if not initialized:
            domain_model.init_database(self.session)

    def list_activities_between(self, start, end):
        q = self.session.query(domain_model.Activity)
        return q.filter(sqlalchemy.and_(
            domain_model.Activity.start_time >= start,
            domain_model.Activity.start_time < end
        )).order_by(sqlalchemy.asc(domain_model.Activity.start_time)).all()
