import pandas as pd
from decimal import Decimal
from pony.orm import db_session, commit
from typing import Dict, Optional
from models.entities import Feature, District, Year, FeatureDistrictYear, Document
from models.excel_enum import ExcelFileType
from repositories import (
    FeatureRepository,
    DistrictRepository,
    YearRepository,
    DocumentRepository,
    FeatureDistrictYearRepository
)


class DataService:
    """Сервис для работы с данными Excel и БД"""

    @staticmethod
    @db_session
    def create_document(filename: str, file_path: str, file_type: ExcelFileType) -> Document:
        """Создать запись о документе в БД"""
        document = Document(
            filename=filename,
            file_path=file_path,
            file_type=file_type.value
        )
        commit()
        return document

    @staticmethod
    @db_session
    def load_full_data(file_path: str, document_id: Optional[int] = None) -> Dict[str, int]:
        """
        Загрузить FULL формат: каждый лист = год, столбцы = районы, строки = признаки

        Args:
            file_path: Путь к Excel файлу
            document_id: ID документа в БД (опционально)

        Returns: Статистика загрузки
        """
        # Получить объект документа по ID внутри транзакции
        document = Document.get(id=document_id) if document_id else None

        excel_file = pd.ExcelFile(file_path)

        stats = {
            'features': 0,
            'districts': 0,
            'years': 0,
            'values': 0
        }

        for sheet_name in excel_file.sheet_names:
            try:
                year_value = int(sheet_name)
            except ValueError:
                print(f"Пропущен лист '{sheet_name}' - название не является годом")
                continue

            year_obj = DataService._process_year(year_value, stats)
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            districts = DataService._process_districts(df, stats)
            district_columns = list(districts.keys())

            for _, row in df.iterrows():
                feature_name = row['Unnamed: 1']
                feature = DataService._process_feature(feature_name, stats)

                for district_name in district_columns:
                    value = row[district_name]
                    DataService._create_feature_value(
                        feature=feature,
                        district=districts[district_name],
                        year=year_obj,
                        value=value,
                        document=document,
                        stats=stats
                    )

            print(f"✓ Загружен год {year_value} из листа '{sheet_name}'")

        commit()
        return stats

    @staticmethod
    def _process_year(year_value: int, stats: Dict) -> Year:
        """Создать или получить год из БД"""
        year_obj = Year.get(year=year_value)
        if not year_obj:
            year_obj = Year(year=year_value)
            stats['years'] += 1
        return year_obj

    @staticmethod
    def _process_districts(df: pd.DataFrame, stats: Dict) -> Dict[str, District]:
        """Извлечь и создать районы из DataFrame"""
        district_columns = [col for col in df.columns if col.startswith('пункт')]

        districts = {}
        for district_name in district_columns:
            district = District.get(name=district_name)
            if not district:
                district = District(name=district_name)
                stats['districts'] += 1
            districts[district_name] = district

        return districts

    @staticmethod
    def _process_feature(feature_name: str, stats: Dict) -> Feature:
        """Создать или получить признак из БД"""
        feature = Feature.get(name=feature_name)
        if not feature:
            feature = Feature(name=feature_name)
            stats['features'] += 1
        return feature

    @staticmethod
    def _create_feature_value(
        feature: Feature,
        district: District,
        year: Year,
        value: any,
        document: Optional[Document],
        stats: Dict
    ) -> None:
        """Создать запись feature-district-year если не существует"""
        decimal_value = Decimal(str(value)) if pd.notna(value) else None

        existing = FeatureDistrictYear.get(
            feature=feature,
            district=district,
            year=year
        )

        if not existing:
            FeatureDistrictYear(
                feature=feature,
                district=district,
                year=year,
                document=document,
                value=decimal_value
            )
            stats['values'] += 1


    @staticmethod
    @db_session
    def load_part_data(file_path: str, year: int) -> Dict[str, int]:
        """Загрузить PART формат (будет реализовано позже)"""
        raise NotImplementedError("Метод load_part_data() будет реализован позже")

    @staticmethod
    @db_session
    def get_data_for_analysis(
        year: Optional[int] = None,
        district: Optional[str] = None,
        exclude_null: bool = True
    ) -> pd.DataFrame:
        """Извлечь данные из БД в формате DataFrame"""
        from models.queries import get_values_with_filter

        values = get_values_with_filter(
            year=year,
            district_name=district,
            exclude_null=exclude_null
        )

        data = []
        for v in values:
            data.append({
                'признак': v.feature.name,
                'район': v.district.name,
                'год': v.year.year,
                'значение': float(v.value) if v.value else None
            })

        return pd.DataFrame(data)

    @staticmethod
    @db_session
    def get_pivot_table(
        index: str = 'признак',
        columns: str = 'район',
        values: str = 'значение',
        year: Optional[int] = None
    ) -> pd.DataFrame:
        """Получить сводную таблицу"""
        df = DataService.get_data_for_analysis(year=year, exclude_null=False)

        if df.empty:
            return pd.DataFrame()

        pivot = df.pivot_table(
            index=index,
            columns=columns,
            values=values,
            aggfunc='first'
        )

        return pivot
