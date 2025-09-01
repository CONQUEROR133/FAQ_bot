using System;
using System.IO;
using System.Threading.Tasks;
using UniversalFAQLoader.Data.Repositories;
using UniversalFAQLoader.Business.Models;

class VerificationTest
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("=== Verification Test for FAQ Data Loading ===");
        
        try
        {
            // Test the exact same path that the main application uses
            string dataDirectory = "../../../data";
            Console.WriteLine($"Using data directory: {dataDirectory}");
            
            // Check if directory exists
            if (!Directory.Exists(dataDirectory))
            {
                Console.WriteLine($"ERROR: Data directory does not exist: {Path.GetFullPath(dataDirectory)}");
                return;
            }
            
            // Check if faq.json exists
            string jsonFilePath = Path.Combine(dataDirectory, "faq.json");
            Console.WriteLine($"Looking for JSON file: {jsonFilePath}");
            Console.WriteLine($"Full path: {Path.GetFullPath(jsonFilePath)}");
            
            if (!File.Exists(jsonFilePath))
            {
                Console.WriteLine("ERROR: faq.json file not found!");
                return;
            }
            
            // Show file info
            var fileInfo = new FileInfo(jsonFilePath);
            Console.WriteLine($"File size: {fileInfo.Length} bytes");
            Console.WriteLine($"Last modified: {fileInfo.LastWriteTime}");
            
            // Test HybridFAQRepository (same as main app)
            Console.WriteLine("\nTesting HybridFAQRepository...");
            var repository = new HybridFAQRepository(dataDirectory);
            
            var nodes = await repository.GetAllAsync();
            Console.WriteLine($"Successfully loaded {nodes.Count()} nodes");
            
            // Show details of first node
            foreach (var node in nodes)
            {
                Console.WriteLine($"\nNode Details:");
                Console.WriteLine($"  ID: {node.Id}");
                Console.WriteLine($"  Query: {node.Query}");
                Console.WriteLine($"  Response: {node.Response}");
                Console.WriteLine($"  Variations: {node.Variations.Count}");
                Console.WriteLine($"  Resources: {node.Resources.Count}");
                if (node.Resources.Count > 0)
                {
                    foreach (var resource in node.Resources)
                    {
                        Console.WriteLine($"    Resource Type: {resource.Type}");
                        Console.WriteLine($"    Resource Title: {resource.Title}");
                        Console.WriteLine($"    Resource Files: {resource.Files.Count}");
                    }
                }
                Console.WriteLine($"  Metadata SourceType: {node.Metadata?.SourceType}");
                Console.WriteLine($"  Metadata Confidence: {node.Metadata?.Confidence}");
                Console.WriteLine($"  Metadata CreatedAt: {node.Metadata?.CreatedAt}");
                Console.WriteLine($"  Metadata Hash: {node.Metadata?.Hash}");
                break; // Only show first node
            }
            
            Console.WriteLine("\n=== Test Completed Successfully ===");
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