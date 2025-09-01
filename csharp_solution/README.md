# Universal FAQ Loader with Algorithmic Management

A C# WPF application for managing FAQ entries with intelligent algorithmic processing.

## Features

- **Universal File Support**: Handles all file types including images, documents, and more
- **Algorithmic Management**: Four core algorithms for intelligent FAQ processing:
  - Dependency Analysis
  - Semantic Grouping
  - Smart Linking
  - Response Optimization
- **Graph Visualization**: Interactive visualization of FAQ connections and relationships
- **Multi-format Storage**: Supports JSON, SQLite, and Graph database storage
- **Russian Language Support**: Full UI and documentation in Russian

## Core Algorithms

1. **Dependency Analyzer**: Identifies semantic, keyword, and file-based connections between FAQ entries
2. **Semantic Grouper**: Intelligently groups FAQ entries by semantic meaning using clustering algorithms
3. **Smart Linker**: Creates intelligent connections between entries (prerequisites, follow-ups, related topics)
4. **Response Optimizer**: Improves FAQ response quality automatically

## Architecture

The application follows a clean MVVM architecture with:
- WPF UI with custom controls
- Algorithm service layer
- Hybrid storage repository
- JSON compatibility for Python bot integration

## Requirements

- .NET 6.0 SDK (for building)
- Windows OS (for WPF)

## Building

```bash
dotnet build
```

## Running

```bash
dotnet run
```

## Project Structure

- `Business/`: Core algorithm implementations and models
- `Presentation/`: WPF UI components (Views, ViewModels, Controls)
- `Data/`: Repository implementations for different storage formats

## License

This project is proprietary and confidential.