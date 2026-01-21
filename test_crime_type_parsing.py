"""Тест парсинга названий признаков с линиями преступлений"""

from services.data_service import DataService

def test_parsing():
    test_cases = [
        ("По линии ОБЭП (Взятки)", ("По линии ОБЭП", "Взятки")),
        ("По линии ОБЭП (Мошенничество)", ("По линии ОБЭП", "Мошенничество")),
        ("Кражи", (None, "Кражи")),
        ("Грабежи", (None, "Грабежи")),
        ("Убийства (Умышленные)", ("Убийства", "Умышленные")),
        ("  По линии ОБЭП  (  Взятки  )  ", ("По линии ОБЭП", "Взятки")),
    ]

    print("=== Тест парсинга названий признаков ===\n")

    all_passed = True
    for input_name, expected in test_cases:
        result = DataService._parse_feature_name(input_name)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_name}'")
        print(f"   Ожидалось: {expected}")
        print(f"   Получено:  {result}")

        if result != expected:
            all_passed = False
        print()

    if all_passed:
        print("✓ Все тесты пройдены!")
    else:
        print("✗ Некоторые тесты не прошли")


if __name__ == '__main__':
    test_parsing()
