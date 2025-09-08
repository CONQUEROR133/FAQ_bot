using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Threading;
using UniversalFAQLoader.Business.Models;
using UniversalFAQLoader.Business.Algorithms;

namespace UniversalFAQLoader.Business.Services
{
    /// <summary>
    /// Сервис управления алгоритмами FAQ
    /// Оркестрирует выполнение всех алгоритмов и управляет их конфигурацией
    /// </summary>
    public class FAQAlgorithmService
    {
        private readonly List<IFAQAlgorithm> _algorithms;
        private readonly Dictionary<string, AlgorithmConfiguration> _configurations;
        private readonly Dictionary<string, bool> _algorithmStatus;

        /// <summary>
        /// Инициализирует новый экземпляр класса FAQAlgorithmService
        /// </summary>
        public FAQAlgorithmService()
        {
            _algorithms = new List<IFAQAlgorithm>
            {
                new DependencyAnalyzer(),
                new SemanticGrouper(),
                new SmartLinker(),
                new ResponseOptimizer()
            };

            _configurations = new Dictionary<string, AlgorithmConfiguration>();
            _algorithmStatus = new Dictionary<string, bool>();

            // Инициализация конфигураций по умолчанию
            InitializeDefaultConfigurations();
        }

        /// <summary>
        /// Инициализация конфигураций по умолчанию
        /// </summary>
        private void InitializeDefaultConfigurations()
        {
            foreach (var algorithm in _algorithms)
            {
                _configurations[algorithm.DisplayName] = algorithm.GetConfiguration();
                _algorithmStatus[algorithm.DisplayName] = algorithm.GetConfiguration().IsEnabled;
            }
        }

        /// <summary>
        /// Получение списка всех алгоритмов
        /// </summary>
        /// <returns>Список всех алгоритмов</returns>
        public IEnumerable<IFAQAlgorithm> GetAllAlgorithms()
        {
            return _algorithms.AsReadOnly();
        }

        /// <summary>
        /// Получение активных алгоритмов
        /// </summary>
        /// <returns>Список активных алгоритмов</returns>
        public IEnumerable<IFAQAlgorithm> GetActiveAlgorithms()
        {
            return _algorithms.Where(a => _algorithmStatus[a.DisplayName]);
        }

        /// <summary>
        /// Получение конфигурации алгоритма
        /// </summary>
        /// <param name="algorithmName">Название алгоритма</param>
        /// <returns>Конфигурация алгоритма или null, если не найдена</returns>
        public AlgorithmConfiguration? GetAlgorithmConfiguration(string algorithmName)
        {
            return _configurations.ContainsKey(algorithmName) ? _configurations[algorithmName] : null;
        }

        /// <summary>
        /// Обновление конфигурации алгоритма
        /// </summary>
        /// <param name="algorithmName">Название алгоритма</param>
        /// <param name="configuration">Новая конфигурация</param>
        public void UpdateAlgorithmConfiguration(string algorithmName, AlgorithmConfiguration configuration)
        {
            if (_configurations.ContainsKey(algorithmName))
            {
                _configurations[algorithmName] = configuration ?? throw new ArgumentNullException(nameof(configuration));
                
                // Обновляем конфигурацию в самом алгоритме
                var algorithm = _algorithms.FirstOrDefault(a => a.DisplayName == algorithmName);
                algorithm?.UpdateConfiguration(configuration);
            }
        }

        /// <summary>
        /// Включение/выключение алгоритма
        /// </summary>
        /// <param name="algorithmName">Название алгоритма</param>
        /// <param name="isEnabled">Статус включения алгоритма</param>
        public void SetAlgorithmStatus(string algorithmName, bool isEnabled)
        {
            if (_algorithmStatus.ContainsKey(algorithmName))
            {
                _algorithmStatus[algorithmName] = isEnabled;
                
                // Обновляем статус в конфигурации
                if (_configurations.ContainsKey(algorithmName))
                {
                    _configurations[algorithmName].IsEnabled = isEnabled;
                    var algorithm = _algorithms.FirstOrDefault(a => a.DisplayName == algorithmName);
                    algorithm?.UpdateConfiguration(_configurations[algorithmName]);
                }
            }
        }

        /// <summary>
        /// Выполнение всех активных алгоритмов
        /// </summary>
        /// <param name="nodes">Список узлов для обработки</param>
        /// <param name="progress">Прогресс выполнения</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Результат выполнения всех алгоритмов</returns>
        public async Task<AlgorithmExecutionResult> ExecuteAllAlgorithmsAsync(
            IEnumerable<FAQNode> nodes, 
            IProgress<AlgorithmProgress>? progress = null,
            CancellationToken cancellationToken = default)
        {
            var results = new List<AlgorithmResult>();
            var allConnections = new List<FAQConnection>();
            var allSuggestions = new List<OptimizationSuggestion>();
            var statistics = new List<AlgorithmStatistics>();

            var activeAlgorithms = GetActiveAlgorithms().ToList();
            var totalAlgorithms = activeAlgorithms.Count;
            var completedAlgorithms = 0;

            foreach (var algorithm in activeAlgorithms)
            {
                cancellationToken.ThrowIfCancellationRequested();

                // Обновляем прогресс
                progress?.Report(new AlgorithmProgress
                {
                    CurrentOperation = $"Выполняем: {algorithm.DisplayName}",
                    PercentageComplete = (completedAlgorithms * 100) / totalAlgorithms,
                    TotalItems = totalAlgorithms,
                    ProcessedItems = completedAlgorithms
                });

                try
                {
                    var context = new AlgorithmContext
                    {
                        InputNodes = nodes,
                        Parameters = _configurations[algorithm.DisplayName].Parameters,
                        CancellationToken = cancellationToken,
                        ProgressReporter = progress
                    };

                    var result = await algorithm.ExecuteAsync(context);
                    results.Add(result);

                    if (result.IsSuccessful)
                    {
                        // Собираем результаты
                        if (result.Connections != null)
                            allConnections.AddRange(result.Connections);

                        if (result.Suggestions != null)
                            allSuggestions.AddRange(result.Suggestions);

                        if (result.Statistics != null)
                            statistics.Add(result.Statistics);
                    }
                }
                catch (Exception ex)
                {
                    // Добавляем результат с ошибкой
                    results.Add(new AlgorithmResult
                    {
                        IsSuccessful = false,
                        ErrorMessages = new[] { $"Ошибка в алгоритме {algorithm.DisplayName}: {ex.Message}" },
                        Statistics = new AlgorithmStatistics()
                    });
                }

                completedAlgorithms++;
            }

            // Финальный прогресс
            progress?.Report(new AlgorithmProgress
            {
                CurrentOperation = "Все алгоритмы выполнены",
                PercentageComplete = 100,
                TotalItems = totalAlgorithms,
                ProcessedItems = completedAlgorithms
            });

            return new AlgorithmExecutionResult
            {
                Results = results,
                AllConnections = allConnections,
                AllSuggestions = allSuggestions,
                AggregatedStatistics = AggregateStatistics(statistics),
                OverallSuccess = results.All(r => r.IsSuccessful),
                ExecutionTime = statistics.Any() ? statistics.Max(s => s.ExecutionTime) : TimeSpan.Zero
            };
        }

        /// <summary>
        /// Выполнение конкретного алгоритма
        /// </summary>
        /// <param name="algorithmName">Название алгоритма</param>
        /// <param name="nodes">Список узлов для обработки</param>
        /// <param name="progress">Прогресс выполнения</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Результат выполнения алгоритма</returns>
        public async Task<AlgorithmResult> ExecuteAlgorithmAsync(
            string algorithmName,
            IEnumerable<FAQNode> nodes,
            IProgress<AlgorithmProgress>? progress = null,
            CancellationToken cancellationToken = default)
        {
            var algorithm = _algorithms.FirstOrDefault(a => a.DisplayName == algorithmName);
            if (algorithm == null)
            {
                return new AlgorithmResult
                {
                    IsSuccessful = false,
                    ErrorMessages = new[] { $"Алгоритм '{algorithmName}' не найден" }
                };
            }

            if (!_algorithmStatus[algorithmName])
            {
                return new AlgorithmResult
                {
                    IsSuccessful = false,
                    ErrorMessages = new[] { $"Алгоритм '{algorithmName}' отключен" }
                };
            }

            var context = new AlgorithmContext
            {
                InputNodes = nodes,
                Parameters = _configurations[algorithmName].Parameters,
                CancellationToken = cancellationToken,
                ProgressReporter = progress
            };

            return await algorithm.ExecuteAsync(context);
        }

        /// <summary>
        /// Агрегация статистики из всех алгоритмов
        /// </summary>
        /// <param name="statistics">Список статистик алгоритмов</param>
        /// <returns>Агрегированная статистика</returns>
        private AggregatedStatistics AggregateStatistics(List<AlgorithmStatistics> statistics)
        {
            if (!statistics.Any())
            {
                return new AggregatedStatistics();
            }

            return new AggregatedStatistics
            {
                TotalExecutionTime = TimeSpan.FromTicks(statistics.Sum(s => s.ExecutionTime.Ticks)),
                TotalNodesProcessed = statistics.Sum(s => s.ProcessedNodesCount),
                TotalConnectionsFound = statistics.Sum(s => s.ConnectionsFound),
                TotalMemoryUsed = statistics.Sum(s => s.MemoryUsedBytes),
                AverageExecutionTime = TimeSpan.FromTicks((long)statistics.Average(s => s.ExecutionTime.Ticks)),
                CustomMetrics = MergeCustomMetrics(statistics.Select(s => s.CustomMetrics))
            };
        }

        /// <summary>
        /// Объединение пользовательских метрик
        /// </summary>
        /// <param name="metrics">Список пользовательских метрик</param>
        /// <returns>Объединенные метрики</returns>
        private Dictionary<string, object> MergeCustomMetrics(IEnumerable<Dictionary<string, object>?> metrics)
        {
            var merged = new Dictionary<string, object>();

            foreach (var metricDict in metrics)
            {
                if (metricDict != null)
                {
                    foreach (var kvp in metricDict)
                    {
                        if (merged.ContainsKey(kvp.Key))
                        {
                            // Если ключ уже существует, суммируем числовые значения
                            if (merged[kvp.Key] is int existingInt && kvp.Value is int newInt)
                            {
                                merged[kvp.Key] = existingInt + newInt;
                            }
                            else if (merged[kvp.Key] is double existingDouble && kvp.Value is double newDouble)
                            {
                                merged[kvp.Key] = existingDouble + newDouble;
                            }
                            // Для других типов оставляем первое значение
                        }
                        else
                        {
                            merged[kvp.Key] = kvp.Value;
                        }
                    }
                }
            }

            return merged;
        }

        /// <summary>
        /// Получение рекомендаций по оптимизации от всех алгоритмов
        /// </summary>
        /// <param name="nodes">Список узлов для анализа</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список рекомендаций по оптимизации</returns>
        public async Task<IEnumerable<OptimizationSuggestion>> GetOptimizationSuggestionsAsync(
            IEnumerable<FAQNode> nodes,
            CancellationToken cancellationToken = default)
        {
            var allSuggestions = new List<OptimizationSuggestion>();

            foreach (var algorithm in GetActiveAlgorithms())
            {
                cancellationToken.ThrowIfCancellationRequested();

                try
                {
                    var context = new AlgorithmContext
                    {
                        InputNodes = nodes,
                        Parameters = _configurations[algorithm.DisplayName].Parameters,
                        CancellationToken = cancellationToken
                    };

                    var result = await algorithm.ExecuteAsync(context);
                    if (result.IsSuccessful && result.Suggestions != null)
                    {
                        allSuggestions.AddRange(result.Suggestions);
                    }
                }
                catch
                {
                    // Игнорируем ошибки отдельных алгоритмов
                }
            }

            return allSuggestions.OrderByDescending(s => s.Priority)
                                .ThenByDescending(s => s.Confidence);
        }

        /// <summary>
        /// Валидация входных данных для всех активных алгоритмов
        /// </summary>
        /// <param name="context">Контекст для валидации</param>
        /// <returns>Список результатов валидации</returns>
        public IEnumerable<ValidationResult> ValidateAllAlgorithms(AlgorithmContext context)
        {
            var results = new List<ValidationResult>();

            foreach (var algorithm in GetActiveAlgorithms())
            {
                var result = algorithm.Validate(context);
                results.Add(result);
            }

            return results;
        }
    }

    /// <summary>
    /// Результат выполнения всех алгоритмов
    /// </summary>
    public class AlgorithmExecutionResult
    {
        /// <summary>
        /// Результаты выполнения каждого алгоритма
        /// </summary>
        public IEnumerable<AlgorithmResult> Results { get; set; } = new List<AlgorithmResult>();

        /// <summary>
        /// Все найденные связи
        /// </summary>
        public IEnumerable<FAQConnection> AllConnections { get; set; } = new List<FAQConnection>();

        /// <summary>
        /// Все предложения по оптимизации
        /// </summary>
        public IEnumerable<OptimizationSuggestion> AllSuggestions { get; set; } = new List<OptimizationSuggestion>();

        /// <summary>
        /// Агрегированная статистика
        /// </summary>
        public AggregatedStatistics AggregatedStatistics { get; set; } = new AggregatedStatistics();

        /// <summary>
        /// Общий успех выполнения
        /// </summary>
        public bool OverallSuccess { get; set; }

        /// <summary>
        /// Общее время выполнения
        /// </summary>
        public TimeSpan ExecutionTime { get; set; }
    }

    /// <summary>
    /// Агрегированная статистика
    /// </summary>
    public class AggregatedStatistics
    {
        /// <summary>
        /// Общее время выполнения
        /// </summary>
        public TimeSpan TotalExecutionTime { get; set; }

        /// <summary>
        /// Общее количество обработанных узлов
        /// </summary>
        public int TotalNodesProcessed { get; set; }

        /// <summary>
        /// Общее количество найденных связей
        /// </summary>
        public int TotalConnectionsFound { get; set; }

        /// <summary>
        /// Общее использование памяти
        /// </summary>
        public long TotalMemoryUsed { get; set; }

        /// <summary>
        /// Среднее время выполнения
        /// </summary>
        public TimeSpan AverageExecutionTime { get; set; }

        /// <summary>
        /// Пользовательские метрики
        /// </summary>
        public Dictionary<string, object> CustomMetrics { get; set; } = new Dictionary<string, object>();
    }
}