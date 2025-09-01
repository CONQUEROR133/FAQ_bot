using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json;
using UniversalFAQLoader.Business.Models;

namespace UniversalFAQLoader.Data.Repositories
{
    /// <summary>
    /// Гибридный репозиторий для FAQ данных
    /// Поддерживает несколько форматов хранения: JSON, SQLite, Graph DB
    /// </summary>
    public class HybridFAQRepository : IFAQRepository
    {
        private readonly string _jsonFilePath;
        private readonly string _sqliteConnectionString;
        // private readonly string _graphDbConnectionString;
        private readonly JsonFAQRepository _jsonRepository;
        private readonly SqliteFAQRepository _sqliteRepository;
        // private readonly GraphFAQRepository _graphRepository;

        /// <summary>
        /// Initializes a new instance of the <see cref="HybridFAQRepository"/> class.
        /// </summary>
        /// <param name="dataDirectory">The data directory path.</param>
        public HybridFAQRepository(string dataDirectory = "../../../data")
        {
            // Инициализация путей для существующего faq_bot проекта
            _jsonFilePath = Path.Combine(dataDirectory, "faq.json");
            _sqliteConnectionString = $"Data Source={Path.Combine(dataDirectory, "analytics.db")}";
            // _graphDbConnectionString = $"neo4j://localhost:7687"; // Пример подключения к Neo4j

            // Создание директории если не существует
            Directory.CreateDirectory(dataDirectory);

            // Инициализация репозиториев
            _jsonRepository = new JsonFAQRepository(_jsonFilePath);
            _sqliteRepository = new SqliteFAQRepository(_sqliteConnectionString);
            // _graphRepository = new GraphFAQRepository(_graphDbConnectionString);
        }

        #region IFAQRepository Implementation

        /// <summary>
        /// Gets a FAQ node by its ID asynchronously.
        /// </summary>
        /// <param name="id">The ID of the FAQ node to retrieve.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ node as result.</returns>
        public async Task<FAQNode?> GetByIdAsync(Guid id)
        {
            // Приоритет: Graph DB -> SQLite -> JSON
            /*try { return await _graphRepository.GetByIdAsync(id); }
            catch { /* Игнорируем ошибки и пробуем следующий репозиторий */ //}*/
            
            try { return await _sqliteRepository.GetByIdAsync(id); }
            catch { /* Игнорируем ошибки и пробуем следующий репозиторий */ }
            
            return await _jsonRepository.GetByIdAsync(id);
        }

        /// <summary>
        /// Gets all FAQ nodes asynchronously.
        /// </summary>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> GetAllAsync()
        {
            // Приоритет: Graph DB -> SQLite -> JSON
            /*try { return await _graphRepository.GetAllAsync(); }
            catch { /* Игнорируем ошибки и пробуем следующий репозиторий */ //}*/
            
            try 
            { 
                var sqliteNodes = await _sqliteRepository.GetAllAsync();
                // Only return SQLite data if it's not empty
                if (sqliteNodes.Any())
                    return sqliteNodes;
            }
            catch 
            { 
                // Игнорируем ошибки и пробуем следующий репозиторий
            }
            
            // Always fall back to JSON repository
            return await _jsonRepository.GetAllAsync();
        }

        /// <summary>
        /// Gets FAQ nodes by query asynchronously.
        /// </summary>
        /// <param name="query">The query to search for.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> GetByQueryAsync(string query)
        {
            // Поиск во всех репозиториях
            var results = new List<FAQNode>();
            
            /*try { results.AddRange(await _graphRepository.GetByQueryAsync(query)); }
            catch { /* Игнорируем ошибки */ //}*/
            
            try { results.AddRange(await _sqliteRepository.GetByQueryAsync(query)); }
            catch { /* Игнорируем ошибки */ }
            
            try { results.AddRange(await _jsonRepository.GetByQueryAsync(query)); }
            catch { /* Игнорируем ошибки */ }
            
            // Удаление дубликатов по ID
            return results.GroupBy(n => n.Id).Select(g => g.First());
        }

        /// <summary>
        /// Saves a FAQ node asynchronously.
        /// </summary>
        /// <param name="node">The FAQ node to save.</param>
        /// <returns>A task representing the asynchronous operation, with the saved FAQ node as result.</returns>
        public async Task<FAQNode> SaveAsync(FAQNode node)
        {
            // Параллельное сохранение во все доступные репозитории
            var tasks = new List<Task>();
            
            // Всегда сохраняем в JSON для совместимости
            tasks.Add(_jsonRepository.SaveAsync(node));
            
            // Сохраняем в SQLite если доступно
            try { tasks.Add(_sqliteRepository.SaveAsync(node)); }
            catch { /* Игнорируем ошибки SQLite */ }
            
            // Сохраняем в Graph DB если доступно
            /*try { tasks.Add(_graphRepository.SaveAsync(node)); }
            catch { /* Игнорируем ошибки Graph DB */ //}*/
            
            // Выполняем все операции параллельно
            await Task.WhenAll(tasks);
            
            return node;
        }

        /// <summary>
        /// Deletes a FAQ node by its ID asynchronously.
        /// </summary>
        /// <param name="id">The ID of the FAQ node to delete.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        public async Task DeleteAsync(Guid id)
        {
            // Удаление из всех репозиториев
            var tasks = new List<Task>
            {
                _jsonRepository.DeleteAsync(id)
            };
            
            try { tasks.Add(_sqliteRepository.DeleteAsync(id)); }
            catch { /* Игнорируем ошибки */ }
            
            /*try { tasks.Add(_graphRepository.DeleteAsync(id)); }
            catch { /* Игнорируем ошибки */ //}*/
            
            await Task.WhenAll(tasks);
        }

        /// <summary>
        /// Gets FAQ nodes by algorithm asynchronously.
        /// </summary>
        /// <param name="algorithmName">The name of the algorithm.</param>
        /// <param name="parameters">The parameters for the algorithm.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> GetNodesByAlgorithmAsync(string algorithmName, object parameters)
        {
            // Выбор репозитория в зависимости от алгоритма
            return algorithmName switch
            {
                // "DependencyAnalysis" => await _graphRepository.GetConnectedNodesAsync(parameters),
                "SemanticSearch" => await _sqliteRepository.GetBySemanticAsync(parameters),
                "KeywordSearch" => await _jsonRepository.GetByKeywordsAsync(parameters),
                _ => await GetAllAsync()
            };
        }

        #endregion

        #region Migration Methods

        /// <summary>
        /// Миграция данных из JSON в другие форматы
        /// </summary>
        /// <returns>A task representing the asynchronous operation.</returns>
        public async Task MigrateFromJsonAsync()
        {
            var nodes = await _jsonRepository.GetAllAsync();
            
            // Миграция в SQLite
            try
            {
                foreach (var node in nodes)
                {
                    await _sqliteRepository.SaveAsync(node);
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Ошибка миграции в SQLite", ex);
            }
            
            // Миграция в Graph DB
            /*try
            {
                foreach (var node in nodes)
                {
                    await _graphRepository.SaveAsync(node);
                }
                
                // Создание связей между узлами
                await _graphRepository.CreateConnectionsAsync(nodes.SelectMany(n => n.Connections));
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Ошибка миграции в Graph DB", ex);
            }*/
        }

        /// <summary>
        /// Экспорт данных в определенный формат
        /// </summary>
        /// <param name="format">The storage format.</param>
        /// <param name="filePath">The file path.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        public async Task ExportToFormatAsync(StorageFormat format, string filePath)
        {
            var nodes = await GetAllAsync();
            
            switch (format)
            {
                case StorageFormat.Json:
                    await _jsonRepository.ExportToFileAsync(nodes, filePath);
                    break;
                    
                case StorageFormat.Sqlite:
                    await _sqliteRepository.ExportToFileAsync(nodes, filePath);
                    break;
                    
                case StorageFormat.GraphDb:
                    // await _graphRepository.ExportToFileAsync(nodes, filePath);
                    break;
                    
                case StorageFormat.Csv:
                    await ExportToCsvAsync(nodes, filePath);
                    break;
                    
                default:
                    throw new ArgumentException($"Неподдерживаемый формат: {format}");
            }
        }

        /// <summary>
        /// Экспорт в CSV формат
        /// </summary>
        /// <param name="nodes">The FAQ nodes to export.</param>
        /// <param name="filePath">The file path.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        private async Task ExportToCsvAsync(IEnumerable<FAQNode> nodes, string filePath)
        {
            await Task.Run(() =>
            {
                var csvLines = new List<string>
                {
                    "Query,Response,Variations,SourceType,Confidence" // Заголовок
                };
                
                csvLines.AddRange(nodes.Select(node => 
                    $"\"{node.Query}\",\"{node.Response}\",\"{string.Join("; ", node.Variations)}\",\"{node.Metadata.SourceType}\",\"{node.Metadata.Confidence}\""));
                
                File.WriteAllLines(filePath, csvLines);
            });
        }

        /// <summary>
        /// Получение статистики по всем репозиториям
        /// </summary>
        /// <returns>A task representing the asynchronous operation, with the statistics as result.</returns>
        public async Task<HybridRepositoryStatistics> GetStatisticsAsync()
        {
            var stats = new HybridRepositoryStatistics();
            
            try { stats.JsonStats = await _jsonRepository.GetStatisticsAsync(); }
            catch { /* Игнорируем ошибки */ }
            
            try { stats.SqliteStats = await _sqliteRepository.GetStatisticsAsync(); }
            catch { /* Игнорируем ошибки */ }
            
            /*try { stats.GraphStats = await _graphRepository.GetStatisticsAsync(); }
            catch { /* Игнорируем ошибки */ //}*/
            
            return stats;
        }

        #endregion
    }

    /// <summary>
    /// Статистика гибридного репозитория
    /// </summary>
    public class HybridRepositoryStatistics
    {
        /// <summary>
        /// Gets or sets the JSON statistics.
        /// </summary>
        public JsonRepositoryStatistics? JsonStats { get; set; }

        /// <summary>
        /// Gets or sets the SQLite statistics.
        /// </summary>
        public SqliteRepositoryStatistics? SqliteStats { get; set; }

        /// <summary>
        /// Gets or sets the Graph DB statistics.
        /// </summary>
        public GraphRepositoryStatistics? GraphStats { get; set; }
    }

    /// <summary>
    /// Статистика JSON репозитория
    /// </summary>
    public class JsonRepositoryStatistics
    {
        /// <summary>
        /// Gets or sets the node count.
        /// </summary>
        public int NodeCount { get; set; }

        /// <summary>
        /// Gets or sets the file size in bytes.
        /// </summary>
        public long FileSizeBytes { get; set; }

        /// <summary>
        /// Gets or sets the last modified date.
        /// </summary>
        public DateTime LastModified { get; set; }
    }

    /// <summary>
    /// Статистика SQLite репозитория
    /// </summary>
    public class SqliteRepositoryStatistics
    {
        /// <summary>
        /// Gets or sets the node count.
        /// </summary>
        public int NodeCount { get; set; }

        /// <summary>
        /// Gets or sets the database size in bytes.
        /// </summary>
        public long DatabaseSizeBytes { get; set; }

        /// <summary>
        /// Gets or sets the last modified date.
        /// </summary>
        public DateTime LastModified { get; set; }
    }

    /// <summary>
    /// Статистика Graph репозитория
    /// </summary>
    public class GraphRepositoryStatistics
    {
        /// <summary>
        /// Gets or sets the node count.
        /// </summary>
        public int NodeCount { get; set; }

        /// <summary>
        /// Gets or sets the connection count.
        /// </summary>
        public int ConnectionCount { get; set; }

        /// <summary>
        /// Gets or sets the cluster count.
        /// </summary>
        public int ClusterCount { get; set; }

        /// <summary>
        /// Gets or sets the last modified date.
        /// </summary>
        public DateTime LastModified { get; set; }
    }

    /// <summary>
    /// Форматы хранения данных
    /// </summary>
    public enum StorageFormat
    {
        /// <summary>
        /// JSON format
        /// </summary>
        Json,

        /// <summary>
        /// SQLite format
        /// </summary>
        Sqlite,

        /// <summary>
        /// Graph database format
        /// </summary>
        GraphDb,

        /// <summary>
        /// CSV format
        /// </summary>
        Csv
    }
}