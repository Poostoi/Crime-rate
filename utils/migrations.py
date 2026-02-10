"""Автоматические миграции базы данных"""

import psycopg2
from settings import settings


class MigrationManager:

    @staticmethod
    def _get_connection():
        """Получить подключение к БД"""
        config = settings.db_config
        return psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )

    @staticmethod
    def check_table_exists(table_name: str) -> bool:
        """Проверить существование таблицы"""
        conn = MigrationManager._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
            [table_name]
        )
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def check_column_exists(table_name: str, column_name: str) -> bool:
        """Проверить существование колонки в таблице"""
        conn = MigrationManager._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
            )
        """
        cursor.execute(query, [table_name, column_name])
        result = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def add_column(table_name: str, column_name: str, column_type: str, nullable: bool = True):
        """Добавить колонку в таблицу"""
        conn = MigrationManager._get_connection()
        cursor = conn.cursor()

        null_constraint = "NULL" if nullable else "NOT NULL"
        query = f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type} {null_constraint}'
        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()
        print(f'✓ Добавлена колонка {column_name} в таблицу {table_name}')

    @staticmethod
    def update_column_value(table_name: str, column_name: str, value: str, condition: str = None):
        """Обновить значения в колонке"""
        conn = MigrationManager._get_connection()
        cursor = conn.cursor()

        if condition:
            query = f'UPDATE {table_name} SET {column_name} = %s WHERE {condition}'
        else:
            query = f'UPDATE {table_name} SET {column_name} = %s'
        cursor.execute(query, [value])
        conn.commit()

        cursor.close()
        conn.close()
        print(f'✓ Обновлены значения в колонке {column_name}')

    @staticmethod
    def set_column_not_null(table_name: str, column_name: str):
        """Сделать колонку NOT NULL"""
        conn = MigrationManager._get_connection()
        cursor = conn.cursor()

        query = f'ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL'
        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()
        print(f'✓ Колонка {column_name} теперь NOT NULL')

    @staticmethod
    def drop_constraint(table_name: str, constraint_name: str):
        """Удалить constraint"""
        conn = MigrationManager._get_connection()
        cursor = conn.cursor()

        query = f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}'
        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()
        print(f'✓ Удален constraint {constraint_name}')

    @staticmethod
    def add_unique_constraint(table_name: str, constraint_name: str, columns: list):
        """Добавить UNIQUE constraint"""
        conn = MigrationManager._get_connection()
        cursor = conn.cursor()

        columns_str = ', '.join(columns)
        query = f'ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({columns_str})'
        try:
            cursor.execute(query)
            conn.commit()
            print(f'✓ Добавлен constraint {constraint_name} на колонки ({columns_str})')
        except Exception as e:
            if 'already exists' in str(e):
                print(f'  Constraint {constraint_name} уже существует')
            else:
                raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def migrate_financial_expenses():
        """Миграция для добавления колонки name в financial_expenses"""
        print('\n=== Миграция: добавление колонки name в financial_expenses ===')

        if not MigrationManager.check_table_exists('financial_expenses'):
            print('✓ Таблица financial_expenses ещё не создана, миграция пропущена\n')
            return

        if not MigrationManager.check_column_exists('financial_expenses', 'name'):
            print('Колонка name не найдена, начинаю миграцию...')

            MigrationManager.add_column('financial_expenses', 'name', 'VARCHAR(255)', nullable=True)
            MigrationManager.update_column_value('financial_expenses', 'name', 'Общие расходы', 'name IS NULL')
            MigrationManager.set_column_not_null('financial_expenses', 'name')
            MigrationManager.drop_constraint('financial_expenses', 'idx_financial_expenses__district_year')
            MigrationManager.drop_constraint('financial_expenses', 'unq_financial_expenses__district_year')
            MigrationManager.add_unique_constraint('financial_expenses', 'idx_financial_expenses__district_year_name', ['district', 'year', 'name'])

            print('✓ Миграция завершена успешно\n')
        else:
            print('✓ Колонка name уже существует, миграция не требуется\n')

    @staticmethod
    def run_all_migrations():
        """Запустить все миграции"""
        print('Запуск всех миграций...')
        MigrationManager.migrate_financial_expenses()
        print('Все миграции выполнены!')


if __name__ == '__main__':
    MigrationManager.run_all_migrations()
