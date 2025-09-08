# Документация проекта Games

## Общая структура проекта

```
Games/
├── faq_bot/           # Telegram бот для предоставления FAQ (Python)
│   ├── src/           # Исходный код бота
│   ├── data/          # Данные FAQ и база данных
│   ├── utils/         # Вспомогательные утилиты бота
│   ├── scripts/       # Скрипты управления ботом
│   ├── templates/     # Шаблоны данных
│   ├── files/         # Файлы FAQ
│   ├── tests/         # Тесты
│   ├── pyproject.toml  # Конфигурация проекта и зависимости бота
│   ├── .env           # Конфигурация бота
│   └── README.md      # Документация бота
│
├── faq_loader/        # Утилита для загрузки FAQ данных (C#)
│   ├── Business/      # Бизнес-логика и алгоритмы
│   ├── Data/          # Репозитории данных
│   ├── Presentation/  # WPF UI компоненты
│   ├── Program.cs     # Точка входа
│   ├── UniversalFAQLoader.sln  # Файл решения Visual Studio
│   ├── UniversalFAQLoader.csproj  # Проектный файл
│   ├── .env           # Конфигурация загрузчика
│   └── README.md      # Документация загрузчика
```

## Описание приложений

### faq_bot (Python Telegram бот)

#### Основные компоненты:

##### src/ - Основной исходный код бота
- `main.py` - Точка входа бота, инициализация и запуск
- `config.py` - Конфигурация приложения, загрузка переменных окружения
- `database.py` - Работа с SQLite базой данных для статистики и аутентификации
- `faq_loader.py` - Загрузка и поиск по FAQ данным с использованием ML
- `handlers.py` - Обработчики команд и сообщений Telegram
- `auth_middleware.py` - Middleware для аутентификации пользователей
- `security_middleware.py` - Middleware для безопасности
- `middlewares.py` - Middleware для внедрения зависимостей
- `performance_manager.py` - Управление производительностью и кэширование

##### utils/ - Вспомогательные утилиты
- `bulk_loader.py` - Загрузка FAQ данных из различных форматов
- `diagnose_bot.py` - Диагностика состояния бота
- `drag_drop_loader.py` - Загрузчик с поддержкой drag-and-drop
- `simple_bulk_loader.py` - Простой загрузчик данных
- `smart_faq_processor.py` - Интеллектуальная обработка FAQ данных

##### data/ - Данные приложения
- `faq.json` - Основной файл с FAQ данными
- `analytics.db` - SQLite база данных для статистики и аутентификации

##### templates/ - Шаблоны для загрузки данных
- Шаблоны в форматах CSV, TXT, XLSX для загрузки FAQ данных

##### files/ - Файлы, связанные с FAQ
- Изображения, документы и другие файлы, упомянутые в FAQ

##### scripts/ - Скрипты управления
- Bat-скрипты для различных операций с ботом

##### tests/ - Тесты
- Unit и интеграционные тесты для компонентов бота

#### Установка зависимостей

```bash
cd faq_bot
pip install -e .
```

Или установка только зависимостей:

```bash
pip install .
```

#### Запуск бота

##### Через Python:

```bash
python run_bot.py
```

##### Через bat-скрипт:

```bash
start_bot.bat
```

#### Конфигурация

Создайте файл `.env` со следующими переменными:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_user_id
ACCESS_PASSWORD=your_access_password
```

### faq_loader (C# приложение)

#### Основные компоненты:

##### Business/ - Бизнес-логика
- `FAQAlgorithmService.cs` - Основной сервис алгоритмов
- `DependencyAnalyzer.cs` - Анализ зависимостей между FAQ
- `SemanticGrouper.cs` - Группировка по семантике
- `SmartLinker.cs` - Умная связь между записями
- `ResponseOptimizer.cs` - Оптимизация ответов
- `IFAQAlgorithm.cs` - Интерфейс алгоритмов
- `FAQModels.cs` - Модели данных

##### Data/ - Репозитории данных
- `IFAQRepository.cs` - Интерфейс репозитория
- `JsonFAQRepository.cs` - Репозиторий для JSON данных
- `SqliteFAQRepository.cs` - Репозиторий для SQLite
- `HybridFAQRepository.cs` - Гибридный репозиторий

##### Presentation/ - WPF UI
- `Views/MainWindow.xaml` - Главное окно приложения
- `ViewModels/MainViewModel.cs` - ViewModel для главного окна
- `Controls/FAQGraphVisualization.xaml` - Контрол для визуализации графа

##### Файлы проекта
- `Program.cs` - Точка входа приложения
- `UniversalFAQLoader.csproj` - проектный файл
- `UniversalFAQLoader.sln` - файл решения Visual Studio

#### Установка и сборка

##### Требования:
- .NET 6.0 SDK
- Visual Studio 2022 или новее (для разработки)

##### Сборка через командную строку:

```bash
cd faq_loader
dotnet build
```

##### Запуск:

```bash
cd faq_loader
dotnet run
```

##### Запуск через bat-скрипт:

```bash
cd faq_loader
start_loader.bat
```

## Связи между приложениями

1. **faq_loader** создает данные для **faq_bot**:
   - Генерирует faq.json
   - Может создавать и обновлять analytics.db

2. **faq_bot** использует данные из **faq_loader**:
   - Загружает faq.json для поиска ответов
   - Использует analytics.db для статистики

## Конфигурация

Каждое приложение использует свой файл `.env` для конфигурации.

## История изменений

Проект был разделен на два независимых приложения и очищен от временных файлов, отчетов и ненужных компонентов. Оставлены только необходимые файлы для работы каждого приложения.