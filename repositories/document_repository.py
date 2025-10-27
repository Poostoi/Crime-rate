"""Репозиторий для работы с документами"""

from typing import List, Dict, Optional
from pony.orm import db_session, select, desc
from models.entities import Document, FeatureDistrictYear
from .base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Репозиторий для работы с документами"""

    entity_class = Document

    @classmethod
    @db_session
    def get_all_sorted_by_date(cls) -> List[Document]:
        """Получить все документы с сортировкой по дате создания (сначала новые)"""
        return cls.get_list(order_by_func=desc(Document.created_at))

    @classmethod
    @db_session
    def get_by_filename(cls, filename: str) -> List[Document]:
        """Найти документы по имени файла"""
        return cls.get_list(filter_func=lambda d: d.filename == filename)

    @classmethod
    @db_session
    def get_data_by_years(cls, document_id: int) -> Optional[Dict]:
        """
        Получить данные документа, сгруппированные по годам
        Формат для двумерной таблицы: признаки × районы

        """
        document = Document.get(id=document_id)
        if not document:
            return None

        # Получить все значения для этого документа
        values = select(
            v for v in FeatureDistrictYear
            if v.document == document
        ).order_by(
            lambda v: (v.year.year, v.feature.name, v.district.name)
        )[:]

        # Сгруппировать данные: год -> признак -> район -> значение
        years_data = {}

        for v in values:
            year_val = v.year.year
            district_name = v.district.name
            feature_name = v.feature.name
            value = float(v.value) if v.value else None

            if year_val not in years_data:
                years_data[year_val] = {
                    'districts': set(),
                    'features': {}
                }

            years_data[year_val]['districts'].add(district_name)

            if feature_name not in years_data[year_val]['features']:
                years_data[year_val]['features'][feature_name] = {}

            years_data[year_val]['features'][feature_name][district_name] = value

        # Преобразовать в список для шаблона
        years_list = []
        for year_val in sorted(years_data.keys()):
            year_info = years_data[year_val]

            # Упорядоченный список районов
            district_names = sorted(year_info['districts'])

            # Список признаков с их значениями по районам
            features_list = []
            for feature_name in sorted(year_info['features'].keys()):
                feature_values = []
                for district_name in district_names:
                    value = year_info['features'][feature_name].get(district_name)
                    feature_values.append(value)

                features_list.append({
                    'name': feature_name,
                    'district_values': feature_values
                })

            years_list.append({
                'year': year_val,
                'district_names': district_names,
                'features': features_list
            })

        return {
            'document': document,
            'years': years_list
        }
