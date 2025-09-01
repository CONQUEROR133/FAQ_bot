using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UniversalFAQLoader.Business.Models;

namespace UniversalFAQLoader.Business.Algorithms
{
    /// <summary>
    /// Базовый интерфейс для всех FAQ алгоритмов
    /// Обеспечивает единообразное управление различными алгоритмическими подходами
    /// </summary>
    public interface IFAQAlgorithm
    {
        /// <summary>
        /// Название алгоритма на русском языке
        /// </summary>
        string DisplayName { get; }
        
        /// <summary>
        /// Описание работы алгоритма
        /// </summary>
        string Description { get; }
        
        /// <summary>
        /// Версия алгоритма для совместимости
        /// </summary>
        Version Version { get; }
        
        /// <summary>
        /// Поддерживаемые типы входных данных
        /// </summary>
        IEnumerable<Type> SupportedInputTypes { get; }
        
        /// <summary>
        /// Асинхронное выполнение алгоритма
        /// </summary>
        /// <param name="context">Контекст выполнения с параметрами</param>
        /// <returns>Результат работы алгоритма</returns>
        Task<AlgorithmResult> ExecuteAsync(AlgorithmContext context);
        
        /// <summary>
        /// Валидация входных данных перед выполнением
        /// </summary>
        /// <param name="context">Контекст для валидации</param>
        /// <returns>Результат валидации</returns>
        ValidationResult Validate(AlgorithmContext context);
        
        /// <summary>
        /// Получение конфигурации алгоритма
        /// </summary>
        /// <returns>Параметры конфигурации</returns>
        AlgorithmConfiguration GetConfiguration();
        
        /// <summary>
        /// Обновление конфигурации алгоритма
        /// </summary>
        /// <param name="configuration">Новая конфигурация</param>
        void UpdateConfiguration(AlgorithmConfiguration configuration);
    }
    
    /// <summary>
    /// Контекст выполнения алгоритма
    /// </summary>
    public class AlgorithmContext
    {
        /// <summary>
        /// Входные FAQ узлы для обработки
        /// </summary>
        public IEnumerable<FAQNode>? InputNodes { get; set; }
        
        /// <summary>
        /// Параметры выполнения алгоритма
        /// </summary>
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Контекст отмены операции
        /// </summary>
        public System.Threading.CancellationToken CancellationToken { get; set; }
        
        /// <summary>
        /// Обратный вызов для отчета о прогрессе
        /// </summary>
        public IProgress<AlgorithmProgress>? ProgressReporter { get; set; }
        
        /// <summary>
        /// Метаданные контекста
        /// </summary>
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Результат выполнения алгоритма
    /// </summary>
    public class AlgorithmResult
    {
        /// <summary>
        /// Обработанные FAQ узлы
        /// </summary>
        public IEnumerable<FAQNode>? ProcessedNodes { get; set; }
        
        /// <summary>
        /// Обнаруженные связи между узлами
        /// </summary>
        public IEnumerable<FAQConnection>? Connections { get; set; }
        
        /// <summary>
        /// Предложения по оптимизации
        /// </summary>
        public IEnumerable<OptimizationSuggestion>? Suggestions { get; set; }
        
        /// <summary>
        /// Общий уровень уверенности в результатах (0.0 - 1.0)
        /// </summary>
        public double OverallConfidence { get; set; }
        
        /// <summary>
        /// Статистика выполнения
        /// </summary>
        public AlgorithmStatistics? Statistics { get; set; }
        
        /// <summary>
        /// Дополнительные данные результата
        /// </summary>
        public Dictionary<string, object> AdditionalData { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Успешность выполнения
        /// </summary>
        public bool IsSuccessful { get; set; }
        
        /// <summary>
        /// Сообщения об ошибках (если есть)
        /// </summary>
        public IEnumerable<string>? ErrorMessages { get; set; }
    }
    
    /// <summary>
    /// Прогресс выполнения алгоритма
    /// </summary>
    public class AlgorithmProgress
    {
        /// <summary>
        /// Процент завершения (0-100)
        /// </summary>
        public int PercentageComplete { get; set; }
        
        /// <summary>
        /// Текущая операция
        /// </summary>
        public string? CurrentOperation { get; set; }
        
        /// <summary>
        /// Обработано элементов
        /// </summary>
        public int ProcessedItems { get; set; }
        
        /// <summary>
        /// Общее количество элементов
        /// </summary>
        public int TotalItems { get; set; }
        
        /// <summary>
        /// Временная метка
        /// </summary>
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
    
    /// <summary>
    /// Результат валидации
    /// </summary>
    public class ValidationResult
    {
        /// <summary>
        /// Валидность входных данных
        /// </summary>
        public bool IsValid { get; set; }
        
        /// <summary>
        /// Сообщения об ошибках валидации
        /// </summary>
        public IEnumerable<string>? ErrorMessages { get; set; }
        
        /// <summary>
        /// Предупреждения
        /// </summary>
        public IEnumerable<string>? Warnings { get; set; }
    }
    
    /// <summary>
    /// Конфигурация алгоритма
    /// </summary>
    public class AlgorithmConfiguration
    {
        /// <summary>
        /// Включен ли алгоритм
        /// </summary>
        public bool IsEnabled { get; set; } = true;
        
        /// <summary>
        /// Параметры конфигурации
        /// </summary>
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Агрегированная статистика выполнения алгоритмов
    /// </summary>
    public class AggregatedStatistics
    {
        /// <summary>
        /// Общее количество обработанных узлов
        /// </summary>
        public int TotalNodesProcessed { get; set; }
        
        /// <summary>
        /// Общее количество найденных связей
        /// </summary>
        public int TotalConnectionsFound { get; set; }
        
        /// <summary>
        /// Общее количество предложений
        /// </summary>
        public int TotalSuggestionsGenerated { get; set; }
        
        /// <summary>
        /// Общее время выполнения всех алгоритмов
        /// </summary>
        public TimeSpan TotalExecutionTime { get; set; }
        
        /// <summary>
        /// Средний уровень уверенности
        /// </summary>
        public double AverageConfidence { get; set; }
        
        /// <summary>
        /// Статистика по каждому алгоритму
        /// </summary>
        public Dictionary<string, AlgorithmStatistics> PerAlgorithmStatistics { get; set; } = new Dictionary<string, AlgorithmStatistics>();
    }
    
    /// <summary>
    /// Статистика выполнения отдельного алгоритма
    /// </summary>
    public class AlgorithmStatistics
    {
        /// <summary>
        /// Количество обработанных узлов
        /// </summary>
        public int ProcessedNodesCount { get; set; }
        
        /// <summary>
        /// Количество найденных связей
        /// </summary>
        public int ConnectionsFound { get; set; }
        
        /// <summary>
        /// Количество сгенерированных предложений
        /// </summary>
        public int SuggestionsGenerated { get; set; }
        
        /// <summary>
        /// Время выполнения
        /// </summary>
        public TimeSpan ExecutionTime { get; set; }
        
        /// <summary>
        /// Использованная память в байтах
        /// </summary>
        public long MemoryUsedBytes { get; set; }
        
        /// <summary>
        /// Дополнительные метрики
        /// </summary>
        public Dictionary<string, object> CustomMetrics { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Предложение по оптимизации
    /// </summary>
    public class OptimizationSuggestion
    {
        /// <summary>
        /// Тип предложения
        /// </summary>
        public SuggestionType Type { get; set; }
        
        /// <summary>
        /// Описание предложения
        /// </summary>
        public string? Description { get; set; }
        
        /// <summary>
        /// Приоритет (1-5, где 5 - наивысший)
        /// </summary>
        public int Priority { get; set; }
        
        /// <summary>
        /// Уровень уверенности (0.0 - 1.0)
        /// </summary>
        public double Confidence { get; set; }
        
        /// <summary>
        /// Затронутые узлы
        /// </summary>
        public IEnumerable<FAQNode>? AffectedNodes { get; set; }
        
        /// <summary>
        /// Предлагаемые действия
        /// </summary>
        public Dictionary<string, object> SuggestedActions { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Дата создания предложения
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
    
    /// <summary>
    /// Тип предложения по оптимизации
    /// </summary>
    public enum SuggestionType
    {
        /// <summary>
        /// Улучшение ответа
        /// </summary>
        ImproveResponse,
        
        /// <summary>
        /// Переформулирование вопроса
        /// </summary>
        RephraseQuestion,
        
        /// <summary>
        /// Добавление ресурсов
        /// </summary>
        AddResources,
        
        /// <summary>
        /// Создание связи
        /// </summary>
        CreateConnection,
        
        /// <summary>
        /// Удаление дубликата
        /// </summary>
        RemoveDuplicate,
        
        /// <summary>
        /// Переструктурирование
        /// </summary>
        Restructure,
        
        /// <summary>
        /// Объединение узлов
        /// </summary>
        MergeNodes
    }
}