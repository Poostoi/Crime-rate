from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from pony.orm import db_session, select, commit
from models.entities import District, Year, Population

population_bp = Blueprint('population', __name__)


@population_bp.route('/population')
@db_session
def population():
    districts = select(d for d in District).order_by(District.name)[:]
    years = select(y for y in Year).order_by(Year.year)[:]

    population_data = {}
    for pop in select(p for p in Population):
        key = (pop.district.id, pop.year.id)
        population_data[key] = pop.value

    return render_template(
        'population.html',
        districts=districts,
        years=years,
        population_data=population_data
    )


@population_bp.route('/api/population/save', methods=['POST'])
@db_session
def save_population():
    try:
        data = request.get_json()
        district_id = data.get('district_id')
        year_id = data.get('year_id')
        value = data.get('value')

        if not all([district_id, year_id, value]):
            return jsonify({'success': False, 'message': 'Не все поля заполнены'}), 400

        district = District.get(id=district_id)
        year = Year.get(id=year_id)

        if not district or not year:
            return jsonify({'success': False, 'message': 'Район или год не найден'}), 404

        population = Population.get(district=district, year=year)

        if population:
            population.value = int(value)
        else:
            Population(district=district, year=year, value=int(value))

        commit()

        return jsonify({'success': True, 'message': 'Данные сохранены'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@population_bp.route('/api/population/delete', methods=['POST'])
@db_session
def delete_population():
    try:
        data = request.get_json()
        district_id = data.get('district_id')
        year_id = data.get('year_id')

        district = District.get(id=district_id)
        year = Year.get(id=year_id)

        if not district or not year:
            return jsonify({'success': False, 'message': 'Район или год не найден'}), 404

        population = Population.get(district=district, year=year)

        if population:
            population.delete()
            commit()
            return jsonify({'success': True, 'message': 'Данные удалены'})
        else:
            return jsonify({'success': False, 'message': 'Запись не найдена'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
