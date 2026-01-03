from flask import Blueprint, render_template
from pony.orm import db_session, select
from models.entities import FeatureDistrictYear, Year, District, Feature

data_bp = Blueprint('data', __name__)


@data_bp.route('/documents')
@db_session
def documents():
    """Страница просмотра всех данных из базы"""
    years_data = []

    years = list(select(y for y in Year).order_by(Year.year))

    for year in years:
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

        years_data.append({
            'year': year.year,
            'district_names': [d.name for d in districts],
            'features': features_data
        })

    return render_template(
        'documents.html',
        years_data=years_data
    )
