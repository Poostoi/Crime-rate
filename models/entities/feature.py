"""Модель признака (показателя)"""

from pony.orm import PrimaryKey, Required, Set
from .database import db


class Feature(db.Entity):
    """Признак (показатель)"""
    _table_ = 'features'

    id = PrimaryKey(int, auto=True)
    name = Required(str, 200, unique=True)
    values = Set('FeatureDistrictYear')

    def __repr__(self):
        return f"Feature(id={self.id}, name='{self.name}')"
