#!/usr/bin/env python3
"""
Module de recherche web pour Phase 3 - Ask-the-Web Agent
Utilise DuckDuckGo pour des recherches web fiables et respectueuses
"""

from ddgs import DDGS
from typing import List, Dict, Any
import requests
import time
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Pattern Circuit Breaker pour éviter les appels répétés en cas de panne
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class WebSearchEngine:
    """
    Moteur de recherche web utilisant DuckDuckGo avec gestion d'erreurs robuste
    """

    def __init__(self, max_retries: int = 3, timeout: int = 10, max_results: int = 5):
        """
        Initialise le moteur de recherche

        Args:
            max_retries: Nombre maximum de tentatives
            timeout: Timeout par requête (secondes)
            max_results: Nombre maximum de résultats par défaut
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.max_results = max_results
        self.circuit_breaker = CircuitBreaker()

        logger.info("WebSearchEngine initialisé")

    def search(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Effectue une recherche web avec gestion complète d'erreurs

        Args:
            query: Terme de recherche
            max_results: Nombre maximum de résultats (optionnel)

        Returns:
            Liste des résultats validés
        """
        if max_results is None:
            max_results = self.max_results

        logger.info(f"Recherche: '{query}' (max {max_results} résultats)")

        try:
            # Utiliser le circuit breaker
            results = self.circuit_breaker.call(
                self._perform_search_with_retry,
                query,
                max_results
            )

            # Valider et nettoyer les résultats
            valid_results = self._validate_results(results)

            logger.info(f"Succès: {len(valid_results)} résultats valides")
            return valid_results

        except Exception as e:
            logger.error(f"Échec recherche: {e}")
            return []

    def _perform_search_with_retry(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Effectue la recherche avec logique de retry
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Tentative {attempt + 1}/{self.max_retries}")

                results = []

                # Utiliser DDGS avec timeout
                with DDGS() as ddgs:
                    search_results = ddgs.text(
                        query,
                        max_results=max_results,
                        timelimit=self.timeout
                    )

                    for result in search_results:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                            "source": "duckduckgo",
                            "timestamp": time.time(),
                            "query": query
                        })

                return results

            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Timeout (tentative {attempt + 1})")
                last_exception = "Timeout"
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponentiel

            except requests.exceptions.ConnectionError:
                logger.warning(f"🌐 Erreur de connexion (tentative {attempt + 1})")
                last_exception = "Connection Error"
                if attempt < self.max_retries - 1:
                    time.sleep(1)

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else "Unknown"
                logger.warning(f"🔴 HTTP {status_code} (tentative {attempt + 1})")

                last_exception = f"HTTP {status_code}"

                # Gestion spécifique des erreurs HTTP
                if status_code == 429:  # Rate limit
                    wait_time = 60
                    logger.info(f"⏳ Rate limit - attente {wait_time}s")
                    time.sleep(wait_time)
                    continue
                elif status_code >= 500:  # Erreur serveur
                    if attempt < self.max_retries - 1:
                        time.sleep(5)
                        continue
                else:
                    # Erreur client (4xx) - ne pas retry
                    break

            except Exception as e:
                logger.error(f"💥 Erreur inattendue: {e}")
                last_exception = str(e)
                if attempt < self.max_retries - 1:
                    time.sleep(1)

        # Toutes les tentatives ont échoué
        raise Exception(f"Échec après {self.max_retries} tentatives. Dernière erreur: {last_exception}")

    def _validate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Valide et nettoie les résultats de recherche
        """
        valid_results = []

        for result in results:
            # Vérifier champs requis
            required_fields = ["title", "url", "snippet"]
            if not all(field in result for field in required_fields):
                continue

            # Valider URL
            url = result["url"]
            if not url.startswith(("http://", "https://")):
                continue

            # Nettoyer et valider contenu
            title = result["title"].strip()
            snippet = result["snippet"].strip()

            if not title or not snippet:
                continue

            # Éviter les résultats trop courts
            if len(title) < 3 or len(snippet) < 10:
                continue

            # Nettoyer et garder
            result["title"] = title
            result["snippet"] = snippet
            result["url"] = url

            valid_results.append(result)

        logger.debug(f"Validation: {len(results)} → {len(valid_results)} résultats valides")
        return valid_results

    def search_multiple_queries(self, queries: List[str], max_results_per_query: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Effectue plusieurs recherches en parallèle

        Args:
            queries: Liste des requêtes
            max_results_per_query: Nombre max de résultats par requête

        Returns:
            Dictionnaire requête → résultats
        """
        results = {}

        for query in queries:
            results[query] = self.search(query, max_results_per_query)

        logger.info(f"Recherches multiples terminées: {len(queries)} requêtes")
        return results

    def get_search_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du moteur de recherche
        """
        return {
            "circuit_breaker_state": self.circuit_breaker.state,
            "failure_count": self.circuit_breaker.failure_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }

# Instance globale
web_search_engine = WebSearchEngine()

def get_web_search_engine() -> WebSearchEngine:
    """Factory function pour l'instance globale"""
    return web_search_engine

# Tests unitaires
if __name__ == "__main__":
    print("🧪 Test du moteur de recherche web")
    print("=" * 50)

    # Initialisation
    search_engine = WebSearchEngine(max_retries=2, timeout=5)

    # Tests de recherche
    test_queries = [
        "prix bitcoin aujourd'hui",
        "météo Paris demain",
        "actualité IA 2024"
    ]

    for query in test_queries:
        print(f"\n🔍 Recherche: '{query}'")
        print("-" * 40)

        results = search_engine.search(query, max_results=3)

        if results:
            for i, result in enumerate(results, 1):
                print(f"{i}. 📄 {result['title']}")
                print(f"   🔗 {result['url']}")
                print(f"   📝 {result['snippet'][:100]}...")
                print()
        else:
            print("❌ Aucun résultat trouvé")

    # Statistiques
    print("\n📊 Statistiques:")
    stats = search_engine.get_search_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ Tests terminés!")