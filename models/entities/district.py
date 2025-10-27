"""Модель района (пункта)"""

from pony.orm import PrimaryKey, Required, Set
from .database import db


class District(db.Entity):
    """Район (пункт)"""
    _table_ = 'districts'

    id = PrimaryKey(int, auto=True)
    name = Required(str, 100, unique=True)
    values = Set('FeatureDistrictYear')

    def __repr__(self):
        return f"District(id={self.id}, name='{self.name}')"
