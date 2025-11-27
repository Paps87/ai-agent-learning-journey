#!/usr/bin/env python3
"""
Test du parsing HTML avec CoinMarketCap (prix Bitcoin)
"""

import sys
sys.path.insert(0, '/home/paps/Projet ai')

from phase3.src.html_parser import WebContentProcessor

def test_coinmarketcap():
    """Test avec CoinMarketCap pour les prix crypto"""

    processor = WebContentProcessor()

    url = "https://coinmarketcap.com/currencies/bitcoin/"

    print("🧪 Test Parsing HTML - CoinMarketCap Bitcoin")
    print("=" * 60)
    print(f"URL: {url}")
    print()

    # Simulation d'un résultat de recherche
    search_result = {
        "title": "Bitcoin (BTC) - Prix, Graphiques, Capitalisation | CoinMarketCap",
        "url": url,
        "snippet": "Prix actuel du Bitcoin (BTC) en temps réel. Consultez les graphiques, la capitalisation boursière, le volume des échanges et bien plus.",
        "query": "prix bitcoin aujourd'hui",
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
        print("🎉 Parsing réussi ! Les données CoinMarketCap ont été découpées en chunks.")

    else:
        print("❌ ÉCHEC - Aucun chunk généré")
        print("Vérifiez les logs pour diagnostiquer le problème.")

if __name__ == "__main__":
    test_coinmarketcap()