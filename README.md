# Анализ уровня преступности (Random Forest)

Веб-приложение на Flask для загрузки, хранения и анализа данных о преступности с использованием модели случайного леса (Random Forest).

## Требования

- **Docker Desktop** — [скачать](https://www.docker.com/products/docker-desktop/)
- **Git** (необязательно, можно скачать архив)

## Установка и запуск

### 1. Получить проект

**Вариант А** — клонировать репозиторий:
```bash
git clone <URL_репозитория>
cd <папка_проекта>
```

**Вариант Б** — скачать архив с GitHub, распаковать и перейти в папку проекта.

### 2. Подготовить дамп базы данных

Положить файл `dump.sql` в корень проекта. Этот файл содержит структуру и данные БД. При первом запуске PostgreSQL автоматически выполнит его и заполнит базу.

### 3. Запустить проект

Убедиться, что **Docker Desktop запущен**, затем выполнить:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: **http://localhost:5000**

### 4. Остановка

```bash
docker-compose down
```

## Обновление данных

Если нужно обновить дамп базы (новый `dump.sql`):
```bash
docker-compose down -v
```
Флаг `-v` удаляет volume с данными PostgreSQL. После этого замените `dump.sql` на новый и запустите:
```bash
docker-compose up --build
```

## Что делать после изменений в коде

После изменения исходного кода пересоберите контейнер:
```bash
docker-compose up --build
```

Если изменились модели БД (добавлены новые таблицы/поля), необходимо пересоздать базу:
```bash
docker-compose down -v
docker-compose up --build
```

## Модели данных

| Модель | Таблица | Описание |
|--------|---------|----------|
| **Year** | `years` | Годы |
| **District** | `districts` | Районы |
| **Feature** | `features` | Признаки/показатели (привязаны к линии преступлений) |
| **CrimeType** | `crime_types` | Линии преступлений |
| **Population** | `population` | Численность населения (район + год) |
| **FeatureDistrictYear** | `feature_district_year` | Значения показателей (признак + район + год) |
| **CrimeStatistics** | `crime_statistics` | Рассчитанная статистика преступности |
| **FinancialExpenses** | `financial_expenses` | Финансовые расходы |
| **Document** | `documents` | Загруженные Excel-файлы |
| **AnalysisResult** | `analysis_results` | Результаты анализа Random Forest |

## Структура проекта

```
├── app.py                  # Точка входа Flask-приложения
├── settings.py             # Настройки из .env
├── docker-compose.yml      # Конфигурация Docker
├── Dockerfile              # Образ приложения
├── dump.sql                # Дамп базы данных
├── requirements.txt        # Python-зависимости
│
├── controllers/            # Маршруты (роуты)
│   ├── main_controller.py        # /  /upload  /upload_financial
│   ├── data_controller.py        # /documents  /api/year-data
│   ├── analysis_controller.py    # /analysis  (выбор, запуск, результаты)
│   ├── map_controller.py         # /map  /api/crime-data
│   └── population_controller.py  # /population  /api/population
│
├── models/entities/        # ORM-модели (Pony ORM)
│
├── services/               # Бизнес-логика
│   ├── file_service.py                # Сохранение загруженных файлов
│   ├── data_service.py                # Парсинг Excel и загрузка в БД
│   ├── analysis_service.py            # Запуск Random Forest
│   ├── crime_calculation_service.py   # Расчет уровня преступности
│   └── crime_line_analysis_service.py # Анализ по линиям преступлений
│
├── repositories/           # Доступ к данным (CRUD)
│
├── utils/                  # Утилиты
│   ├── db.py               # Инициализация и подключение к БД
│   └── migrations.py       # Автоматические миграции
│
├── templates/              # HTML-шаблоны
├── static/                 # CSS, JS, графики, GeoJSON
└── files/                  # Загруженные Excel-файлы
```

## Куда смотреть при изменениях

| Что нужно изменить | Где искать |
|---|---|
| Добавить новую страницу | `controllers/` + `templates/` |
| Изменить модель данных | `models/entities/` |
| Изменить логику анализа | `services/analysis_service.py` |
| Изменить парсинг Excel | `services/data_service.py` |
| Изменить расчёт преступности | `services/crime_calculation_service.py` |
| Изменить карту | `templates/map.html` + `static/js/map.js` |
| Настройки подключения к БД | `docker-compose.yml` (environment) |
| Добавить миграцию БД | `utils/migrations.py` |

## Используемые технологии

- **Python 3.12** / Flask
- **PostgreSQL 16** / Pony ORM
- **scikit-learn** (Random Forest)
- **pandas** / **matplotlib**
- **Docker** / Docker Compose
