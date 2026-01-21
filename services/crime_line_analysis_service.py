from decimal import Decimal
from pony.orm import db_session, select
from models.entities import CrimeType, District, Year, Population, FeatureDistrictYear, FinancialExpenses
import pandas as pd


class CrimeLineAnalysisService:

    @staticmethod
    @db_session
    def get_all_crime_types():
        """Получить список всех линий преступлений"""
        crime_types = list(select(ct for ct in CrimeType))
        return crime_types

    @staticmethod
    @db_session
    def get_financial_indicators():
        """Получить список уникальных финансовых показателей с текущим статусом"""
        indicators = {}
        for expense in select(fe for fe in FinancialExpenses):
            if expense.name not in indicators:
                indicators[expense.name] = expense.include_in_analysis

        return [{'name': name, 'include_in_analysis': include}
                for name, include in indicators.items()]

    @staticmethod
    @db_session
    def update_indicator_status(indicator_name: str, include: bool):
        """Обновить статус участия показателя в анализе"""
        expenses = select(fe for fe in FinancialExpenses if fe.name == indicator_name)
        for expense in expenses:
            expense.include_in_analysis = include

    @staticmethod
    @db_session
    def calculate_crime_level_by_line(crime_type_id: int) -> pd.DataFrame:
        """
        Рассчитать уровень преступности по линии для всех районов и годов

        Returns:
            DataFrame где индекс - года, колонки - районы, значения - уровень преступности
        """
        crime_type = CrimeType[crime_type_id]
        districts = list(select(d for d in District))
        years = list(select(y for y in Year))

        data = {}

        for district in districts:
            district_data = {}
            for year in years:
                total_crimes = CrimeLineAnalysisService._get_total_crimes_for_line(
                    crime_type, district, year
                )

                population_list = list(select(p for p in Population
                                             if p.district == district and p.year == year))
                if not population_list or population_list[0].value == 0:
                    continue

                population = population_list[0].value
                crime_level = (Decimal(total_crimes) / Decimal(population)) * Decimal(100000)
                district_data[year.year] = float(crime_level)

            if district_data:
                data[district.name] = district_data

        df = pd.DataFrame(data)
        return df.T

    @staticmethod
    def _get_total_crimes_for_line(crime_type: CrimeType, district: District, year: Year) -> int:
        """Суммировать преступления для линии, района и года"""
        values = list(select(v for v in FeatureDistrictYear
                           if v.feature.crime_type == crime_type
                           and v.district == district
                           and v.year == year))

        total = sum(float(v.value) for v in values if v.value is not None)
        return int(total)

    @staticmethod
    @db_session
    def prepare_analysis_data(crime_type_id: int) -> pd.DataFrame:
        """
        Подготовить данные для анализа Random Forest

        Returns:
            DataFrame где строки - показатели (финансовые + "Уровень преступности"),
            столбцы - года
        """
        crime_level_df = CrimeLineAnalysisService.calculate_crime_level_by_line(crime_type_id)

        crime_level_by_year = crime_level_df.mean(axis=0)

        financial_data = {}
        years = list(select(y for y in Year))

        selected_expenses = list(select(fe for fe in FinancialExpenses
                                       if fe.include_in_analysis == True))

        indicator_names = set(exp.name for exp in selected_expenses)

        for indicator_name in indicator_names:
            indicator_data = {}
            for year in years:
                expenses = list(select(fe for fe in FinancialExpenses
                                     if fe.name == indicator_name
                                     and fe.year == year
                                     and fe.include_in_analysis == True))

                if expenses:
                    avg_amount = sum(float(exp.amount) for exp in expenses) / len(expenses)
                    indicator_data[year.year] = avg_amount

            if indicator_data:
                financial_data[indicator_name] = indicator_data

        financial_df = pd.DataFrame(financial_data).T

        crime_level_series = pd.Series(crime_level_by_year, name="Уровень преступности")

        result_df = pd.concat([financial_df, crime_level_series.to_frame().T])

        return result_df
