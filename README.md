# Games Project

Этот проект содержит два независимых приложения для управления FAQ системой.

## Структура проекта

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

## Установка

Каждое приложение имеет свои зависимости и устанавливается отдельно:

### Установка Telegram бота

```bash
cd faq_bot
pip install -e .
```

Или установка только зависимостей:

```bash
pip install .
```

### Установка загрузчика FAQ (C#)

Для работы с C# проектом требуется:
- .NET 6.0 SDK
- Visual Studio или Visual Studio Code с расширениями C#

Сборка проекта:
```bash
cd faq_loader
dotnet build
```

## Запуск приложений

### Запуск Telegram бота

```bash
cd faq_bot
python run_bot.py
```

Или через bat-скрипт:

```bash
cd faq_bot
start_bot.bat
```

### Запуск загрузчика FAQ (C#)

```bash
cd faq_loader
dotnet run
```

Или через bat-скрипт:

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

Каждое приложение использует свой файл `.env` для конфигурации. См. документацию каждого приложения для деталей.