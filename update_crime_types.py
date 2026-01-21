"""Скрипт для обновления существующих признаков с линиями преступлений"""

import utils.db as db
from services.data_service import DataService

def main():
    print("=== Обновление признаков с линиями преступлений ===\n")

    db.init_from_env()

    print("Начинаю обновление...\n")
    stats = DataService.update_existing_features_with_crime_types()

    print("\n=== Результаты ===")
    print(f"Создано линий преступлений: {stats['crime_types_created']}")
    print(f"Обновлено признаков: {stats['updated']}")
    print("\n✓ Обновление завершено!")


if __name__ == '__main__':
    main()
