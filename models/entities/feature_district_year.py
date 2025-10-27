"""Модель связи признак-район-год с числовым значением"""

from pony.orm import PrimaryKey, Required, Optional, composite_key
from decimal import Decimal
from .database import db


class FeatureDistrictYear(db.Entity):
    """Связь признак-район-год с числовым значением"""
    _table_ = 'feature_district_year'

    id = PrimaryKey(int, auto=True)
    feature = Required('Feature')
    district = Required('District')
    year = Required('Year')
    document = Optional('Document')
    value = Optional(Decimal, precision=10, scale=2)

    composite_key(feature, district, year)

    def __repr__(self):
        return (f"FeatureDistrictYear(feature='{self.feature.name}', "
                f"district='{self.district.name}', year={self.year.year}, value={self.value})")
