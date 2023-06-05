from aqt import mw
from anki.notes import Note
from aqt.qt import (
    Qt,
    QHBoxLayout,
    QCheckBox,
    QComboBox,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QWidget,
    QLabel,
    QSortFilterProxyModel,
    QRegularExpression,
    QItemSelectionModel,
)
import re
from typing import Optional

from .model import KindleLookupModel
from .table import KindleLookupTableView


class BookFilterWidget(QWidget):
    def __init__(self, unique_books, parent=None):
        super().__init__(parent)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All"] + unique_books)
        self.filter_combo.currentTextChanged.connect(self.filter_table)

        layout = QHBoxLayout()
        layout.addWidget(self.filter_combo)
        layout.addStretch()
        self.setLayout(layout)

        self.proxy_model = None

    def setProxyModel(self, proxy_model):
        self.proxy_model = proxy_model

    def filter_table(self, filter_text):
        if self.proxy_model:
            self.proxy_model.setFilterKeyColumn(2)
            if filter_text == "All":
                self.proxy_model.setFilterRegularExpression("")
            else:
                self.proxy_model.setFilterRegularExpression(f"^{filter_text}")


class UniqueSentenceCheckboxWidget(QWidget):
    def __init__(self, unique_sentences, parent=None):
        super().__init__(parent)

        self.unique_sentences = unique_sentences

        unique_sentence_checkbox = QCheckBox("Show unique sentences only")
        unique_sentence_checkbox.stateChanged.connect(self.filter_table)

        layout = QHBoxLayout()
        layout.addWidget(unique_sentence_checkbox)
        self.setLayout(layout)

        self.proxy_model = None

    def setProxyModel(self, proxy_model):
        self.proxy_model = proxy_model

    def filter_table(self, state):
        if self.proxy_model:
            self.proxy_model.setFilterKeyColumn(1)
            if state == Qt.CheckState.Checked.value:
                # Set the filter using a lambda function
                pattern = self.generate_regex_pattern(self.unique_sentences)
                regex = QRegularExpression(pattern)
                self.proxy_model.setFilterRegularExpression(regex)
            else:
                self.proxy_model.setFilterRegularExpression(QRegularExpression(".*"))

    def generate_regex_pattern(self, items: list):
        pattern = "|".join([QRegularExpression.escape(item) for item in items])
        pattern = "\\b(" + pattern + ")\\b"
        return pattern


def update_import_button_text(button: QPushButton, table_view: KindleLookupTableView):
    num_selected = len(table_view.selectionModel().selectedRows())
    button_text = f"Import {num_selected} sentences"
    button.setText(button_text)


class KindleBrowserWindow(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(QDialog, self).__init__(parent)

        self.setWindowTitle("Kindle Browser")
        self.setMinimumSize(1200, 450)

        layout = QVBoxLayout()
        self.setLayout(layout)

        data_model = KindleLookupModel()

        unique_books = data_model.uniqueBooks()
        unique_sentences = data_model.uniqueSentences()

        unique_sentence_checkbox = UniqueSentenceCheckboxWidget(unique_sentences)

        book_filter_label = QLabel("Book")
        book_filter_widget = BookFilterWidget(unique_books)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(data_model)
        book_filter_widget.setProxyModel(proxy_model)
        unique_sentence_checkbox.setProxyModel(proxy_model)

        self.lookup_table = KindleLookupTableView(model=proxy_model)

        self.import_button = QPushButton("Import Sentence")
        self.import_button.setEnabled(False)  # Initially disabled
        self.import_button.clicked.connect(self.on_import_click)

        update_buttons = lambda: update_import_button_text(button=self.import_button, table_view=self.lookup_table)

        self.lookup_table.setOnSelect(update_buttons)
        self.lookup_table.clicked.connect(update_buttons)

        delete_button = QPushButton("Delete Sentence")

        # Create layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(delete_button)
        """ button_layout.addWidget(unique_sentence_checkbox) """

        book_filter_layout = QVBoxLayout(self)
        book_filter_layout.addWidget(book_filter_label)
        book_filter_layout.addWidget(book_filter_widget)
        layout.addLayout(book_filter_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.lookup_table)

        # Connect the selection model's selectionChanged signal to a custom slot
        selection_model: QItemSelectionModel = self.lookup_table.selectionModel()
        selection_model.selectionChanged.connect(self.selection_changed)

    def selection_changed(self, selected, deselected):
        selection_model: QItemSelectionModel = self.lookup_table.selectionModel()

        self.import_button.setEnabled(selection_model.hasSelection())

    def on_import_click(self):
        # Get the selection model of the table view
        selection_model: QItemSelectionModel = self.lookup_table.selectionModel()

        # Get the selected rows
        selected_rows = [index.row() for index in selection_model.selectedRows()]

        # Get the model associated with the table view
        model = self.lookup_table.model()

        # Get the data in each selected row
        selected_data = []
        for row in selected_rows:
            row_data = []
            for column in range(model.columnCount()):
                index = model.index(row, column)
                value = model.data(index)
                row_data.append(value)
            selected_data.append(row_data)

        # Print the selected data
        print("Selected Data:", selected_data)

    @classmethod
    def show_modal(cls, parent: Optional[QWidget] = None) -> None:
        # LookupWindow.close_instance()     # To make sure everything updates
        dlg = cls(parent=parent)
        return dlg.exec_()
