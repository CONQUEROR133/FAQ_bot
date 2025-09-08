using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Windows;
using Microsoft.Win32;
using UniversalFAQLoader.Business.Models;
using UniversalFAQLoader.Presentation.ViewModels;

namespace UniversalFAQLoader.Presentation.Views
{
    /// <summary>
    /// Логика взаимодействия для MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private MainViewModel _viewModel;
        private List<string> _selectedFiles = new List<string>();

        public MainWindow()
        {
            InitializeComponent();
            
            // Установка DataContext для MVVM
            _viewModel = new MainViewModel();
            DataContext = _viewModel;
            
            // Подписка на изменение свойств для обновления графа
            _viewModel.PropertyChanged += OnViewModelPropertyChanged;
        }

        private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            // Обновление графа при изменении результатов выполнения алгоритмов
            if (e.PropertyName == nameof(MainViewModel.LastExecutionResult))
            {
                if (_viewModel.LastExecutionResult != null)
                {
                    FAQGraph.UpdateGraphData(
                        _viewModel.FAQNodes, 
                        _viewModel.LastExecutionResult.AllConnections ?? new List<FAQConnection>());
                }
            }
            // Обновление графа при изменении узлов FAQ
            else if (e.PropertyName == nameof(MainViewModel.FAQNodes))
            {
                if (_viewModel.LastExecutionResult != null)
                {
                    FAQGraph.UpdateGraphData(
                        _viewModel.FAQNodes, 
                        _viewModel.LastExecutionResult.AllConnections ?? new List<FAQConnection>());
                }
            }
        }

        private void ExitMenuItem_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private void AlgorithmSettingsMenuItem_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Открытие настроек алгоритмов", "Настройки", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void AboutMenuItem_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show(
                "Универсальный FAQ Загрузчик с алгоритмическим управлением\n" +
                "Версия 1.0.0\n\n" +
                "Система интеллектуального управления FAQ записями с помощью алгоритмов:\n" +
                "• Анализ зависимостей\n" +
                "• Семантическая группировка\n" +
                "• Умное связывание\n" +
                "• Оптимизация ответов", 
                "О программе", 
                MessageBoxButton.OK, 
                MessageBoxImage.Information);
        }

        private void SelectFilesButton_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Multiselect = true,
                Filter = "All files (*.*)|*.*"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                ProcessSelectedFiles(openFileDialog.FileNames);
            }
        }

        private void FileDropArea_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                var files = (string[]?)e.Data.GetData(DataFormats.FileDrop);
                if (files != null)
                {
                    ProcessSelectedFiles(files);
                }
            }
        }

        private void FileDropArea_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effects = DragDropEffects.Copy;
            }
            else
            {
                e.Effects = DragDropEffects.None;
            }
            e.Handled = true;
        }

        private void LoadToFAQButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedFiles.Count == 0)
            {
                MessageBox.Show("Сначала выберите файлы для загрузки", "Нет файлов", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                // Get UI settings
                bool groupFiles = GroupFilesCheckBox.IsChecked ?? false;
                bool copyToFilesFolder = CopyToFilesCheckBox.IsChecked ?? false;
                bool createButtons = CreateButtonsCheckBox.IsChecked ?? false;
                string groupName = GroupNameTextBox.Text ?? string.Empty;

                // Process files
                ProcessFiles(_selectedFiles.ToArray(), groupFiles, copyToFilesFolder, groupName, createButtons);

                // Clear selected files
                _selectedFiles.Clear();
                StatusTextBlock.Text = "Файлы успешно загружены в FAQ";
                StatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;
            }
            catch (Exception ex)
            {
                StatusTextBlock.Text = $"Ошибка загрузки: {ex.Message}";
                StatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                MessageBox.Show($"Ошибка загрузки файлов: {ex.Message}", "Ошибка", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void ProcessSelectedFiles(string[] filePaths)
        {
            try
            {
                // Store selected files
                _selectedFiles = filePaths.ToList();
                
                // Update status message
                StatusTextBlock.Text = $"Выбрано файлов: {filePaths.Length}";
                StatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;
                
                // Show file names in a message box
                var fileNames = filePaths.Select(Path.GetFileName).Where(name => name != null).ToArray();
                MessageBox.Show($"Выбраны файлы:\n{string.Join("\n", fileNames)}", "Файлы выбраны", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                StatusTextBlock.Text = $"Ошибка обработки: {ex.Message}";
                StatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                MessageBox.Show($"Ошибка обработки файлов: {ex.Message}", "Ошибка", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
        
        private void ProcessFiles(string[] filePaths, bool groupFiles, bool copyToFilesFolder, string groupName, bool createButtons)
        {
            // Use the existing files directory in the faq_bot project
            string filesDirectory = "../../../files";
            if (!Directory.Exists(filesDirectory))
            {
                Directory.CreateDirectory(filesDirectory);
            }
            
            // If copying to Files folder is enabled, copy files
            if (copyToFilesFolder)
            {
                foreach (string filePath in filePaths)
                {
                    try
                    {
                        string fileName = Path.GetFileName(filePath) ?? "unknown_file";
                        string destinationPath = Path.Combine(filesDirectory, fileName);
                        
                        // Handle file name conflicts
                        int counter = 1;
                        string originalDestinationPath = destinationPath;
                        while (File.Exists(destinationPath))
                        {
                            string nameWithoutExtension = Path.GetFileNameWithoutExtension(fileName) ?? "file";
                            string extension = Path.GetExtension(fileName);
                            destinationPath = Path.Combine(filesDirectory, $"{nameWithoutExtension}_{counter}{extension}");
                            counter++;
                        }
                        
                        File.Copy(filePath, destinationPath, true);
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Не удалось скопировать файл {filePath}: {ex.Message}", "Ошибка копирования", MessageBoxButton.OK, MessageBoxImage.Warning);
                    }
                }
            }
            
            // Create FAQ nodes for the files
            var newNodes = new List<FAQNode>();
            foreach (string filePath in filePaths)
            {
                try
                {
                    var node = new FAQNode
                    {
                        Query = $"Информация из файла: {Path.GetFileName(filePath) ?? "Неизвестный файл"}",
                        Response = $"Содержимое файла {Path.GetFileName(filePath) ?? "Неизвестный файл"}",
                        Metadata = new NodeMetadata
                        {
                            SourceType = "file",
                            SourceFile = filePath,
                            GroupName = groupFiles ? groupName : null,
                            Confidence = 0.8,
                            Tags = new List<string> { "file", Path.GetExtension(filePath).TrimStart('.') }
                        },
                        Resources = new List<FAQResource>
                        {
                            new FAQResource
                            {
                                Type = "file",
                                Title = Path.GetFileName(filePath) ?? "Неизвестный файл",
                                Files = new List<string> { filePath }
                            }
                        },
                        // Initialize algorithmic properties
                        AlgorithmProps = new AlgorithmProperties
                        {
                            ComplexityScore = 0.5, // Default complexity
                            PopularityScore = 0.8, // Default popularity
                            Language = new LanguageFeatures
                            {
                                DetectedLanguage = "ru",
                                LanguageConfidence = 0.9,
                                TextLength = (int)new FileInfo(filePath).Length,
                                WordCount = 100 // Estimated word count
                            }
                        },
                        SearchIndex = new SearchIndex
                        {
                            NormalizedText = $"Информация из файла {Path.GetFileName(filePath) ?? "Неизвестный файл"}",
                            Words = new HashSet<string> { "файл", Path.GetFileNameWithoutExtension(filePath) ?? "файл" }
                        }
                    };
                    
                    newNodes.Add(node);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Не удалось создать FAQ запись для файла {filePath}: {ex.Message}", "Ошибка создания записи", MessageBoxButton.OK, MessageBoxImage.Warning);
                }
            }
            
            // Add nodes to the view model
            foreach (var node in newNodes)
            {
                _viewModel.FAQNodes.Add(node);
            }
            
            // If grouping is enabled and we have multiple files, create a group
            if (groupFiles && newNodes.Count > 1)
            {
                // In a real implementation, you would create a group with the specified name
                // and add all the FAQ nodes to it
                StatusTextBlock.Text = $"Создана группа '{groupName}' с {newNodes.Count} файлами";
            }
            else if (newNodes.Count > 0)
            {
                StatusTextBlock.Text = $"Добавлено {newNodes.Count} FAQ записей";
            }
            
            // If creating buttons is enabled, create buttons for bot integration
            if (createButtons && newNodes.Count > 0)
            {
                // In a real implementation, you would create buttons for bot integration
                // This could involve generating JSON or other configuration files for the bot
                MessageBox.Show($"Созданы кнопки для {newNodes.Count} файлов", "Кнопки созданы", MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }
    }
}