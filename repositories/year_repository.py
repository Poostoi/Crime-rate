"""Репозиторий для работы с годами"""

from typing import Optional, List
from pony.orm import db_session
from models.entities import Year
from .base_repository import BaseRepository


class YearRepository(BaseRepository[Year]):
    """Репозиторий для работы с годами"""

    entity_class = Year

    @classmethod
    @db_session
    def get_by_value(cls, year: int) -> Optional[Year]:
        """Найти год по значению"""
        return Year.get(year=year)

    @classmethod
    @db_session
    def get_all_sorted(cls) -> List[Year]:
        """Получить все годы с сортировкой по году"""
        return cls.get_list(order_by_func=lambda y: y.year)
