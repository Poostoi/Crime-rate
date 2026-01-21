from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from services.analysis_service import AnalysisService
from services.crime_line_analysis_service import CrimeLineAnalysisService

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analysis')
def analysis():
    """Страница анализа данных"""
    crime_types = CrimeLineAnalysisService.get_all_crime_types()

    if request.args.get('new'):
        return render_template('analysis.html', crime_types=crime_types, step=1)

    latest_result = AnalysisService.get_latest_result_any()

    if latest_result:
        return render_template(
            'analysis.html',
            crime_types=crime_types,
            results=latest_result,
            step=3
        )

    return render_template(
        'analysis.html',
        crime_types=crime_types
    )


@analysis_bp.route('/analysis/select-indicators', methods=['POST'])
def select_indicators():
    """Показать форму выбора финансовых показателей"""
    crime_type_id = request.form.get('crime_type_id')

    if not crime_type_id:
        flash('Выберите линию преступлений', 'danger')
        return redirect(url_for('analysis.analysis'))

    crime_types = CrimeLineAnalysisService.get_all_crime_types()
    indicators = CrimeLineAnalysisService.get_financial_indicators()

    return render_template(
        'analysis.html',
        crime_types=crime_types,
        selected_crime_type_id=int(crime_type_id),
        indicators=indicators,
        step=2
    )


@analysis_bp.route('/analysis/run', methods=['POST'])
def run_analysis():
    """Запустить анализ с выбранными показателями"""
    crime_type_id = request.form.get('crime_type_id')
    selected_indicators = request.form.getlist('indicators')

    if not crime_type_id:
        flash('Выберите линию преступлений', 'danger')
        return redirect(url_for('analysis.analysis'))

    if not selected_indicators:
        flash('Выберите хотя бы один финансовый показатель', 'danger')
        return redirect(url_for('analysis.select_indicators'))

    all_indicators = CrimeLineAnalysisService.get_financial_indicators()
    for indicator in all_indicators:
        include = indicator['name'] in selected_indicators
        CrimeLineAnalysisService.update_indicator_status(indicator['name'], include)

    try:
        results = AnalysisService.run_analysis_from_db(int(crime_type_id))

        crime_types = CrimeLineAnalysisService.get_all_crime_types()

        return render_template(
            'analysis.html',
            crime_types=crime_types,
            results=results,
            step=3
        )
    except Exception as e:
        flash(f'Ошибка при анализе: {str(e)}', 'danger')
        return redirect(url_for('analysis.analysis'))


@analysis_bp.route('/analysis/results/<int:crime_type_id>')
def show_results(crime_type_id):
    """Показать последние результаты анализа для линии преступлений"""
    results = AnalysisService.get_latest_result(crime_type_id)

    if not results:
        flash('Нет результатов анализа для данной линии преступлений', 'info')
        return redirect(url_for('analysis.analysis'))

    crime_types = CrimeLineAnalysisService.get_all_crime_types()

    return render_template(
        'analysis.html',
        crime_types=crime_types,
        results=results,
        step=3
    )
