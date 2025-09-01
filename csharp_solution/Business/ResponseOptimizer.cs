using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Text.RegularExpressions;
using UniversalFAQLoader.Business.Models;
using UniversalFAQLoader.Business.Algorithms;

namespace UniversalFAQLoader.Business.Algorithms
{
    /// <summary>
    /// Алгоритм оптимизации FAQ ответов
    /// Улучшает качество ответов на основе анализа связей, полноты и ясности
    /// </summary>
    public class ResponseOptimizer : IFAQAlgorithm
    {
        private AlgorithmConfiguration _configuration;
        
        /// <summary>
        /// Название алгоритма на русском языке
        /// </summary>
        public string DisplayName => "⚡ Оптимизация ответов";
        
        /// <summary>
        /// Описание работы алгоритма
        /// </summary>
        public string Description => "Улучшает качество FAQ ответов на основе анализа связей, полноты, ясности и структурированности";
        
        /// <summary>
        /// Версия алгоритма для совместимости
        /// </summary>
        public Version Version => new Version(1, 0, 0);
        
        /// <summary>
        /// Поддерживаемые типы входных данных
        /// </summary>
        public IEnumerable<Type> SupportedInputTypes => new[] { typeof(IEnumerable<FAQNode>) };

        /// <summary>
        /// Инициализирует новый экземпляр класса ResponseOptimizer
        /// </summary>
        public ResponseOptimizer()
        {
            _configuration = new AlgorithmConfiguration
            {
                IsEnabled = true,
                Parameters = new Dictionary<string, object>
                {
                    ["ClarityThreshold"] = 0.7,              // Порог ясности ответа
                    ["CompletenessThreshold"] = 0.65,       // Порог полноты ответа
                    ["StructureThreshold"] = 0.6,           // Порог структурированности
                    ["MinConfidenceForAutoOptimize"] = 0.8, // Минимальная уверенность для автоматической оптимизации
                    ["MaxSuggestionsPerNode"] = 3,          // Максимум предложений на узел
                    ["OptimizationWeights"] = new Dictionary<string, double>
                    {
                        ["ClarityWeight"] = 0.4,            // Вес ясности
                        ["CompletenessWeight"] = 0.3,       // Вес полноты
                        ["StructureWeight"] = 0.2,          // Вес структуры
                        ["RelevanceWeight"] = 0.1           // Вес релевантности
                    }
                }
            };
        }

        /// <summary>
        /// Получение конфигурации алгоритма
        /// </summary>
        /// <returns>Параметры конфигурации</returns>
        public AlgorithmConfiguration GetConfiguration() => _configuration;
        
        /// <summary>
        /// Обновление конфигурации алгоритма
        /// </summary>
        /// <param name="configuration">Новая конфигурация</param>
        public void UpdateConfiguration(AlgorithmConfiguration configuration) => _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));

        /// < <summary>
        /// Валидация входных данных перед выполнением
        /// </summary>
        /// <param name="context">Контекст для валидации</param>
        /// <returns>Результат валидации</returns>
        public ValidationResult Validate(AlgorithmContext context)
        {
            var errors = new List<string>();
            var warnings = new List<string>();

            if (context?.InputNodes == null)
                errors.Add("Входные узлы не могут быть null");

            var nodesList = context?.InputNodes?.ToList();
            if (nodesList?.Count == 0)
                warnings.Add("Список узлов пуст - оптимизация не будет выполнена");

            return new ValidationResult { IsValid = errors.Count == 0, ErrorMessages = errors, Warnings = warnings };
        }

        /// <summary>
        /// Асинхронное выполнение алгоритма
        /// </summary>
        /// <param name="context">Контекст выполнения с параметрами</param>
        /// <returns>Результат работы алгоритма</returns>
        public async Task<AlgorithmResult> ExecuteAsync(AlgorithmContext context)
        {
            var startTime = DateTime.UtcNow;
            var statistics = new AlgorithmStatistics();
            
            try
            {
                var validationResult = Validate(context);
                if (!validationResult.IsValid)
                {
                    return new AlgorithmResult
                    {
                        IsSuccessful = false,
                        ErrorMessages = validationResult.ErrorMessages,
                        Statistics = statistics
                    };
                }

                var nodes = (context.InputNodes ?? Enumerable.Empty<FAQNode>()).ToList();
                statistics.ProcessedNodesCount = nodes.Count;

                var progress = context.ProgressReporter;
                var optimizedNodes = new List<FAQNode>();
                var suggestions = new List<OptimizationSuggestion>();

                // 1. Анализ качества ответов
                progress?.Report(new AlgorithmProgress { CurrentOperation = "Анализ качества ответов...", PercentageComplete = 10 });
                var qualityScores = AnalyzeResponseQuality(nodes, context.CancellationToken).Result;

                // 2. Оптимизация ответов
                progress?.Report(new AlgorithmProgress { CurrentOperation = "Оптимизация ответов...", PercentageComplete = 30 });
                var optimizationResults = await OptimizeResponses(nodes, qualityScores, context.CancellationToken);
                optimizedNodes.AddRange(optimizationResults.optimizedNodes);

                // 3. Генерация предложений по улучшению
                progress?.Report(new AlgorithmProgress { CurrentOperation = "Генерация предложений...", PercentageComplete = 60 });
                var nodeSuggestions = GenerateOptimizationSuggestions(nodes, qualityScores, context.CancellationToken);
                suggestions.AddRange(nodeSuggestions.SelectMany(s => s));

                // 4. Обновление статистики
                progress?.Report(new AlgorithmProgress { CurrentOperation = "Обновление статистики...", PercentageComplete = 90 });
                await UpdateQualityStatistics(nodes, qualityScores);

                var executionTime = DateTime.UtcNow - startTime;
                statistics.ExecutionTime = executionTime;
                statistics.MemoryUsedBytes = GC.GetTotalMemory(false);
                statistics.CustomMetrics = new Dictionary<string, object>
                {
                    ["ResponsesOptimized"] = optimizationResults.optimizedCount,
                    ["AutoOptimized"] = optimizationResults.autoOptimizedCount,
                    ["ManualSuggestions"] = suggestions.Count(s => s.Priority >= 3),
                    ["AverageQualityScore"] = qualityScores.Any() ? qualityScores.Average(q => q.overallScore) : 0.0,
                    ["QualityImprovements"] = optimizationResults.qualityImprovements
                };

                progress?.Report(new AlgorithmProgress { CurrentOperation = "Оптимизация завершена!", PercentageComplete = 100, ProcessedItems = nodes.Count });

                var overallConfidence = qualityScores.Any() ? qualityScores.Average(q => q.overallScore) : 0.0;

                return new AlgorithmResult
                {
                    IsSuccessful = true,
                    ProcessedNodes = optimizedNodes.Any() ? optimizedNodes : nodes,
                    Suggestions = suggestions,
                    OverallConfidence = overallConfidence,
                    Statistics = statistics
                };
            }
            catch (Exception ex)
            {
                statistics.ExecutionTime = DateTime.UtcNow - startTime;
                return new AlgorithmResult { IsSuccessful = false, ErrorMessages = new[] { ex.Message }, Statistics = statistics };
            }
        }

        /// <summary>
        /// Анализ качества ответов
        /// </summary>
        /// <param name="nodes">Список узлов для анализа</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список оценок качества для каждого узла</returns>
        private Task<List<(FAQNode node, double clarity, double completeness, double structure, double relevance, double overallScore)>> 
            AnalyzeResponseQuality(List<FAQNode> nodes, System.Threading.CancellationToken cancellationToken)
        {
            var qualityScores = new List<(FAQNode node, double clarity, double completeness, double structure, double relevance, double overallScore)>();

            foreach (var node in nodes)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var clarity = AnalyzeClarity(node);
                var completeness = AnalyzeCompleteness(node);
                var structure = AnalyzeStructure(node);
                var relevance = AnalyzeRelevance(node);

                var weights = (Dictionary<string, double>)_configuration.Parameters["OptimizationWeights"];
                var overallScore = (clarity * weights["ClarityWeight"]) +
                                 (completeness * weights["CompletenessWeight"]) +
                                 (structure * weights["StructureWeight"]) +
                                 (relevance * weights["RelevanceWeight"]);

                qualityScores.Add((node, clarity, completeness, structure, relevance, overallScore));
            }

            return Task.FromResult(qualityScores);
        }

        /// <summary>
        /// Анализ полноты ответа
        /// </summary>
        /// <param name="node">Узел для анализа</param>
        /// <returns>Оценка полноты ответа (0.0 - 1.0)</returns>
        private double AnalyzeCompleteness(FAQNode node)
        {
            var score = 0.0;

            // 1. Наличие ответа
            if (!string.IsNullOrWhiteSpace(node.Response))
                score += 0.3;

            // 2. Наличие ресурсов
            if (node.Resources?.Any() == true)
                score += 0.2;

            // 3. Наличие вариаций вопроса
            if (node.Variations?.Any() == true)
                score += 0.1;

            // 4. Длина ответа (минимум 50 символов)
            if ((node.Response?.Length ?? 0) > 50)
                score += 0.2;

            // 5. Структурированность (наличие пунктов, заголовков)
            if (!string.IsNullOrWhiteSpace(node.Response) && HasStructuredElements(node.Response))
                score += 0.2;

            return score;
        }

        /// <summary>
        /// Анализ структурированности ответа
        /// </summary>
        /// <param name="node">Узел для анализа</param>
        /// <returns>Оценка структурированности ответа (0.0 - 1.0)</returns>
        private double AnalyzeStructure(FAQNode node)
        {
            if (string.IsNullOrWhiteSpace(node.Response))
                return 0.0;

            var score = 0.0;

            // 1. Наличие абзацев
            var paragraphs = node.Response.Split(new[] { "\n\n", "\r\n\r\n" }, StringSplitOptions.RemoveEmptyEntries);
            score += Math.Min(paragraphs.Length / 3.0, 0.3);

            // 2. Наличие списков
            if (node.Response.Contains("\n-") || node.Response.Contains("\n*") || node.Response.Contains("\n•"))
                score += 0.2;

            // 3. Наличие заголовков
            if (Regex.IsMatch(node.Response, @"^\s*[A-ZА-Я].*[:\r\n]", RegexOptions.Multiline))
                score += 0.2;

            // 4. Наличие нумерованных списков
            if (Regex.IsMatch(node.Response, @"\d+\.\s"))
                score += 0.15;

            // 5. Наличие ссылок или файлов
            if (node.Resources?.Any() == true)
                score += 0.15;

            return Math.Min(1.0, score);
        }

        /// <summary>
        /// Анализ релевантности ответа
        /// </summary>
        /// <param name="node">Узел для анализа</param>
        /// <returns>Оценка релевантности ответа (0.0 - 1.0)</returns>
        private double AnalyzeRelevance(FAQNode node)
        {
            // Релевантность определяется по популярности и частоте обращений
            var accessCount = node.Metadata.AccessCount;
            var usefulness = node.Metadata.Usefulness;

            // Нормализуем популярность (до 100 обращений = максимальная популярность)
            var popularityScore = Math.Min(accessCount / 100.0, 1.0);
            
            // Комбинируем с полезностью
            return (popularityScore * 0.7) + (usefulness * 0.3);
        }

        /// <summary>
        /// Оптимизация ответов
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="qualityScores">Оценки качества узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Результаты оптимизации</returns>
        private async Task<(List<FAQNode> optimizedNodes, int optimizedCount, int autoOptimizedCount, double qualityImprovements)> 
            OptimizeResponses(
                List<FAQNode> nodes, 
                List<(FAQNode node, double clarity, double completeness, double structure, double relevance, double overallScore)> qualityScores,
                System.Threading.CancellationToken cancellationToken)
        {
            var optimizedNodes = new List<FAQNode>();
            var optimizedCount = 0;
            var autoOptimizedCount = 0;
            var qualityImprovements = 0.0;
            var minConfidence = (double)_configuration.Parameters["MinConfidenceForAutoOptimize"];

            foreach (var (node, clarity, completeness, structure, relevance, overallScore) in qualityScores)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var improvementsMade = false;
                var originalScore = overallScore;

                // Автоматическая оптимизация при высокой уверенности
                if (overallScore < minConfidence)
                {
                    var improvedResponse = AutoOptimizeResponse(node, clarity, completeness, structure).Result;
                    if (improvedResponse != node.Response)
                    {
                        node.Response = improvedResponse;
                        autoOptimizedCount++;
                        improvementsMade = true;
                    }
                }

                // Улучшение структуры при необходимости
                if (structure < 0.5)
                {
                    node.Response = ImproveStructure(node.Response);
                    improvementsMade = true;
                }

                // Добавление связанных ресурсов при низкой полноте
                if (completeness < 0.5 && node.Resources?.Any() == true)
                {
                    node.Response = AddResourceReferences(node.Response, node.Resources);
                    improvementsMade = true;
                }

                if (improvementsMade)
                {
                    optimizedCount++;
                    var newScores = AnalyzeResponseQuality(new List<FAQNode> { node }, cancellationToken).Result;
                    var newScore = newScores.First().overallScore;
                    qualityImprovements += (newScore - originalScore);
                }

                optimizedNodes.Add(node);
            }

            return (optimizedNodes, optimizedCount, autoOptimizedCount, qualityImprovements);
        }

        /// <summary>
        /// Автоматическая оптимизация ответа
        /// </summary>
        /// <param name="node">Узел для оптимизации</param>
        /// <param name="clarity">Оценка ясности</param>
        /// <param name="completeness">Оценка полноты</param>
        /// <param name="structure">Оценка структурированности</param>
        /// <returns>Оптимизированный ответ</returns>
        private Task<string> AutoOptimizeResponse(FAQNode node, double clarity, double completeness, double structure)
        {
            var response = node.Response ?? "";

            // Улучшаем ясность при низкой оценке
            if (clarity < 0.5)
            {
                response = ImproveClarity(response);
            }

            // Добавляем элементы полноты при необходимости
            if (completeness < 0.5)
            {
                response = ImproveCompleteness(response, node);
            }

            return Task.FromResult(response);
        }

        /// <summary>
        /// Генерация предложений по оптимизации
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="qualityScores">Оценки качества узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список предложений по оптимизации</returns>
        private List<List<OptimizationSuggestion>> GenerateOptimizationSuggestions(
            List<FAQNode> nodes,
            List<(FAQNode node, double clarity, double completeness, double structure, double relevance, double overallScore)> qualityScores,
            System.Threading.CancellationToken cancellationToken)
        {
            var allSuggestions = new List<List<OptimizationSuggestion>>();
            var maxSuggestions = (int)_configuration.Parameters["MaxSuggestionsPerNode"];

            foreach (var (node, clarity, completeness, structure, relevance, overallScore) in qualityScores)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var nodeSuggestions = new List<OptimizationSuggestion>();

                // Предложения по улучшению ясности
                if (clarity < 0.6)
                {
                    nodeSuggestions.Add(new OptimizationSuggestion
                    {
                        Type = SuggestionType.ImproveResponse,
                        Description = $"Ответ на '{node.Query}' требует улучшения ясности (оценка: {clarity:P1})",
                        Priority = clarity < 0.4 ? 4 : 3,
                        Confidence = 1.0 - clarity,
                        AffectedNodes = new[] { node },
                        SuggestedActions = new Dictionary<string, object>
                        {
                            ["Action"] = "ImproveClarity",
                            ["NodeId"] = node.Id,
                            ["SuggestedImprovements"] = GenerateClarityImprovements(node.Response)
                        }
                    });
                }

                // Предложения по улучшению полноты
                if (completeness < 0.6)
                {
                    nodeSuggestions.Add(new OptimizationSuggestion
                    {
                        Type = SuggestionType.ImproveResponse,
                        Description = $"Ответ на '{node.Query}' требует дополнения (полнота: {completeness:P1})",
                        Priority = completeness < 0.4 ? 4 : 3,
                        Confidence = 1.0 - completeness,
                        AffectedNodes = new[] { node },
                        SuggestedActions = new Dictionary<string, object>
                        {
                            ["Action"] = "ImproveCompleteness",
                            ["NodeId"] = node.Id,
                            ["MissingElements"] = IdentifyMissingElements(node)
                        }
                    });
                }

                // Предложения по улучшению структуры
                if (structure < 0.5)
                {
                    nodeSuggestions.Add(new OptimizationSuggestion
                    {
                        Type = SuggestionType.Restructure,
                        Description = $"Ответ на '{node.Query}' требует структурирования (оценка: {structure:P1})",
                        Priority = 3,
                        Confidence = 1.0 - structure,
                        AffectedNodes = new[] { node },
                        SuggestedActions = new Dictionary<string, object>
                        {
                            ["Action"] = "RestructureResponse",
                            ["NodeId"] = node.Id,
                            ["SuggestedStructure"] = GenerateSuggestedStructure(node.Response)
                        }
                    });
                }

                // Ограничиваем количество предложений на узел
                allSuggestions.Add(nodeSuggestions.Take(maxSuggestions).ToList());
            }

            return allSuggestions;
        }

        #region Quality Analysis Methods

        /// <summary>
        /// Анализ ясности ответа
        /// </summary>
        /// <param name="node">Узел для анализа</param>
        /// <returns>Оценка ясности ответа (0.0 - 1.0)</returns>
        private double AnalyzeClarity(FAQNode node)
        {
            if (string.IsNullOrWhiteSpace(node.Response))
                return 0.0;

            var score = 1.0;

            // 1. Проверка на сложные предложения
            var sentenceComplexity = CalculateSentenceComplexity(node.Response);
            score -= sentenceComplexity * 0.3;

            // 2. Проверка на технический жаргон
            var jargonCount = CountTechnicalJargon(node.Response);
            score -= Math.Min(jargonCount / 10.0, 0.4);

            // 3. Проверка на двусмысленность
            var ambiguityScore = DetectAmbiguity(node.Response);
            score -= ambiguityScore * 0.3;

            return Math.Max(0.0, Math.Min(1.0, score));
        }

        #endregion

        #region Optimization Methods

        /// <summary>
        /// Улучшение ясности ответа
        /// </summary>
        /// <param name="response">Ответ для улучшения</param>
        /// <returns>Улучшенный ответ</returns>
        private string ImproveClarity(string response)
        {
            if (string.IsNullOrWhiteSpace(response))
                return "Ответ на ваш вопрос...";

            // Разбиваем на более простые предложения
            var sentences = Regex.Split(response, @"(?<=[\.!?])\s+")
                                .Where(s => !string.IsNullOrWhiteSpace(s))
                                .ToList();

            var improvedSentences = new List<string>();
            foreach (var sentence in sentences)
            {
                // Упрощаем сложные предложения
                var simplified = SimplifyComplexSentence(sentence);
                improvedSentences.Add(simplified);
            }

            return string.Join(" ", improvedSentences);
        }

        /// <summary>
        /// Улучшение полноты ответа
        /// </summary>
        /// <param name="response">Ответ для улучшения</param>
        /// <param name="node">Узел с дополнительной информацией</param>
        /// <returns>Улучшенный ответ</returns>
        private string ImproveCompleteness(string response, FAQNode node)
        {
            if (string.IsNullOrWhiteSpace(response))
                response = "По вашему запросу предоставлена следующая информация:";

            // Добавляем ссылки на ресурсы
            if (node.Resources?.Any() == true)
            {
                response = AddResourceReferences(response, node.Resources);
            }

            // Добавляем вариации вопроса
            if (node.Variations?.Any() == true)
            {
                response = $"Также могут быть полезны следующие вопросы:\n{string.Join("\n", node.Variations.Select(v => $"- {v}"))}\n\n{response}";
            }

            return response;
        }

        /// <summary>
        /// Улучшение структуры ответа
        /// </summary>
        /// <param name="response">Ответ для улучшения</param>
        /// <returns>Ответ с улучшенной структурой</returns>
        private string ImproveStructure(string response)
        {
            if (string.IsNullOrWhiteSpace(response))
                return "";

            // Добавляем структуру если её нет
            if (!HasStructuredElements(response))
            {
                // Простое структурирование: добавляем заголовки
                return $"## Ответ\n\n{response}\n\n## Дополнительная информация\n\nСм. прикрепленные файлы и ресурсы.";
            }

            return response;
        }

        /// <summary>
        /// Добавление ссылок на ресурсы в ответ
        /// </summary>
        /// <param name="response">Ответ для улучшения</param>
        /// <param name="resources">Список ресурсов</param>
        /// <returns>Ответ с добавленными ссылками на ресурсы</returns>
        private string AddResourceReferences(string response, List<FAQResource> resources)
        {
            if (resources?.Any() != true)
                return response;

            var resourceText = "\n\n**Прикрепленные материалы:**\n";
            foreach (var resource in resources)
            {
                if (resource.Files?.Any() == true)
                {
                    resourceText += $"- Файлы: {string.Join(", ", resource.Files)}\n";
                }
                if (!string.IsNullOrWhiteSpace(resource.Link))
                {
                    resourceText += $"- Ссылка: {resource.Link}\n";
                }
            }

            return $"{response}{resourceText}";
        }

        #endregion

        #region Helper Methods

        /// <summary>
        /// Расчет сложности предложений
        /// </summary>
        /// <param name="text">Текст для анализа</param>
        /// <returns>Оценка сложности предложений (0.0 - 1.0)</returns>
        private double CalculateSentenceComplexity(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return 1.0;

            var sentences = Regex.Split(text, @"(?<=[\.!?])\s+")
                                .Where(s => !string.IsNullOrWhiteSpace(s))
                                .ToList();

            if (!sentences.Any())
                return 1.0;

            var totalComplexity = 0.0;
            foreach (var sentence in sentences)
            {
                // Сложность по количеству слов
                var wordCount = Regex.Split(sentence, @"\s+").Length;
                var wordComplexity = Math.Min(wordCount / 20.0, 1.0);

                // Сложность по количеству запятых (подчиненные конструкции)
                var commaCount = sentence.Count(c => c == ',');
                var commaComplexity = Math.Min(commaCount / 5.0, 1.0);

                totalComplexity += (wordComplexity + commaComplexity) / 2.0;
            }

            return totalComplexity / sentences.Count;
        }

        /// <summary>
        /// Подсчет технического жаргона в тексте
        /// </summary>
        /// <param name="text">Текст для анализа</param>
        /// <returns>Количество технических терминов</returns>
        private int CountTechnicalJargon(string text)
        {
            var jargonTerms = new HashSet<string>
            {
                "инициализация", "конфигурация", "параметризация", "деплой", "деплоить",
                "имплементация", "реализация", "интеграция", "оптимизация", "рефакторинг",
                "ассинхронный", "синхронизация", "кэширование", "репликация"
            };

            var count = 0;
            var lowerText = text.ToLowerInvariant();

            foreach (var term in jargonTerms)
            {
                if (lowerText.Contains(term))
                    count++;
            }

            return count;
        }

        /// <summary>
        /// Обнаружение двусмысленности в тексте
        /// </summary>
        /// <param name="text">Текст для анализа</param>
        /// <returns>Оценка двусмысленности (0.0 - 1.0)</returns>
        private double DetectAmbiguity(string text)
        {
            var ambiguousPhrases = new[]
            {
                "иногда", "обычно", "как правило", "в большинстве случаев",
                "примерно", "приблизительно", "около", "возможно", "может быть"
            };

            var count = ambiguousPhrases.Count(phrase => text.ToLowerInvariant().Contains(phrase));
            return Math.Min(count / 5.0, 1.0);
        }

        /// <summary>
        /// Проверка наличия структурированных элементов в тексте
        /// </summary>
        /// <param name="text">Текст для анализа</param>
        /// <returns>True, если текст содержит структурированные элементы</returns>
        private bool HasStructuredElements(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return false;

            return text.Contains("\n-") || 
                   text.Contains("\n*") || 
                   text.Contains("\n•") ||
                   Regex.IsMatch(text, @"\d+\.\s") ||
                   Regex.IsMatch(text, @"^\s*[A-ZА-Я].*[:\r\n]", RegexOptions.Multiline);
        }

        /// <summary>
        /// Упрощение сложного предложения
        /// </summary>
        /// <param name="sentence">Предложение для упрощения</param>
        /// <returns>Упрощенное предложение</returns>
        private string SimplifyComplexSentence(string sentence)
        {
            // Простое упрощение: убираем подчиненные конструкции в скобках
            return Regex.Replace(sentence, @"\s*\([^)]+\)", "");
        }

        /// <summary>
        /// Генерация предложений по улучшению ясности
        /// </summary>
        /// <param name="response">Ответ для анализа</param>
        /// <returns>Список предложений по улучшению</returns>
        private List<string> GenerateClarityImprovements(string response)
        {
            var improvements = new List<string>();

            if (CalculateSentenceComplexity(response) > 0.6)
                improvements.Add("Разбить сложные предложения на более простые");

            if (CountTechnicalJargon(response) > 3)
                improvements.Add("Заменить технический жаргон на понятные формулировки");

            if (DetectAmbiguity(response) > 0.4)
                improvements.Add("Уточнить неоднозначные формулировки");

            if (!improvements.Any())
                improvements.Add("Ответ достаточно понятный");

            return improvements;
        }

        /// <summary>
        /// Идентификация отсутствующих элементов в узле
        /// </summary>
        /// <param name="node">Узел для анализа</param>
        /// <returns>Список отсутствующих элементов</returns>
        private List<string> IdentifyMissingElements(FAQNode node)
        {
            var missing = new List<string>();

            if (string.IsNullOrWhiteSpace(node.Response))
                missing.Add("Основной ответ на вопрос");

            if (node.Resources?.Any() != true)
                missing.Add("Ссылки на дополнительные материалы");

            if (node.Variations?.Any() != true)
                missing.Add("Варианты формулировок вопроса");

            if ((node.Response?.Length ?? 0) < 50)
                missing.Add("Более полное содержание ответа");

            return missing;
        }

        /// <summary>
        /// Генерация предлагаемой структуры ответа
        /// </summary>
        /// <param name="response">Ответ для анализа</param>
        /// <returns>Предлагаемая структура ответа</returns>
        private Dictionary<string, object> GenerateSuggestedStructure(string response)
        {
            return new Dictionary<string, object>
            {
                ["StructureType"] = "FAQ_Response",
                ["Sections"] = new[]
                {
                    new { Name = "Ответ на вопрос", Content = "Краткий и точный ответ" },
                    new { Name = "Подробное объяснение", Content = "Развернутое объяснение с примерами" },
                    new { Name = "Дополнительные материалы", Content = "Ссылки и файлы" }
                }
            };
        }

        /// <summary>
        /// Обновление статистики качества узлов
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="qualityScores">Оценки качества узлов</param>
        private Task UpdateQualityStatistics(List<FAQNode> nodes, 
            List<(FAQNode node, double clarity, double completeness, double structure, double relevance, double overallScore)> qualityScores)
        {
            foreach (var (node, clarity, completeness, structure, relevance, overallScore) in qualityScores)
            {
                // Обновляем алгоритмические свойства узла
                node.AlgorithmProps.ComplexityScore = overallScore;
                node.AlgorithmProps.Language.TextLength = node.Response?.Length ?? 0;
                
                // Обновляем метаданные
                node.Metadata.ExtendedProperties["QualityScore"] = overallScore;
                node.Metadata.ExtendedProperties["ClarityScore"] = clarity;
                node.Metadata.ExtendedProperties["CompletenessScore"] = completeness;
                node.Metadata.ExtendedProperties["StructureScore"] = structure;
            }
            
            return Task.CompletedTask;
        }

        #endregion
    }
}