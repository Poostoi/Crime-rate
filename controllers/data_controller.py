from flask import Blueprint, render_template, request
from repositories import DocumentRepository, FeatureDistrictYearRepository
from pony.orm import db_session, select
from models.entities import FeatureDistrictYear, Document

data_bp = Blueprint('data', __name__)


@data_bp.route('/documents')
def documents():
    """Страница просмотра данных документов"""
    # Получить список всех документов
    documents_list = DocumentRepository.get_all_sorted_by_date()

    # Проверить, выбран ли документ
    document_id = request.args.get('id', type=int)
    document_data = None

    if document_id:
        document_data = DocumentRepository.get_data_by_years(document_id)

    return render_template(
        'documents.html',
        documents=documents_list,
        selected_id=document_id,
        document_data=document_data
    )
