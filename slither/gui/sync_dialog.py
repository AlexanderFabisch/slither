try:
    from PyQt4.QtGui import QProgressDialog
except ImportError:
    from PyQt5.QtWidgets import QProgressDialog


class SyncDialog(QProgressDialog):
    def __init__(self):
        super(SyncDialog, self).__init__("Synchronization", "Cancel", 0, 0)
