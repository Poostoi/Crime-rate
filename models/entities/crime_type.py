"""Модель линии уголовной ответственности"""

from pony.orm import PrimaryKey, Required, Set
from .database import db


class CrimeType(db.Entity):
    """Линия уголовной ответственности (категория преступлений)"""
    _table_ = 'crime_types'

    id = PrimaryKey(int, auto=True)
    name = Required(str, 200, unique=True)
    features = Set('Feature')

    def __repr__(self):
        return f"CrimeType(id={self.id}, name='{self.name}')"
