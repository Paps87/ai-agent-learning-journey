#!/usr/bin/env python3
"""
Pipeline RAG Étendu - Phase 3
Combine connaissances locales et web pour créer un agent web-aware
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json
import sys
import os

# Configuration du logging AVANT les imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au path pour imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, grandparent_dir)

# Imports Phase 2 (existants) - optionnels si Qdrant non disponible
try:
    from phase2.src.rag_pipeline import get_rag_pipeline
    from phase2.src.embeddings import EmbeddingManager
    from phase2.src.vector_db import VectorDatabase
    PHASE2_AVAILABLE = True
except Exception as e:
    logger.warning(f"Phase 2 components not available: {e}")
    PHASE2_AVAILABLE = False
    get_rag_pipeline = None
    EmbeddingManager = None
    VectorDatabase = None

# Imports Phase 3 (nouveaux)
from src.web_search import get_web_search_engine
from src.html_parser import get_web_processor


class ConversationMemory:
    """
    Gestionnaire de mémoire conversationnelle pour l'agent web-aware
    """

    def __init__(self, max_memory: int = 10, ttl_hours: int = 24):
        """
        Args:
            max_memory: Nombre maximum d'interactions en mémoire
            ttl_hours: Durée de vie des interactions (heures)
        """
        self.max_memory = max_memory
        self.ttl_hours = ttl_hours
        self.interactions = []
        self.search_cache = {}  # Cache des recherches récentes

        logger.info(f"ConversationMemory initialisé: max={max_memory}, ttl={ttl_hours}h")

    def add_interaction(self, question: str, response: Dict[str, Any]):
        """Ajouter une interaction à la mémoire"""

        interaction = {
            "timestamp": datetime.now(),
            "question": question,
            "response": response,
            "search_queries": response.get("search_queries", []),
            "web_sources": response.get("web_sources", [])
        }

        self.interactions.append(interaction)

        # Limiter la taille
        if len(self.interactions) > self.max_memory:
            self.interactions.pop(0)

        # Nettoyer les anciennes interactions
        self._cleanup_expired()

    def get_recent_context(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Récupérer le contexte récent"""
        cutoff = datetime.now() - timedelta(hours=hours)

        recent = [i for i in self.interactions if i["timestamp"] > cutoff]
        return recent[-5:]  # Dernières 5 interactions

    def is_recently_searched(self, query: str, hours: int = 1) -> bool:
        """Vérifier si une recherche similaire a été faite récemment"""
        cutoff = datetime.now() - timedelta(hours=hours)

        for interaction in self.interactions:
            if interaction["timestamp"] > cutoff:
                if any(self._similar_queries(query, q) for q in interaction["search_queries"]):
                    return True

        return False

    def _similar_queries(self, query1: str, query2: str) -> bool:
        """Vérifier similarité basique entre requêtes"""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())

        # Intersection > 70%
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) > 0.7 if union else False

    def _cleanup_expired(self):
        """Nettoyer les interactions expirées"""
        cutoff = datetime.now() - timedelta(hours=self.ttl_hours)

        self.interactions = [
            i for i in self.interactions
            if i["timestamp"] > cutoff
        ]

class ExtendedRAGPipeline:
    """
    Pipeline RAG étendu combinant connaissances locales et web
    """

    def __init__(self):
        """Initialisation du pipeline étendu"""

        # Vérifier disponibilité des composants locaux (Phase 2)
        if PHASE2_AVAILABLE:
            try:
                self.local_rag = get_rag_pipeline()
                self.embedding_manager = EmbeddingManager()
                self.vector_db = VectorDatabase()
                self.local_available = True
                logger.info("Composants Phase 2 chargés avec succès")
            except Exception as e:
                logger.warning(f"Composants Phase 2 non disponibles: {e}")
                self.local_rag = None
                self.embedding_manager = None
                self.vector_db = None
                self.local_available = False
        else:
            logger.info("Phase 2 non disponible - Mode web-only")
            self.local_rag = None
            self.embedding_manager = None
            self.vector_db = None
            self.local_available = False

        # Composants Phase 3 (nouveaux)
        self.web_search = get_web_search_engine()
        self.web_processor = get_web_processor()
        self.memory = ConversationMemory()

        # Statistiques
        self.stats = {
            "total_queries": 0,
            "web_searches": 0,
            "local_searches": 0,
            "cache_hits": 0
        }

        logger.info(f"ExtendedRAGPipeline initialisé (local_available={self.local_available})")

    def ask_question(self, question: str, use_web: bool = True, max_web_results: int = 3) -> Dict[str, Any]:
        """
        Répondre à une question en combinant connaissances locales et web

        Args:
            question: Question de l'utilisateur
            use_web: Activer la recherche web
            max_web_results: Nombre maximum de résultats web

        Returns:
            Réponse complète avec métadonnées
        """

        self.stats["total_queries"] += 1
        start_time = datetime.now()

        logger.info(f"Traitement question: '{question}' (web={use_web})")

        try:
            # 1. Recherche locale (toujours effectuée)
            local_results = self._search_local(question)
            self.stats["local_searches"] += 1

            # 2. Recherche web (si activée et pas en cache)
            web_results = []
            search_queries = []

            if use_web:
                if not self.memory.is_recently_searched(question):
                    web_results, queries = self._search_web_enhanced(question, max_web_results)
                    search_queries = queries
                    self.stats["web_searches"] += 1
                else:
                    self.stats["cache_hits"] += 1
                    logger.info("Utilisation du cache pour éviter recherche répétée")

            # 3. Fusion des résultats
            combined_context = self._fuse_results(local_results, web_results)

            # 4. Génération de la réponse
            response = self._generate_response(question, combined_context)

            # 5. Mise à jour mémoire
            full_response = {
                **response,
                "search_queries": search_queries,
                "web_sources": [r.get("url", "") for r in web_results],
                "local_sources": len(local_results),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

            self.memory.add_interaction(question, full_response)

            # 6. Logging final
            logger.info(f"Réponse générée: {len(response['answer'])} caractères, "
                       f"{len(combined_context)} chunks utilisés")

            return full_response

        except Exception as e:
            logger.error(f"Erreur traitement question: {e}")
            return {
                "answer": "Désolé, une erreur s'est produite lors du traitement de votre question.",
                "sources": [],
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

    def _search_local(self, question: str) -> List[Dict[str, Any]]:
        """Recherche dans les connaissances locales (Phase 2)"""

        if not self.local_available:
            logger.debug("Recherche locale ignorée - composants locaux non disponibles")
            return []

        try:
            # Utiliser le pipeline RAG existant
            result = self.local_rag.ask_question(question, max_context_results=5)

            # Convertir en format standard
            local_chunks = []
            if "context" in result:
                # Parser le contexte pour extraire les chunks
                context_parts = result["context"].split("\n\n")
                for i, part in enumerate(context_parts):
                    if part.strip():
                        local_chunks.append({
                            "text": part.strip(),
                            "source": "local_documents",
                            "chunk_id": i,
                            "source_type": "local",
                            "relevance_score": 0.8  # Score par défaut pour local
                        })

            logger.debug(f"Recherche locale: {len(local_chunks)} chunks trouvés")
            return local_chunks

        except Exception as e:
            logger.warning(f"Erreur recherche locale: {e}")
            return []

    def _search_web_enhanced(self, question: str, max_results: int) -> tuple[List[Dict[str, Any]], List[str]]:
        """Recherche web avec processing complet"""

        search_queries = [question]  # Pour l'instant, requête simple

        try:
            # Recherche web
            search_results = self.web_search.search(question, max_results=max_results)

            # Processing HTML pour chaque résultat
            web_chunks = []
            for result in search_results:
                chunks = self.web_processor.process_search_result(result)
                web_chunks.extend(chunks)

            # Indexation temporaire (optionnel pour recherche future)
            if web_chunks:
                self._index_web_chunks_temporarily(web_chunks)

            logger.debug(f"Recherche web: {len(search_results)} résultats → {len(web_chunks)} chunks")
            return web_chunks, search_queries

        except Exception as e:
            logger.warning(f"Erreur recherche web: {e}")
            return [], search_queries

    def _index_web_chunks_temporarily(self, chunks: List[Dict[str, Any]]):
        """Indexation temporaire des chunks web (pour recherche future)"""

        try:
            # Préparer les données pour Qdrant
            points = []
            embeddings = []

            for chunk in chunks[:20]:  # Limiter pour performance
                # Générer embedding
                embedding = self.embedding_manager.encode_text(chunk["text"])

                # Préparer point
                point = {
                    "id": f"web_{chunk.get('chunk_id', 0)}_{hash(chunk['text']) % 1000000}",
                    "vector": embedding,
                    "payload": {
                        "text": chunk["text"],
                        "source": chunk.get("url", "web"),
                        "source_type": "web",
                        "timestamp": chunk.get("timestamp", datetime.now().timestamp())
                    }
                }

                points.append(point)
                embeddings.append(embedding)

            if points:
                # Indexer dans Qdrant (collection temporaire)
                self.vector_db.add_documents_batch(points)

                logger.debug(f"Indexation temporaire: {len(points)} chunks web")

        except Exception as e:
            logger.warning(f"Erreur indexation temporaire: {e}")

    def _fuse_results(self, local_results: List[Dict[str, Any]],
                     web_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fusion intelligente des résultats locaux et web
        """

        # Combiner tous les résultats
        all_results = local_results + web_results

        # Calculer scores de pertinence
        for result in all_results:
            result["relevance_score"] = self._calculate_relevance_score(result)

        # Trier par score décroissant
        sorted_results = sorted(all_results,
                              key=lambda x: x["relevance_score"],
                              reverse=True)

        # Diversification des sources (max 3 par source type)
        diversified = self._diversify_sources(sorted_results, max_per_source=3)

        # Limiter total
        final_results = diversified[:10]  # Maximum 10 chunks

        logger.debug(f"Fusion: {len(local_results)} local + {len(web_results)} web "
                    f"→ {len(final_results)} final")

        return final_results

    def _calculate_relevance_score(self, result: Dict[str, Any]) -> float:
        """Calculer score de pertinence d'un résultat"""

        score = 0.5  # Score de base

        # Bonus pour contenu récent (web)
        if result.get("source_type") == "web":
            timestamp = result.get("timestamp", 0)
            hours_old = (datetime.now().timestamp() - timestamp) / 3600

            if hours_old < 24:  # Moins de 24h
                score += 0.3
            elif hours_old < 168:  # Moins d'une semaine
                score += 0.2

        # Bonus pour sources locales (plus fiables)
        if result.get("source_type") == "local":
            score += 0.2

        # Pénalité pour texte trop court
        text_length = len(result.get("text", ""))
        if text_length < 100:
            score -= 0.2
        elif text_length > 1000:
            score += 0.1  # Bonus pour contenu détaillé

        return max(0.0, min(1.0, score))  # Normaliser entre 0 et 1

    def _diversify_sources(self, results: List[Dict[str, Any]],
                          max_per_source: int = 3) -> List[Dict[str, Any]]:
        """Diversification des sources pour éviter biais"""

        source_counts = {}
        diversified = []

        for result in results:
            source_type = result.get("source_type", "unknown")

            if source_counts.get(source_type, 0) < max_per_source:
                diversified.append(result)
                source_counts[source_type] = source_counts.get(source_type, 0) + 1

        return diversified

    def _generate_response(self, question: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Génération de réponse avec sources"""

        # Construction du contexte textuel
        context_text = self._build_context_text(context)

        # Construction du prompt
        prompt = self._build_web_aware_prompt(question, context_text)

        # Simulation de génération (à remplacer par vrai LLM)
        answer = self._simulate_generation(question, context)

        # Extraction des sources
        sources = self._extract_sources(context)

        return {
            "answer": answer,
            "sources": sources,
            "context_chunks": len(context),
            "context_length": len(context_text)
        }

    def _build_context_text(self, context: List[Dict[str, Any]]) -> str:
        """Construire le texte de contexte à partir des chunks"""

        context_parts = []

        for i, chunk in enumerate(context):
            source_type = chunk.get("source_type", "unknown")
            source = chunk.get("source", "unknown")

            # Marquer la source
            source_marker = f"[{source_type.upper()}: {source}]"

            context_parts.append(f"{source_marker}\n{chunk['text']}")

        return "\n\n---\n\n".join(context_parts)

    def _build_web_aware_prompt(self, question: str, context: str) -> str:
        """Construction du prompt pour agent web-aware"""

        prompt = f"""
Vous êtes un assistant intelligent qui combine connaissances internes et informations web.

CONTEXTE DISPONIBLE:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Utilisez les informations du contexte pour répondre
- Privilégiez les informations récentes pour les données temporelles
- Indiquez clairement vos sources quand pertinent
- Si l'information n'est pas dans le contexte, dites-le clairement
- Soyez précis et factuel

RÉPONSE:
"""

        return prompt.strip()

    def _simulate_generation(self, question: str, context: List[Dict[str, Any]]) -> str:
        """Génération de réponse avec LM Studio"""
        
        # Essayer d'utiliser LM Studio si disponible
        try:
            from src.lmstudio_client import get_lm_studio_client
            
            llm_client = get_lm_studio_client()
            
            # Tester la connexion
            if not llm_client.test_connection():
                logger.warning("LM Studio non disponible, utilisation du fallback")
                return self._fallback_generation(question, context)
            
            # Préparer les sources pour LM Studio
            sources = []
            for chunk in context[:5]:  # Max 5 sources
                sources.append({
                    "title": chunk.get("title", chunk.get("source", "Source")),
                    "url": chunk.get("url", chunk.get("source", "")),
                    "snippet": chunk.get("text", "")[:300]  # Limiter la longueur
                })
            
            # Construire le contexte textuel
            context_text = "\n\n".join([
                chunk.get("text", "")[:500]
                for chunk in context[:10]
            ])
            
            # Générer avec LM Studio
            logger.info(f"Génération LM Studio pour: '{question}'")
            answer = llm_client.generate_with_context(
                question=question,
                context=context_text,
                sources=sources
            )
            
            return answer
            
        except ImportError:
            logger.warning("Module lmstudio_client non disponible")
            return self._fallback_generation(question, context)
        except Exception as e:
            logger.error(f"Erreur génération LM Studio: {e}")
            return self._fallback_generation(question, context)
    
    def _fallback_generation(self, question: str, context: List[Dict[str, Any]]) -> str:
        """Génération de fallback si LM Studio non disponible"""
        
        # Analyse basique du contexte
        has_local = any(c.get("source_type") == "local" for c in context)
        has_web = any(c.get("source_type") == "web" for c in context)

        # Réponse basée sur disponibilité des sources
        if has_web and has_local:
            return "Basé sur les documents internes et les informations web récentes, voici la réponse à votre question."
        elif has_web:
            return "Selon les informations trouvées sur le web, voici ce que je peux vous dire."
        elif has_local:
            return "D'après les documents internes, voici la réponse à votre question."
        else:
            return "Je n'ai pas trouvé d'informations pertinentes dans les sources disponibles."

    def _extract_sources(self, context: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extraire la liste des sources utilisées"""

        sources = []
        seen_sources = set()

        for chunk in context:
            source = chunk.get("source", "unknown")
            source_type = chunk.get("source_type", "unknown")

            if source not in seen_sources:
                sources.append({
                    "url": source if source_type == "web" else "",
                    "type": source_type,
                    "title": chunk.get("title", source)
                })
                seen_sources.add(source)

        return sources

    def get_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques du pipeline"""
        return {
            **self.stats,
            "memory_interactions": len(self.memory.interactions),
            "cache_size": len(self.memory.search_cache)
        }

# Instance globale
extended_rag_pipeline = ExtendedRAGPipeline()

def get_extended_rag_pipeline() -> ExtendedRAGPipeline:
    """Factory function pour l'instance globale"""
    return extended_rag_pipeline

# Tests unitaires
if __name__ == "__main__":
    print("🧪 Test du ExtendedRAGPipeline")
    print("=" * 50)

    # Initialisation
    pipeline = ExtendedRAGPipeline()

    # Test simple
    question = "prix bitcoin aujourd'hui"

    print(f"🔍 Test question: '{question}'")
    print("-" * 40)

    try:
        response = pipeline.ask_question(question, use_web=True, max_web_results=2)

        print("✅ Réponse générée:")
        print(f"   Texte: {response['answer'][:100]}...")
        print(f"   Sources: {len(response.get('sources', []))}")
        print(f"   Chunks locaux: {response.get('local_sources', 0)}")
        print(f"   Temps: {response.get('processing_time', 0):.2f}s")

        # Statistiques
        stats = pipeline.get_stats()
        print("\n📊 Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

    print("\n✅ Test terminé!")