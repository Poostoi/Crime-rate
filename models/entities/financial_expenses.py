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
    name = Required(str)
    include_in_analysis = Required(bool, default=True)

    composite_key(district, year, name)

    def __repr__(self):
        return (f"FinancialExpenses(district='{self.district.name}', "
                f"year={self.year.year}, name='{self.name}', amount={self.amount})")
