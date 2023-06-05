from aqt import mw
from aqt.qt import QFont, QHeaderView, QTableView, QKeyEvent, Qt, QKeySequence


class KindleLookupTableView(QTableView):
    def __init__(self, model) -> None:
        super().__init__()

        self.setModel(model)
        self.on_select = None

        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 700)
        self.setColumnWidth(2, 200)
        self.setColumnWidth(3, 100)

        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    def setOnSelect(self, func):
        self.on_select = func

    def keyPressEvent(self, event: QKeyEvent) -> None:
        print(event)

        if event.matches(QKeySequence.StandardKey.SelectAll):
            if self.on_select:
                print("ON SELECT")
                self.on_select()

            """ self.selectAll() """
            """ self.selectionChanged.emit(self.selectionModel().selectedIndexes()) """
        """ else: """

        super().keyPressEvent(event)
