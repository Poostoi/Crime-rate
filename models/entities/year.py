"""Модель года"""

from pony.orm import PrimaryKey, Required, Set
from .database import db


class Year(db.Entity):
    """Год"""
    _table_ = 'years'

    id = PrimaryKey(int, auto=True)
    year = Required(int, unique=True)
    values = Set('FeatureDistrictYear')
    populations = Set('Population')
    crime_statistics = Set('CrimeStatistics')
    financial_expenses = Set('FinancialExpenses')

    def __repr__(self):
        return f"Year(id={self.id}, year={self.year})"
