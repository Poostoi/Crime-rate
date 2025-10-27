"""Репозиторий для работы с районами"""

from typing import Optional, List
from pony.orm import db_session
from models.entities import District
from .base_repository import BaseRepository


class DistrictRepository(BaseRepository[District]):
    """Репозиторий для работы с районами"""

    entity_class = District

    @classmethod
    @db_session
    def get_by_name(cls, name: str) -> Optional[District]:
        """Найти район по имени"""
        return District.get(name=name)

    @classmethod
    @db_session
    def get_all_sorted(cls) -> List[District]:
        """Получить все районы с сортировкой по имени"""
        return cls.get_list(order_by_func=lambda d: d.name)
