"""Базовый репозиторий с CRUD операциями"""

from typing import TypeVar, Generic, List, Optional, Callable
from pony.orm import db_session, select

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Базовый класс репозитория с CRUD операциями

    Включает 5 основных методов:
    - get_by_id: получение по ID
    - get_list: получение списка с фильтрацией и сортировкой
    - create: создание
    - update: обновление
    - delete: удаление
    """

    entity_class: type = None  # Переопределяется в дочерних классах

    @classmethod
    @db_session
    def get_by_id(cls, entity_id: int) -> Optional[T]:
        """Получить сущность по ID"""
        if not cls.entity_class:
            raise NotImplementedError("entity_class должен быть определен в дочернем классе")
        return cls.entity_class.get(id=entity_id)

    @classmethod
    @db_session
    def get_list(
        cls,
        filter_func: Optional[Callable] = None,
        order_by_func: Optional[Callable] = None
    ) -> List[T]:
        """
        Получить список сущностей с фильтрацией и сортировкой

        Args:
            filter_func: Функция фильтрации для Pony ORM
            order_by_func: Функция/поле для сортировки

        Examples:
            # Все сущности
            YearRepository.get_list()

            # С фильтрацией
            YearRepository.get_list(filter_func=lambda y: y.year > 2020)

            # С сортировкой
            YearRepository.get_list(order_by_func=lambda y: y.year)
            # или
            YearRepository.get_list(order_by_func=Year.year)

            # Фильтрация + сортировка
            FeatureRepository.get_list(
                filter_func=lambda f: f.name.startswith('У'),
                order_by_func=lambda f: f.name
            )
        """
        if not cls.entity_class:
            raise NotImplementedError("entity_class должен быть определен в дочернем классе")

        query = select(e for e in cls.entity_class)

        if filter_func:
            query = query.filter(filter_func)

        if order_by_func:
            query = query.order_by(order_by_func)

        return query[:]

    @classmethod
    @db_session
    def create(cls, **kwargs) -> T:
        """
        Создать новую сущность

        Args:
            **kwargs: Параметры для создания
        """
        if not cls.entity_class:
            raise NotImplementedError("entity_class должен быть определен в дочернем классе")

        return cls.entity_class(**kwargs)

    @classmethod
    @db_session
    def update(cls, entity_id: int, **kwargs) -> Optional[T]:
        """
        Обновить сущность по ID

        Args:
            entity_id: ID сущности
            **kwargs: Поля для обновления

        Returns:
            Обновленная сущность или None
        """
        if not cls.entity_class:
            raise NotImplementedError("entity_class должен быть определен в дочернем классе")

        entity = cls.entity_class.get(id=entity_id)
        if not entity:
            return None

        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        return entity

    @classmethod
    @db_session
    def delete(cls, entity_id: int) -> bool:
        """
        Удалить сущность по ID

        Args:
            entity_id: ID сущности

        Returns:
            True если удалено, False если не найдено
        """
        if not cls.entity_class:
            raise NotImplementedError("entity_class должен быть определен в дочернем классе")

        entity = cls.entity_class.get(id=entity_id)
        if not entity:
            return False

        entity.delete()
        return True