try:
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtCore import *
from datetime import datetime
from .sync_dialog import SyncDialog


class Controller(QObject):
    def __init__(self, service, app):
        super(Controller, self).__init__()
        self.service = service
        self.app = app
        self.main_window = None
        self.activities_tab = None
        self.records_tab = None
        self.calendar_tab = None
        self.workers = []
        self.workers_mutex = QMutex()

    started = pyqtSignal()

    def initialization_finished(self, main_window):
        self.main_window = main_window
        self.activities_tab = main_window.activities_tab
        self.calendar_tab = main_window.calendar_tab
        self.records_tab = main_window.records_tab
        self.started.connect(self.sync)
        self.started.emit()

    def sync(self):
        if self.service.remote is None:
            return
        self.sync_dialog = SyncDialog()
        self.sync_dialog.show()
        worker = SyncThread(self.service)
        worker.finished.connect(self.sync_dialog.close)
        self._run_worker(worker)

    def delete_activity(self, activity):
        self.service.delete_activity(activity)
        self.update_overview()
        self.sync()

    def update_overview(self):
        self.activities_tab.activity_overview.update_overview()
        self.records_tab.load_records()
        self._cleanup_workers()

    def show_activity_details(self, activity):
        self.activities_tab.load_activity_details(activity)

    def show_activity(self, date):
        activities = self.service.list_activity_for_date(
            datetime(year=date.year(), month=date.month(), day=date.day()))

        if len(activities) > 0:
            # TODO what if there are multiple activities?
            self.main_window.goto_tab("overview")
            self.main_window.activities_tab.load_activity_details(activities[0])

    def save_activity(self, metadata, activity=None):
        if activity is None:
            self.service.new_activity(metadata)
        else:
            self.service.update_activity(activity, metadata)
        self.sync()

    def import_activity(self, filename):
        worker = ImportActivityThread(filename, self.service)
        worker.finished.connect(self.sync)
        self._run_worker(worker)

    def _run_worker(self, worker):
        worker.finished.connect(self.update_overview)
        self.workers_mutex.lock()
        self.workers.append(worker)
        self.workers_mutex.unlock()
        worker.start()

    def _cleanup_workers(self):
        self.workers_mutex.lock()
        self.workers = [w for w in self.workers if not w.isFinished()]
        self.workers_mutex.unlock()


class ImportActivityThread(QThread):
    def __init__(self, filename, service):
        self.running_service = service.clone()
        self.filename = filename
        super(ImportActivityThread, self).__init__()

    def run(self):
        if isinstance(self.filename, tuple):
            filename = self.filename[0]
        else:
            filename = self.filename
        with open(filename, "r") as f:
            self.running_service.import_activity(f.read(), filename)


class SyncThread(QThread):
    def __init__(self, service):
        self.service = service.clone()
        super(SyncThread, self).__init__()

    def run(self):
        self.service.sync_to_server()
