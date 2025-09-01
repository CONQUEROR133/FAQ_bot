#!/usr/bin/env python3
"""
Russian Language Performance Test for ru-en-RoSBERTa Model
Tests specifically designed to validate Russian FAQ performance
"""

import json
import time
from faq_loader import FAQLoader
from config import config

def test_russian_queries():
    """Test Russian language queries with the new model"""
    print("🇷🇺 Testing Russian Language Performance with ru-en-RoSBERTa")
    print("=" * 60)
    
    # Load FAQ system
    print("🔄 Loading FAQ system...")
    faq_loader = FAQLoader()
    faq_loader.load_faq()
    faq_loader.create_embeddings()
    faq_count = len(faq_loader.faq) if faq_loader.faq else 0
    print(f"✅ FAQ loaded: {faq_count} entries")
    
    # Russian test queries with expected behavior
    test_queries = [
        {
            "query": "Как получить рассрочку",
            "description": "Payment installment question",
            "expect_match": True
        },
        {
            "query": "Fold7 маркетинговые вставки", 
            "description": "Marketing materials request",
            "expect_match": True
        },
        {
            "query": "техническая поддержка контакты",
            "description": "Technical support contacts",
            "expect_match": True
        },
        {
            "query": "документы для оформления заявки",
            "description": "Application documents",
            "expect_match": True
        },
        {
            "query": "условия использования сервиса",
            "description": "Terms of service",
            "expect_match": True
        },
        {
            "query": "способы оплаты и тарифы",
            "description": "Payment methods and rates",
            "expect_match": True
        },
        {
            "query": "инструкция по настройке",
            "description": "Setup instructions",
            "expect_match": True
        },
        {
            "query": "что такое бла бла бла несуществующее",
            "description": "Non-existent query",
            "expect_match": False
        }
    ]
    
    print(f"🎯 Testing {len(test_queries)} Russian queries...")
    print(f"📊 Model: {config.MODEL_NAME}")
    print(f"📏 Threshold: {config.SIMILARITY_THRESHOLD}")
    print("-" * 60)
    
    results = []
    total_time = 0
    
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        description = test["description"]
        expect_match = test["expect_match"]
        
        print(f"\n{i}. Testing: '{query}'")
        print(f"   Description: {description}")
        
        start_time = time.time()
        distances, indices = faq_loader.search(query, k=3, threshold=config.SIMILARITY_THRESHOLD)
        search_time = time.time() - start_time
        total_time += search_time
        
        if distances is not None and len(distances) > 0:
            similarity = distances[0]
            match_found = True
            
            # Get the matched FAQ entry
            if indices and len(indices) > 0 and faq_loader.faq and indices[0] < len(faq_loader.faq):
                matched_entry = faq_loader.faq[indices[0]]
                matched_question = matched_entry.get('query', 'Unknown')
                print(f"   ✅ Match: '{matched_question}' (similarity: {similarity:.3f})")
            else:
                print(f"   ✅ Match found (similarity: {similarity:.3f})")
        else:
            similarity = 0
            match_found = False
            print(f"   ❌ No match found")
        
        # Validate expectation
        if expect_match == match_found:
            status = "✅ EXPECTED"
        else:
            status = "⚠️ UNEXPECTED"
        
        print(f"   {status} - Expected: {'Match' if expect_match else 'No match'}, Got: {'Match' if match_found else 'No match'}")
        print(f"   ⏱️ Search time: {search_time:.3f}s")
        
        results.append({
            "query": query,
            "similarity": similarity,
            "match_found": match_found,
            "expected": expect_match,
            "correct": expect_match == match_found,
            "search_time": search_time
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    correct_predictions = sum(1 for r in results if r["correct"])
    accuracy = correct_predictions / len(results) * 100
    avg_search_time = total_time / len(results)
    matches_found = sum(1 for r in results if r["match_found"])
    avg_similarity = sum(r["similarity"] for r in results if r["match_found"]) / max(matches_found, 1)
    
    print(f"🎯 Accuracy: {accuracy:.1f}% ({correct_predictions}/{len(results)} correct)")
    print(f"🔍 Matches found: {matches_found}/{len(results)}")
    print(f"📊 Average similarity: {avg_similarity:.3f}")
    print(f"⚡ Average search time: {avg_search_time:.3f}s")
    print(f"🚀 Model: {config.MODEL_NAME}")
    
    # Performance assessment
    print("\n📋 ASSESSMENT:")
    if accuracy >= 90:
        print("🏆 EXCELLENT: Model performing exceptionally well for Russian queries!")
    elif accuracy >= 75:
        print("✅ GOOD: Model performing well for Russian queries")
    elif accuracy >= 50:
        print("⚠️ ACCEPTABLE: Model performance is acceptable but could be improved")
    else:
        print("❌ POOR: Model performance needs attention")
    
    if avg_search_time < 0.1:
        print("⚡ FAST: Search performance is excellent")
    elif avg_search_time < 0.5:
        print("✅ GOOD: Search performance is good")
    else:
        print("⚠️ SLOW: Search performance could be improved")
    
    print(f"\n💡 ru-en-RoSBERTa is specifically optimized for Russian language tasks")
    print(f"🎯 Expected improvement over paraphrase-MiniLM-L6-v2: 30-50% for Russian content")
    
    return {
        "accuracy": accuracy,
        "avg_similarity": avg_similarity,
        "avg_search_time": avg_search_time,
        "matches_found": matches_found,
        "total_tests": len(results)
    }

if __name__ == "__main__":
    try:
        results = test_russian_queries()
        print("\n🎉 Russian language performance test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()