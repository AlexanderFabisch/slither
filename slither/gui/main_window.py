"""Slither main window."""
try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except ImportError:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
from .activity import ActivityTab
from .calendar_overview import CalendarOverview
from .record_table import RecordTable
from .new_activity import EditActivity
from .summary import SummaryTab


class MainWindow(QMainWindow):
    """Slither main window.

    Parameters
    ----------
    controller : Controller
        GUI controller.
    """
    def __init__(self, controller):
        super(MainWindow, self).__init__()

        self.controller = controller

        self.setWindowTitle("Slither")

        self.menu_bar = QMenuBar()
        new_action = QAction("New Activity", self)
        new_action.triggered.connect(self.new_activity)
        self.menu_bar.addAction(new_action)
        self.setMenuBar(self.menu_bar)

        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self.activities_tab = ActivityTab(self.controller)
        self.central_widget.addTab(self.activities_tab, "Activities")

        self.calendar_tab = CalendarOverview(self.controller)
        self.central_widget.addTab(self.calendar_tab, "Calendar")

        self.records_tab = RecordTable(self.controller)
        self.central_widget.addTab(self.records_tab, "Personal Records")

        self.summary_tab = SummaryTab(self.controller)
        self.central_widget.addTab(self.summary_tab, "Summary")

        self.controller.initialization_finished(self)

    def goto_tab(self, name):
        """Switch tab.

        Parameters
        ----------
        name : str
            Name of the tab.
        """
        tab = {"overview": self.activities_tab,
               "calendar": self.calendar_tab,
               "records": self.records_tab,
               "summary": self.summary_tab}[name]
        self.central_widget.setCurrentWidget(tab)

    def new_activity(self):
        """Open dialog to create new activity."""
        dialog = QDialog()
        layout = QHBoxLayout()
        layout.addWidget(EditActivity(self.controller))
        dialog.setLayout(layout)
        dialog.setWindowTitle("New Activity")
        dialog.exec_()
