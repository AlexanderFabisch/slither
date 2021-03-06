import os

import folium
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
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
from scipy.signal import medfilt

from ..data_utils import is_outlier
from .new_activity import EditActivity
from ..config import slither_ressource_filename
from ..config import config
from ..data_utils import d, convert_mps_to_kmph, check_coords


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

        layout.addWidget(self.activity_table, 1, 0, 1, 4)

    def import_data(self):
        filename = QFileDialog.getOpenFileName(self, "Open TCX file")
        if filename == "":
            return
        self.controller.import_activity(filename)

    def delete_selection(self):
        activity = self.activity_table.selected_activity()
        self.controller.delete_activity(activity)

    def load_details(self):
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
        color_cycle = [QColor(255, 100, 100, 50), QColor(100, 100, 255, 50)]
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

        tabs = QTabWidget()
        layout.addWidget(tabs, 6, 0, 1, 5)

        self.plot_widget = Plot()
        tabs.addTab(self.plot_widget, "Plot")

        self.map_widget = Map()
        tabs.addTab(self.map_widget, "Map")

        self.pace_widget = PaceTable()
        tabs.addTab(self.pace_widget, "Pace")

        self.best_split_widget = BestSplitTable(self.main_window)
        tabs.addTab(self.best_split_widget, "Best Splits")

        self.velocity_histogram = VelocityHistogram()
        tabs.addTab(self.velocity_histogram, "Velocities")

    def display_activity(self, activity):
        self._display_general_info(activity)
        self.plot_widget.load_plot(activity)
        self.map_widget.load_map(activity)
        self.pace_widget.load_paces(activity)
        self.best_split_widget.load_best_splits(activity)
        self.velocity_histogram.load_velocity_histogram(activity)

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
            plt.style.use("ggplot")
        except AttributeError:
            pass  # TODO log?

        self.fig_velocity = Figure((5, 3), dpi=100)
        self.fig_velocity.patch.set_facecolor("lightgray")
        self.fig_velocity.subplots_adjust(
            left=0.12, right=0.88, bottom=0.15, top=0.98)

        self.ax_velocity = self.fig_velocity.add_subplot(111)
        self.ax_heartrate = self.ax_velocity.twinx()
        self.legend = self.fig_velocity.legend([], [])

        self.canvas = FigureCanvas(self.fig_velocity)
        self.canvas.setParent(self)
        toolbar = NavigationToolbar(self.canvas, self)

        self.setStyleSheet("background-color:lightgray;")
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
            lines, labels = plot(self.ax_velocity, self.ax_heartrate, path)
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
        self.setStyleSheet("background-color:lightgray;")

    def load_map(self, activity):
        if activity.has_path:
            html = render_map(activity)
            self.setHtml(html)
        else:
            self.setHtml("")


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

        # TODO do we really want to compute this here?
        paces = activity.get_paces()
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
            plt.style.use("ggplot")
        except AttributeError:
            pass  # TODO log?

        self.fig = Figure((5, 3), dpi=100)
        self.fig.patch.set_facecolor("lightgray")
        self.fig.subplots_adjust(left=0.12, right=0.88, bottom=0.15, top=0.98)

        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        toolbar = NavigationToolbar(self.canvas, self)

        self.setStyleSheet("background-color:lightgray;")
        plot_layout = QVBoxLayout()
        self.setLayout(plot_layout)
        plot_layout.addWidget(self.canvas)
        plot_layout.addWidget(toolbar)

    def load_velocity_histogram(self, activity):
        self.fig.delaxes(self.ax)
        self.ax = self.fig.add_subplot(111)

        if activity.has_path:
            plot_velocities(activity, self.ax)
        else:
            self.ax.set_xticks(())
            self.ax.set_yticks(())

        self.canvas.draw()


def plot(vel_axis, hr_axis, path):
    timestamps, velocities, heartrates = post_processing(path)

    matplotlib.rcParams["font.size"] = 10
    matplotlib.rcParams["legend.fontsize"] = 10

    handles = []
    labels = []

    n_steps = len(timestamps)

    vel_line, = vel_axis.plot(timestamps, velocities, color="#4f86f7",
                              alpha=0.8, lw=2)
    handles.append(vel_line)
    labels.append("Velocity")

    vel_axis.set_xlim((timestamps[0], timestamps[-1]))
    mean = np.nanmean(np.sort(velocities)[n_steps // 4:-n_steps // 4])
    vel_axis.set_ylim((0, 2 * mean))
    vel_axis.set_xlabel("Time [min]")
    vel_axis.set_ylabel("Velocity [km/h]")
    vel_axis.tick_params(axis="both", which="both", length=0)
    vel_axis.grid(True)

    if np.isfinite(heartrates).any():
        mean = np.nanmean(np.sort(heartrates)[n_steps // 4:-n_steps // 4])
        hr_line, = hr_axis.plot(timestamps, heartrates, color="#a61f34",
                                alpha=0.8, lw=2)
        handles.append(hr_line)
        labels.append("Heart Rate")

        hr_axis.set_ylim((0, 2 * mean))
        hr_axis.set_ylabel("Heart Rate [bpm]")
        hr_axis.tick_params(axis="both", which="both", length=0)
        hr_axis.spines["top"].set_visible(False)
    else:
        hr_axis.set_yticks(())
    hr_axis.grid(False)

    return handles, labels


def post_processing(path):
    timestamps = np.copy(path["timestamps"])
    timestamps -= timestamps[0]
    timestamps /= 60.0

    filter_width = config["plot"]["filter_width"]
    velocities = medfilt(path["velocities"], filter_width)
    velocities = convert_mps_to_kmph(velocities)

    heartrates = medfilt(path["heartrates"], filter_width)

    return timestamps, velocities, heartrates


def render_map(activity):
    """Draw path on map with leaflet.js."""
    path = activity.get_path()
    coords = np.rad2deg(check_coords(path["coords"]))
    distance_markers = activity.generate_distance_markers()
    valid_velocities = np.isfinite(path["velocities"])
    path["velocities"][np.logical_not(valid_velocities)] = 0.0
    # TODO find a way to colorize path according to velocities

    center = np.mean(coords, axis=0)
    m = folium.Map(location=center)
    folium.Marker(
        coords[0].tolist(), tooltip="Start",
        icon=folium.Icon(color="red", icon="flag")).add_to(m)
    folium.Marker(
        coords[-1].tolist(), tooltip="Finish",
        icon=folium.Icon(color="green", icon="flag")).add_to(m)
    for label, marker in distance_markers.items():
        marker_location = coords[marker].tolist()
        folium.Marker(
            marker_location, tooltip=label,
            icon=folium.Icon(color="blue", icon="flag")).add_to(m)
    folium.PolyLine(coords).add_to(m)
    south_west = np.min(coords, axis=0).tolist()
    north_east = np.max(coords, axis=0).tolist()
    folium.FitBounds([south_west, north_east]).add_to(m)
    return m.get_root().render()


def plot_velocities(activity, ax):
    path = activity.get_path()
    velocities = path["velocities"][1:]
    finite_velocities = np.isfinite(velocities)
    velocities = velocities[finite_velocities]
    no_outlier = np.logical_not(is_outlier(velocities))
    velocities = velocities[no_outlier] * 3.6
    dt = np.diff(path["timestamps"])[finite_velocities][no_outlier]

    ax.hist(velocities, bins=50, weights=dt)
    ax.set_xlabel("Velocity [km/h]")
    ax.set_ylabel("Percentage")
    ax.set_yticks(())
