import re
from typing import List, Optional

from anki.notes import Note
from aqt import mw
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QItemSelectionModel,
    QLabel,
    QPushButton,
    QRect,
    QRegularExpression,
    QSortFilterProxyModel,
    Qt,
    QVBoxLayout,
    QWidget,
)

from .model import KindleLookupModel
from .table import KindleLookupTableView


class ActionButton(QPushButton):
    def __init__(self, parent=None, label: str = "") -> None:
        super().__init__(parent)
        self.label = label


class BookFilterComboBox(QComboBox):
    def __init__(self, unique_books: List[str], parent=None):
        super().__init__(parent)

        self.addItems(["All"] + unique_books)
        self.currentTextChanged.connect(self.filter_table)
        self.proxy_model = None

    def setProxyModel(self, proxy_model: QSortFilterProxyModel) -> None:
        self.proxy_model = proxy_model

    def filter_table(self, filter_text: str) -> None:
        if self.proxy_model:
            self.proxy_model.setFilterKeyColumn(2)
            if filter_text == "All":
                self.proxy_model.setFilterRegularExpression("")
            else:
                self.proxy_model.setFilterRegularExpression(f"^{filter_text}")


class LanguageFilterComboBox(QComboBox):
    def __init__(self, unique_langs: List[str], parent=None):
        super().__init__(parent)

        self.addItems(["All"] + unique_langs)
        self.currentTextChanged.connect(self.filter_table)
        self.proxy_model = None

    def setProxyModel(self, proxy_model: QSortFilterProxyModel) -> None:
        self.proxy_model = proxy_model

    def filter_table(self, filter_text: str) -> None:
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


class KindleBrowserWindow(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(QDialog, self).__init__(parent)

        data_model = KindleLookupModel()
        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(data_model)

        unique_books = data_model.uniqueBooks()
        unique_langs = data_model.uniqueLangs()
        unique_sentences = data_model.uniqueSentences()

        self.setWindowTitle("Kindle Browser")
        self.setMinimumSize(1200, 450)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Set up Filters layout
        filters_group_box = QGroupBox("Filters")
        filters_vertical_layout = QVBoxLayout()
        filters_dropdowns_horizontal_layout = QHBoxLayout()
        filters_checkboxes_horizontal_layout = QHBoxLayout()

        # Add the two horizontal layouts to the group box vertical layout
        filters_vertical_layout.addLayout(filters_dropdowns_horizontal_layout)
        filters_vertical_layout.addLayout(filters_checkboxes_horizontal_layout)
        filters_group_box.setLayout(filters_vertical_layout)

        # Create the two drop down list layouts
        language_selection_vertical_layout = self._create_language_selection_vertical_layout(unique_langs, proxy_model)
        book_selection_vertical_layout = self._create_book_selection_vertical_layout(unique_books, proxy_model)

        # Add the dropdowns tothe layout
        filters_dropdowns_horizontal_layout.addLayout(language_selection_vertical_layout)
        filters_dropdowns_horizontal_layout.addLayout(book_selection_vertical_layout)

        unique_sentence_checkbox = UniqueSentenceCheckboxWidget(unique_sentences)
        unique_sentence_checkbox.setProxyModel(proxy_model)
        filters_checkboxes_horizontal_layout.addWidget(unique_sentence_checkbox)

        # Add the filters group box to the main layout
        main_layout.addWidget(filters_group_box)

        # Set up Actions layout
        actions_group_box = QGroupBox("Actions")
        actions_horizontal_layout = QHBoxLayout()
        actions_group_box.setLayout(actions_horizontal_layout)

        self.import_button = ActionButton("Import Sentence", label="Import")
        self.import_button.setEnabled(False)  # Initially disabled
        self.import_button.clicked.connect(self.on_import_click)
        self.delete_button = ActionButton("Delete Sentence", label="Delete")
        self.delete_button.setEnabled(False)  # Initially disabled

        # Create layout for buttons
        actions_horizontal_layout.addWidget(self.import_button)
        actions_horizontal_layout.addWidget(self.delete_button)

        main_layout.addWidget(actions_group_box)

        self.lookup_table = KindleLookupTableView(model=proxy_model)

        update_buttons = lambda: self.update_action_buttons_text(
            buttons=[self.import_button, self.delete_button], table_view=self.lookup_table
        )

        self.lookup_table.setOnSelect(update_buttons)
        self.lookup_table.clicked.connect(update_buttons)
        main_layout.addWidget(self.lookup_table)

        # Connect the selection model's selectionChanged signal to a custom slot
        selection_model: QItemSelectionModel = self.lookup_table.selectionModel()
        selection_model.selectionChanged.connect(self.selection_changed)

    def _create_language_selection_vertical_layout(
        self, unique_langs: List[str], proxy_model: QSortFilterProxyModel
    ) -> QVBoxLayout:
        language_selection_vertical_layout = QVBoxLayout()

        language_label = QLabel("Language")
        language_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        language_selection_combo_box = LanguageFilterComboBox(unique_langs)
        language_selection_combo_box.setProxyModel(proxy_model)

        language_selection_vertical_layout.addWidget(language_label)
        language_selection_vertical_layout.addWidget(language_selection_combo_box)
        return language_selection_vertical_layout

    def _create_book_selection_vertical_layout(
        self, unique_books: List[str], proxy_model: QSortFilterProxyModel
    ) -> QVBoxLayout:
        book_selection_vertical_layout = QVBoxLayout()

        book_filter_label = QLabel("Book")
        book_filter_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        book_filter_combo_box = BookFilterComboBox(unique_books)
        book_filter_combo_box.setProxyModel(proxy_model)

        book_selection_vertical_layout.addWidget(book_filter_label)
        book_selection_vertical_layout.addWidget(book_filter_combo_box)
        return book_selection_vertical_layout

    def selection_changed(self, selected, deselected):
        selection_model: QItemSelectionModel = self.lookup_table.selectionModel()

        self.import_button.setEnabled(selection_model.hasSelection())
        self.delete_button.setEnabled(selection_model.hasSelection())

    def update_action_buttons_text(self, buttons: List[QPushButton], table_view: KindleLookupTableView) -> None:
        for button in buttons:
            num_selected = len(table_view.selectionModel().selectedRows())
            button_text = f"{button.label} {num_selected} sentences"
            button.setText(button_text)

    def on_import_click(self) -> None:
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
        return dlg.exec()
