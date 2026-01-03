"""Модель расчётных показателей преступности"""

from pony.orm import PrimaryKey, Required, composite_key
from decimal import Decimal
from .database import db


class CrimeStatistics(db.Entity):
    """Расчётные показатели преступности для района и года"""
    _table_ = 'crime_statistics'

    id = PrimaryKey(int, auto=True)
    district = Required('District')
    year = Required('Year')
    total_crimes = Required(int)
    population = Required(int)
    coefficient = Required(Decimal, precision=10, scale=2)
    normalized = Required(Decimal, precision=5, scale=2)

    composite_key(district, year)

    def __repr__(self):
        return (f"CrimeStatistics(district='{self.district.name}', "
                f"year={self.year.year}, crimes={self.total_crimes}, "
                f"coefficient={self.coefficient}, normalized={self.normalized})")
