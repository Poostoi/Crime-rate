import os
import re
from datetime import datetime
from werkzeug.datastructures import FileStorage
from settings import settings


class FileService:
    """Сервис для работы с файлами"""

    @staticmethod
    def safe_filename(filename: str) -> str:
        """Создает безопасное имя файла с поддержкой кириллицы и защитой от path traversal"""
        filename = filename.replace(' ', '_')
        filename = re.sub(r'[^а-яА-ЯёЁa-zA-Z0-9._-]', '', filename)
        filename = re.sub(r'\.{2,}', '.', filename)
        filename = filename.lstrip('.')

        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'upload_{timestamp}'

        return filename

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Проверка разрешенного расширения файла"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.allowed_extensions_set

    @staticmethod
    def save_uploaded_file(file: FileStorage) -> tuple[str, str]:
        """
        Сохранить загруженный файл на диск

        Returns: (filename, filepath)
        """
        filename = FileService.safe_filename(file.filename)
        filepath = os.path.join(settings.upload_folder, filename)

        os.makedirs(settings.upload_folder, exist_ok=True)
        file.save(filepath)

        return filename, filepath
