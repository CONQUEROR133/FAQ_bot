using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Input;
using UniversalFAQLoader.Business.Models;
using UniversalFAQLoader.Business.Algorithms;
using UniversalFAQLoader.Business.Services;
using UniversalFAQLoader.Data.Repositories;

namespace UniversalFAQLoader.Presentation.ViewModels
{
    /// <summary>
    /// Главная ViewModel для управления FAQ с алгоритмами
    /// </summary>
    public class MainViewModel : INotifyPropertyChanged
    {
        private readonly FAQAlgorithmService _algorithmService;
        private readonly HybridFAQRepository _repository;
        private ObservableCollection<FAQNode> _faqNodes;
        private ObservableCollection<AlgorithmViewModel> _algorithms;
        private AlgorithmExecutionResult? _lastExecutionResult;
        private string _statusMessage = string.Empty;
        private int _progressPercentage;
        private bool _isProcessing;

        /// <summary>
        /// Initializes a new instance of the <see cref="MainViewModel"/> class.
        /// </summary>
        public MainViewModel()
        {
            _algorithmService = new FAQAlgorithmService();
            _repository = new HybridFAQRepository("../../../data");
            _faqNodes = new ObservableCollection<FAQNode>();
            _algorithms = new ObservableCollection<AlgorithmViewModel>();
            
            InitializeCommands();
            LoadAlgorithms();
            
            // Load existing data from the faq.json file
            _ = LoadExistingFAQDataAsync();
        }

        #region Properties

        /// <summary>
        /// Gets or sets the FAQ nodes.
        /// </summary>
        public ObservableCollection<FAQNode> FAQNodes
        {
            get => _faqNodes;
            set
            {
                _faqNodes = value;
                OnPropertyChanged(nameof(FAQNodes));
                OnPropertyChanged(nameof(CanExecuteAlgorithms));
            }
        }

        /// <summary>
        /// Gets or sets the algorithms.
        /// </summary>
        public ObservableCollection<AlgorithmViewModel> Algorithms
        {
            get => _algorithms;
            set
            {
                _algorithms = value;
                OnPropertyChanged(nameof(Algorithms));
            }
        }

        /// <summary>
        /// Gets or sets the last execution result.
        /// </summary>
        public AlgorithmExecutionResult? LastExecutionResult
        {
            get => _lastExecutionResult;
            set
            {
                _lastExecutionResult = value;
                OnPropertyChanged(nameof(LastExecutionResult));
                OnPropertyChanged(nameof(HasExecutionResult));
                // Update graph when execution result changes
                UpdateGraphData();
            }
        }

        /// <summary>
        /// Gets a value indicating whether there is an execution result.
        /// </summary>
        public bool HasExecutionResult => _lastExecutionResult != null;

        /// <summary>
        /// Gets or sets the status message.
        /// </summary>
        public string StatusMessage
        {
            get => _statusMessage;
            set
            {
                _statusMessage = value ?? string.Empty;
                OnPropertyChanged(nameof(StatusMessage));
            }
        }

        /// <summary>
        /// Gets or sets the progress percentage.
        /// </summary>
        public int ProgressPercentage
        {
            get => _progressPercentage;
            set
            {
                _progressPercentage = value;
                OnPropertyChanged(nameof(ProgressPercentage));
            }
        }

        /// <summary>
        /// Gets or sets a value indicating whether processing is in progress.
        /// </summary>
        public bool IsProcessing
        {
            get => _isProcessing;
            set
            {
                _isProcessing = value;
                OnPropertyChanged(nameof(IsProcessing));
                OnPropertyChanged(nameof(CanExecuteAlgorithms));
            }
        }

        /// <summary>
        /// Gets a value indicating whether algorithms can be executed.
        /// </summary>
        public bool CanExecuteAlgorithms => !IsProcessing && FAQNodes != null && FAQNodes.Any();

        #endregion

        #region Commands

        /// <summary>
        /// Gets the execute all algorithms command.
        /// </summary>
        public ICommand ExecuteAllAlgorithmsCommand { get; private set; } = null!;

        /// <summary>
        /// Gets the load FAQ data command.
        /// </summary>
        public ICommand LoadFAQDataCommand { get; private set; } = null!;

        /// <summary>
        /// Gets the clear FAQ data command.
        /// </summary>
        public ICommand ClearFAQDataCommand { get; private set; } = null!;

        /// <summary>
        /// Gets the toggle algorithm command.
        /// </summary>
        public ICommand ToggleAlgorithmCommand { get; private set; } = null!;

        private void InitializeCommands()
        {
            ExecuteAllAlgorithmsCommand = new RelayCommand(async () => await ExecuteAllAlgorithmsAsync(), () => CanExecuteAlgorithms);
            LoadFAQDataCommand = new RelayCommand(async () => await LoadFAQDataAsync());
            ClearFAQDataCommand = new RelayCommand(ClearFAQData, () => FAQNodes.Any());
            ToggleAlgorithmCommand = new RelayCommand<string>(ToggleAlgorithm);
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Executes all algorithms asynchronously.
        /// </summary>
        /// <returns>A task representing the asynchronous operation.</returns>
        public async Task ExecuteAllAlgorithmsAsync()
        {
            if (!FAQNodes.Any())
            {
                StatusMessage = "Нет данных для обработки. Сначала загрузите данные из файла faq.json";
                return;
            }

            IsProcessing = true;
            StatusMessage = "Начинаем выполнение алгоритмов...";
            ProgressPercentage = 0;

            try
            {
                var progress = new Progress<AlgorithmProgress>(ReportProgress);
                var result = await _algorithmService.ExecuteAllAlgorithmsAsync(FAQNodes, progress);

                LastExecutionResult = result;
                StatusMessage = result.OverallSuccess 
                    ? $"Алгоритмы выполнены успешно! Найдено {result.AllConnections?.Count() ?? 0} связей" 
                    : "Выполнение алгоритмов завершено с ошибками";

                // Обновляем список узлов если алгоритмы внесли изменения
                if (result.Results?.Any(r => r.ProcessedNodes != null) == true)
                {
                    var processedNodes = result.Results.Where(r => r.ProcessedNodes != null).SelectMany(r => r.ProcessedNodes!).Distinct();
                    FAQNodes = new ObservableCollection<FAQNode>(processedNodes);
                }
                
                // Сохраняем результаты в репозиторий
                await SaveResultsToRepository(result);
            }
            catch (Exception ex)
            {
                StatusMessage = $"Ошибка выполнения алгоритмов: {ex.Message}";
                if (ex.InnerException != null)
                {
                    StatusMessage += $" ({ex.InnerException.Message})";
                }
            }
            finally
            {
                IsProcessing = false;
            }
        }

        private async Task SaveResultsToRepository(AlgorithmExecutionResult result)
        {
            try
            {
                // Сохраняем обновленные узлы в репозиторий
                foreach (var node in FAQNodes)
                {
                    await _repository.SaveAsync(node);
                }
                
                StatusMessage += " Результаты сохранены.";
            }
            catch (Exception ex)
            {
                StatusMessage += $" Ошибка сохранения: {ex.Message}";
            }
        }

        private async void LoadExistingFAQData()
        {
            try
            {
                // Автоматически загружаем данные при запуске
                await LoadFAQDataAsync();
            }
            catch (Exception ex)
            {
                StatusMessage = $"Ошибка автоматической загрузки: {ex.Message}";
            }
        }

        private async Task LoadExistingFAQDataAsync()
        {
            try
            {
                // Автоматически загружаем данные при запуске
                await LoadFAQDataAsync();
            }
            catch (Exception ex)
            {
                StatusMessage = $"Ошибка автоматической загрузки: {ex.Message}";
            }
        }

        /// <summary>
        /// Loads FAQ data asynchronously.
        /// </summary>
        /// <returns>A task representing the asynchronous operation.</returns>
        public async Task LoadFAQDataAsync()
        {
            StatusMessage = "Загрузка данных FAQ...";
            
            try
            {
                // Загружаем данные из существующего файла faq.json
                var nodes = await _repository.GetAllAsync();
                FAQNodes = new ObservableCollection<FAQNode>(nodes);
                
                StatusMessage = $"Загружено {FAQNodes.Count} FAQ записей";
                
                // If we have data, enable the algorithms
                if (FAQNodes.Any())
                {
                    StatusMessage += " - готовы к выполнению алгоритмов";
                }
                else
                {
                    StatusMessage += " - нет данных для обработки";
                }
                
                OnPropertyChanged(nameof(CanExecuteAlgorithms));
            }
            catch (Exception ex)
            {
                StatusMessage = $"Ошибка загрузки данных: {ex.Message}";
                if (ex.InnerException != null)
                {
                    StatusMessage += $" ({ex.InnerException.Message})";
                }
            }
        }

        /// <summary>
        /// Clears FAQ data.
        /// </summary>
        public void ClearFAQData()
        {
            FAQNodes.Clear();
            LastExecutionResult = null;
            StatusMessage = "Данные очищены";
            OnPropertyChanged(nameof(CanExecuteAlgorithms));
        }

        /// <summary>
        /// Toggles an algorithm.
        /// </summary>
        /// <param name="algorithmName">The name of the algorithm to toggle.</param>
        public void ToggleAlgorithm(string algorithmName)
        {
            var algorithm = Algorithms.FirstOrDefault(a => a.Name == algorithmName);
            if (algorithm != null)
            {
                algorithm.IsEnabled = !algorithm.IsEnabled;
            }
        }

        private void LoadAlgorithms()
        {
            // Загрузка доступных алгоритмов
            Algorithms = new ObservableCollection<AlgorithmViewModel>
            {
                new AlgorithmViewModel
                {
                    Name = "DependencyAnalyzer",
                    Description = "Анализ зависимостей между узлами FAQ",
                    Version = "1.0",
                    IsEnabled = true,
                    Configuration = new AlgorithmConfiguration()
                },
                new AlgorithmViewModel
                {
                    Name = "SemanticGrouper",
                    Description = "Семантическая группировка узлов FAQ",
                    Version = "1.0",
                    IsEnabled = true,
                    Configuration = new AlgorithmConfiguration()
                },
                new AlgorithmViewModel
                {
                    Name = "SmartLinker",
                    Description = "Умное связывание узлов FAQ",
                    Version = "1.0",
                    IsEnabled = true, // Включаем по умолчанию
                    Configuration = new AlgorithmConfiguration()
                },
                new AlgorithmViewModel
                {
                    Name = "ResponseOptimizer",
                    Description = "Оптимизация ответов FAQ",
                    Version = "1.0",
                    IsEnabled = true,
                    Configuration = new AlgorithmConfiguration()
                }
            };
        }

        private void ReportProgress(AlgorithmProgress progress)
        {
            ProgressPercentage = progress.PercentageComplete;
            StatusMessage = progress.CurrentOperation;
        }

        private void UpdateGraphData()
        {
            // Уведомляем о необходимости обновления графа
            OnPropertyChanged(nameof(LastExecutionResult));
        }

        #endregion

        #region INotifyPropertyChanged

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
            
            // Обновляем состояние команд при изменении свойств
            if (propertyName == nameof(IsProcessing) || propertyName == nameof(FAQNodes))
            {
                if (ExecuteAllAlgorithmsCommand is RelayCommand relayCommand)
                {
                    relayCommand.RaiseCanExecuteChanged();
                }
                
                if (ClearFAQDataCommand is RelayCommand clearCommand)
                {
                    clearCommand.RaiseCanExecuteChanged();
                }
            }
        }

        #endregion
    }

    /// <summary>
    /// ViewModel для отдельного алгоритма
    /// </summary>
    public class AlgorithmViewModel : INotifyPropertyChanged
    {
        private string _name = string.Empty;
        private string _description = string.Empty;
        private string _version = string.Empty;
        private bool _isEnabled;
        private AlgorithmConfiguration _configuration = new AlgorithmConfiguration();

        /// <summary>
        /// Gets or sets the name.
        /// </summary>
        public string Name
        {
            get => _name;
            set
            {
                _name = value ?? string.Empty;
                OnPropertyChanged(nameof(Name));
            }
        }

        /// <summary>
        /// Gets or sets the description.
        /// </summary>
        public string Description
        {
            get => _description;
            set
            {
                _description = value ?? string.Empty;
                OnPropertyChanged(nameof(Description));
            }
        }

        /// <summary>
        /// Gets or sets the version.
        /// </summary>
        public string Version
        {
            get => _version;
            set
            {
                _version = value ?? string.Empty;
                OnPropertyChanged(nameof(Version));
            }
        }

        /// <summary>
        /// Gets or sets a value indicating whether the algorithm is enabled.
        /// </summary>
        public bool IsEnabled
        {
            get => _isEnabled;
            set
            {
                _isEnabled = value;
                OnPropertyChanged(nameof(IsEnabled));
            }
        }

        /// <summary>
        /// Gets or sets the configuration.
        /// </summary>
        public AlgorithmConfiguration Configuration
        {
            get => _configuration;
            set
            {
                _configuration = value ?? new AlgorithmConfiguration();
                OnPropertyChanged(nameof(Configuration));
            }
        }

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
    /// Простая реализация ICommand
    /// </summary>
    public class RelayCommand : ICommand
    {
        private readonly Action _execute;
        private readonly Func<bool>? _canExecute;
        private bool _isExecuting;

        /// <summary>
        /// Initializes a new instance of the <see cref="RelayCommand"/> class.
        /// </summary>
        /// <param name="execute">The action to execute.</param>
        /// <param name="canExecute">The function to determine if the command can execute.</param>
        public RelayCommand(Action execute, Func<bool>? canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }

        /// <summary>
        /// Occurs when changes occur that affect whether or not the command should execute.
        /// </summary>
        public event EventHandler? CanExecuteChanged;

        /// <summary>
        /// Defines the method that determines whether the command can execute in its current state.
        /// </summary>
        /// <param name="parameter">Data used by the command.</param>
        /// <returns>true if this command can be executed; otherwise, false.</returns>
        public bool CanExecute(object? parameter)
        {
            return !_isExecuting && (_canExecute?.Invoke() ?? true);
        }

        /// <summary>
        /// Defines the method to be called when the command is invoked.
        /// </summary>
        /// <param name="parameter">Data used by the command.</param>
        public void Execute(object? parameter)
        {
            if (CanExecute(parameter))
            {
                _isExecuting = true;
                try
                {
                    RaiseCanExecuteChanged();
                    _execute();
                }
                finally
                {
                    _isExecuting = false;
                    RaiseCanExecuteChanged();
                }
            }
        }

        /// <summary>
        /// Raises the CanExecuteChanged event.
        /// </summary>
        public void RaiseCanExecuteChanged()
        {
            CanExecuteChanged?.Invoke(this, EventArgs.Empty);
        }
    }

    /// <summary>
    /// RelayCommand с параметром
    /// </summary>
    /// <typeparam name="T">The type of the parameter.</typeparam>
    public class RelayCommand<T> : ICommand
    {
        private readonly Action<T> _execute;
        private readonly Func<T, bool>? _canExecute;
        private bool _isExecuting;

        /// <summary>
        /// Initializes a new instance of the <see cref="RelayCommand{T}"/> class.
        /// </summary>
        /// <param name="execute">The action to execute.</param>
        /// <param name="canExecute">The function to determine if the command can execute.</param>
        public RelayCommand(Action<T> execute, Func<T, bool>? canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }

        /// <summary>
        /// Occurs when changes occur that affect whether or not the command should execute.
        /// </summary>
        public event EventHandler? CanExecuteChanged;

        /// <summary>
        /// Defines the method that determines whether the command can execute in its current state.
        /// </summary>
        /// <param name="parameter">Data used by the command.</param>
        /// <returns>true if this command can be executed; otherwise, false.</returns>
        public bool CanExecute(object? parameter)
        {
            if (parameter is T typedParameter)
            {
                return !_isExecuting && (_canExecute?.Invoke(typedParameter) ?? true);
            }
            return !_isExecuting;
        }

        /// <summary>
        /// Defines the method to be called when the command is invoked.
        /// </summary>
        /// <param name="parameter">Data used by the command.</param>
        public void Execute(object? parameter)
        {
            if (CanExecute(parameter))
            {
                _isExecuting = true;
                try
                {
                    RaiseCanExecuteChanged();
                    
                    if (parameter is T typedParameter)
                    {
                        _execute(typedParameter);
                    }
                    else if (parameter == null && default(T) == null)
                    {
                        _execute(default(T)!);
                    }
                }
                finally
                {
                    _isExecuting = false;
                    RaiseCanExecuteChanged();
                }
            }
        }

        /// <summary>
        /// Raises the CanExecuteChanged event.
        /// </summary>
        public void RaiseCanExecuteChanged()
        {
            CanExecuteChanged?.Invoke(this, EventArgs.Empty);
        }
    }
}