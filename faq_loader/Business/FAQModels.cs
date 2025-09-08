using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;

namespace UniversalFAQLoader.Business.Models
{
    /// <summary>
    /// Узел FAQ (вопрос-ответ)
    /// </summary>
    public class FAQNode : INotifyPropertyChanged
    {
        private string _query = string.Empty;
        private string _response = string.Empty;

        /// <summary>
        /// Уникальный идентификатор узла
        /// </summary>
        public Guid Id { get; set; } = Guid.NewGuid();

        /// <summary>
        /// Вопрос или запрос пользователя
        /// </summary>
        public string Query
        {
            get => _query;
            set
            {
                _query = value ?? string.Empty;
                OnPropertyChanged(nameof(Query));
            }
        }

        /// <summary>
        /// Ответ на вопрос
        /// </summary>
        public string Response
        {
            get => _response;
            set
            {
                _response = value ?? string.Empty;
                OnPropertyChanged(nameof(Response));
            }
        }

        /// <summary>
        /// Альтернативные формулировки вопроса
        /// </summary>
        public List<string> Variations { get; set; } = new List<string>();

        /// <summary>
        /// Связи с другими узлами FAQ
        /// </summary>
        public List<FAQConnection> Connections { get; set; } = new List<FAQConnection>();

        /// <summary>
        /// Ресурсы, связанные с этим узлом (файлы, ссылки)
        /// </summary>
        public List<FAQResource> Resources { get; set; } = new List<FAQResource>();

        /// <summary>
        /// Метаданные узла
        /// </summary>
        public NodeMetadata Metadata { get; set; } = new NodeMetadata();

        /// <summary>
        /// Алгоритмические свойства узла
        /// </summary>
        public AlgorithmProperties AlgorithmProps { get; set; } = new AlgorithmProperties();

        /// <summary>
        /// Поисковый индекс для быстрого поиска
        /// </summary>
        public SearchIndex SearchIndex { get; set; } = new SearchIndex();

        /// <summary>
        /// Occurs when a property value changes.
        /// </summary>
        public event PropertyChangedEventHandler? PropertyChanged;

        /// <summary>
        /// Raises the PropertyChanged event.
        /// </summary>
        /// <param name="propertyName">The name of the property that changed.</param>
        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        /// <summary>
        /// Converts the FAQNode to a JSON-compatible object.
        /// </summary>
        /// <returns>A dictionary representing the FAQNode.</returns>
        public object ToJsonCompatible()
        {
            var result = new Dictionary<string, object>
            {
                ["id"] = Id.ToString(),
                ["query"] = Query,
                ["response"] = Response
            };

            if (Variations?.Any() == true)
                result["variations"] = Variations;

            if (Resources?.Any() == true)
                result["resources"] = Resources.Select(r => r.ToJsonCompatible()).ToList();

            if (Connections?.Any() == true)
                result["connections"] = Connections.Select(c => new Dictionary<string, object>
                {
                    ["id"] = c.Id.ToString(),
                    ["source_node_id"] = c.SourceNodeId.ToString(),
                    ["target_node_id"] = c.TargetNodeId.ToString(),
                    ["type"] = c.Type.ToString(),
                    ["strength"] = c.Strength,
                    ["description"] = c.Description,
                    ["created_by_algorithm"] = c.CreatedByAlgorithm,
                    ["algorithm_confidence"] = c.AlgorithmConfidence,
                    ["created_at"] = c.CreatedAt.ToString("o"),
                    ["is_user_confirmed"] = c.IsUserConfirmed
                }).ToList();

            result["metadata"] = new Dictionary<string, object>
            {
                ["source_type"] = Metadata.SourceType,
                ["confidence"] = Metadata.Confidence,
                ["created_at"] = Metadata.CreatedAt.ToString("o"),
                ["hash"] = Metadata.Hash,
                ["group_name"] = Metadata.GroupName
            };

            result["search_index"] = new Dictionary<string, object>
            {
                ["normalized_text"] = SearchIndex.NormalizedText,
                ["words"] = SearchIndex.Words.ToList(),
                ["word_frequencies"] = SearchIndex.WordFrequencies
            };

            result["algorithm_props"] = new Dictionary<string, object>
            {
                ["complexity_score"] = AlgorithmProps.ComplexityScore,
                ["popularity_score"] = AlgorithmProps.PopularityScore,
                ["cluster_id"] = AlgorithmProps.ClusterId,
                ["last_algorithm_update"] = AlgorithmProps.LastAlgorithmUpdate.ToString("o")
            };

            return result;
        }

        /// <summary>
        /// Creates a FAQNode from JSON data.
        /// </summary>
        /// <param name="jsonData">The JSON data to deserialize.</param>
        /// <returns>A new FAQNode instance.</returns>
        public static FAQNode FromJson(dynamic jsonData)
        {
            var node = new FAQNode
            {
                Id = Guid.Parse(jsonData.id?.ToString() ?? Guid.NewGuid().ToString()),
                Query = jsonData.query,
                Response = jsonData.response
            };

            if (jsonData.variations != null)
            {
                node.Variations = ((IEnumerable<dynamic>)jsonData.variations)?.Select(v => (string)v).ToList() ?? new List<string>();
            }

            if (jsonData.resources != null)
            {
                node.Resources = ((IEnumerable<dynamic>)jsonData.resources)?.Select(FAQResource.FromJson).ToList() ?? new List<FAQResource>();
            }

            // Only try to deserialize connections if they exist in the JSON
            if (jsonData.connections != null)
            {
                node.Connections = ((IEnumerable<dynamic>)jsonData.connections)?.Select(c => new FAQConnection
                {
                    Id = Guid.Parse(c.id?.ToString() ?? Guid.NewGuid().ToString()),
                    SourceNodeId = Guid.Parse(c.source_node_id?.ToString() ?? Guid.Empty.ToString()),
                    TargetNodeId = Guid.Parse(c.target_node_id?.ToString() ?? Guid.Empty.ToString()),
                    Type = Enum.TryParse<ConnectionType>(c.type?.ToString(), out ConnectionType type) ? type : ConnectionType.Semantic,
                    Strength = (double)(c.strength ?? 0.0),
                    Description = c.description,
                    CreatedByAlgorithm = c.created_by_algorithm,
                    AlgorithmConfidence = (double)(c.algorithm_confidence ?? 0.0),
                    CreatedAt = DateTime.TryParse(c.created_at?.ToString(), out DateTime createdAt) ? createdAt : DateTime.UtcNow,
                    IsUserConfirmed = (bool)(c.is_user_confirmed ?? false)
                }).ToList() ?? new List<FAQConnection>();
            }

            node.Metadata = NodeMetadata.FromJson(jsonData.metadata);
            
            // Only try to deserialize search_index if it exists in the JSON
            if (jsonData.search_index != null)
            {
                node.SearchIndex = new SearchIndex
                {
                    Words = new HashSet<string>(((IEnumerable<dynamic>)jsonData.search_index.words)?.Select(w => (string)w).ToList() ?? new List<string>()),
                    NormalizedText = jsonData.search_index.normalized_text,
                    WordFrequencies = ((IEnumerable<dynamic>)jsonData.search_index.word_frequencies)?.ToDictionary(
                        pair => (string)pair.Name, 
                        pair => (int)pair.Value) ?? new Dictionary<string, int>()
                };
            }

            // Only try to deserialize algorithm_props if it exists in the JSON
            if (jsonData.algorithm_props != null)
            {
                node.AlgorithmProps = new AlgorithmProperties
                {
                    ComplexityScore = (double)(jsonData.algorithm_props.complexity_score ?? 0.0),
                    PopularityScore = (double)(jsonData.algorithm_props.popularity_score ?? 0.0),
                    ClusterId = jsonData.algorithm_props.cluster_id,
                    LastAlgorithmUpdate = DateTime.TryParse(
                        jsonData.algorithm_props.last_algorithm_update?.ToString(), 
                        out DateTime lastUpdate) ? lastUpdate : DateTime.UtcNow
                };
            }

            return node;
        }
    }

    /// <summary>
    /// Ресурс FAQ (файл, ссылка)
    /// </summary>
    public class FAQResource
    {
        /// <summary>
        /// Тип ресурса
        /// </summary>
        public string Type { get; set; } = string.Empty;

        /// <summary>
        /// Название ресурса
        /// </summary>
        public string Title { get; set; } = string.Empty;

        /// <summary>
        /// Список файлов
        /// </summary>
        public List<string> Files { get; set; } = new List<string>();

        /// <summary>
        /// Ссылка (для ресурсов типа link)
        /// </summary>
        public string Link { get; set; } = string.Empty;

        /// <summary>
        /// Дополнительный текст
        /// </summary>
        public string AdditionalText { get; set; } = string.Empty;

        /// <summary>
        /// Converts the FAQResource to a JSON-compatible object.
        /// </summary>
        /// <returns>A dictionary representing the FAQResource.</returns>
        public object ToJsonCompatible()
        {
            var result = new Dictionary<string, object>
            {
                ["type"] = Type,
                ["title"] = Title
            };

            if (Files?.Any() == true)
                result["files"] = Files;

            if (!string.IsNullOrEmpty(Link))
                result["link"] = Link;

            if (!string.IsNullOrEmpty(AdditionalText))
                result["additional_text"] = AdditionalText;

            return result;
        }

        /// <summary>
        /// Creates a FAQResource from JSON data.
        /// </summary>
        /// <param name="jsonData">The JSON data to deserialize.</param>
        /// <returns>A new FAQResource instance.</returns>
        public static FAQResource FromJson(dynamic jsonData)
        {
            return new FAQResource
            {
                Type = jsonData.type?.ToString() ?? string.Empty,
                Title = jsonData.title?.ToString() ?? string.Empty,
                Files = ((IEnumerable<dynamic>)jsonData.files)?.Select(f => (string)f).ToList() ?? new List<string>(),
                Link = jsonData.link?.ToString() ?? string.Empty,
                AdditionalText = jsonData.additional_text?.ToString() ?? string.Empty
            };
        }
    }

    /// <summary>
    /// Метаданные узла FAQ
    /// </summary>
    public class NodeMetadata
    {
        /// <summary>
        /// Тип источника данных
        /// </summary>
        public string SourceType { get; set; } = string.Empty;

        /// <summary>
        /// Уверенность в корректности данных (0.0 - 1.0)
        /// </summary>
        public double Confidence { get; set; } = 1.0;

        /// <summary>
        /// Дата создания
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Дата последнего обновления
        /// </summary>
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Хэш для обнаружения дубликатов
        /// </summary>
        public string Hash { get; set; } = string.Empty;

        /// <summary>
        /// Название группы (если узел принадлежит группе)
        /// </summary>
        public string GroupName { get; set; } = string.Empty;

        /// <summary>
        /// Исходный файл
        /// </summary>
        public string SourceFile { get; set; } = string.Empty;

        /// <summary>
        /// Количество обращений к узлу
        /// </summary>
        public int AccessCount { get; set; }

        /// <summary>
        /// Рейтинг полезности
        /// </summary>
        public double Usefulness { get; set; } = 0.5;

        /// <summary>
        /// Теги для классификации
        /// </summary>
        public List<string> Tags { get; set; } = new List<string>();

        /// <summary>
        /// Дополнительные свойства
        /// </summary>
        public Dictionary<string, object> ExtendedProperties { get; set; } = new Dictionary<string, object>();

        /// <summary>
        /// Creates a NodeMetadata from JSON data.
        /// </summary>
        /// <param name="jsonData">The JSON data to deserialize.</param>
        /// <returns>A new NodeMetadata instance.</returns>
        public static NodeMetadata FromJson(dynamic jsonData)
        {
            var metadata = new NodeMetadata();

            if (jsonData.source_type != null)
                metadata.SourceType = jsonData.source_type;

            if (jsonData.confidence != null)
                metadata.Confidence = (double)jsonData.confidence;

            // Handle both "created_at" and "processed_at" fields for compatibility
            if (jsonData.created_at != null)
            {
                if (DateTime.TryParse((string)jsonData.created_at, out var createdAt))
                {
                    metadata.CreatedAt = createdAt;
                }
            }
            else if (jsonData.processed_at != null)
            {
                if (DateTime.TryParse((string)jsonData.processed_at, out var processedAt))
                {
                    metadata.CreatedAt = processedAt;
                }
            }

            if (jsonData.hash != null)
                metadata.Hash = jsonData.hash;

            if (jsonData.group_name != null)
                metadata.GroupName = jsonData.group_name;

            return metadata;
        }
    }

    /// <summary>
    /// Связь между FAQ узлами
    /// </summary>
    public class FAQConnection : INotifyPropertyChanged
    {
        private double _strength;
        private ConnectionType _type;

        /// <summary>
        /// Уникальный идентификатор связи
        /// </summary>
        public Guid Id { get; set; } = Guid.NewGuid();

        /// <summary>
        /// Исходный узел
        /// </summary>
        public Guid SourceNodeId { get; set; }

        /// <summary>
        /// Целевой узел
        /// </summary>
        public Guid TargetNodeId { get; set; }

        /// <summary>
        /// Тип связи
        /// </summary>
        public ConnectionType Type
        {
            get => _type;
            set
            {
                _type = value;
                OnPropertyChanged(nameof(Type));
            }
        }

        /// <summary>
        /// Сила связи (0.0 - 1.0)
        /// </summary>
        public double Strength
        {
            get => _strength;
            set
            {
                _strength = Math.Max(0.0, Math.Min(1.0, value));
                OnPropertyChanged(nameof(Strength));
            }
        }

        /// <summary>
        /// Описание связи
        /// </summary>
        public string Description { get; set; } = string.Empty;

        /// <summary>
        /// Алгоритм, создавший связь
        /// </summary>
        public string CreatedByAlgorithm { get; set; } = string.Empty;

        /// <summary>
        /// Уверенность алгоритма в корректности связи
        /// </summary>
        public double AlgorithmConfidence { get; set; }

        /// <summary>
        /// Дата создания связи
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Подтверждена ли связь пользователем
        /// </summary>
        public bool IsUserConfirmed { get; set; }

        /// <summary>
        /// Дополнительные данные связи
        /// </summary>
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        /// <summary>
        /// Occurs when a property value changes.
        /// </summary>
        public event PropertyChangedEventHandler? PropertyChanged;

        /// <summary>
        /// Raises the PropertyChanged event.
        /// </summary>
        /// <param name="propertyName">The name of the property that changed.</param>
        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    /// <summary>
    /// Типы связей между FAQ узлами
    /// </summary>
    public enum ConnectionType
    {
        /// <summary>
        /// Семантическая похожесть
        /// </summary>
        Semantic,

        /// <summary>
        /// Пререквизит (требуется знание одного для понимания другого)
        /// </summary>
        Prerequisite,

        /// <summary>
        /// Продолжение (логическое продолжение темы)
        /// </summary>
        FollowUp,

        /// <summary>
        /// Связанная тема
        /// </summary>
        Related,

        /// <summary>
        /// Противоположность/конфликт
        /// </summary>
        Contradiction,

        /// <summary>
        /// Часть группы
        /// </summary>
        GroupMember,

        /// <summary>
        /// Дубликат
        /// </summary>
        Duplicate,

        /// <summary>
        /// Файловая зависимость
        /// </summary>
        FileReference,

        /// <summary>
        /// Пользовательская связь
        /// </summary>
        Custom
    }

    /// <summary>
    /// Алгоритмические свойства узла
    /// </summary>
    public class AlgorithmProperties
    {
        /// <summary>
        /// Семантический вектор для быстрого сравнения
        /// </summary>
        public float[] SemanticVector { get; set; } = new float[0];

        /// <summary>
        /// Ключевые слова, извлеченные алгоритмически
        /// </summary>
        public List<string> ExtractedKeywords { get; set; } = new List<string>();

        /// <summary>
        /// Оценка сложности вопроса (0.0 - 1.0)
        /// </summary>
        public double ComplexityScore { get; set; }

        /// <summary>
        /// Оценка популярности (на основе обращений)
        /// </summary>
        public double PopularityScore { get; set; }

        /// <summary>
        /// Языковые характеристики
        /// </summary>
        public LanguageFeatures Language { get; set; } = new LanguageFeatures();

        /// <summary>
        /// Кластер, к которому принадлежит узел
        /// </summary>
        public string ClusterId { get; set; } = string.Empty;

        /// <summary>
        /// Последний раз когда алгоритмы обновляли свойства
        /// </summary>
        public DateTime LastAlgorithmUpdate { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Языковые характеристики текста
    /// </summary>
    public class LanguageFeatures
    {
        /// <summary>
        /// Определенный язык
        /// </summary>
        public string DetectedLanguage { get; set; } = "ru";

        /// <summary>
        /// Уверенность в определении языка
        /// </summary>
        public double LanguageConfidence { get; set; } = 1.0;

        /// <summary>
        /// Тональность текста (-1.0 до 1.0)
        /// </summary>
        public double Sentiment { get; set; } = 0.0;

        /// <summary>
        /// Длина текста в символах
        /// </summary>
        public int TextLength { get; set; }

        /// <summary>
        /// Количество слов
        /// </summary>
        public int WordCount { get; set; }

        /// <summary>
        /// Уровень формальности (0.0 - 1.0)
        /// </summary>
        public double FormalityLevel { get; set; } = 0.5;
    }

    /// <summary>
    /// Поисковый индекс для быстрого поиска
    /// </summary>
    public class SearchIndex
    {
        /// <summary>
        /// Нормализованный текст для поиска
        /// </summary>
        public string NormalizedText { get; set; } = string.Empty;

        /// <summary>
        /// Все слова из запроса и вариантов
        /// </summary>
        public HashSet<string> Words { get; set; } = new HashSet<string>();

        /// <summary>
        /// Биграммы для нечеткого поиска
        /// </summary>
        public HashSet<string> Bigrams { get; set; } = new HashSet<string>();

        /// <summary>
        /// Частота слов для ранжирования
        /// </summary>
        public Dictionary<string, int> WordFrequencies { get; set; } = new Dictionary<string, int>();

        /// <summary>
        /// Векторное представление для семантического поиска
        /// </summary>
        public float[] VectorRepresentation { get; set; } = new float[0];
    }

    /// <summary>
    /// Группа FAQ узлов
    /// </summary>
    public class FAQGroup
    {
        /// <summary>
        /// Уникальный идентификатор группы
        /// </summary>
        public Guid Id { get; set; } = Guid.NewGuid();

        /// <summary>
        /// Название группы
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Описание группы
        /// </summary>
        public string Description { get; set; } = string.Empty;

        /// <summary>
        /// Узлы в группе
        /// </summary>
        public List<FAQNode> Nodes { get; set; } = new List<FAQNode>();

        /// <summary>
        /// Средняя семантическая схожесть узлов в группе
        /// </summary>
        public double AverageSimilarity { get; set; }

        /// <summary>
        /// Предлагаемый родительский вопрос для группы
        /// </summary>
        public string SuggestedParentQuery { get; set; } = string.Empty;

        /// <summary>
        /// Дата создания группы
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Алгоритм, создавший группу
        /// </summary>
        public string CreatedByAlgorithm { get; set; } = string.Empty;

        /// <summary>
        /// Подтверждена ли группа пользователем
        /// </summary>
        public bool IsUserConfirmed { get; set; }
    }
}