"""Модели Pony ORM для анализа данных"""

from .database import db
from .feature import Feature
from .district import District
from .year import Year
from .document import Document
from .feature_district_year import FeatureDistrictYear

__all__ = [
    'db',
    'Feature',
    'District',
    'Year',
    'Document',
    'FeatureDistrictYear',
]
