"""
Модуль моделей данных для приложения анализа преступности
"""
from .entities import db, Feature, District, Year, FeatureDistrictYear

__all__ = ['db', 'Feature', 'District', 'Year', 'FeatureDistrictYear']
