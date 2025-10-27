"""Enums для работы с Excel"""

from enum import Enum


class ExcelFileType(str, Enum):
    """Типы Excel файлов: FULL (годы в листах) или PART (годы в столбцах)"""

    FULL = "full"
    PART = "part"
