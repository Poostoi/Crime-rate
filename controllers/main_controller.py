from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.data_service import DataService
from services.file_service import FileService
from models.excel_enum import ExcelFileType

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загрузки файла"""
    if 'file' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('main.index'))

    file = request.files['file']

    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('main.index'))

    if file and FileService.allowed_file(file.filename):
        filename, filepath = FileService.save_uploaded_file(file)

        document = DataService.create_document(
            filename=filename,
            file_path=filepath,
            file_type=ExcelFileType.FULL
        )

        try:
            # Передаем ID документа, а не сам объект, чтобы избежать смешивания транзакций
            stats = DataService.load_full_data(filepath, document.id)
            flash(
                f'Файл "{filename}" загружен и обработан. '
                f'Добавлено: {stats["features"]} признаков, '
                f'{stats["districts"]} районов, '
                f'{stats["years"]} лет, '
                f'{stats["values"]} значений',
                'success'
            )
        except Exception as e:
            flash(f'Ошибка при обработке файла: {str(e)}', 'danger')

        return redirect(url_for('main.index'))
    else:
        flash('Недопустимый формат файла. Разрешены только .xlsx файлы', 'danger')
        return redirect(url_for('main.index'))
