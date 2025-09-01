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
    /// Алгоритм умного связывания FAQ записей
    /// Создает интеллектуальные связи: пререквизиты, продолжения, связанные темы
    /// </summary>
    public class SmartLinker : IFAQAlgorithm
    {
        private AlgorithmConfiguration _configuration;
        
        /// <summary>
        /// Название алгоритма на русском языке
        /// </summary>
        public string DisplayName => "🔗 Умное связывание";
        
        /// <summary>
        /// Описание работы алгоритма
        /// </summary>
        public string Description => "Создает интеллектуальные связи между FAQ записями: пререквизиты, продолжения, связанные темы и противоречия";
        
        /// <summary>
        /// Версия алгоритма для совместимости
        /// </summary>
        public Version Version => new Version(1, 0, 0);
        
        /// <summary>
        /// Поддерживаемые типы входных данных
        /// </summary>
        public IEnumerable<Type> SupportedInputTypes => new[] { typeof(IEnumerable<FAQNode>) };

        /// <summary>
        /// Инициализирует новый экземпляр класса SmartLinker
        /// </summary>
        public SmartLinker()
        {
            _configuration = new AlgorithmConfiguration
            {
                IsEnabled = true,
                Parameters = new Dictionary<string, object>
                {
                    ["PrerequisiteThreshold"] = 0.7,
                    ["FollowUpThreshold"] = 0.65,
                    ["RelatedThreshold"] = 0.6,
                    ["ContradictionThreshold"] = 0.5,
                    ["MaxLinksPerNode"] = 8,
                    ["UseDifficultyAnalysis"] = true
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

        /// <summary>
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
            if (nodesList?.Count <= 1)
                warnings.Add("Недостаточно узлов для создания связей");

            return new ValidationResult { IsValid = errors.Count == 0, ErrorMessages = errors, Warnings = warnings };
        }

        /// <summary>
        /// Асинхронное выполнение алгоритма
        /// </summary>
        /// <param name="context">Контекст выполнения с параметрами</param>
        /// <returns>Результат работы алгоритма</returns>
        public Task<AlgorithmResult> ExecuteAsync(AlgorithmContext context)
        {
            var startTime = DateTime.UtcNow;
            var statistics = new AlgorithmStatistics();
            
            try
            {
                var validationResult = Validate(context);
                if (!validationResult.IsValid)
                {
                    return Task.FromResult(new AlgorithmResult { IsSuccessful = false, ErrorMessages = validationResult.ErrorMessages, Statistics = statistics });
                }

                var nodes = (context.InputNodes ?? Enumerable.Empty<FAQNode>()).ToList();
                statistics.ProcessedNodesCount = nodes.Count;
                var progress = context.ProgressReporter;
                var allConnections = new List<FAQConnection>();

                // 1. Анализ сложности узлов
                progress?.Report(new AlgorithmProgress { CurrentOperation = "Анализ сложности вопросов...", PercentageComplete = 10 });
                AnalyzeNodeComplexity(nodes, context.CancellationToken);

                // 2. Поиск пререквизитов
                var prerequisiteConnections = FindPrerequisites(nodes, context.CancellationToken);

                // 3. Поиск продолжений тем
                var followUpConnections = FindFollowUps(nodes, context.CancellationToken);

                // 4. Поиск связанных тем
                var relatedConnections = FindRelatedTopics(nodes, context.CancellationToken);

                // 5. Поиск противоречий
                var contradictionConnections = FindContradictions(nodes, context.CancellationToken);

                // Collect all connections
                allConnections.AddRange(prerequisiteConnections);
                allConnections.AddRange(followUpConnections);
                allConnections.AddRange(relatedConnections);
                allConnections.AddRange(contradictionConnections);

                // 6. Оптимизация связей
                progress?.Report(new AlgorithmProgress { CurrentOperation = "Оптимизация связей...", PercentageComplete = 95 });
                var optimizedConnections = OptimizeConnections(allConnections);

                // 7. Генерация предложений по связыванию
                var suggestions = GenerateLinkingSuggestions(nodes, optimizedConnections, context.CancellationToken);

                var executionTime = DateTime.UtcNow - startTime;
                statistics.ExecutionTime = executionTime;
                statistics.ConnectionsFound = optimizedConnections.Count;
                statistics.MemoryUsedBytes = GC.GetTotalMemory(false);
                statistics.CustomMetrics = new Dictionary<string, object>
                {
                    ["PrerequisiteLinks"] = optimizedConnections.Count(c => c.Type == ConnectionType.Prerequisite),
                    ["FollowUpLinks"] = optimizedConnections.Count(c => c.Type == ConnectionType.FollowUp),
                    ["RelatedLinks"] = optimizedConnections.Count(c => c.Type == ConnectionType.Related),
                    ["ContradictionLinks"] = optimizedConnections.Count(c => c.Type == ConnectionType.Contradiction)
                };

                progress?.Report(new AlgorithmProgress { CurrentOperation = "Связывание завершено!", PercentageComplete = 100, ProcessedItems = nodes.Count });

                var overallConfidence = optimizedConnections.Any() ? optimizedConnections.Average(c => c.AlgorithmConfidence) : 0.0;

                return Task.FromResult(new AlgorithmResult
                {
                    IsSuccessful = true,
                    ProcessedNodes = nodes,
                    Connections = optimizedConnections,
                    Suggestions = suggestions,
                    OverallConfidence = overallConfidence,
                    Statistics = statistics
                });
            }
            catch (Exception ex)
            {
                statistics.ExecutionTime = DateTime.UtcNow - startTime;
                return Task.FromResult(new AlgorithmResult { IsSuccessful = false, ErrorMessages = new[] { ex.Message }, Statistics = statistics });
            }
        }

        /// <summary>
        /// Анализ сложности узлов
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        private void AnalyzeNodeComplexity(List<FAQNode> nodes, System.Threading.CancellationToken cancellationToken)
        {
            var useDifficultyAnalysis = (bool)_configuration.Parameters["UseDifficultyAnalysis"];
            if (!useDifficultyAnalysis) return;

            foreach (var node in nodes)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var complexity = 0.0;
                var textLength = (node.Query?.Length ?? 0) + (node.Response?.Length ?? 0);
                complexity += Math.Min(textLength / 1000.0, 1.0) * 0.4;

                var techTermsCount = CountTechnicalTerms(node);
                complexity += Math.Min(techTermsCount / 10.0, 1.0) * 0.4;

                complexity += Math.Min((node.Variations?.Count ?? 0) / 5.0, 1.0) * 0.2;

                node.AlgorithmProps.ComplexityScore = Math.Min(complexity, 1.0);
            }
        }

        /// <summary>
        /// Поиск пререквизитов
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список связей пререквизитов</returns>
        private List<FAQConnection> FindPrerequisites(List<FAQNode> nodes, System.Threading.CancellationToken cancellationToken)
        {
            var connections = new List<FAQConnection>();
            var threshold = (double)_configuration.Parameters["PrerequisiteThreshold"];

            for (int i = 0; i < nodes.Count; i++)
            {
                for (int j = 0; j < nodes.Count; j++)
                {
                    if (i == j) continue;
                    cancellationToken.ThrowIfCancellationRequested();

                    var currentNode = nodes[i];
                    var candidatePrerequisite = nodes[j];

                    if (candidatePrerequisite.AlgorithmProps.ComplexityScore >= currentNode.AlgorithmProps.ComplexityScore)
                        continue;

                    var strength = CalculatePrerequisiteStrength(currentNode, candidatePrerequisite);
                    
                    if (strength >= threshold)
                    {
                        connections.Add(new FAQConnection
                        {
                            SourceNodeId = candidatePrerequisite.Id,
                            TargetNodeId = currentNode.Id,
                            Type = ConnectionType.Prerequisite,
                            Strength = strength,
                            AlgorithmConfidence = strength,
                            CreatedByAlgorithm = DisplayName,
                            Description = $"Пререквизит: '{candidatePrerequisite.Query}' → '{currentNode.Query}'"
                        });
                    }
                }
            }

            return connections;
        }

        /// <summary>
        /// Поиск продолжений тем
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список связей продолжений</returns>
        private List<FAQConnection> FindFollowUps(List<FAQNode> nodes, System.Threading.CancellationToken cancellationToken)
        {
            var connections = new List<FAQConnection>();
            var threshold = (double)_configuration.Parameters["FollowUpThreshold"];

            foreach (var node in nodes)
            {
                cancellationToken.ThrowIfCancellationRequested();

                foreach (var candidateFollowUp in nodes)
                {
                    if (node.Id == candidateFollowUp.Id) continue;

                    var strength = CalculateFollowUpStrength(node, candidateFollowUp);
                    
                    if (strength >= threshold)
                    {
                        connections.Add(new FAQConnection
                        {
                            SourceNodeId = node.Id,
                            TargetNodeId = candidateFollowUp.Id,
                            Type = ConnectionType.FollowUp,
                            Strength = strength,
                            AlgorithmConfidence = strength,
                            CreatedByAlgorithm = DisplayName,
                            Description = $"Продолжение: '{node.Query}' → '{candidateFollowUp.Query}'"
                        });
                    }
                }
            }

            return connections;
        }

        /// <summary>
        /// Поиск связанных тем
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список связей связанных тем</returns>
        private List<FAQConnection> FindRelatedTopics(List<FAQNode> nodes, System.Threading.CancellationToken cancellationToken)
        {
            var connections = new List<FAQConnection>();
            var threshold = (double)_configuration.Parameters["RelatedThreshold"];

            for (int i = 0; i < nodes.Count; i++)
            {
                for (int j = i + 1; j < nodes.Count; j++)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    var strength = CalculateRelatedStrength(nodes[i], nodes[j]);
                    
                    if (strength >= threshold)
                    {
                        connections.Add(new FAQConnection
                        {
                            SourceNodeId = nodes[i].Id,
                            TargetNodeId = nodes[j].Id,
                            Type = ConnectionType.Related,
                            Strength = strength,
                            AlgorithmConfidence = strength,
                            CreatedByAlgorithm = DisplayName,
                            Description = $"Связанные темы: '{nodes[i].Query}' ↔ '{nodes[j].Query}'"
                        });
                    }
                }
            }

            return connections;
        }

        /// <summary>
        /// Поиск противоречий
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список связей противоречий</returns>
        private List<FAQConnection> FindContradictions(List<FAQNode> nodes, System.Threading.CancellationToken cancellationToken)
        {
            var connections = new List<FAQConnection>();
            var threshold = (double)_configuration.Parameters["ContradictionThreshold"];

            for (int i = 0; i < nodes.Count; i++)
            {
                for (int j = i + 1; j < nodes.Count; j++)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    var strength = CalculateContradictionStrength(nodes[i], nodes[j]);
                    
                    if (strength >= threshold)
                    {
                        connections.Add(new FAQConnection
                        {
                            SourceNodeId = nodes[i].Id,
                            TargetNodeId = nodes[j].Id,
                            Type = ConnectionType.Contradiction,
                            Strength = strength,
                            AlgorithmConfidence = strength,
                            CreatedByAlgorithm = DisplayName,
                            Description = $"Потенциальное противоречие: '{nodes[i].Query}' ⚡ '{nodes[j].Query}'"
                        });
                    }
                }
            }

            return connections;
        }

        /// <summary>
        /// Оптимизация связей
        /// </summary>
        /// <param name="connections">Список связей для оптимизации</param>
        /// <returns>Оптимизированный список связей</returns>
        private List<FAQConnection> OptimizeConnections(List<FAQConnection> connections)
        {
            var maxLinksPerNode = (int)_configuration.Parameters["MaxLinksPerNode"];

            return connections
                .GroupBy(c => c.SourceNodeId)
                .SelectMany(g => g.OrderByDescending(c => c.Strength).Take(maxLinksPerNode))
                .ToList();
        }

        /// <summary>
        /// Генерация предложений по связыванию
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="connections">Список связей</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список предложений по оптимизации</returns>
        private List<OptimizationSuggestion> GenerateLinkingSuggestions(
            List<FAQNode> nodes, List<FAQConnection> connections, System.Threading.CancellationToken cancellationToken)
        {
            var suggestions = new List<OptimizationSuggestion>();

            // Предложения для изолированных узлов
            var isolatedNodes = nodes.Where(n => !connections.Any(c => c.SourceNodeId == n.Id || c.TargetNodeId == n.Id)).ToList();
            
            foreach (var isolatedNode in isolatedNodes)
            {
                suggestions.Add(new OptimizationSuggestion
                {
                    Type = SuggestionType.CreateConnection,
                    Description = $"Узел '{isolatedNode.Query}' не имеет связей. Рекомендуется найти связанные темы.",
                    Priority = 3,
                    Confidence = 0.8,
                    AffectedNodes = new[] { isolatedNode }
                });
            }

            // Предложения по противоречиям
            var contradictions = connections.Where(c => c.Type == ConnectionType.Contradiction).ToList();
            foreach (var contradiction in contradictions)
            {
                var sourceNode = nodes.FirstOrDefault(n => n.Id == contradiction.SourceNodeId);
                var targetNode = nodes.FirstOrDefault(n => n.Id == contradiction.TargetNodeId);
                
                if (sourceNode != null && targetNode != null)
                {
                    suggestions.Add(new OptimizationSuggestion
                    {
                        Type = SuggestionType.ImproveResponse,
                        Description = $"Обнаружено противоречие между '{sourceNode.Query}' и '{targetNode.Query}'. Требуется проверка.",
                        Priority = 4,
                        Confidence = contradiction.AlgorithmConfidence,
                        AffectedNodes = new[] { sourceNode, targetNode }
                    });
                }
            }

            return suggestions;
        }

        #region Helper Methods

        /// <summary>
        /// Подсчет технических терминов в узле
        /// </summary>
        /// <param name="node">Узел для анализа</param>
        /// <returns>Количество технических терминов</returns>
        private int CountTechnicalTerms(FAQNode node)
        {
            var technicalTerms = new HashSet<string>
            {
                "API", "база данных", "сервер", "клиент", "протокол", "интерфейс", 
                "конфигурация", "параметр", "алгоритм", "функция", "метод", "класс"
            };

            var text = $"{node.Query} {node.Response}".ToLowerInvariant();
            return technicalTerms.Count(term => text.Contains(term));
        }

        /// <summary>
        /// Расчет силы связи пререквизита
        /// </summary>
        /// <param name="currentNode">Текущий узел</param>
        /// <param name="candidatePrerequisite">Потенциальный пререквизит</param>
        /// <returns>Сила связи пререквизита</returns>
        private double CalculatePrerequisiteStrength(FAQNode currentNode, FAQNode candidatePrerequisite)
        {
            var strength = 0.0;

            var complexityDiff = currentNode.AlgorithmProps.ComplexityScore - candidatePrerequisite.AlgorithmProps.ComplexityScore;
            strength += Math.Min(complexityDiff * 2, 0.4);

            var semanticSimilarity = CalculateSemanticSimilarity(currentNode, candidatePrerequisite);
            strength += Math.Min(semanticSimilarity, 0.3);

            var prerequisiteKeywords = new[] { "сначала", "перед", "предварительно", "требуется", "необходимо" };
            var hasPrerequisiteKeywords = prerequisiteKeywords.Any(kw => 
                currentNode.Query?.ToLowerInvariant().Contains(kw) == true ||
                currentNode.Response?.ToLowerInvariant().Contains(kw) == true);
            
            if (hasPrerequisiteKeywords) strength += 0.3;

            return Math.Min(strength, 1.0);
        }

        /// <summary>
        /// Расчет силы связи продолжения
        /// </summary>
        /// <param name="baseNode">Базовый узел</param>
        /// <param name="candidateFollowUp">Потенциальное продолжение</param>
        /// <returns>Сила связи продолжения</returns>
        private double CalculateFollowUpStrength(FAQNode baseNode, FAQNode candidateFollowUp)
        {
            var strength = 0.0;

            var semanticSimilarity = CalculateSemanticSimilarity(baseNode, candidateFollowUp);
            strength += semanticSimilarity * 0.4;

            var followUpKeywords = new[] { "далее", "затем", "потом", "также", "кроме того", "дополнительно" };
            var hasFollowUpKeywords = followUpKeywords.Any(kw => 
                candidateFollowUp.Query?.ToLowerInvariant().Contains(kw) == true ||
                candidateFollowUp.Response?.ToLowerInvariant().Contains(kw) == true);
            
            if (hasFollowUpKeywords) strength += 0.3;

            var complexityIncrease = candidateFollowUp.AlgorithmProps.ComplexityScore - baseNode.AlgorithmProps.ComplexityScore;
            if (complexityIncrease > 0) strength += Math.Min(complexityIncrease, 0.3);

            return Math.Min(strength, 1.0);
        }

        /// <summary>
        /// Расчет силы связи связанных тем
        /// </summary>
        /// <param name="node1">Первый узел</param>
        /// <param name="node2">Второй узел</param>
        /// <returns>Сила связи связанных тем</returns>
        private double CalculateRelatedStrength(FAQNode node1, FAQNode node2)
        {
            var strength = 0.0;

            var semanticSimilarity = CalculateSemanticSimilarity(node1, node2);
            strength += semanticSimilarity * 0.5;

            var commonKeywords = FindCommonKeywords(node1, node2);
            strength += Math.Min(commonKeywords.Count / 5.0, 0.3);

            var commonResources = FindCommonResources(node1, node2);
            if (commonResources > 0) strength += 0.2;

            return Math.Min(strength, 1.0);
        }

        /// <summary>
        /// Расчет силы связи противоречий
        /// </summary>
        /// <param name="node1">Первый узел</param>
        /// <param name="node2">Второй узел</param>
        /// <returns>Сила связи противоречий</returns>
        private double CalculateContradictionStrength(FAQNode node1, FAQNode node2)
        {
            var strength = 0.0;

            var contradictionKeywords = new[] 
            { 
                ("да", "нет"), ("можно", "нельзя"), ("рекомендуется", "не рекомендуется"),
                ("включить", "отключить"), ("активировать", "деактивировать")
            };

            var text1 = $"{node1.Query} {node1.Response}".ToLowerInvariant();
            var text2 = $"{node2.Query} {node2.Response}".ToLowerInvariant();

            foreach (var (positive, negative) in contradictionKeywords)
            {
                if ((text1.Contains(positive) && text2.Contains(negative)) ||
                    (text1.Contains(negative) && text2.Contains(positive)))
                {
                    strength += 0.3;
                }
            }

            var questionSimilarity = CalculateTextSimilarity(node1.Query, node2.Query);
            var responseSimilarity = CalculateTextSimilarity(node1.Response, node2.Response);
            
            if (questionSimilarity > 0.7 && responseSimilarity < 0.3)
            {
                strength += 0.4;
            }

            return Math.Min(strength, 1.0);
        }

        /// <summary>
        /// Расчет семантической схожести между узлами
        /// </summary>
        /// <param name="node1">Первый узел</param>
        /// <param name="node2">Второй узел</param>
        /// <returns>Значение семантической схожести</returns>
        private double CalculateSemanticSimilarity(FAQNode node1, FAQNode node2)
        {
            if (node1.AlgorithmProps.SemanticVector == null || node2.AlgorithmProps.SemanticVector == null)
                return 0.0;

            return CalculateCosineSimilarity(node1.AlgorithmProps.SemanticVector, node2.AlgorithmProps.SemanticVector);
        }

        /// <summary>
        /// Расчет косинусного сходства между векторами
        /// </summary>
        /// <param name="vector1">Первый вектор</param>
        /// <param name="vector2">Второй вектор</param>
        /// <returns>Значение косинусного сходства</returns>
        private double CalculateCosineSimilarity(float[] vector1, float[] vector2)
        {
            if (vector1.Length != vector2.Length) return 0.0;

            var dotProduct = 0.0;
            var magnitude1 = 0.0;
            var magnitude2 = 0.0;

            for (int i = 0; i < vector1.Length; i++)
            {
                dotProduct += vector1[i] * vector2[i];
                magnitude1 += vector1[i] * vector1[i];
                magnitude2 += vector2[i] * vector2[i];
            }

            return magnitude1 == 0.0 || magnitude2 == 0.0 ? 0.0 : dotProduct / (Math.Sqrt(magnitude1) * Math.Sqrt(magnitude2));
        }

        /// <summary>
        /// Расчет сходства текстов
        /// </summary>
        /// <param name="text1">Первый текст</param>
        /// <param name="text2">Второй текст</param>
        /// <returns>Значение сходства текстов</returns>
        private double CalculateTextSimilarity(string text1, string text2)
        {
            if (string.IsNullOrWhiteSpace(text1) || string.IsNullOrWhiteSpace(text2))
                return 0.0;

            var words1 = new HashSet<string>(Regex.Split(text1.ToLowerInvariant(), @"\W+").Where(w => w.Length > 2));
            var words2 = new HashSet<string>(Regex.Split(text2.ToLowerInvariant(), @"\W+").Where(w => w.Length > 2));

            var intersection = words1.Intersect(words2).Count();
            var union = words1.Union(words2).Count();

            return union == 0 ? 0.0 : (double)intersection / union;
        }

        /// <summary>
        /// Поиск общих ключевых слов между узлами
        /// </summary>
        /// <param name="node1">Первый узел</param>
        /// <param name="node2">Второй узел</param>
        /// <returns>Список общих ключевых слов</returns>
        private List<string> FindCommonKeywords(FAQNode node1, FAQNode node2)
        {
            var keywords1 = ExtractKeywords($"{node1.Query} {string.Join(" ", node1.Variations)}");
            var keywords2 = ExtractKeywords($"{node2.Query} {string.Join(" ", node2.Variations)}");
            
            return keywords1.Intersect(keywords2).ToList();
        }

        /// <summary>
        /// Поиск общих ресурсов между узлами
        /// </summary>
        /// <param name="node1">Первый узел</param>
        /// <param name="node2">Второй узел</param>
        /// <returns>Количество общих ресурсов</returns>
        private int FindCommonResources(FAQNode node1, FAQNode node2)
        {
            var files1 = node1.Resources?.SelectMany(r => r.Files ?? new List<string>()).ToHashSet() ?? new HashSet<string>();
            var files2 = node2.Resources?.SelectMany(r => r.Files ?? new List<string>()).ToHashSet() ?? new HashSet<string>();
            
            return files1.Intersect(files2).Count();
        }

        /// <summary>
        /// Извлечение ключевых слов из текста
        /// </summary>
        /// <param name="text">Текст для анализа</param>
        /// <returns>Список ключевых слов</returns>
        private List<string> ExtractKeywords(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return new List<string>();

            var stopWords = new HashSet<string> 
            { 
                "как", "что", "где", "когда", "почему", "который", "которая", "которое", 
                "в", "на", "с", "по", "для", "от", "до", "из", "к", "и", "или", "не", 
                "но", "а", "так", "это", "есть", "быть", "была", "был", "было", "будет", "будут" 
            };

            return Regex.Split(text.ToLowerInvariant(), @"\W+")
                       .Where(w => w.Length > 2 && !stopWords.Contains(w))
                       .Distinct()
                       .ToList();
        }

        #endregion
    }
}