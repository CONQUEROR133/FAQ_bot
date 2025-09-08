# FAQ Loader (C# приложение)

C# WPF приложение для управления FAQ записями с интеллектуальной алгоритмической обработкой.

## Основные компоненты

### Business/ - Бизнес-логика
- `FAQAlgorithmService.cs` - Основной сервис алгоритмов
- `DependencyAnalyzer.cs` - Анализ зависимостей между FAQ
- `SemanticGrouper.cs` - Группировка по семантике
- `SmartLinker.cs` - Умная связь между записями
- `ResponseOptimizer.cs` - Оптимизация ответов
- `IFAQAlgorithm.cs` - Интерфейс алгоритмов
- `FAQModels.cs` - Модели данных

### Data/ - Репозитории данных
- `IFAQRepository.cs` - Интерфейс репозитория
- `JsonFAQRepository.cs` - Репозиторий для JSON данных
- `SqliteFAQRepository.cs` - Репозиторий для SQLite
- `HybridFAQRepository.cs` - Гибридный репозиторий

### Presentation/ - WPF UI
- `Views/MainWindow.xaml` - Главное окно приложения
- `ViewModels/MainViewModel.cs` - ViewModel для главного окна
- `Controls/FAQGraphVisualization.xaml` - Контрол для визуализации графа

### Файлы проекта
- `Program.cs` - Точка входа приложения
- `UniversalFAQLoader.csproj` - Проектный файл
- `UniversalFAQLoader.sln` - Файл решения Visual Studio

## Установка и сборка

### Требования:
- .NET 6.0 SDK
- Visual Studio 2022 или новее (для разработки)

### Сборка через командную строку:

```bash
dotnet build
```

### Запуск:

```bash
dotnet run
```

### Запуск через bat-скрипт:

```bash
start_loader.bat
```

## Связи с другими компонентами

Это приложение создает данные, используемые faq_bot (Python Telegram ботом):
- Генерирует faq.json для использования ботом
- Может создавать и обновлять analytics.db

## Подробная документация

Полную документацию по проекту см. в файле [DOCUMENTATION.md](../DOCUMENTATION.md) в корневой директории.