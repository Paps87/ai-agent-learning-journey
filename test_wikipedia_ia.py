#!/usr/bin/env python3
"""
Test du parsing HTML avec l'article Wikipedia Intelligence Artificielle
"""

import sys
sys.path.insert(0, '/home/paps/Projet ai')

from phase3.src.html_parser import WebContentProcessor

def test_wikipedia_ia():
    """Test avec l'article Wikipedia IA"""

    processor = WebContentProcessor()

    url = "https://fr.wikipedia.org/wiki/Intelligence_artificielle"

    print("🧪 Test Parsing HTML - Article Wikipedia IA")
    print("=" * 60)
    print(f"URL: {url}")
    print()

    # Simulation d'un résultat de recherche
    search_result = {
        "title": "Intelligence artificielle — Wikipédia",
        "url": url,
        "snippet": "L'intelligence artificielle (IA) est l'ensemble des théories et des techniques...",
        "query": "intelligence artificielle définition",
        "timestamp": 1731110000
    }

    print("🔄 Traitement du résultat de recherche...")
    print("-" * 40)

    # Traitement complet
    chunks = processor.process_search_result(search_result)

    if chunks:
        print("✅ SUCCÈS !")
        print(f"📊 {len(chunks)} chunks générés")
        print()

        # Statistiques
        total_words = sum(chunk.get("word_count", 0) for chunk in chunks)
        print(f"📈 Statistiques:")
        print(f"   Chunks: {len(chunks)}")
        print(f"   Mots totaux: {total_words}")
        print(f"   Mots moyens par chunk: {total_words/len(chunks):.0f}")
        print()

        # Afficher les premiers chunks
        print("📝 Aperçu des chunks:")
        for i, chunk in enumerate(chunks[:3], 1):  # 3 premiers chunks
            print(f"\n🔹 Chunk {i} ({chunk.get('word_count', 0)} mots):")
            text_preview = chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            print(f"   {text_preview}")

        print(f"\n{'='*60}")
        print("🎉 Parsing réussi ! L'article Wikipedia a été découpé en chunks utilisables par le RAG.")

    else:
        print("❌ ÉCHEC - Aucun chunk généré")
        print("Vérifiez les logs pour diagnostiquer le problème.")

if __name__ == "__main__":
    test_wikipedia_ia()