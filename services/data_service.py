import pandas as pd
from decimal import Decimal
from pony.orm import db_session, commit
from typing import Dict, Optional
from models.entities import Feature, District, Year, FeatureDistrictYear, Document, FinancialExpenses
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

            feature_column = DataService._find_feature_column(df)
            if not feature_column:
                print(f"Пропущен лист '{sheet_name}' - не найдена колонка с признаками")
                continue

            districts = DataService._process_districts(df, stats)

            for _, row in df.iterrows():
                feature_name = row[feature_column]
                if pd.isna(feature_name) or str(feature_name).strip() == '':
                    continue

                feature_name_str = str(feature_name).strip()
                skip_names = ['СУММА', 'НАСЕЛЕНИЕ', 'НОРМИРОВКА', 'сумма', 'население', 'нормировка']
                if feature_name_str in skip_names:
                    continue

                feature = DataService._process_feature(feature_name_str, stats)

                for col_name, district in districts.items():
                    value = row[col_name]
                    DataService._create_feature_value(
                        feature=feature,
                        district=district,
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
    def _find_feature_column(df: pd.DataFrame) -> Optional[str]:
        """Найти колонку с признаками"""
        possible_names = ['ПОКАЗАТЕЛЬ', 'Unnamed: 1', 'показатель', 'признак']
        for col in df.columns:
            if col in possible_names:
                return col
        return None

    @staticmethod
    def _process_districts(df: pd.DataFrame, stats: Dict) -> Dict:
        """Извлечь и создать районы из DataFrame, возвращает {col_name: District}"""
        exclude_columns = ['ПОКАЗАТЕЛЬ', 'Unnamed: 0', 'Unnamed: 1', 'ПМР', 'Unnamed: 9', 'Unnamed: 10']
        districts = {}

        for col in df.columns:
            if pd.isna(col):
                continue
            if col in exclude_columns:
                continue
            if isinstance(col, str) and col.startswith('Unnamed'):
                continue

            district_name = str(col)
            district = District.get(name=district_name)
            if not district:
                district = District(name=district_name)
                stats['districts'] += 1
            districts[col] = district

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

    @staticmethod
    def parse_financial_expenses_from_excel(file_path: str) -> Dict[int, float]:
        """
        Парсит Excel файл с финансовыми расходами
        Формат: первая колонка - показатели, остальные - годы
        Возвращает словарь {год: сумма_по_всем_показателям}
        """
        df = pd.read_excel(file_path)

        year_columns = []
        for col in df.columns:
            if col != 'ПОКАЗАТЕЛЬ' and not str(col).startswith('Unnamed'):
                try:
                    year_int = int(col)
                    year_columns.append(year_int)
                except (ValueError, TypeError):
                    pass

        if not year_columns:
            raise ValueError("Не найдены колонки с годами")

        expenses_by_year = {}

        for year in year_columns:
            total = 0.0
            for _, row in df.iterrows():
                value = row[year]
                if pd.notna(value):
                    try:
                        total += float(value)
                    except (ValueError, TypeError):
                        pass
            expenses_by_year[year] = total

        return expenses_by_year

    @staticmethod
    @db_session
    def load_financial_expenses(expenses_by_year: Dict[int, float]) -> Dict[str, int]:
        """
        Загружает финансовые расходы в БД
        Принимает словарь {год: сумма}
        """
        stats = {
            'districts': 0,
            'years': 0,
            'records': 0
        }

        pmr_district = District.get(name='ПМР')
        if not pmr_district:
            pmr_district = District(name='ПМР')
            stats['districts'] += 1

        for year_int, amount in expenses_by_year.items():
            year_obj = Year.get(year=year_int)
            if not year_obj:
                year_obj = Year(year=year_int)
                stats['years'] += 1

            existing = FinancialExpenses.get(district=pmr_district, year=year_obj)
            if not existing:
                FinancialExpenses(
                    district=pmr_district,
                    year=year_obj,
                    amount=amount,
                    include_in_analysis=True
                )
                stats['records'] += 1

        commit()
        return stats
