"""Модель результатов анализа Random Forest"""

from pony.orm import PrimaryKey, Required, Optional
from datetime import datetime
from .database import db


class AnalysisResult(db.Entity):
    """Результаты анализа Random Forest для линии преступлений"""
    _table_ = 'analysis_results'

    id = PrimaryKey(int, auto=True)
    crime_type = Required('CrimeType')
    selected_indicators = Optional(str, 2000)
    importance_plot = Optional(str, 500)
    tree_plot = Optional(str, 500)
    most_important = Optional(str, 500)
    created_at = Required(datetime, default=datetime.now)

    def __repr__(self):
        return f"AnalysisResult(id={self.id}, crime_type='{self.crime_type.name}', created_at={self.created_at})"
