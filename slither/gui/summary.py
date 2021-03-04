try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except ImportError:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
from slither.core.config import config
from slither.core.ui_text import d
from datetime import timedelta


class SummaryTab(QWidget):
    def __init__(self, controller, parent=None):
        super(SummaryTab, self).__init__(parent)
        self.controller = controller
        self.init()

    def init(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.sports = config["sports"]
        self.periods = ["Year", "Month", "Week"]  # TODO

        self.sport_combobox = QComboBox()
        for sport in self.sports:
            self.sport_combobox.addItem(d.display_sport(sport))
        layout.addWidget(self.sport_combobox, 0, 0)

        self.period_combobox = QComboBox()
        for period in self.periods:
            self.period_combobox.addItem(period)
        layout.addWidget(self.period_combobox, 0, 1)

        self.update_button = QPushButton("Update")
        layout.addWidget(self.update_button, 0, 2)
        self.update_button.clicked.connect(self.update_view)

        self.summary_table = SummaryTable(self.controller)
        layout.addWidget(self.summary_table, 1, 0, 1, 3)

    def update_view(self):
        sport = self.sports[self.sport_combobox.currentIndex()]
        period = self.periods[self.period_combobox.currentIndex()]
        if period == "Year":
            entries = self.controller.service.summarize_years(sport)
        elif period == "Month":
            entries = self.controller.service.summarize_months(sport)
        else:
            entries = self.controller.service.summarize_weeks(sport)
        self.summary_table.load_summary(entries)


class SummaryTable(QTableWidget):
    def __init__(self, controller, parent=None):
        super(SummaryTable, self).__init__(parent)
        self.controller = controller
        self.init()

    def init(self):
        self.setShowGrid(False)
        self.setColumnCount(5)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().hide()

        self.load_summary([])

    def load_summary(self, entries):
        self.setHorizontalHeaderLabels(
            ["Start", "End", "Distance", "Time", "Activities"])

        self.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self.setItem(i, 0, QTableWidgetItem(d.display_date(entry["start"])))
            # display last day of the period
            self.setItem(i, 1, QTableWidgetItem(
                d.display_date(entry["end"] - timedelta(seconds=1))))
            self.setItem(i, 2, QTableWidgetItem(
                d.display_distance(entry["distance"])))
            self.setItem(i, 3, QTableWidgetItem(d.display_time(entry["time"])))
            self.setItem(i, 4, QTableWidgetItem(str(entry["n_activities"])))

        self.resizeColumnsToContents()