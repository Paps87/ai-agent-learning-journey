#!/usr/bin/env python3
"""
Tests unitaires pour le module web_search.py
Phase 3 - Ask-the-Web Agent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from phase3.src.web_search import WebSearchEngine, CircuitBreaker

class TestWebSearchEngine:

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.search_engine = WebSearchEngine(max_retries=1, timeout=5)

    def test_initialization(self):
        """Test d'initialisation du moteur de recherche"""
        assert self.search_engine.max_retries == 1
        assert self.search_engine.timeout == 5
        assert self.search_engine.max_results == 5
        assert hasattr(self.search_engine, 'circuit_breaker')

    def test_search_basic(self):
        """Test recherche basique"""
        results = self.search_engine.search("test recherche python", max_results=2)

        assert isinstance(results, list)
        if results:  # Si résultats trouvés
            result = results[0]
            assert "title" in result
            assert "url" in result
            assert "snippet" in result
            assert "source" in result
            assert "timestamp" in result
            assert result["url"].startswith(("http://", "https://"))
            assert len(result["title"].strip()) > 0
            assert len(result["snippet"].strip()) > 0

    def test_search_empty_query(self):
        """Test requête vide"""
        results = self.search_engine.search("", max_results=1)
        # Devrait retourner liste vide ou gérer l'erreur gracieusement
        assert isinstance(results, list)

    def test_search_max_results(self):
        """Test limitation du nombre de résultats"""
        results = self.search_engine.search("python programming", max_results=1)
        assert isinstance(results, list)
        assert len(results) <= 1

    def test_multiple_queries(self):
        """Test recherches multiples"""
        queries = ["python", "javascript"]
        results = self.search_engine.search_multiple_queries(queries, max_results_per_query=1)

        assert isinstance(results, dict)
        assert len(results) == len(queries)
        for query in queries:
            assert query in results
            assert isinstance(results[query], list)

    def test_get_search_stats(self):
        """Test récupération des statistiques"""
        stats = self.search_engine.get_search_stats()

        required_keys = ["circuit_breaker_state", "failure_count", "max_retries", "timeout"]
        for key in required_keys:
            assert key in stats

        assert stats["circuit_breaker_state"] in ["CLOSED", "OPEN", "HALF_OPEN"]
        assert isinstance(stats["failure_count"], int)
        assert isinstance(stats["max_retries"], int)
        assert isinstance(stats["timeout"], int)

class TestCircuitBreaker:

    def test_initialization(self):
        """Test initialisation du circuit breaker"""
        cb = CircuitBreaker()
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 60
        assert cb.failure_count == 0
        assert cb.state == "CLOSED"

    def test_success_call(self):
        """Test appel réussi"""
        cb = CircuitBreaker()

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.failure_count == 0
        assert cb.state == "CLOSED"

    def test_failure_call(self):
        """Test appel en échec"""
        cb = CircuitBreaker(failure_threshold=2)

        def failure_func():
            raise Exception("test error")

        # Premier échec
        with pytest.raises(Exception):
            cb.call(failure_func)
        assert cb.failure_count == 1
        assert cb.state == "CLOSED"

        # Deuxième échec - seuil atteint
        with pytest.raises(Exception):
            cb.call(failure_func)
        assert cb.failure_count == 2
        assert cb.state == "OPEN"

if __name__ == "__main__":
    # Exécution simple des tests
    print("🧪 Exécution des tests unitaires web_search.py")

    # Test basique
    try:
        test_instance = TestWebSearchEngine()
        test_instance.setup_method()
        test_instance.test_initialization()
        print("✅ Test initialisation: OK")

        test_instance.test_get_search_stats()
        print("✅ Test statistiques: OK")

        # Test de recherche (commenté car nécessite connexion internet)
        # test_instance.test_search_basic()
        # print("✅ Test recherche basique: OK")

        print("🎉 Tests unitaires terminés avec succès!")

    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()