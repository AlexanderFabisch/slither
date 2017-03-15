from PyQt4.QtGui import *


class SyncDialog(QProgressDialog):
    def __init__(self):
        super(SyncDialog, self).__init__("Synchronization", "Cancel", 0, 0)
