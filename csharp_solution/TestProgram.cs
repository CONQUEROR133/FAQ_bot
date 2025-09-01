using System;
using System.IO;
using System.Threading.Tasks;
using UniversalFAQLoader.Data.Repositories;
using UniversalFAQLoader.Business.Models;

class TestProgram
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("=== Test Program for FAQ Data Loading ===");
        
        try
        {
            // Test 1: Check file paths
            Console.WriteLine("\n1. Checking file paths:");
            string dataDirectory = "../../../data";
            string jsonFilePath = Path.Combine(dataDirectory, "faq.json");
            
            Console.WriteLine($"Data directory: {dataDirectory}");
            Console.WriteLine($"Full data directory path: {Path.GetFullPath(dataDirectory)}");
            Console.WriteLine($"JSON file path: {jsonFilePath}");
            Console.WriteLine($"Full JSON file path: {Path.GetFullPath(jsonFilePath)}");
            Console.WriteLine($"JSON file exists: {File.Exists(jsonFilePath)}");
            
            if (File.Exists(jsonFilePath))
            {
                var fileInfo = new FileInfo(jsonFilePath);
                Console.WriteLine($"File size: {fileInfo.Length} bytes");
                Console.WriteLine($"Last modified: {fileInfo.LastWriteTime}");
                
                // Show first 500 characters of the file
                string content = File.ReadAllText(jsonFilePath);
                Console.WriteLine($"Content preview (first 500 chars):\n{content.Substring(0, Math.Min(500, content.Length))}");
            }
            
            // Test 2: Try to load data using JsonFAQRepository
            Console.WriteLine("\n2. Testing JsonFAQRepository:");
            var jsonRepo = new JsonFAQRepository(jsonFilePath);
            var nodes = await jsonRepo.GetAllAsync();
            Console.WriteLine($"Loaded {nodes.Count()} nodes from JSON repository");
            
            // Test 3: Try to load data using HybridFAQRepository
            Console.WriteLine("\n3. Testing HybridFAQRepository:");
            var hybridRepo = new HybridFAQRepository(dataDirectory);
            var hybridNodes = await hybridRepo.GetAllAsync();
            Console.WriteLine($"Loaded {hybridNodes.Count()} nodes from hybrid repository");
            
            // Show details of first few nodes
            int count = 0;
            foreach (var node in hybridNodes)
            {
                if (count++ >= 3) break;
                Console.WriteLine($"\nNode {count}:");
                Console.WriteLine($"  ID: {node.Id}");
                Console.WriteLine($"  Query: {node.Query}");
                Console.WriteLine($"  Response: {node.Response}");
                Console.WriteLine($"  Variations: {node.Variations.Count}");
                Console.WriteLine($"  Resources: {node.Resources.Count}");
                Console.WriteLine($"  Metadata SourceType: {node.Metadata?.SourceType}");
                Console.WriteLine($"  Metadata Confidence: {node.Metadata?.Confidence}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"ERROR: {ex.Message}");
            Console.WriteLine($"STACK TRACE: {ex.StackTrace}");
            
            if (ex.InnerException != null)
            {
                Console.WriteLine($"INNER EXCEPTION: {ex.InnerException.Message}");
            }
        }
        
        Console.WriteLine("\nPress any key to exit...");
        Console.ReadKey();
    }
}