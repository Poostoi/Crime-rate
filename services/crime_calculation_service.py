from decimal import Decimal
from pony.orm import db_session, select, commit
from models.entities import District, Year, Population, FeatureDistrictYear, CrimeStatistics


class CrimeCalculationService:

    @staticmethod
    def calculate_for_year(year_value: int) -> dict:
        """
        Вычислить уровень преступности для всех районов за год

        Returns:
            dict: {district_id: normalized_value}
        """
        year_list = list(select(y for y in Year if y.year == year_value))
        if not year_list:
            return {}

        year = year_list[0]

        districts = list(select(d for d in District))
        coefficients = {}

        for district in districts:
            total_crimes = CrimeCalculationService._get_total_crimes(district, year)

            population_list = list(select(p for p in Population if p.district == district and p.year == year))
            if not population_list:
                continue

            population = population_list[0]
            if population.value == 0:
                continue

            coefficient = (Decimal(total_crimes) / Decimal(population.value)) * Decimal(100000)
            coefficients[district.id] = {
                'district': district,
                'total_crimes': total_crimes,
                'population': population.value,
                'coefficient': coefficient
            }

        if not coefficients:
            return {}

        normalized = CrimeCalculationService._normalize_coefficients(coefficients)

        for district_id, data in normalized.items():
            CrimeCalculationService._save_statistics(
                district=data['district'],
                year=year,
                total_crimes=data['total_crimes'],
                population=data['population'],
                coefficient=data['coefficient'],
                normalized=data['normalized']
            )

        return {district_id: float(data['normalized']) for district_id, data in normalized.items()}

    @staticmethod
    @db_session
    def calculate_all_years() -> dict:
        """Вычислить для всех годов где есть данные"""
        years = list(select(y for y in Year))
        results = {}

        for year in years:
            results[year.year] = CrimeCalculationService.calculate_for_year(year.year)

        return results

    @staticmethod
    def _get_total_crimes(district: District, year: Year) -> int:
        """Суммировать все преступления для района и года"""
        values = list(select(
            v for v in FeatureDistrictYear
            if v.district == district and v.year == year
        ))

        total = sum(float(v.value) for v in values if v.value is not None)
        return int(total)

    @staticmethod
    def _normalize_coefficients(coefficients: dict) -> dict:
        """
        Нормировать коэффициенты в диапазон 1-5 методом min-max масштабирования
        """
        if not coefficients:
            return {}

        coef_values = [data['coefficient'] for data in coefficients.values()]
        min_coef = min(coef_values)
        max_coef = max(coef_values)

        if min_coef == max_coef:
            for district_id in coefficients:
                coefficients[district_id]['normalized'] = Decimal('3.5')
        else:
            for district_id in coefficients:
                coef = coefficients[district_id]['coefficient']
                normalized = ((coef - min_coef) / (max_coef - min_coef)) * Decimal('3') + Decimal('2')
                coefficients[district_id]['normalized'] = normalized.quantize(Decimal('0.01'))

        return coefficients

    @staticmethod
    def _save_statistics(district: District, year: Year, total_crimes: int,
                        population: int, coefficient: Decimal, normalized: Decimal):
        """Сохранить расчеты в таблицу crime_statistics"""
        existing_list = list(select(s for s in CrimeStatistics if s.district == district and s.year == year))

        if existing_list:
            existing = existing_list[0]
            existing.total_crimes = total_crimes
            existing.population = population
            existing.coefficient = coefficient
            existing.normalized = normalized
        else:
            CrimeStatistics(
                district=district,
                year=year,
                total_crimes=total_crimes,
                population=population,
                coefficient=coefficient,
                normalized=normalized
            )

        commit()

    @staticmethod
    @db_session
    def get_crime_data_for_map() -> dict:
        """
        Получить данные для карты в формате {year: {district_id: normalized_value}}
        """
        result = {}

        for stat in list(select(s for s in CrimeStatistics)):
            year_value = stat.year.year
            district_id = stat.district.id

            if year_value not in result:
                result[year_value] = {}

            result[year_value][district_id] = float(stat.normalized)

        return result
