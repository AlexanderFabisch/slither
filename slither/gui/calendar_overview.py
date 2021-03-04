try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except ImportError:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
from datetime import datetime
from slither.core.ui_text import d


class CalendarOverview(QCalendarWidget):
    def __init__(self, controller):
        super(CalendarOverview, self).__init__()
        self.controller = controller
        self.clicked.connect(self.controller.show_activity)

    def paintCell(self, painter, rect, date):
        activities = self.controller.service.list_activity_for_date(
            datetime(year=date.year(), month=date.month(), day=date.day()))

        painter.save()
        content = "%d\n" % date.day()
        for activity in activities:
            content += ("%s %s\n" % (d.display_sport(activity.sport),
                                     d.display_distance(activity.distance)))
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignTop, content)
        painter.restore()