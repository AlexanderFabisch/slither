from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ..data_utils import d, time_representation, split_time
from ..config import config
from datetime import datetime


class EditActivity(QWidget):
    def __init__(self, controller, activity=None):
        super(EditActivity, self).__init__()
        self.controller = controller
        self.activity = activity

        self.sports = config["sports"]

        layout = QGridLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignTop)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(8, 1)

        layout.addWidget(QLabel("Start time"), 0, 1, Qt.AlignRight | Qt.AlignTop)
        self.calendar = QCalendarWidget()
        self.calendar.setMaximumHeight(200)
        layout.addWidget(self.calendar, 0, 2, 1, 6)
        self.time_edit = QTimeEdit(QTime.currentTime())
        layout.addWidget(self.time_edit, 1, 2)

        layout.addWidget(QLabel("Sport"), 2, 1, Qt.AlignRight)
        self.sport_combo_box = QComboBox()
        for sport in self.sports:
            self.sport_combo_box.addItem(d.display_sport(sport))
        layout.addWidget(self.sport_combo_box, 2, 2, 1, 6)

        layout.addWidget(QLabel("Distance"), 3, 1, Qt.AlignRight)
        self.distance_edit = QDoubleSpinBox()
        self.distance_edit.setMinimum(0.0)
        self.distance_edit.setSingleStep(0.1)
        layout.addWidget(self.distance_edit, 3, 2, 1, 5)
        layout.addWidget(QLabel("km"), 3, 7)

        layout.addWidget(QLabel("Time"), 4, 1, Qt.AlignRight)
        self.hour_edit = QSpinBox()
        self.hour_edit.setMinimum(0)
        layout.addWidget(self.hour_edit, 4, 2)
        layout.addWidget(QLabel("h"), 4, 3)
        self.minute_edit = QSpinBox()
        self.minute_edit.setRange(0, 59)
        layout.addWidget(self.minute_edit, 4, 4)
        layout.addWidget(QLabel("min"), 4, 5)
        self.seconds_edit = QDoubleSpinBox()
        self.seconds_edit.setRange(0.0, 59.99)
        layout.addWidget(self.seconds_edit, 4, 6)
        layout.addWidget(QLabel("s"), 4, 7)

        layout.addWidget(QLabel("Calories"), 5, 1, Qt.AlignRight)
        self.calories_edit = QDoubleSpinBox()
        self.calories_edit.setRange(0.0, 10000.0)  # TODO magic numbers
        layout.addWidget(self.calories_edit, 5, 2, 1, 6)

        layout.addWidget(QLabel("Heartrate"), 6, 1, Qt.AlignRight)
        self.heartrate_edit = QDoubleSpinBox()
        self.heartrate_edit.setRange(0.0, 300.0)  # TODO magic numbers
        layout.addWidget(self.heartrate_edit, 6, 2, 1, 6)

        save_button = QPushButton("Save")
        layout.addWidget(save_button, 7, 2, 1, 6, Qt.AlignRight)

        QObject.connect(save_button, SIGNAL("clicked()"),
                        self.send_activity_info)

        if self.activity is not None:
            self._load_activity(self.activity)

    def _load_activity(self, activity):
        self.calendar.setSelectedDate(
            QDate(activity.start_time.year,
                  activity.start_time.month,
                  activity.start_time.day))
        self.time_edit.setTime(
            QTime(activity.start_time.hour,
                  activity.start_time.minute,
                  activity.start_time.second))
        self.distance_edit.setValue(activity.distance / 1000.0)
        h, m, s = split_time(activity.time)
        self.hour_edit.setValue(h)
        self.minute_edit.setValue(m)
        self.seconds_edit.setValue(s)
        if activity.sport in self.sports:
            sport_index = self.sports.index(activity.sport)
        else:
            sport_index = self.sports.index("other")
        self.sport_combo_box.setCurrentIndex(sport_index)
        if activity.calories is None:
            calories = 0.0
        else:
            calories = activity.calories
        self.calories_edit.setValue(calories)
        if activity.heartrate is None:
            heartrate = 0.0
        else:
            heartrate = activity.heartrate
        self.heartrate_edit.setValue(heartrate)

    def send_activity_info(self):
        try:
            start_time = self._validate_start_time()
            distance = self._validate_distance()
            time = self._validate_time()
            calories = self.calories_edit.value()
            heartrate = self.heartrate_edit.value()
        except:
            return

        metadata = {
            "sport": self.sports[self.sport_combo_box.currentIndex()],
            "start_time": start_time,
            "distance": distance,
            "time": time,
            "calories": calories,
            "heartrate": heartrate
        }
        self.controller.save_activity(metadata, activity=self.activity)
        self.controller.update_overview()

    def _validate_start_time(self):
        date = self.calendar.selectedDate()
        time = self.time_edit.time()
        return datetime(year=date.year(), month=date.month(), day=date.day(),
                        hour=time.hour(), minute=time.minute())

    def _validate_distance(self):
        return 1000.0 * self.distance_edit.value()

    def _validate_time(self):
        hours = self.hour_edit.value()
        minutes = self.minute_edit.value()
        seconds = self.seconds_edit.value()
        return time_representation(hours, minutes, seconds)