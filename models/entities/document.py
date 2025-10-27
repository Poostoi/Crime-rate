"""Модель документа (загруженного Excel файла)"""

from pony.orm import PrimaryKey, Required, Set
from datetime import datetime
from .database import db


class Document(db.Entity):
    """Документ (загруженный Excel файл)"""
    _table_ = 'documents'

    id = PrimaryKey(int, auto=True)
    filename = Required(str, 255)
    file_path = Required(str, 500)
    file_type = Required(str, 10)
    created_at = Required(datetime, default=lambda: datetime.now())
    values = Set('FeatureDistrictYear')

    def __repr__(self):
        return f"Document(id={self.id}, filename='{self.filename}', type='{self.file_type}')"
