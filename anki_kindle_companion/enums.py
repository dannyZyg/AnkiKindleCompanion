from enum import Enum

###
# SQLite tables
###

"""
Represents the column names we will use in this program as set in the sql query `get_lookups`.
Some of these are original column names and some are custom, so they will not be 100% 1:1
"""


class WordTable(Enum):
    ID_COL = "word_id"
    WORD_COL = "word"
    STEM_COL = "stem"
    LANG_COL = "lang"
    CATEGORY_COL = "category"


class LookupTable(Enum):
    ID_COL = "lookup_id"
    WORD_COL = "word_key"
    BOOK_COL = "book_key"
    USAGE_COL = "usage"
    TIMESTAMP_COL = "timestamp"


class BookTable(Enum):
    ID_COL = "book_id"
    TITLE_COL = "book_title"
    AUTHORS_COL = "book_authors"


class LearningState(Enum):
    LEARNING = 0
    MASTERED = 100


class Column(Enum):
    WORD = 0
    SENTENCE = 1
    BOOK = 2
    LANGUAGE = 3


TABLE_COLUMNS_TO_ATTRIBUTES = {
    Column.WORD: "word",
    Column.SENTENCE: "sentence",
    Column.BOOK: "book",
    Column.LANGUAGE: "language",
}
