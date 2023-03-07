from aqt.qt import QAbstractTableModel, QVariant, Qt, QModelIndex
from ..enums import TABLE_COLUMNS_TO_ATTRIBUTES, Column


class KindleLookupModel(QAbstractTableModel):
    def __init__(self) -> None:
        super(KindleLookupModel, self).__init__()
        self._headers = ["Word", "Sentence", "Book", "Language"]
        from ..kindle import KindleConnection

        kindle_connection = KindleConnection()
        self._data = kindle_connection.get_lookups()

    def update(self) -> None:
        pass

    def rowCount(self, parent=QModelIndex) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                row = index.row()
                column = index.column()

                object = self._data[row]
                attr_name = TABLE_COLUMNS_TO_ATTRIBUTES[Column(column)]
                return getattr(object, attr_name)
            except IndexError:
                return QVariant()
        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[col]
        return None
