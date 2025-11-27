#!/usr/bin/env python3
"""
Test automatisé de recherches live
"""

import sys
sys.path.insert(0, '/home/paps/Projet ai')

from phase3.src.web_search import WebSearchEngine

def test_live_searches():
    """Test automatisé de plusieurs recherches"""

    search_engine = WebSearchEngine(max_retries=2, timeout=8)

    # Requêtes de test
    test_queries = [
        "météo Paris demain",
        "prix bitcoin aujourd'hui",
        "actualité IA 2024",
        "recette cuisine française",
        "match foot ce soir"
    ]

    print("🔍 Test Automatisé de Recherches Live")
    print("=" * 50)

    total_results = 0
    successful_searches = 0

    for query in test_queries:
        print(f"\n🔎 Test: '{query}'")
        print("-" * 30)

        try:
            results = search_engine.search(query, max_results=2)

            if results:
                successful_searches += 1
                total_results += len(results)

                print(f"✅ {len(results)} résultats")

                # Afficher le premier résultat
                first = results[0]
                print(f"📄 {first['title'][:60]}...")
                print(f"🔗 {first['url']}")

            else:
                print("❌ Aucun résultat")

        except Exception as e:
            print(f"💥 Erreur: {e}")

    # Résumé
    print(f"\n📊 RÉSULTATS FINAUX:")
    print(f"   Recherches réussies: {successful_searches}/{len(test_queries)}")
    print(f"   Total résultats: {total_results}")

    stats = search_engine.get_search_stats()
    print(f"   Circuit breaker: {stats['circuit_breaker_state']}")
    print(f"   Échecs cumulés: {stats['failure_count']}")

if __name__ == "__main__":
    test_live_searches()