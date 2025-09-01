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
    /// Репозиторий для работы с FAQ данными в формате JSON
    /// Обеспечивает совместимость с существующей Python системой
    /// </summary>
    public class JsonFAQRepository : IFAQRepository
    {
        private readonly string _filePath;
        private readonly object _lock = new object();

        /// <summary>
        /// Initializes a new instance of the <see cref="JsonFAQRepository"/> class.
        /// </summary>
        /// <param name="filePath">The file path.</param>
        public JsonFAQRepository(string filePath)
        {
            _filePath = filePath ?? throw new ArgumentNullException(nameof(filePath));
            
            // Создание файла если не существует
            if (!File.Exists(_filePath))
            {
                File.WriteAllText(_filePath, "[]");
            }
        }

        #region IFAQRepository Implementation

        /// <summary>
        /// Gets a FAQ node by its ID asynchronously.
        /// </summary>
        /// <param name="id">The ID of the FAQ node to retrieve.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ node as result.</returns>
        public async Task<FAQNode?> GetByIdAsync(Guid id)
        {
            var nodes = await GetAllAsync();
            return nodes.FirstOrDefault(n => n.Id == id);
        }

        /// <summary>
        /// Gets all FAQ nodes asynchronously.
        /// </summary>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> GetAllAsync()
        {
            return await Task.Run(() =>
            {
                lock (_lock)
                {
                    if (!File.Exists(_filePath))
                        return new List<FAQNode>();

                    var json = File.ReadAllText(_filePath);
                    if (string.IsNullOrWhiteSpace(json))
                        return new List<FAQNode>();

                    var jsonArray = JsonConvert.DeserializeObject<dynamic[]>(json);
                    return jsonArray.Select(FAQNode.FromJson).Where(n => n != null).ToList();
                }
            });
        }

        /// <summary>
        /// Gets FAQ nodes by query asynchronously.
        /// </summary>
        /// <param name="query">The query to search for.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> GetByQueryAsync(string query)
        {
            var nodes = await GetAllAsync();
            var lowerQuery = query.ToLowerInvariant();
            
            return nodes.Where(n => 
                n.Query?.ToLowerInvariant().Contains(lowerQuery) == true ||
                n.Variations?.Any(v => v.ToLowerInvariant().Contains(lowerQuery)) == true ||
                n.Response?.ToLowerInvariant().Contains(lowerQuery) == true);
        }

        /// <summary>
        /// Saves a FAQ node asynchronously.
        /// </summary>
        /// <param name="node">The FAQ node to save.</param>
        /// <returns>A task representing the asynchronous operation, with the saved FAQ node as result.</returns>
        public async Task<FAQNode> SaveAsync(FAQNode node)
        {
            if (node == null)
                throw new ArgumentNullException(nameof(node));

            return await Task.Run(() =>
            {
                lock (_lock)
                {
                    var nodes = GetAllNodesFromFile();
                    
                    // Удаление существующего узла с таким же ID
                    nodes.RemoveAll(n => n.Id == node.Id);
                    
                    // Добавление нового узла
                    nodes.Add(node);
                    
                    // Сохранение в файл
                    SaveNodesToFile(nodes);
                    
                    return node;
                }
            });
        }

        /// <summary>
        /// Deletes a FAQ node by its ID asynchronously.
        /// </summary>
        /// <param name="id">The ID of the FAQ node to delete.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        public async Task DeleteAsync(Guid id)
        {
            await Task.Run(() =>
            {
                lock (_lock)
                {
                    var nodes = GetAllNodesFromFile();
                    nodes.RemoveAll(n => n.Id == id);
                    SaveNodesToFile(nodes);
                }
            });
        }

        /// <summary>
        /// Gets FAQ nodes by algorithm asynchronously.
        /// </summary>
        /// <param name="algorithmName">The name of the algorithm.</param>
        /// <param name="parameters">The parameters for the algorithm.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> GetNodesByAlgorithmAsync(string algorithmName, object parameters)
        {
            // Для JSON репозитория возвращаем все узлы
            return await GetAllAsync();
        }

        #endregion

        #region JSON Specific Methods

        /// <summary>
        /// Получение узлов по ключевым словам
        /// </summary>
        /// <param name="parameters">The parameters.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> GetByKeywordsAsync(object parameters)
        {
            if (parameters is not Dictionary<string, object> paramDict || 
                !paramDict.ContainsKey("keywords") || 
                paramDict["keywords"] is not string keywordsString)
            {
                return await GetAllAsync();
            }

            var keywords = keywordsString.Split(new[] { ' ', ',', ';' }, StringSplitOptions.RemoveEmptyEntries);
            var nodes = await GetAllAsync();
            
            return nodes.Where(n => 
                keywords.Any(k => 
                    n.Query?.ToLowerInvariant().Contains(k.ToLowerInvariant()) == true ||
                    n.Variations?.Any(v => v.ToLowerInvariant().Contains(k.ToLowerInvariant())) == true));
        }

        /// <summary>
        /// Экспорт узлов в файл
        /// </summary>
        /// <param name="nodes">The FAQ nodes to export.</param>
        /// <param name="filePath">The file path.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
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
        /// Импорт узлов из файла
        /// </summary>
        /// <param name="filePath">The file path.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        public async Task<IEnumerable<FAQNode>> ImportFromFileAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                if (!File.Exists(filePath))
                    throw new FileNotFoundException($"Файл {filePath} не найден");

                var json = File.ReadAllText(filePath);
                var jsonArray = JsonConvert.DeserializeObject<dynamic[]>(json);
                return jsonArray.Select(FAQNode.FromJson).Where(n => n != null).ToList();
            });
        }

        /// <summary>
        /// Получение статистики репозитория
        /// </summary>
        /// <returns>A task representing the asynchronous operation, with the statistics as result.</returns>
        public async Task<JsonRepositoryStatistics> GetStatisticsAsync()
        {
            return await Task.Run(() =>
            {
                var nodes = GetAllNodesFromFile();
                var fileInfo = new FileInfo(_filePath);
                
                return new JsonRepositoryStatistics
                {
                    NodeCount = nodes.Count,
                    FileSizeBytes = fileInfo.Length,
                    LastModified = fileInfo.LastWriteTime
                };
            });
        }

        #endregion

        #region Private Methods

        private List<FAQNode> GetAllNodesFromFile()
        {
            if (!File.Exists(_filePath))
                return new List<FAQNode>();

            var json = File.ReadAllText(_filePath);
            if (string.IsNullOrWhiteSpace(json))
                return new List<FAQNode>();

            try
            {
                var jsonArray = JsonConvert.DeserializeObject<dynamic[]>(json);
                return jsonArray?.Select(FAQNode.FromJson).Where(n => n != null).ToList() ?? new List<FAQNode>();
            }
            catch
            {
                return new List<FAQNode>();
            }
        }

        private void SaveNodesToFile(List<FAQNode> nodes)
        {
            var json = JsonConvert.SerializeObject(nodes.Select(n => n.ToJsonCompatible()), 
                                                 Formatting.Indented);
            File.WriteAllText(_filePath, json);
        }

        #endregion
    }
}