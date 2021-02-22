try:
    from PyQt4.QtGui import *
except ImportError:
    from PyQt5.QtWidgets import *
from ..ui_text import d


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

        self.itemDoubleClicked.connect(self.record_double_clicked)

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

    def record_double_clicked(self, item):
        invalidate_record = InvalidateRecord()
        invalidate_record.setWindowTitle("Record")
        if invalidate_record.exec_():
            record_idx = item.row()
            self.controller.invalidate_record(self.records[record_idx])
            self.load_records()


class InvalidateRecord(QDialog):
    def __init__(self):
        super(InvalidateRecord, self).__init__()

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Invalidate record?"))
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)
