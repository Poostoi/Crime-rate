"""Тесты для моделей БД"""

import pytest
from decimal import Decimal
from pony.orm import db_session, TransactionIntegrityError
from utils.db import init_database
from models.entities import Feature, District, Year, FeatureDistrictYear


@pytest.fixture(scope='function')
def test_db():
    """Создать in-memory БД для теста"""
    init_database(provider='sqlite', database=':memory:', create_tables=True)
    yield


class TestFeature:
    """Тесты Feature"""

    @db_session
    def test_create_feature(self, test_db):
        """Создание признака"""
        feature = Feature(name='Уровень безработицы')
        assert feature.id is not None
        assert feature.name == 'Уровень безработицы'

    @db_session
    def test_unique_feature_name(self, test_db):
        """Уникальность имени признака"""
        Feature(name='Уровень безработицы')

        with pytest.raises(TransactionIntegrityError):
            Feature(name='Уровень безработицы')

    @db_session
    def test_get_feature_by_name(self, test_db):
        """Поиск признака по имени"""
        Feature(name='Уровень безработицы')

        found = Feature.get(name='Уровень безработицы')
        assert found is not None
        assert found.name == 'Уровень безработицы'


class TestDistrict:
    """Тесты District"""

    @db_session
    def test_create_district(self, test_db):
        """Создание района"""
        district = District(name='пункт 1')
        assert district.id is not None
        assert district.name == 'пункт 1'

    @db_session
    def test_unique_district_name(self, test_db):
        """Уникальность имени района"""
        District(name='пункт 1')

        with pytest.raises(TransactionIntegrityError):
            District(name='пункт 1')


class TestYear:
    """Тесты Year"""

    @db_session
    def test_create_year(self, test_db):
        """Создание года"""
        year = Year(year=2015)
        assert year.id is not None
        assert year.year == 2015

    @db_session
    def test_unique_year(self, test_db):
        """Уникальность года"""
        Year(year=2015)

        with pytest.raises(TransactionIntegrityError):
            Year(year=2015)


class TestFeatureDistrictYear:
    """Тесты FeatureDistrictYear"""

    @db_session
    def test_create_value(self, test_db):
        """Создание значения"""
        feature = Feature(name='Уровень безработицы')
        district = District(name='пункт 1')
        year = Year(year=2015)

        value = FeatureDistrictYear(
            feature=feature,
            district=district,
            year=year,
            value=Decimal('7.5')
        )

        assert value.id is not None
        assert value.feature.name == 'Уровень безработицы'
        assert value.district.name == 'пункт 1'
        assert value.year.year == 2015
        assert value.value == Decimal('7.5')

    @db_session
    def test_null_value(self, test_db):
        """Создание значения с NULL"""
        feature = Feature(name='Уровень безработицы')
        district = District(name='пункт 1')
        year = Year(year=2015)

        value = FeatureDistrictYear(
            feature=feature,
            district=district,
            year=year,
            value=None
        )

        assert value.value is None

    @db_session
    def test_composite_key_uniqueness(self, test_db):
        """Уникальность составного ключа"""
        feature = Feature(name='Уровень безработицы')
        district = District(name='пункт 1')
        year = Year(year=2015)

        FeatureDistrictYear(
            feature=feature,
            district=district,
            year=year,
            value=Decimal('7.5')
        )

        with pytest.raises(TransactionIntegrityError):
            FeatureDistrictYear(
                feature=feature,
                district=district,
                year=year,
                value=Decimal('8.0')
            )

    @db_session
    def test_different_combinations(self, test_db):
        """Создание разных комбинаций"""
        feature1 = Feature(name='Уровень безработицы')
        feature2 = Feature(name='Уровень бедности')
        district1 = District(name='пункт 1')
        district2 = District(name='пункт 2')
        year1 = Year(year=2015)
        year2 = Year(year=2016)

        v1 = FeatureDistrictYear(feature=feature1, district=district1, year=year1, value=Decimal('7.5'))
        v2 = FeatureDistrictYear(feature=feature1, district=district2, year=year1, value=Decimal('8.0'))
        v3 = FeatureDistrictYear(feature=feature2, district=district1, year=year1, value=Decimal('6.5'))
        v4 = FeatureDistrictYear(feature=feature1, district=district1, year=year2, value=Decimal('9.0'))

        assert v1.id != v2.id != v3.id != v4.id
