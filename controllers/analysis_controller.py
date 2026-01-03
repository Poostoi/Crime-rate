from flask import Blueprint, render_template, request, flash, redirect, url_for
from services.analysis_service import AnalysisService

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analysis')
def analysis():
    """Страница анализа данных"""
    files = AnalysisService.get_available_files()
    selected_file = request.args.get('file')
    results = None

    if selected_file:
        try:
            results = AnalysisService.run_analysis(selected_file)
            results['selected_file'] = selected_file
        except Exception as e:
            flash(f'Ошибка при анализе файла: {str(e)}', 'danger')
            return redirect(url_for('analysis.analysis'))

    return render_template(
        'analysis.html',
        files=files,
        selected_file=selected_file,
        results=results
    )
