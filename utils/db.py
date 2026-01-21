from pony.orm import db_session, set_sql_debug
from models.entities import db
from settings import settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database_if_not_exists(config: dict):
    """Создать БД если не существует"""
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (config['database'],)
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {config['database']}")
            print(f"✓ База данных '{config['database']}' создана")
        else:
            print(f"✓ База данных '{config['database']}' уже существует")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        raise


def init_database(
    provider: str = 'postgres',
    user: str = None,
    password: str = None,
    host: str = 'localhost',
    port: int = 5432,
    database: str = 'crime_analysis',
    create_tables: bool = True,
    sql_debug: bool = False
):
    """Инициализировать подключение к БД и создать таблицы"""
    if sql_debug:
        set_sql_debug(True)

    if provider == 'postgres':
        if not user or not password:
            raise ValueError("Для PostgreSQL требуются user и password")

        db.bind(
            provider='postgres',
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
    else:
        raise ValueError(f"Неподдерживаемый провайдер БД: {provider}")

    db.generate_mapping(create_tables=create_tables)
    print(f"✓ База данных инициализирована: {provider} - {database}")


def init_from_env(create_tables: bool = True, sql_debug: bool = False):
    """Инициализировать БД из Settings (создает БД если не существует)"""
    config = settings.db_config
    create_database_if_not_exists(config)

    init_database(
        provider=config['provider'],
        user=config['user'],
        password=config['password'],
        host=config['host'],
        port=config['port'],
        database=config['database'],
        create_tables=create_tables,
        sql_debug=sql_debug
    )


def init_for_migrations(sql_debug: bool = False):
    """Инициализировать БД только для выполнения миграций (без создания таблиц)"""
    if sql_debug:
        set_sql_debug(True)

    config = settings.db_config
    create_database_if_not_exists(config)

    db.bind(
        provider='postgres',
        user=config['user'],
        password=config['password'],
        host=config['host'],
        port=config['port'],
        database=config['database']
    )
    print(f"✓ База данных подключена для миграций: {config['database']}")


def clear_database():
    """Удалить все таблицы (УДАЛЯЕТ ВСЕ ДАННЫЕ И СТРУКТУРУ!)"""
    try:
        config = settings.db_config
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public' AND tablename = 'feature_district_year'
        """)

        if not cursor.fetchone():
            print("✓ Таблицы не существуют, очистка не требуется")
            cursor.close()
            conn.close()
            return

        cursor.execute("DROP TABLE IF EXISTS crime_statistics CASCADE")
        cursor.execute("DROP TABLE IF EXISTS population CASCADE")
        cursor.execute("DROP TABLE IF EXISTS feature_district_year CASCADE")
        cursor.execute("DROP TABLE IF EXISTS features CASCADE")
        cursor.execute("DROP TABLE IF EXISTS crime_types CASCADE")
        cursor.execute("DROP TABLE IF EXISTS districts CASCADE")
        cursor.execute("DROP TABLE IF EXISTS years CASCADE")
        cursor.execute("DROP TABLE IF EXISTS documents CASCADE")

        conn.commit()
        cursor.close()
        conn.close()

        print("✓ Таблицы удалены")

    except psycopg2.OperationalError as e:
        print(f"✓ База данных не существует или недоступна: {e}")
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {e}")
