"""Репозитории для работы с данными"""

from .base_repository import BaseRepository
from .feature_repository import FeatureRepository
from .district_repository import DistrictRepository
from .year_repository import YearRepository
from .document_repository import DocumentRepository
from .feature_district_year_repository import FeatureDistrictYearRepository

__all__ = [
    'BaseRepository',
    'FeatureRepository',
    'DistrictRepository',
    'YearRepository',
    'DocumentRepository',
    'FeatureDistrictYearRepository',
]
