from __future__ import annotations
from datetime import datetime
import sqlite3
from dataclasses import dataclass
from typing import TypedDict, Optional
from .enums import BookTable, WordTable, LookupTable, LearningState


class LearningStateInput(TypedDict):
    category: int


@dataclass
class Lookup:
    id: str  # CR!D7ZAMANRR92JQCKW5YCR7V5E92ST:CC94DA53:1133:5
    word: str
    book: str
    sentence: str  # The actual highlighted sentence!
    date: datetime
    word_id: str
    language: str  # ja
    category: LearningState  # enum e.g. LearningState.LEARNING


class KindleConnection:
    def __init__(self) -> None:
        self.connection = sqlite3.connect("/Users/danny/Desktop/vocab.db")
        self.connection.row_factory = self._lookup_factory

    def _convert_to_datetime(self, timestamp: int) -> datetime:
        """Returns the UTC datetime from the db timestamp. We divide by 1000 to convert ms to seconds."""
        return datetime.utcfromtimestamp(timestamp / 1000)

    def _lookup_factory(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> Lookup:
        fields = [column[0] for column in cursor.description]
        names_to_values = {key: value for key, value in zip(fields, row)}

        # Extract the lookup instance from the data
        return Lookup(
            id=names_to_values.get(LookupTable.ID_COL.value, None),
            sentence=names_to_values.get(LookupTable.USAGE_COL.value, None),
            date=self._convert_to_datetime(names_to_values.get(LookupTable.TIMESTAMP_COL.value, 0)),
            word=names_to_values.get(WordTable.WORD_COL.value, None),
            word_id=names_to_values.get(WordTable.ID_COL.value, None),
            book=names_to_values.get(BookTable.TITLE_COL.value, None),
            language=names_to_values.get(WordTable.LANG_COL.value, None),
            category=LearningState(names_to_values.get(WordTable.CATEGORY_COL.value)),
        )

    def get_lookups(self, learning_state: Optional[LearningState] = None) -> list[Lookup]:
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
