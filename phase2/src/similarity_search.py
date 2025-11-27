"""
Recherche de similarité pour RAG - Phase 2
Interface pour la recherche sémantique dans la base vectorielle
"""

from typing import List, Dict, Any, Optional
import logging
from .embeddings import EmbeddingManager
from .vector_db import VectorDatabase

logger = logging.getLogger(__name__)

class SimilaritySearch:
    """
    Gestionnaire de recherche de similarité sémantique
    Combine embeddings et base vectorielle pour trouver documents pertinents
    """

    def __init__(self, embedding_manager: Optional[EmbeddingManager] = None,
                 vector_db: Optional[VectorDatabase] = None):
        """
        Initialise le système de recherche

        Args:
            embedding_manager: Instance d'EmbeddingManager (optionnel)
            vector_db: Instance de VectorDatabase (optionnel)
        """
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_db = vector_db or VectorDatabase()
        
        # Charger les modèles
        self.embedding_manager.load_model()
        self.vector_db.connect()
        
        logger.info("SimilaritySearch initialisé")

    def search_documents(self, query: str, limit: int = 5, 
                       score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Recherche les documents les plus pertinents pour une requête

        Args:
            query: Texte de la requête
            limit: Nombre maximum de résultats
            score_threshold: Seuil minimal de similarité

        Returns:
            Liste des documents pertinents avec scores
        """
        try:
            # Encoder la requête
            query_embedding = self.embedding_manager.encode_text(query)
            
            # Rechercher dans la base vectorielle
            results = self.vector_db.search_similar(query_embedding, limit=limit)
            
            # Filtrer par seuil de score
            filtered_results = [
                result for result in results 
                if result["score"] >= score_threshold
            ]
            
            logger.info(f"Recherche: '{query}' -> {len(filtered_results)} résultats (seuil: {score_threshold})")
            return filtered_results

        except Exception as e:
            logger.error(f"Erreur recherche documents: {e}")
            raise

    def search_with_context(self, query: str, context: Optional[str] = None,
                          limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche avec contexte supplémentaire pour améliorer la pertinence

        Args:
            query: Requête principale
            context: Contexte supplémentaire (ex: domaine, type de document)
            limit: Nombre maximum de résultats

        Returns:
            Liste des documents pertinents
        """
        try:
            # Combiner requête et contexte
            full_query = query
            if context:
                full_query = f"{context} {query}"
            
            return self.search_documents(full_query, limit=limit)

        except Exception as e:
            logger.error(f"Erreur recherche avec contexte: {e}")
            raise

    def get_top_result(self, query: str, score_threshold: float = 0.4) -> Optional[Dict[str, Any]]:
        """
        Retourne le meilleur résultat uniquement si il dépasse le seuil

        Args:
            query: Texte de la requête
            score_threshold: Seuil minimal de confiance

        Returns:
            Meilleur document ou None si aucun bon résultat
        """
        results = self.search_documents(query, limit=1, score_threshold=score_threshold)
        
        if results and results[0]["score"] >= score_threshold:
            return results[0]
        
        return None

    def batch_search(self, queries: List[str], limit: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recherche par lot pour plusieurs requêtes

        Args:
            queries: Liste de requêtes
            limit: Résultats par requête

        Returns:
            Dictionnaire {requête: résultats}
        """
        try:
            results = {}
            
            for query in queries:
                results[query] = self.search_documents(query, limit=limit)
            
            logger.info(f"Recherche batch: {len(queries)} requêtes traitées")
            return results

        except Exception as e:
            logger.error(f"Erreur recherche batch: {e}")
            raise

    def evaluate_search_quality(self, query: str, expected_source: str,
                              results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Évalue la qualité des résultats de recherche

        Args:
            query: Requête testée
            expected_source: Source attendue pour validation
            results: Résultats à évaluer

        Returns:
            Métriques d'évaluation
        """
        if not results:
            return {
                "query": query,
                "has_results": False,
                "top_score": 0.0,
                "relevant_found": False
            }

        top_result = results[0]
        is_relevant = expected_source in top_result.get("source", "")
        
        return {
            "query": query,
            "has_results": True,
            "top_score": top_result["score"],
            "relevant_found": is_relevant,
            "top_result_source": top_result.get("source", ""),
            "num_results": len(results)
        }

# Instance globale
similarity_search = SimilaritySearch()

def get_similarity_search() -> SimilaritySearch:
    """Factory function pour l'instance globale"""
    return similarity_search

# Tests unitaires
if __name__ == "__main__":
    print("=== Test SimilaritySearch ===")
    
    try:
        search = SimilaritySearch()
        
        # Test recherche simple
        query = "Comment configurer le VPN ?"
        results = search.search_documents(query, limit=3)
        
        print(f"Recherche: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.3f} - {result['text'][:80]}...")
        
        # Test avec contexte
        print(f"\nRecherche avec contexte:")
        hr_query = "demande congés"
        hr_results = search.search_with_context(hr_query, context="ressources humaines")
        
        for i, result in enumerate(hr_results, 1):
            print(f"{i}. Score: {result['score']:.3f} - {result['text'][:80]}...")
        
        # Test top résultat
        top_result = search.get_top_result("configuration email")
        if top_result:
            print(f"\nTop résultat: Score {top_result['score']:.3f} - {top_result['text'][:80]}...")
        else:
            print("\nAucun bon résultat trouvé")
        
        print("\n✅ Tests SimilaritySearch réussis !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()