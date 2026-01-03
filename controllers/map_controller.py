from flask import Blueprint, render_template, jsonify
from services.crime_calculation_service import CrimeCalculationService
from pony.orm import db_session, select
from models.entities import District

map_bp = Blueprint('map', __name__)

DISTRICT_MAP_ID = {
    'Слободзея': 1,
    'Слободзейский': 1,
    'Тирасполь': 2,
    'Тираспольский': 2,
    'Бендеры': 3,
    'Бендерский': 3,
    'Григориополь': 4,
    'Григориопольский': 4,
    'Дубоссары': 5,
    'Дубоссарский': 5,
    'Рыбница': 6,
    'Рыбницкий': 6,
    'Каменка': 7,
    'Каменский': 7
}


@db_session
def get_district_map_id(district_name: str) -> int:
    """Получить ID района для карты по названию"""
    for key, map_id in DISTRICT_MAP_ID.items():
        if key.lower() in district_name.lower():
            return map_id
    return None


@map_bp.route('/map')
def show_map():
    return render_template('map.html')


@map_bp.route('/api/crime-data')
@db_session
def crime_data():
    crime_stats = CrimeCalculationService.get_crime_data_for_map()

    result = {}
    for year, districts_data in crime_stats.items():
        result[year] = {}
        for district_id, normalized_value in districts_data.items():
            district = District.get(id=district_id)
            if district:
                map_id = get_district_map_id(district.name)
                if map_id:
                    result[year][map_id] = normalized_value

    return jsonify(result)


@map_bp.route('/api/calculate-crime-level', methods=['POST'])
@db_session
def calculate_crime_level():
    try:
        results = CrimeCalculationService.calculate_all_years()

        total_calculated = sum(len(districts) for districts in results.values())

        return jsonify({
            'success': True,
            'message': f'Расчет завершен. Обработано {len(results)} лет, {total_calculated} записей.',
            'years': list(results.keys())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка при расчете: {str(e)}'
        }), 500
