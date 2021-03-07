import os
from functools import partial

from slither.core.visualization import render_map, plot_velocity_histogram, plot_speed_heartrate, plot_elevation

try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4.QtSvg import *
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as \
        FigureCanvas
    from matplotlib.backends.backend_qt4agg import \
        NavigationToolbar2QT as NavigationToolbar
except ImportError:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtSvg import *
    from PyQt5.QtWidgets import *
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
        FigureCanvas
    from matplotlib.backends.backend_qt5agg import \
        NavigationToolbar2QT as NavigationToolbar
try:
    from PyQt4.QtWebKit import *
    WebView = QWebView
    WebPage = QWebPage
except ImportError:
    try:
        from PyQt5.QtWebKitWidgets import *
        from PyQt5.QtWebKit import *
        WebView = QWebView
        WebPage = QWebPage
    except ImportError:
        from PyQt5.QtWebEngineWidgets import *
        WebView = QWebEngineView
        WebPage = QWebEnginePage
from matplotlib.figure import Figure

from .new_activity import EditActivity
from slither.core.config import slither_ressource_filename
from slither.core.config import config
from slither.core.ui_text import d
from slither.core.analysis import get_paces


class ActivityTab(QWidget):
    def __init__(self, controller):
        super(ActivityTab, self).__init__()
        self.controller = controller

        activities_layout = QHBoxLayout()
        self.setLayout(activities_layout)

        splitter = QSplitter(Qt.Horizontal)
        self.activity_overview = ActivityOverview(self.controller, self)
        splitter.addWidget(self.activity_overview)
        self.details_widget = Details(self.controller)
        splitter.addWidget(self.details_widget)
        policy = QSizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Maximum)
        policy.setVerticalPolicy(QSizePolicy.Preferred)
        self.details_widget.setSizePolicy(policy)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        activities_layout.addWidget(splitter)

    def load_activity_details(self, activity):
        self.details_widget.display_activity(activity)


class ActivityOverview(QWidget):
    def __init__(self, controller, parent):
        super(ActivityOverview, self).__init__(parent)
        self.parent = parent

        self.controller = controller
        self.activity_table = ActivityTable(self.controller)

        layout = QGridLayout()
        self.setLayout(layout)

        import_button = QPushButton("Import")
        layout.addWidget(import_button, 0, 0)
        import_button.clicked.connect(self.import_data)

        delete_button = QPushButton("Delete")
        layout.addWidget(delete_button, 0, 1)
        delete_button.clicked.connect(self.delete_selection)

        details_button = QPushButton("Details")
        layout.addWidget(details_button, 0, 2)
        details_button.clicked.connect(self.load_details)

        edit_button = QPushButton("Edit")
        layout.addWidget(edit_button, 0, 3)
        edit_button.clicked.connect(self.edit)

        self.activity_table.itemDoubleClicked.connect(self.load_details)

        layout.addWidget(self.activity_table, 1, 0, 1, 4)

    def import_data(self):
        filename = QFileDialog.getOpenFileName(self, "Open TCX file")
        if filename == "" or filename[0] == "":  # Qt4 and 5 compatible
            return
        self.controller.import_activity(filename)

    def delete_selection(self):
        activity = self.activity_table.selected_activity()
        self.controller.delete_activity(activity)

    def load_details(self, item=None):
        if isinstance(item, QTableWidgetItem):
            activity = self.activity_table.activities[item.row()]
        else:
            activity = self.activity_table.selected_activity()
        self.controller.show_activity_details(activity)

    def edit(self):
        activity = self.activity_table.selected_activity()
        dialog = QDialog()
        layout = QHBoxLayout()
        layout.addWidget(EditActivity(self.controller, activity))
        dialog.setLayout(layout)
        dialog.setWindowTitle("New Activity")
        dialog.exec_()

    def update_overview(self):
        self.activity_table.load_activities()


class ActivityTable(QTableWidget):
    def __init__(self, controller, parent=None):
        super(ActivityTable, self).__init__(parent)
        self.controller = controller
        self.init()

    def init(self):
        self.setShowGrid(False)
        self.setColumnCount(6)

        self.setStyleSheet("QTableView {selection-background-color: red;}")
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalHeaderLabels(["Date", "Sport", "Distance", "Time",
                                        "Calories", "Heart Rate"])
        self.verticalHeader().hide()

        self.load_activities()

    def load_activities(self):
        self.activities = self.controller.service.list_activities()
        self.setRowCount(len(self.activities))
        last_week_id = 0
        cycle_index = 0
        color_cycle = [QColor(255, 222, 87, 100), QColor(69, 132, 255, 100)]
        for i, activity in enumerate(self.activities):
            # We just need some unique week identifier...
            week_of_year = activity.start_time.isocalendar()[1]
            week_id = activity.start_time.year * 53 + week_of_year
            if last_week_id != week_id:
                cycle_index += 1
            last_week_id = week_id
            brush = QBrush(color_cycle[cycle_index % len(color_cycle)])

            items = [QTableWidgetItem(d.display_datetime(activity.start_time)),
                     QTableWidgetItem(d.display_sport(activity.sport)),
                     QTableWidgetItem(d.display_distance(activity.distance)),
                     QTableWidgetItem(d.display_time(activity.time)),
                     QTableWidgetItem(d.display_calories(activity.calories)),
                     QTableWidgetItem(d.display_heartrate(activity.heartrate))]
            for j, item in enumerate(items):
                item.setBackground(brush)
                self.setItem(i, j, item)
        self.resizeColumnsToContents()

        self.setFixedWidth(self.verticalHeader().width() +
                           self.horizontalHeader().length() +
                           self.verticalScrollBar().sizeHint().width() +
                           self.frameWidth() * 2)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def selected_activity(self):
        indices = self.selectedIndexes()
        if len(indices) > self.columnCount():
            raise Exception("More than one activity selected.")
        if len(indices) == self.columnCount():
            index = indices[0].row()
            return self.activities[index]
        raise Exception("No activity selected.")


class Details(QWidget):
    def __init__(self, main_window, parent=None):
        super(Details, self).__init__(parent)
        self.main_window = main_window
        layout = QGridLayout()
        self.setLayout(layout)

        small_picto_size = (30, 30)
        text_size = 80

        self.start_time_label = QLabel("-")
        layout.addWidget(self.start_time_label, 0, 0, 1, 5)
        self.sport_pictogram = QSvgWidget()
        self.sport_pictogram.load(slither_ressource_filename("unknown.svg"))
        self.sport_pictogram.setFixedSize(50, 50)
        layout.addWidget(self.sport_pictogram, 2, 0, 2, 1)
        self.sport_label = QLabel("-")
        self.sport_label.setFixedWidth(text_size)
        layout.addWidget(self.sport_label, 4, 0)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line, 1, 0, 1, 5)

        distance_pictogram = QSvgWidget(slither_ressource_filename("distance.svg"))
        distance_pictogram.setFixedSize(*small_picto_size)
        layout.addWidget(distance_pictogram, 2, 1)
        layout.addWidget(QLabel("Distance"), 3, 1)
        self.distance_label = QLabel("-")
        self.distance_label.setFixedWidth(text_size)
        layout.addWidget(self.distance_label, 4, 1)

        time_pictogram = QSvgWidget(slither_ressource_filename("time.svg"))
        time_pictogram.setFixedSize(*small_picto_size)
        layout.addWidget(time_pictogram, 2, 2)
        layout.addWidget(QLabel("Time"), 3, 2)
        self.time_label = QLabel("-")
        self.time_label.setFixedWidth(text_size)
        layout.addWidget(self.time_label, 4, 2)

        hr_pictogram = QSvgWidget(slither_ressource_filename("heartrate.svg"))
        hr_pictogram.setFixedSize(*small_picto_size)
        layout.addWidget(hr_pictogram, 2, 3)
        layout.addWidget(QLabel("Heart Rate"), 3, 3)
        self.heartrate_label = QLabel("-")
        self.heartrate_label.setFixedWidth(text_size)
        layout.addWidget(self.heartrate_label, 4, 3)

        calories_pictogram = QSvgWidget(slither_ressource_filename("calories.svg"))
        calories_pictogram.setFixedSize(*small_picto_size)
        layout.addWidget(calories_pictogram, 2, 4)
        layout.addWidget(QLabel("Calories"), 3, 4)
        self.calories_label = QLabel("-")
        self.calories_label.setFixedWidth(text_size)
        layout.addWidget(self.calories_label, 4, 4)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line, 5, 0, 1, 5)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 6, 0, 1, 5)

        self.plot_widget = Plot()
        self.tabs.addTab(self.plot_widget, "Plot")

        self.map_widget = Map()
        map_item = self.tabs.addTab(self.map_widget, "Map")

        self.pace_widget = PaceTable()
        self.tabs.addTab(self.pace_widget, "Pace")

        self.best_split_widget = BestSplitTable(self.main_window)
        self.tabs.addTab(self.best_split_widget, "Best Splits")

        self.velocity_histogram = VelocityHistogram()
        self.tabs.addTab(self.velocity_histogram, "Velocities")

        self.elevation_profile = ElevationProfile()
        self.tabs.addTab(self.elevation_profile, "Elevation Profile")

        # We reload the map when we switch to this tab and we have
        # a new activity because otherwise the map would sometimes
        # be zoomed out.
        self.tabs.currentChanged.connect(
            partial(self.map_widget.refresh_if_changed_to_map,
                    map_item=map_item))

    def display_activity(self, activity):
        self._display_general_info(activity)
        self.plot_widget.load_plot(activity)
        self.map_widget.load_map(activity)
        self.pace_widget.load_paces(activity)
        self.best_split_widget.load_best_splits(activity)
        self.velocity_histogram.load_velocity_histogram(activity)
        self.elevation_profile.load_elevation_profile(activity)

    def _display_general_info(self, activity):
        self.start_time_label.setText(
            d.display_datetime(activity.start_time))
        self._pictogram(activity)
        self.sport_label.setText(d.display_sport(activity.sport))
        self.distance_label.setText(d.display_distance(activity.distance))
        self.time_label.setText(d.display_time(activity.time))
        self.heartrate_label.setText(d.display_heartrate(activity.heartrate))
        self.calories_label.setText(d.display_calories(activity.calories))

    def _pictogram(self, activity):
        pictogram_filename = slither_ressource_filename(activity.sport + ".svg")
        if os.path.exists(pictogram_filename):
            self.sport_pictogram.load(pictogram_filename)
        else:
            self.sport_pictogram.load(slither_ressource_filename("unknown.svg"))


class Plot(QWidget):
    def __init__(self, parent=None):
        super(Plot, self).__init__(parent)

        try:
            import seaborn as sns
            sns.set()
        except AttributeError:
            pass  # TODO log?

        self.fig_velocity = Figure((5, 3), dpi=100)
        self.fig_velocity.subplots_adjust(
            left=0.12, right=0.88, bottom=0.15, top=0.98)

        self.ax_velocity = self.fig_velocity.add_subplot(111)
        self.ax_heartrate = self.ax_velocity.twinx()
        self.legend = self.fig_velocity.legend([], [])

        self.canvas = FigureCanvas(self.fig_velocity)
        self.canvas.setParent(self)
        toolbar = NavigationToolbar(self.canvas, self)

        plot_layout = QVBoxLayout()
        self.setLayout(plot_layout)
        plot_layout.addWidget(self.canvas)
        plot_layout.addWidget(toolbar)

    def load_plot(self, activity):
        self.fig_velocity.delaxes(self.ax_velocity)
        self.fig_velocity.delaxes(self.ax_heartrate)
        self.legend.remove()
        self.ax_velocity = self.fig_velocity.add_subplot(111)
        self.ax_heartrate = self.ax_velocity.twinx()

        if activity.has_path:
            path = activity.get_path()
            lines, labels = plot_speed_heartrate(self.ax_velocity, self.ax_heartrate, path)
            axbox = self.ax_velocity.get_position()
            self.legend = self.fig_velocity.legend(
                handles=lines, labels=labels, loc=(axbox.x0 + 0.1,
                                                   axbox.y0 + 0.1))
        else:
            self.ax_velocity.set_xticks(())
            self.ax_velocity.set_yticks(())
            self.ax_heartrate.set_yticks(())
            self.legend = self.fig_velocity.legend([], [])

        self.canvas.draw()


class Map(WebView):
    def __init__(self, parent=None):
        super(Map, self).__init__(parent)
        self.setPage(WebPage())
        self.new_activity_loaded = False

    def load_map(self, activity):
        if activity.has_path:
            html = render_map(activity.get_path())
            self.setHtml(html)
            self.new_activity_loaded = True
        else:
            self.setHtml("")

    def refresh_if_changed_to_map(self, item, map_item):
        if item == map_item and self.new_activity_loaded:
            self.new_activity_loaded = False
            self.reload()


class PaceTable(QTableWidget):
    def __init__(self, parent=None):
        super(PaceTable, self).__init__(parent)
        self.init()

    def init(self):
        self.setShowGrid(False)
        self.setColumnCount(2)

        self.setHorizontalHeaderLabels(["Distance", "Pace"])
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().hide()

    def load_paces(self, activity):
        pdt = config["pace_distance_table"]
        pace_distance = pdt.get(activity.sport, pdt["other"])
        self.setHorizontalHeaderLabels(
            ["Distance", "Pace / %s" % d.display_distance(pace_distance)])

        if activity.get_path() is None:
            self.setRowCount(0)
            return

        paces = get_paces(activity.get_path(), activity.sport)
        self.setRowCount(len(paces))
        for i, pace in enumerate(paces):
            self.setItem(i, 0, QTableWidgetItem(d.display_distance(pace[0])))
            self.setItem(i, 1, QTableWidgetItem(d.display_time(pace[1])))

        self.resizeColumnsToContents()


class BestSplitTable(QTableWidget):
    def __init__(self, main_window, parent=None):
        super(BestSplitTable, self).__init__(parent)
        self.main_window = main_window
        self.init()

    def init(self):
        self.setShowGrid(False)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Distance", "Time"])
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().hide()

    def load_best_splits(self, activity):
        best_splits = self.main_window.service.get_best_splits(activity)
        self.setRowCount(len(best_splits))
        for i, best_split in enumerate(best_splits):
            self.setItem(i, 0, QTableWidgetItem(
                d.display_distance(best_split[0])))
            self.setItem(i, 1, QTableWidgetItem(
                d.display_time(best_split[1])))

        self.resizeColumnsToContents()


class VelocityHistogram(QWidget):
    def __init__(self, parent=None):
        super(VelocityHistogram, self).__init__(parent)

        try:
            import seaborn as sns
            sns.set()
        except AttributeError:
            pass  # TODO log?

        self.fig = Figure((5, 3), dpi=100)
        self.fig.subplots_adjust(left=0.12, right=0.88, bottom=0.15, top=0.98)

        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        toolbar = NavigationToolbar(self.canvas, self)

        plot_layout = QVBoxLayout()
        self.setLayout(plot_layout)
        plot_layout.addWidget(self.canvas)
        plot_layout.addWidget(toolbar)

    def load_velocity_histogram(self, activity):
        self.fig.delaxes(self.ax)
        self.ax = self.fig.add_subplot(111)

        if activity.has_path:
            plot_velocity_histogram(activity.get_path(), self.ax)
        else:
            self.ax.set_xticks(())
            self.ax.set_yticks(())

        self.canvas.draw()


class ElevationProfile(QWidget):
    def __init__(self, parent=None):
        super(ElevationProfile, self).__init__(parent)

        try:
            import seaborn as sns
            sns.set()
        except AttributeError:
            pass  # TODO log?

        self.fig = Figure((5, 3), dpi=100)
        self.fig.subplots_adjust(left=0.12, right=0.88, bottom=0.15, top=0.88)

        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        toolbar = NavigationToolbar(self.canvas, self)

        plot_layout = QVBoxLayout()
        self.setLayout(plot_layout)
        plot_layout.addWidget(self.canvas)
        plot_layout.addWidget(toolbar)

    def load_elevation_profile(self, activity):
        self.fig.delaxes(self.ax)
        self.ax = self.fig.add_subplot(111)

        if activity.has_path:
            plot_elevation(activity.get_path(), self.ax)
        else:
            self.ax.set_xticks(())
            self.ax.set_yticks(())

        self.canvas.draw()
