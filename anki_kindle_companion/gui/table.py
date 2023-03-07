from aqt import mw
from aqt.qt import QTableView


class KindleLookupTableView(QTableView):
    def __init__(self, model) -> None:
        super().__init__()

        self.setModel(model)
