"""Репозиторий для работы со значениями признак-район-год"""

from typing import Optional, List
from decimal import Decimal
from pony.orm import db_session, select
from models.entities import FeatureDistrictYear, Feature, District, Year, Document
from .base_repository import BaseRepository


class FeatureDistrictYearRepository(BaseRepository[FeatureDistrictYear]):
    """Репозиторий для работы со значениями признак-район-год"""

    entity_class = FeatureDistrictYear

    @classmethod
    @db_session
    def get_value(cls, feature_name: str, district_name: str, year: int) -> Optional[float]:
        """Получить значение признака для района и года"""
        result = FeatureDistrictYear.get(
            feature=lambda f: f.name == feature_name,
            district=lambda d: d.name == district_name,
            year=lambda y: y.year == year
        )
        return float(result.value) if result and result.value else None

    @classmethod
    @db_session
    def get_by_feature(cls, feature_name: str) -> List[FeatureDistrictYear]:
        """Получить все значения для признака"""
        return select(
            v for v in FeatureDistrictYear
            if v.feature.name == feature_name
        ).order_by(
            lambda v: (v.year.year, v.district.name)
        )[:]

    @classmethod
    @db_session
    def get_by_district(cls, district_name: str) -> List[FeatureDistrictYear]:
        """Получить все значения для района"""
        return select(
            v for v in FeatureDistrictYear
            if v.district.name == district_name
        ).order_by(
            lambda v: (v.year.year, v.feature.name)
        )[:]

    @classmethod
    @db_session
    def get_by_year(cls, year: int) -> List[FeatureDistrictYear]:
        """Получить все значения для года"""
        return select(
            v for v in FeatureDistrictYear
            if v.year.year == year
        ).order_by(
            lambda v: (v.district.name, v.feature.name)
        )[:]

    @classmethod
    @db_session
    def get_by_document(cls, document_id: int) -> List[FeatureDistrictYear]:
        """Получить все значения для документа"""
        return select(
            v for v in FeatureDistrictYear
            if v.document and v.document.id == document_id
        ).order_by(
            lambda v: (v.year.year, v.feature.name, v.district.name)
        )[:]

    @classmethod
    @db_session
    def get_with_filter(
        cls,
        feature_name: Optional[str] = None,
        district_name: Optional[str] = None,
        year: Optional[int] = None,
        exclude_null: bool = False
    ) -> List[FeatureDistrictYear]:
        """Получить значения с фильтрацией по параметрам"""
        query = select(v for v in FeatureDistrictYear)

        if feature_name:
            query = query.filter(lambda v: v.feature.name == feature_name)

        if district_name:
            query = query.filter(lambda v: v.district.name == district_name)

        if year:
            query = query.filter(lambda v: v.year.year == year)

        if exclude_null:
            query = query.filter(lambda v: v.value is not None)

        return query.order_by(
            lambda v: (v.year.year, v.district.name, v.feature.name)
        )[:]

    @classmethod
    @db_session
    def create_or_get(
        cls,
        feature: Feature,
        district: District,
        year: Year,
        document: Optional[Document] = None,
        value: Optional[Decimal] = None
    ) -> FeatureDistrictYear:
        """
        Создать или получить существующее значение

        Если запись с такой комбинацией feature-district-year существует,
        вернуть её, иначе создать новую
        """
        existing = FeatureDistrictYear.get(
            feature=feature,
            district=district,
            year=year
        )

        if existing:
            # Обновить значение если передано
            if value is not None:
                existing.value = value
            if document:
                existing.document = document
            return existing

        return FeatureDistrictYear(
            feature=feature,
            district=district,
            year=year,
            document=document,
            value=value
        )
