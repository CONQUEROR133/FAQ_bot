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
    /// Алгоритм семантической группировки FAQ записей
    /// Создает интеллектуальные группы на основе смысла, а не только ключевых слов
    /// </summary>
    public class SemanticGrouper : IFAQAlgorithm
    {
        private AlgorithmConfiguration _configuration;
        
        /// <summary>
        /// Название алгоритма на русском языке
        /// </summary>
        public string DisplayName => "🎯 Семантическая группировка";
        
        /// <summary>
        /// Описание работы алгоритма
        /// </summary>
        public string Description => "Создает интеллектуальные группы FAQ записей на основе семантического анализа смысла вопросов и ответов";
        
        /// <summary>
        /// Версия алгоритма для совместимости
        /// </summary>
        public Version Version => new Version(1, 0, 0);
        
        /// <summary>
        /// Поддерживаемые типы входных данных
        /// </summary>
        public IEnumerable<Type> SupportedInputTypes => new[] { typeof(IEnumerable<FAQNode>) };

        /// <summary>
        /// Инициализирует новый экземпляр класса SemanticGrouper
        /// </summary>
        public SemanticGrouper()
        {
            _configuration = new AlgorithmConfiguration
            {
                IsEnabled = true,
                Parameters = new Dictionary<string, object>
                {
                    ["GroupSimilarityThreshold"] = 0.75,
                    ["MinGroupSize"] = 2,
                    ["MaxGroupSize"] = 15,
                    ["AutoGenerateParentQuery"] = true,
                    ["UseHierarchicalClustering"] = true
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
            if (nodesList?.Count == 0)
                warnings.Add("Список узлов пуст - группировка не будет выполнена");

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
                    return Task.FromResult(new AlgorithmResult
                    {
                        IsSuccessful = false,
                        ErrorMessages = validationResult.ErrorMessages,
                        Statistics = statistics
                    });
                }

                var nodes = (context.InputNodes ?? Enumerable.Empty<FAQNode>()).ToList();
                statistics.ProcessedNodesCount = nodes.Count;

                var progress = context.ProgressReporter;

                // 1. Создание семантических векторов
                progress?.Report(new AlgorithmProgress { CurrentOperation = "Создание семантических векторов...", PercentageComplete = 10 });
                var nodeVectors = CreateSemanticVectors(nodes, context.CancellationToken);

                // 2. Расчет матрицы сходства между узлами
                var similarityMatrix = CalculateSimilarityMatrix(nodes, nodeVectors, context.CancellationToken);

                // 3. Выполнение кластеризации узлов
                var clusters = PerformClustering(nodes, similarityMatrix, context.CancellationToken);

                // 4. Создание FAQ групп из кластеров
                var groups = CreateFAQGroups(clusters, context.CancellationToken);

                // 5. Создание связей между группами
                var connections = CreateGroupConnections(groups, context.CancellationToken);

                // 6. Обновление узлов информацией о группе
                UpdateNodesWithGroupInfo(nodes, groups);

                // 7. Генерация предложений по группировке
                var suggestions = GenerateGroupingSuggestions(groups, context.CancellationToken);

                var executionTime = DateTime.UtcNow - startTime;
                statistics.ExecutionTime = executionTime;
                statistics.ConnectionsFound = connections.Count;
                statistics.MemoryUsedBytes = GC.GetTotalMemory(false);
                statistics.CustomMetrics = new Dictionary<string, object>
                {
                    ["GroupsCreated"] = groups.Count,
                    ["AverageGroupSize"] = groups.Any() ? groups.Average(g => g.Nodes.Count) : 0,
                    ["NodesGrouped"] = groups.Sum(g => g.Nodes.Count)
                };

                progress?.Report(new AlgorithmProgress { CurrentOperation = "Группировка завершена!", PercentageComplete = 100, ProcessedItems = nodes.Count });

                var overallConfidence = groups.Any() ? groups.Average(g => g.AverageSimilarity) : 0.0;

                return Task.FromResult(new AlgorithmResult
                {
                    IsSuccessful = true,
                    ProcessedNodes = nodes,
                    Connections = connections,
                    Suggestions = suggestions,
                    OverallConfidence = overallConfidence,
                    Statistics = statistics,
                    AdditionalData = new Dictionary<string, object> { ["FAQGroups"] = groups }
                });
            }
            catch (Exception ex)
            {
                statistics.ExecutionTime = DateTime.UtcNow - startTime;
                return Task.FromResult(new AlgorithmResult { IsSuccessful = false, ErrorMessages = new[] { ex.Message }, Statistics = statistics });
            }
        }

        /// <summary>
        /// Создание семантических векторов для узлов
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Словарь с векторами для каждого узла</returns>
        private Dictionary<FAQNode, float[]> CreateSemanticVectors(List<FAQNode> nodes, System.Threading.CancellationToken cancellationToken)
        {
            // Создание векторов для каждого узла
            var nodeVectors = new Dictionary<FAQNode, float[]>();
            foreach (var node in nodes)
            {
                cancellationToken.ThrowIfCancellationRequested();
                var combinedText = $"{node.Query} {string.Join(" ", node.Variations)} {node.Response}";
                var vector = CreateTextVector(combinedText);
                nodeVectors[node] = vector;
                node.AlgorithmProps.SemanticVector = vector;
            }

            return nodeVectors;
        }

        /// <summary>
        /// Создание текстового вектора
        /// </summary>
        /// <param name="text">Текст для векторизации</param>
        /// <returns>Вектор признаков текста</returns>
        private float[] CreateTextVector(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return new float[100];

            var normalizedText = text.ToLowerInvariant().Replace("ё", "е");
            var words = Regex.Split(normalizedText, @"\W+").Where(w => w.Length > 2).ToList();
            var vector = new float[100];
            
            foreach (var word in words.Distinct())
            {
                var hash = Math.Abs(word.GetHashCode()) % 100;
                var frequency = (float)words.Count(w => w == word) / words.Count;
                vector[hash] += frequency;
            }

            // Нормализация
            var magnitude = (float)Math.Sqrt(vector.Sum(v => v * v));
            if (magnitude > 0)
            {
                for (int i = 0; i < vector.Length; i++)
                    vector[i] /= magnitude;
            }

            return vector;
        }

        /// <summary>
        /// Расчет матрицы сходства между узлами
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="nodeVectors">Векторы узлов</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Матрица сходства</returns>
        private Dictionary<(FAQNode, FAQNode), double> CalculateSimilarityMatrix(
            List<FAQNode> nodes, Dictionary<FAQNode, float[]> nodeVectors, System.Threading.CancellationToken cancellationToken)
        {
            var similarityMatrix = new Dictionary<(FAQNode, FAQNode), double>();

            for (int i = 0; i < nodes.Count; i++)
            {
                for (int j = i + 1; j < nodes.Count; j++)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var similarity = CalculateCosineSimilarity(nodeVectors[nodes[i]], nodeVectors[nodes[j]]);
                    similarityMatrix[(nodes[i], nodes[j])] = similarity;
                }
            }

            return similarityMatrix;
        }

        /// <summary>
        /// Расчет косинусного сходства между векторами
        /// </summary>
        /// <param name="vector1">Первый вектор</param>
        /// <param name="vector2">Второй вектор</param>
        /// <returns>Значение косинусного сходства (0.0 - 1.0)</returns>
        private double CalculateCosineSimilarity(float[] vector1, float[] vector2)
        {
            if (vector1.Length != vector2.Length)
                return 0.0;

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
        /// Выполнение кластеризации узлов
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="similarityMatrix">Матрица сходства</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список кластеров</returns>
        private List<List<FAQNode>> PerformClustering(
            List<FAQNode> nodes, Dictionary<(FAQNode, FAQNode), double> similarityMatrix, System.Threading.CancellationToken cancellationToken)
        {
            var groupThreshold = (double)_configuration.Parameters["GroupSimilarityThreshold"];
            var clusters = new List<List<FAQNode>>();
            var processed = new HashSet<FAQNode>();

            foreach (var node in nodes)
            {
                cancellationToken.ThrowIfCancellationRequested();

                if (processed.Contains(node))
                    continue;

                var cluster = new List<FAQNode> { node };
                processed.Add(node);

                foreach (var otherNode in nodes)
                {
                    if (processed.Contains(otherNode))
                        continue;

                    var similarity = GetSimilarity(node, otherNode, similarityMatrix);
                    if (similarity >= groupThreshold)
                    {
                        cluster.Add(otherNode);
                        processed.Add(otherNode);
                    }
                }

                var minGroupSize = (int)_configuration.Parameters["MinGroupSize"];
                var maxGroupSize = (int)_configuration.Parameters["MaxGroupSize"];
                
                if (cluster.Count >= minGroupSize && cluster.Count <= maxGroupSize)
                    clusters.Add(cluster);
            }

            return clusters;
        }

        /// <summary>
        /// Получение сходства между двумя узлами
        /// </summary>
        /// <param name="node1">Первый узел</param>
        /// <param name="node2">Второй узел</param>
        /// <param name="similarityMatrix">Матрица сходства</param>
        /// <returns>Значение сходства</returns>
        private double GetSimilarity(FAQNode node1, FAQNode node2, Dictionary<(FAQNode, FAQNode), double> similarityMatrix)
        {
            return similarityMatrix.TryGetValue((node1, node2), out var similarity) ? similarity :
                   similarityMatrix.TryGetValue((node2, node1), out similarity) ? similarity : 0.0;
        }

        /// <summary>
        /// Создание FAQ групп из кластеров
        /// </summary>
        /// <param name="clusters">Список кластеров</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список FAQ групп</returns>
        private List<FAQGroup> CreateFAQGroups(List<List<FAQNode>> clusters, System.Threading.CancellationToken cancellationToken)
        {
            var groups = new List<FAQGroup>();
            var autoGenerateParent = (bool)_configuration.Parameters["AutoGenerateParentQuery"];

            foreach (var cluster in clusters)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var group = new FAQGroup
                {
                    Nodes = cluster,
                    CreatedByAlgorithm = DisplayName,
                    AverageSimilarity = CalculateClusterAverageSimilarity(cluster),
                    CreatedAt = DateTime.UtcNow,
                    IsUserConfirmed = false,
                    Name = GenerateGroupName(cluster),
                    Description = $"Группа из {cluster.Count} семантически связанных вопросов"
                };

                if (autoGenerateParent)
                    group.SuggestedParentQuery = GenerateParentQuery(cluster);

                groups.Add(group);
            }

            return groups;
        }

        /// <summary>
        /// Расчет среднего сходства в кластере
        /// </summary>
        /// <param name="cluster">Кластер узлов</param>
        /// <returns>Среднее значение сходства</returns>
        private double CalculateClusterAverageSimilarity(List<FAQNode> cluster)
        {
            if (cluster.Count < 2)
                return 1.0;

            var similarities = new List<double>();
            for (int i = 0; i < cluster.Count; i++)
            {
                for (int j = i + 1; j < cluster.Count; j++)
                {
                    var similarity = CalculateCosineSimilarity(
                        cluster[i].AlgorithmProps.SemanticVector,
                        cluster[j].AlgorithmProps.SemanticVector);
                    similarities.Add(similarity);
                }
            }

            return similarities.Any() ? similarities.Average() : 0.0;
        }

        /// <summary>
        /// Генерация названия группы
        /// </summary>
        /// <param name="cluster">Кластер узлов</param>
        /// <returns>Название группы</returns>
        private string GenerateGroupName(List<FAQNode> cluster)
        {
            var allKeywords = new Dictionary<string, int>();

            foreach (var node in cluster)
            {
                var keywords = ExtractKeywords(node.Query + " " + string.Join(" ", node.Variations));
                foreach (var keyword in keywords)
                    allKeywords[keyword] = allKeywords.GetValueOrDefault(keyword, 0) + 1;
            }

            var topKeywords = allKeywords
                .Where(kvp => kvp.Value >= cluster.Count / 2)
                .OrderByDescending(kvp => kvp.Value)
                .Take(2)
                .Select(kvp => kvp.Key)
                .ToList();

            return topKeywords.Any() ? string.Join(" ", topKeywords).ToUpperInvariant() : "ГРУППА ВОПРОСОВ";
        }

        /// <summary>
        /// Генерация родительского запроса для группы
        /// </summary>
        /// <param name="cluster">Кластер узлов</param>
        /// <returns>Родительский запрос</returns>
        private string GenerateParentQuery(List<FAQNode> cluster)
        {
            var commonKeywords = FindCommonKeywords(cluster);
            return commonKeywords.Any() ? $"Вопросы о {string.Join(", ", commonKeywords.Take(2))}" : "Общие вопросы по теме группы";
        }

        /// <summary>
        /// Создание связей между группами
        /// </summary>
        /// <param name="groups">Список групп</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список связей между группами</returns>
        private List<FAQConnection> CreateGroupConnections(List<FAQGroup> groups, System.Threading.CancellationToken cancellationToken)
        {
            var connections = new List<FAQConnection>();

            foreach (var group in groups)
            {
                for (int i = 0; i < group.Nodes.Count; i++)
                {
                    for (int j = i + 1; j < group.Nodes.Count; j++)
                    {
                        connections.Add(new FAQConnection
                        {
                            SourceNodeId = group.Nodes[i].Id,
                            TargetNodeId = group.Nodes[j].Id,
                            Type = ConnectionType.GroupMember,
                            Strength = group.AverageSimilarity,
                            AlgorithmConfidence = 0.8,
                            CreatedByAlgorithm = DisplayName,
                            Description = $"Члены группы '{group.Name}'",
                            Metadata = new Dictionary<string, object> { ["GroupId"] = group.Id, ["GroupName"] = group.Name }
                        });
                    }
                }
            }

            return connections;
        }

        /// <summary>
        /// Обновление узлов информацией о группе
        /// </summary>
        /// <param name="nodes">Список узлов</param>
        /// <param name="groups">Список групп</param>
        private void UpdateNodesWithGroupInfo(List<FAQNode> nodes, List<FAQGroup> groups)
        {
            foreach (var group in groups)
            {
                foreach (var node in group.Nodes)
                {
                    node.Metadata.GroupName = group.Name;
                    node.AlgorithmProps.ClusterId = group.Id.ToString();
                    if (!node.Metadata.Tags.Contains(group.Name))
                        node.Metadata.Tags.Add(group.Name);
                }
            }
        }

        /// <summary>
        /// Генерация предложений по группировке
        /// </summary>
        /// <param name="groups">Список групп</param>
        /// <param name="cancellationToken">Токен отмены операции</param>
        /// <returns>Список предложений по оптимизации</returns>
        private List<OptimizationSuggestion> GenerateGroupingSuggestions(List<FAQGroup> groups, System.Threading.CancellationToken cancellationToken)
        {
            var suggestions = new List<OptimizationSuggestion>();
            var maxGroupSize = (int)_configuration.Parameters["MaxGroupSize"];

            // Предложения по разделению больших групп
            var largeGroups = groups.Where(g => g.Nodes.Count > maxGroupSize * 0.8).ToList();
            foreach (var largeGroup in largeGroups)
            {
                suggestions.Add(new OptimizationSuggestion
                {
                    Type = SuggestionType.Restructure,
                    Description = $"Группа '{largeGroup.Name}' содержит {largeGroup.Nodes.Count} узлов. Рекомендуется разделение.",
                    Priority = 2,
                    Confidence = 0.7,
                    AffectedNodes = largeGroup.Nodes,
                    SuggestedActions = new Dictionary<string, object>
                    {
                        ["Action"] = "SplitGroup",
                        ["GroupId"] = largeGroup.Id,
                        ["SuggestedSubgroups"] = 2
                    }
                });
            }

            return suggestions;
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

        /// <summary>
        /// Поиск общих ключевых слов в кластере
        /// </summary>
        /// <param name="cluster">Кластер узлов</param>
        /// <returns>Список общих ключевых слов</returns>
        private List<string> FindCommonKeywords(List<FAQNode> cluster)
        {
            var keywordCounts = new Dictionary<string, int>();
            
            foreach (var node in cluster)
            {
                var keywords = ExtractKeywords(node.Query + " " + string.Join(" ", node.Variations));
                foreach (var keyword in keywords)
                    keywordCounts[keyword] = keywordCounts.GetValueOrDefault(keyword, 0) + 1;
            }

            return keywordCounts
                .Where(kvp => kvp.Value >= cluster.Count / 2)
                .OrderByDescending(kvp => kvp.Value)
                .Select(kvp => kvp.Key)
                .ToList();
        }
    }
}