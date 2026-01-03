"""Модель признака (показателя)"""

from pony.orm import PrimaryKey, Required, Optional, Set
from .database import db


class Feature(db.Entity):
    """Признак (показатель)"""
    _table_ = 'features'

    id = PrimaryKey(int, auto=True)
    name = Required(str, 300, unique=True)
    crime_type = Optional('CrimeType')
    values = Set('FeatureDistrictYear')

    def __repr__(self):
        return f"Feature(id={self.id}, name='{self.name}', crime_type='{self.crime_type.name if self.crime_type else None}')"
