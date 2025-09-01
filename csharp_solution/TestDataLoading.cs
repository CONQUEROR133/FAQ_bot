using System;
using System.IO;
using System.Threading.Tasks;
using UniversalFAQLoader.Data.Repositories;

class TestDataLoading
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("Testing FAQ data loading...");
        
        try
        {
            // Use the same path as the main application
            var repository = new HybridFAQRepository("../../../data");
            
            Console.WriteLine($"Looking for FAQ data in: ../../../data");
            Console.WriteLine($"Full path: {Path.GetFullPath("../../../data")}");
            
            // Check if faq.json exists
            var jsonPath = Path.Combine("../../../data", "faq.json");
            Console.WriteLine($"FAQ.json exists: {File.Exists(jsonPath)}");
            
            if (File.Exists(jsonPath))
            {
                var fileInfo = new FileInfo(jsonPath);
                Console.WriteLine($"File size: {fileInfo.Length} bytes");
                Console.WriteLine($"Last modified: {fileInfo.LastWriteTime}");
                
                // Read first 500 characters to see content
                var content = File.ReadAllText(jsonPath);
                Console.WriteLine($"File content preview:");
                Console.WriteLine(content.Substring(0, Math.Min(500, content.Length)));
            }
            
            // Try to load data
            Console.WriteLine("Loading FAQ data...");
            var nodes = await repository.GetAllAsync();
            
            Console.WriteLine($"Loaded {nodes.Count()} FAQ nodes");
            
            foreach (var node in nodes)
            {
                Console.WriteLine($"- Query: {node.Query}");
                Console.WriteLine($"  Response: {node.Response}");
                Console.WriteLine($"  Resources: {node.Resources.Count}");
                Console.WriteLine();
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
        }
        
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
    }
}