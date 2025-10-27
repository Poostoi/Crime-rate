"""Репозиторий для работы с признаками"""

from typing import Optional, List
from pony.orm import db_session
from models.entities import Feature
from .base_repository import BaseRepository


class FeatureRepository(BaseRepository[Feature]):
    """Репозиторий для работы с признаками"""

    entity_class = Feature

    @classmethod
    @db_session
    def get_by_name(cls, name: str) -> Optional[Feature]:
        """Найти признак по имени"""
        return Feature.get(name=name)

    @classmethod
    @db_session
    def get_all_sorted(cls) -> List[Feature]:
        """Получить все признаки с сортировкой по имени"""
        return cls.get_list(order_by_func=lambda f: f.name)
