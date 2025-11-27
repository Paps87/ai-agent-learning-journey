#!/usr/bin/env python3
"""
Script de test pour Phase 3 - Ask-the-Web Agent
Test les fonctionnalités de recherche web sans charger les modèles lourds
"""

import sys
import os

# Ajouter le répertoire src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_web_search():
    """Test du moteur de recherche web"""
    print("🧪 Test 1: Moteur de recherche web")
    print("-" * 50)
    
    try:
        from web_search import WebSearchEngine
        
        engine = WebSearchEngine(max_retries=2, timeout=10)
        
        # Test de recherche simple
        query = "prix bitcoin"
        print(f"🔍 Recherche: '{query}'")
        
        results = engine.search(query, max_results=3)
        
        if results:
            print(f"✅ Succès: {len(results)} résultats trouvés")
            for i, result in enumerate(results, 1):
                print(f"\n  {i}. {result['title']}")
                print(f"     URL: {result['url']}")
                print(f"     Snippet: {result['snippet'][:100]}...")
            return True
        else:
            print("❌ Aucun résultat trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_html_parser():
    """Test du parser HTML"""
    print("\n🧪 Test 2: Parser HTML")
    print("-" * 50)
    
    try:
        from html_parser import HTMLParser, TextChunker
        
        parser = HTMLParser(timeout=5)
        
        # Test avec une URL simple
        test_url = "https://httpbin.org/html"
        print(f"🔍 Parsing URL: {test_url}")
        
        text = parser.parse_url(test_url)
        
        if text:
            print(f"✅ Succès: {len(text)} caractères extraits")
            print(f"   Aperçu: {text[:150]}...")
            
            # Test chunking
            chunker = TextChunker(chunk_size=100, overlap=20)
            chunks = chunker.chunk_text(text)
            print(f"✅ Chunking: {len(chunks)} chunks créés")
            
            return True
        else:
            print("❌ Échec du parsing")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_processor():
    """Test du processeur web complet"""
    print("\n🧪 Test 3: Processeur Web Complet")
    print("-" * 50)
    
    try:
        from web_search import WebSearchEngine
        from html_parser import WebContentProcessor
        
        # Recherche
        search_engine = WebSearchEngine(max_retries=1, timeout=5)
        results = search_engine.search("python programming", max_results=1)
        
        if not results:
            print("⚠️ Aucun résultat de recherche")
            return False
        
        # Processing
        processor = WebContentProcessor(chunk_size=200, overlap=30)
        
        print(f"🔍 Processing: {results[0]['url']}")
        chunks = processor.process_search_result(results[0])
        
        if chunks:
            print(f"✅ Succès: {len(chunks)} chunks créés")
            print(f"   Premier chunk: {chunks[0]['text'][:100]}...")
            return True
        else:
            print("⚠️ Aucun chunk créé (parsing peut avoir échoué)")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🚀 TESTS PHASE 3 - ASK-THE-WEB AGENT")
    print("=" * 60)
    
    results = []
    
    # Test 1: Web Search
    results.append(("Web Search", test_web_search()))
    
    # Test 2: HTML Parser
    results.append(("HTML Parser", test_html_parser()))
    
    # Test 3: Web Processor
    results.append(("Web Processor", test_web_processor()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès!")
        return 0
    else:
        print("⚠️ Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    exit(main())
