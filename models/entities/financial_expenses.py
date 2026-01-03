"""Модель финансовых расходов района по годам"""

from pony.orm import PrimaryKey, Required, composite_key
from .database import db


class FinancialExpenses(db.Entity):
    """Финансовые расходы района в определённом году"""
    _table_ = 'financial_expenses'

    id = PrimaryKey(int, auto=True)
    district = Required('District')
    year = Required('Year')
    amount = Required(float)
    include_in_analysis = Required(bool, default=True)

    composite_key(district, year)

    def __repr__(self):
        return (f"FinancialExpenses(district='{self.district.name}', "
                f"year={self.year.year}, amount={self.amount})")
