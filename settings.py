from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из .env файла"""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='.',
        extra='ignore'
    )

    db_provider: str = 'postgres'
    db_user: str
    db_password: str
    db_host: str = 'localhost'
    db_port: int = 5432
    db_name: str = 'crime_analysis'

    secret_key: str
    upload_folder: str = 'files'
    max_content_length: int = 16777216
    allowed_extensions: str = 'xlsx'

    @property
    def database_url(self) -> str:
        """Строка подключения к PostgreSQL"""
        if self.db_provider == 'postgres':
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return ""

    @property
    def db_config(self) -> dict:
        """Конфигурация для Pony ORM"""
        return {
            'provider': self.db_provider,
            'user': self.db_user,
            'password': self.db_password,
            'host': self.db_host,
            'port': self.db_port,
            'database': self.db_name
        }

    @property
    def allowed_extensions_set(self) -> set:
        """Set разрешенных расширений файлов"""
        return {ext.strip().lower() for ext in self.allowed_extensions.split(',')}

    @property
    def flask_config(self) -> dict:
        """Конфигурация Flask"""
        return {
            'SECRET_KEY': self.secret_key,
            'UPLOAD_FOLDER': self.upload_folder,
            'MAX_CONTENT_LENGTH': self.max_content_length
        }


settings = Settings()