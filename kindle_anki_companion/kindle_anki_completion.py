from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict, Optional


class SQLiteTableRef:
    """
    Represents the column names we will use in this program as set in the sql query `get_lookups`.
    Some of these are original column names and some are custom, so they will not be 100% 1:1
    """


class WordTable(SQLiteTableRef):
    ID_COL: str = "word_id"
    WORD_COL: str = "word"
    STEM_COL: str = "stem"
    LANG_COL: str = "lang"
    CATEGORY_COL: str = "category"


class LookupTable(SQLiteTableRef):
    ID_COL: str = "lookup_id"
    WORD_COL: str = "word_key"
    BOOK_COL: str = "book_key"
    USAGE_COL: str = "usage"
    TIMESTAMP_COL: str = "timestamp"


class BookTable(SQLiteTableRef):
    ID_COL: str = "book_id"
    TITLE_COL: str = "book_title"
    AUTHORS_COL: str = "book_authors"


class LearningState(Enum):
    LEARNING = 0
    MASTERED = 100


class LearningStateInput(TypedDict):
    category: int


@dataclass
class Word:
    id: str  # ja:立場
    word: str  # 立場
    stem: str  # たち‐ば
    lang: str  # ja
    category: LearningState  # enum e.g. LearningState.LEARNING


@dataclass
class Lookup:
    id: str  # CR!D7ZAMANRR92JQCKW5YCR7V5E92ST:CC94DA53:1133:5
    word: Word  # Instance of Word class
    book: Book  # Instance of Book class
    usage: str  # The actual highlighted sentence!
    timestamp: int  # 1566038540110


@dataclass
class Book:
    id: str
    title: str
    authors: str


class KindleConnection:
    def __init__(self):
        self.connection = sqlite3.connect("/Users/danny/Desktop/vocab.db")
        self.connection.row_factory = self._lookup_factory

    def _lookup_factory(self, cursor, row):
        fields = [column[0] for column in cursor.description]
        names_to_values = {key: value for key, value in zip(fields, row)}

        # Extract the word instance from the data
        word = Word(
            id=names_to_values.get(WordTable.ID_COL, None),
            word=names_to_values.get(WordTable.WORD_COL, None),
            stem=names_to_values.get(WordTable.STEM_COL, None),
            lang=names_to_values.get(WordTable.LANG_COL, None),
            category=LearningState(names_to_values.get(WordTable.CATEGORY_COL)),
        )
        # Extract the book instance from the data
        book = Book(
            id=names_to_values.get(BookTable.ID_COL, None),
            title=names_to_values.get(BookTable.TITLE_COL, None),
            authors=names_to_values.get(BookTable.AUTHORS_COL, None),
        )

        # Extract the lookup instance from the data
        return Lookup(
            id=names_to_values.get(LookupTable.ID_COL, None),
            usage=names_to_values.get(LookupTable.USAGE_COL, None),
            timestamp=names_to_values.get(LookupTable.TIMESTAMP_COL, None),
            word=word,
            book=book,
        )

    # def _map_rows_to_objects(self, rows):
    def get_lookups(
        self, learning_state: Optional[LearningState] = None
    ) -> list[Lookup]:
        cursor = self.connection.cursor()

        sql = """
        SELECT
            lu.id as lookup_id,
            lu.word_key,
            lu.book_key,
            lu.usage,
            lu.timestamp,
            w.id as word_id,
            w.word,
            w.stem,
            w.lang,
            w.category,
            b.id as book_id,
            b.title as book_title,
            b.authors as book_authors
        FROM LOOKUPS lu
        INNER JOIN WORDS w ON w.id = lu.word_key
        INNER JOIN BOOK_INFO b ON b.id = lu.book_key
        """

        values: LearningStateInput = {
            "category": LearningState.MASTERED.value,
        }

        if learning_state:
            sql = sql + " WHERE w.category = :category"

        result = cursor.execute(sql, values)
        return result.fetchall()


kindle_connection = KindleConnection()
lookups = kindle_connection.get_lookups()
from pprint import pprint

pprint(lookups)
# print(words[0])
breakpoint()
# print(words[0])
