using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UniversalFAQLoader.Business.Models;

namespace UniversalFAQLoader.Data.Repositories
{
    /// <summary>
    /// Интерфейс репозитория для работы с FAQ данными
    /// </summary>
    public interface IFAQRepository
    {
        /// <summary>
        /// Получение узла FAQ по идентификатору
        /// </summary>
        /// <param name="id">The identifier.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ node as result.</returns>
        Task<FAQNode?> GetByIdAsync(Guid id);

        /// <summary>
        /// Получение всех узлов FAQ
        /// </summary>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        Task<IEnumerable<FAQNode>> GetAllAsync();

        /// <summary>
        /// Поиск узлов FAQ по запросу
        /// </summary>
        /// <param name="query">The query.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        Task<IEnumerable<FAQNode>> GetByQueryAsync(string query);

        /// <summary>
        /// Сохранение узла FAQ
        /// </summary>
        /// <param name="node">The node.</param>
        /// <returns>A task representing the asynchronous operation, with the saved FAQ node as result.</returns>
        Task<FAQNode> SaveAsync(FAQNode node);

        /// <summary>
        /// Удаление узла FAQ по идентификатору
        /// </summary>
        /// <param name="id">The identifier.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        Task DeleteAsync(Guid id);

        /// <summary>
        /// Получение узлов FAQ по алгоритму
        /// </summary>
        /// <param name="algorithmName">Name of the algorithm.</param>
        /// <param name="parameters">The parameters.</param>
        /// <returns>A task representing the asynchronous operation, with the FAQ nodes as result.</returns>
        Task<IEnumerable<FAQNode>> GetNodesByAlgorithmAsync(string algorithmName, object parameters);
    }
}