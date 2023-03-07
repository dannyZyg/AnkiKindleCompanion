from aqt import mw
from aqt.qt import *
from .model import KindleLookupModel
from .table import KindleLookupTableView


class KindleBrowserWindow(QDialog):
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle("Kindle Browser")
        self.setMinimumSize(920, 450)

        layout = QVBoxLayout()
        self.setLayout(layout)

        import_button = QPushButton("Import Sentence")
        delete_button = QPushButton("Delete Sentence")

        data_model = KindleLookupModel()
        self.lookup_table = KindleLookupTableView(model=data_model)

        layout.addWidget(import_button)
        layout.addWidget(delete_button)
        layout.addWidget(self.lookup_table)

    @classmethod
    def show_modal(cls, parent=None):
        # LookupWindow.close_instance()     # To make sure everything updates
        dlg = cls(parent=parent)
        return dlg.exec_()
