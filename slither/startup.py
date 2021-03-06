import sys

try:
    from PyQt4.QtGui import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication

from .gui import Controller, MainWindow
from .service import Service


def start(args):
    service = Service(args.debug, args.db_filename, args.datadir,
                      args.remote, args.username, args.password)
    app = QApplication(sys.argv)
    controller = Controller(service, app)
    win = MainWindow(controller)
    win.show()
    sys.exit(app.exec_())