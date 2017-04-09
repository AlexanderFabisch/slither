try:
    from PyQt4.QtGui import *
except ImportError:
    from PyQt5.QtWidgets import *
from ..data_utils import d


class RecordTable(QTableWidget):
    def __init__(self, controller, parent=None):
        super(RecordTable, self).__init__(parent)
        self.controller = controller
        self.init()

    def init(self):
        self.setShowGrid(False)
        self.setColumnCount(4)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalHeaderLabels(["Sport", "Distance", "Time", "Date"])
        self.verticalHeader().hide()

        self.load_records()

    def load_records(self):
        self.records = self.controller.service.list_records()
        self.setRowCount(len(self.records))
        for i, record in enumerate(self.records):
            self.setItem(i, 0, QTableWidgetItem(d.display_sport(record.sport)))
            self.setItem(i, 1, QTableWidgetItem(
                d.display_distance(record.distance)))
            self.setItem(i, 2, QTableWidgetItem(d.display_time(record.time)))
            activity = record.activity
            if activity is not None:
                self.setItem(i, 3, QTableWidgetItem(
                    d.display_date(record.activity.start_time)))

        self.resizeColumnsToContents()