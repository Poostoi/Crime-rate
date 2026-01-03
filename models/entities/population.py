"""Модель населения района по годам"""

from pony.orm import PrimaryKey, Required, composite_key
from .database import db


class Population(db.Entity):
    """Население района в определённом году"""
    _table_ = 'population'

    id = PrimaryKey(int, auto=True)
    district = Required('District')
    year = Required('Year')
    value = Required(int)

    composite_key(district, year)

    def __repr__(self):
        return (f"Population(district='{self.district.name}', "
                f"year={self.year.year}, value={self.value})")
