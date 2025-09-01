using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json;
using UniversalFAQLoader.Business.Models;

namespace UniversalFAQLoader.Data.Repositories
{
    /// <summary>
    /// Репозиторий для работы с FAQ данными в формате SQLite
    /// Обеспечивает высокую производительность для алгоритмов
    /// </summary>
    public class SqliteFAQRepository : IFAQRepository
    {
        private readonly string _connectionString;

        public SqliteFAQRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
            InitializeDatabase();
        }

        #region Database Initialization

        private void InitializeDatabase()
        {
            using var connection = new SQLiteConnection(_connectionString);
            connection.Open();

            using var command = new SQLiteCommand(connection);
            
            // Создание таблицы узлов FAQ
            command.CommandText = @"
                CREATE TABLE IF NOT EXISTS FAQNodes (
                    Id TEXT PRIMARY KEY,
                    Query TEXT NOT NULL,
                    Response TEXT NOT NULL,
                    Variations TEXT,
                    Resources TEXT,
                    Metadata TEXT,
                    SearchIndex TEXT,
                    AlgorithmProps TEXT,
                    CreatedAt TEXT,
                    UpdatedAt TEXT
                )";
            command.ExecuteNonQuery();

            // Создание таблицы связей
            command.CommandText = @"
                CREATE TABLE IF NOT EXISTS FAQConnections (
                    Id TEXT PRIMARY KEY,
                    SourceNodeId TEXT NOT NULL,
                    TargetNodeId TEXT NOT NULL,
                    Type TEXT NOT NULL,
                    Strength REAL NOT NULL,
                    Description TEXT,
                    CreatedByAlgorithm TEXT,
                    AlgorithmConfidence REAL,
                    CreatedAt TEXT,
                    IsUserConfirmed INTEGER
                )";
            command.ExecuteNonQuery();

            // Создание индексов для улучшения производительности
            command.CommandText = "CREATE INDEX IF NOT EXISTS idx_faqnodes_query ON FAQNodes(Query)";
            command.ExecuteNonQuery();

            command.CommandText = "CREATE INDEX IF NOT EXISTS idx_faqconnections_source ON FAQConnections(SourceNodeId)";
            command.ExecuteNonQuery();

            command.CommandText = "CREATE INDEX IF NOT EXISTS idx_faqconnections_target ON FAQConnections(TargetNodeId)";
            command.ExecuteNonQuery();
        }

        #endregion

        #region IFAQRepository Implementation

        public async Task<FAQNode?> GetByIdAsync(Guid id)
        {
            return await Task.Run(() =>
            {
                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                using var command = new SQLiteCommand(
                    "SELECT * FROM FAQNodes WHERE Id = @Id", connection);
                command.Parameters.AddWithValue("@Id", id.ToString());

                using var reader = command.ExecuteReader();
                if (reader.Read())
                {
                    return DeserializeFAQNode(reader);
                }

                return null;
            });
        }

        public async Task<IEnumerable<FAQNode>> GetAllAsync()
        {
            return await Task.Run(() =>
            {
                var nodes = new List<FAQNode>();

                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                using var command = new SQLiteCommand("SELECT * FROM FAQNodes", connection);
                using var reader = command.ExecuteReader();

                while (reader.Read())
                {
                    nodes.Add(DeserializeFAQNode(reader));
                }

                return nodes;
            });
        }

        public async Task<IEnumerable<FAQNode>> GetByQueryAsync(string query)
        {
            return await Task.Run(() =>
            {
                var nodes = new List<FAQNode>();
                var lowerQuery = query.ToLowerInvariant();

                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                using var command = new SQLiteCommand(
                    "SELECT * FROM FAQNodes WHERE LOWER(Query) LIKE @Query OR LOWER(Response) LIKE @Query", connection);
                command.Parameters.AddWithValue("@Query", $"%{lowerQuery}%");

                using var reader = command.ExecuteReader();

                while (reader.Read())
                {
                    nodes.Add(DeserializeFAQNode(reader));
                }

                return nodes;
            });
        }

        public async Task<FAQNode> SaveAsync(FAQNode node)
        {
            if (node == null)
                throw new ArgumentNullException(nameof(node));

            return await Task.Run(() =>
            {
                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                using var command = new SQLiteCommand(@"
                    INSERT OR REPLACE INTO FAQNodes 
                    (Id, Query, Response, Variations, Resources, Metadata, SearchIndex, AlgorithmProps, CreatedAt, UpdatedAt)
                    VALUES 
                    (@Id, @Query, @Response, @Variations, @Resources, @Metadata, @SearchIndex, @AlgorithmProps, @CreatedAt, @UpdatedAt)", connection);

                command.Parameters.AddWithValue("@Id", node.Id.ToString());
                command.Parameters.AddWithValue("@Query", node.Query);
                command.Parameters.AddWithValue("@Response", node.Response);
                command.Parameters.AddWithValue("@Variations", JsonConvert.SerializeObject(node.Variations));
                command.Parameters.AddWithValue("@Resources", JsonConvert.SerializeObject(node.Resources?.Select(r => r.ToJsonCompatible())));
                command.Parameters.AddWithValue("@Metadata", JsonConvert.SerializeObject(node.Metadata));
                command.Parameters.AddWithValue("@SearchIndex", JsonConvert.SerializeObject(new
                {
                    words = node.SearchIndex.Words.ToList(),
                    normalized_text = node.SearchIndex.NormalizedText,
                    word_frequencies = node.SearchIndex.WordFrequencies
                }));
                command.Parameters.AddWithValue("@AlgorithmProps", JsonConvert.SerializeObject(node.AlgorithmProps));
                command.Parameters.AddWithValue("@CreatedAt", DateTime.UtcNow.ToString("o"));
                command.Parameters.AddWithValue("@UpdatedAt", DateTime.UtcNow.ToString("o"));

                command.ExecuteNonQuery();

                return node;
            });
        }

        public async Task DeleteAsync(Guid id)
        {
            await Task.Run(() =>
            {
                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                // Удаление связей
                using (var command = new SQLiteCommand(
                    "DELETE FROM FAQConnections WHERE SourceNodeId = @Id OR TargetNodeId = @Id", connection))
                {
                    command.Parameters.AddWithValue("@Id", id.ToString());
                    command.ExecuteNonQuery();
                }

                // Удаление узла
                using (var command = new SQLiteCommand(
                    "DELETE FROM FAQNodes WHERE Id = @Id", connection))
                {
                    command.Parameters.AddWithValue("@Id", id.ToString());
                    command.ExecuteNonQuery();
                }
            });
        }

        public async Task<IEnumerable<FAQNode>> GetNodesByAlgorithmAsync(string algorithmName, object parameters)
        {
            // Для SQLite репозитория возвращаем все узлы
            return await GetAllAsync();
        }

        #endregion

        #region SQLite Specific Methods

        /// <summary>
        /// Получение узлов по семантическому запросу
        /// </summary>
        public async Task<IEnumerable<FAQNode>> GetBySemanticAsync(object parameters)
        {
            if (parameters is not Dictionary<string, object> paramDict)
            {
                return await GetAllAsync();
            }

            return await Task.Run(() =>
            {
                var nodes = new List<FAQNode>();

                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                // Семантический поиск по ключевым словам в SearchIndex
                using var command = new SQLiteCommand(
                    "SELECT * FROM FAQNodes WHERE SearchIndex LIKE @Keywords", connection);
                
                if (paramDict.ContainsKey("keywords") && paramDict["keywords"] is string keywordsString)
                {
                    var keywords = keywordsString.Split(new[] { ' ', ',', ';' }, StringSplitOptions.RemoveEmptyEntries);
                    var keywordPattern = string.Join(" OR ", keywords.Select(k => $"%{k}%"));
                    command.Parameters.AddWithValue("@Keywords", keywordPattern);
                }
                else
                {
                    command.Parameters.AddWithValue("@Keywords", "%");
                }

                using var reader = command.ExecuteReader();

                while (reader.Read())
                {
                    nodes.Add(DeserializeFAQNode(reader));
                }

                return nodes;
            });
        }

        /// <summary>
        /// Получение связанных узлов
        /// </summary>
        public async Task<IEnumerable<FAQConnection>> GetConnectedNodesAsync(object parameters)
        {
            return await Task.Run(() =>
            {
                var connections = new List<FAQConnection>();

                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                using var command = new SQLiteCommand("SELECT * FROM FAQConnections", connection);
                using var reader = command.ExecuteReader();

                while (reader.Read())
                {
                    connections.Add(new FAQConnection
                    {
                        Id = Guid.Parse(reader["Id"].ToString() ?? Guid.NewGuid().ToString()),
                        SourceNodeId = Guid.Parse(reader["SourceNodeId"].ToString() ?? Guid.Empty.ToString()),
                        TargetNodeId = Guid.Parse(reader["TargetNodeId"].ToString() ?? Guid.Empty.ToString()),
                        Type = Enum.TryParse<ConnectionType>(reader["Type"]?.ToString(), out var type) ? type : ConnectionType.Semantic,
                        Strength = Convert.ToDouble(reader["Strength"] ?? 0.0),
                        Description = reader["Description"]?.ToString(),
                        CreatedByAlgorithm = reader["CreatedByAlgorithm"]?.ToString(),
                        AlgorithmConfidence = Convert.ToDouble(reader["AlgorithmConfidence"] ?? 0.0),
                        CreatedAt = DateTime.TryParse(reader["CreatedAt"]?.ToString(), out var date) ? date : DateTime.UtcNow,
                        IsUserConfirmed = Convert.ToBoolean(reader["IsUserConfirmed"] ?? false)
                    });
                }

                return connections;
            });
        }

        /// <summary>
        /// Создание связей между узлами
        /// </summary>
        public async Task CreateConnectionsAsync(IEnumerable<FAQConnection> connections)
        {
            await Task.Run(() =>
            {
                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                using var transaction = connection.BeginTransaction();

                try
                {
                    foreach (var connectionObj in connections)
                    {
                        using var command = new SQLiteCommand(@"
                            INSERT OR REPLACE INTO FAQConnections 
                            (Id, SourceNodeId, TargetNodeId, Type, Strength, Description, CreatedByAlgorithm, AlgorithmConfidence, CreatedAt, IsUserConfirmed)
                            VALUES 
                            (@Id, @SourceNodeId, @TargetNodeId, @Type, @Strength, @Description, @CreatedByAlgorithm, @AlgorithmConfidence, @CreatedAt, @IsUserConfirmed)", connection);

                        command.Parameters.AddWithValue("@Id", connectionObj.Id.ToString());
                        command.Parameters.AddWithValue("@SourceNodeId", connectionObj.SourceNodeId.ToString());
                        command.Parameters.AddWithValue("@TargetNodeId", connectionObj.TargetNodeId.ToString());
                        command.Parameters.AddWithValue("@Type", connectionObj.Type.ToString());
                        command.Parameters.AddWithValue("@Strength", connectionObj.Strength);
                        command.Parameters.AddWithValue("@Description", connectionObj.Description ?? "");
                        command.Parameters.AddWithValue("@CreatedByAlgorithm", connectionObj.CreatedByAlgorithm ?? "");
                        command.Parameters.AddWithValue("@AlgorithmConfidence", connectionObj.AlgorithmConfidence);
                        command.Parameters.AddWithValue("@CreatedAt", connectionObj.CreatedAt.ToString("o"));
                        command.Parameters.AddWithValue("@IsUserConfirmed", connectionObj.IsUserConfirmed);

                        command.ExecuteNonQuery();
                    }

                    transaction.Commit();
                }
                catch
                {
                    transaction.Rollback();
                    throw;
                }
            });
        }

        /// <summary>
        /// Экспорт данных в файл
        /// </summary>
        public async Task ExportToFileAsync(IEnumerable<FAQNode> nodes, string filePath)
        {
            await Task.Run(() =>
            {
                var json = JsonConvert.SerializeObject(nodes.Select(n => n.ToJsonCompatible()), 
                                                     Formatting.Indented);
                File.WriteAllText(filePath, json);
            });
        }

        /// <summary>
        /// Получение статистики репозитория
        /// </summary>
        public async Task<SqliteRepositoryStatistics> GetStatisticsAsync()
        {
            return await Task.Run(() =>
            {
                using var connection = new SQLiteConnection(_connectionString);
                connection.Open();

                // Получение количества узлов
                using var countCommand = new SQLiteCommand("SELECT COUNT(*) FROM FAQNodes", connection);
                var nodeCount = Convert.ToInt32(countCommand.ExecuteScalar());

                // Получение размера файла базы данных
                var dbPath = _connectionString.Replace("Data Source=", "");
                var fileInfo = new FileInfo(dbPath);
                var fileSize = fileInfo.Exists ? fileInfo.Length : 0;

                return new SqliteRepositoryStatistics
                {
                    NodeCount = nodeCount,
                    DatabaseSizeBytes = fileSize,
                    LastModified = fileInfo.Exists ? fileInfo.LastWriteTime : DateTime.MinValue
                };
            });
        }

        #endregion

        #region Private Methods

        private FAQNode DeserializeFAQNode(SQLiteDataReader reader)
        {
            var node = new FAQNode
            {
                Id = Guid.Parse(reader["Id"]?.ToString() ?? Guid.NewGuid().ToString()),
                Query = reader["Query"]?.ToString() ?? "",
                Response = reader["Response"]?.ToString() ?? ""
            };

            // Десериализация вариаций
            if (reader["Variations"] != DBNull.Value && reader["Variations"] != null)
            {
                try
                {
                    var variationsJson = reader["Variations"]?.ToString();
                    if (!string.IsNullOrEmpty(variationsJson))
                    {
                        node.Variations = JsonConvert.DeserializeObject<List<string>>(variationsJson) ?? new List<string>();
                    }
                }
                catch
                {
                    node.Variations = new List<string>();
                }
            }

            // Десериализация ресурсов
            if (reader["Resources"] != DBNull.Value && reader["Resources"] != null)
            {
                try
                {
                    var resourcesJson = reader["Resources"]?.ToString();
                    if (!string.IsNullOrEmpty(resourcesJson))
                    {
                        var resourcesData = JsonConvert.DeserializeObject<List<dynamic>>(resourcesJson);
                        var resources = new List<FAQResource>();
                        if (resourcesData != null)
                        {
                            foreach (var data in resourcesData)
                            {
                                try
                                {
                                    resources.Add(FAQResource.FromJson(data));
                                }
                                catch
                                {
                                    // Игнорируем ошибки десериализации отдельных ресурсов
                                }
                            }
                        }
                        node.Resources = resources;
                    }
                }
                catch
                {
                    node.Resources = new List<FAQResource>();
                }
            }

            // Десериализация метаданных
            if (reader["Metadata"] != DBNull.Value && reader["Metadata"] != null)
            {
                try
                {
                    var metadataJson = reader["Metadata"]?.ToString();
                    if (!string.IsNullOrEmpty(metadataJson))
                    {
                        var metadataData = JsonConvert.DeserializeObject<dynamic>(metadataJson);
                        node.Metadata = NodeMetadata.FromJson(metadataData);
                    }
                }
                catch
                {
                    node.Metadata = new NodeMetadata();
                }
            }

            // Десериализация поискового индекса
            if (reader["SearchIndex"] != DBNull.Value && reader["SearchIndex"] != null)
            {
                try
                {
                    var searchJson = reader["SearchIndex"]?.ToString();
                    if (!string.IsNullOrEmpty(searchJson))
                    {
                        var searchData = JsonConvert.DeserializeObject<dynamic>(searchJson);
                        node.SearchIndex = new SearchIndex
                        {
                            Words = searchData?.words != null ? new HashSet<string>(searchData.words?.ToObject<List<string>>() ?? new List<string>()) : new HashSet<string>(),
                            NormalizedText = searchData?.normalized_text?.ToString() ?? "",
                            WordFrequencies = searchData?.word_frequencies != null ? searchData.word_frequencies?.ToObject<Dictionary<string, int>>() ?? new Dictionary<string, int>() : new Dictionary<string, int>()
                        };
                    }
                }
                catch
                {
                    node.SearchIndex = new SearchIndex();
                }
            }

            // Десериализация алгоритмических свойств
            if (reader["AlgorithmProps"] != DBNull.Value && reader["AlgorithmProps"] != null)
            {
                try
                {
                    var algoJson = reader["AlgorithmProps"]?.ToString();
                    if (!string.IsNullOrEmpty(algoJson))
                    {
                        var algoData = JsonConvert.DeserializeObject<dynamic>(algoJson);
                        DateTime lastUpdate = DateTime.UtcNow;
                        var lastUpdateStr = algoData.last_algorithm_update?.ToString();
                        if (!string.IsNullOrEmpty(lastUpdateStr))
                        {
                            DateTime parsedDate;
                            if (DateTime.TryParse(lastUpdateStr, out parsedDate))
                            {
                                lastUpdate = parsedDate;
                            }
                        }
                        
                        node.AlgorithmProps = new AlgorithmProperties
                        {
                            ComplexityScore = (double)(algoData.complexity_score ?? 0.0),
                            PopularityScore = (double)(algoData.popularity_score ?? 0.0),
                            ClusterId = algoData.cluster_id?.ToString() ?? "",
                            LastAlgorithmUpdate = lastUpdate
                        };
                    }
                }
                catch
                {
                    node.AlgorithmProps = new AlgorithmProperties();
                }
            }

            return node;
        }

        #endregion
    }
}