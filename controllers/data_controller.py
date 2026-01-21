from flask import Blueprint, render_template, jsonify
from pony.orm import db_session, select
from models.entities import FeatureDistrictYear, Year, District, Feature, FinancialExpenses

data_bp = Blueprint('data', __name__)


@data_bp.route('/documents')
@db_session
def documents():
    """Страница просмотра всех данных из базы"""
    from flask import request

    data_type = request.args.get('data_type', None)
    years_list = None
    first_year_data = None
    financial_data = None

    if data_type == 'crime':
        years = list(select(y for y in Year).order_by(Year.year))
        years_list = [y.year for y in years]

        if years:
            first_year = years[0]
            first_year_data = get_year_data(first_year.year)

    elif data_type == 'financial':
        financial_data = get_financial_data()

    return render_template(
        'documents.html',
        years_list=years_list,
        first_year_data=first_year_data,
        financial_data=financial_data,
        data_type=data_type
    )


@data_bp.route('/api/year-data/<int:year>')
@db_session
def get_year_data_api(year):
    """API для получения данных по конкретному году"""
    data = get_year_data(year)
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Данные не найдены'}), 404


def get_year_data(year_value):
    """Получить данные за конкретный год"""
    year = Year.get(year=year_value)
    if not year:
        return None

    districts = list(select(d for d in District).order_by(District.id))
    features = list(select(f for f in Feature).order_by(Feature.id))

    features_data = []
    for feature in features:
        district_values = []
        for district in districts:
            records = list(select(
                fdy for fdy in FeatureDistrictYear
                if fdy.year == year and fdy.district == district and fdy.feature == feature
            ))
            value = float(records[0].value) if records and records[0].value is not None else None
            district_values.append(value)

        features_data.append({
            'name': feature.name,
            'district_values': district_values
        })

    return {
        'year': year.year,
        'district_names': [d.name for d in districts],
        'features': features_data
    }


def get_financial_data():
    """Получить финансовые данные сгруппированные по показателям и годам"""
    all_expenses = list(select(fe for fe in FinancialExpenses).order_by(FinancialExpenses.name, FinancialExpenses.year))

    if not all_expenses:
        return None

    years_set = sorted(set(fe.year.year for fe in all_expenses))
    indicators_dict = {}

    for expense in all_expenses:
        indicator_name = expense.name
        if indicator_name not in indicators_dict:
            indicators_dict[indicator_name] = {}

        indicators_dict[indicator_name][expense.year.year] = {
            'amount': expense.amount,
            'district': expense.district.name
        }

    indicators_list = []
    for indicator_name, year_data in indicators_dict.items():
        year_values = []
        for year in years_set:
            if year in year_data:
                year_values.append(year_data[year]['amount'])
            else:
                year_values.append(None)

        indicators_list.append({
            'name': indicator_name,
            'year_values': year_values
        })

    return {
        'years': years_set,
        'indicators': indicators_list
    }
