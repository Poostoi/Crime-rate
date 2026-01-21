"""Модели Pony ORM для анализа данных"""

from .database import db
from .feature import Feature
from .district import District
from .year import Year
from .document import Document
from .feature_district_year import FeatureDistrictYear
from .crime_type import CrimeType
from .population import Population
from .crime_statistics import CrimeStatistics
from .financial_expenses import FinancialExpenses
from .analysis_result import AnalysisResult

__all__ = [
    'db',
    'Feature',
    'District',
    'Year',
    'Document',
    'FeatureDistrictYear',
    'CrimeType',
    'Population',
    'CrimeStatistics',
    'FinancialExpenses',
    'AnalysisResult',
]
