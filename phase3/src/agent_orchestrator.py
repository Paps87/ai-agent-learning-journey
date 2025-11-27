#!/usr/bin/env python3
"""
Agent Orchestrator pour Phase 3 - Ask-the-Web Agent
Coordonne les recherches multi-étapes et la synthèse d'informations
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import re
from datetime import datetime
import json
import sys
import os

# Ajouter le répertoire parent au path pour imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Imports Phase 3
from src.extended_rag_pipeline import get_extended_rag_pipeline
from src.web_search import get_web_search_engine

logger = logging.getLogger(__name__)

class SearchPlanner:
    """
    Planificateur de recherches pour questions complexes
    """

    def __init__(self):
        self.complexity_patterns = {
            "comparison": re.compile(r"(comparer|comparaison|vs|versus|différence)", re.I),
            "multi_aspect": re.compile(r"(et|ainsi que|également|plus|comment|pourquoi|quand|où)", re.I),
            "temporal": re.compile(r"(aujourd'hui|hier|demain|cette année|dernier|prochain|récemment)", re.I),
            "quantitative": re.compile(r"(prix|coût|valeur|montant|chiffre|statistique|pourcentage)", re.I)
        }

    def analyze_question(self, question: str) -> Dict[str, Any]:
        """
        Analyse la question pour déterminer la stratégie de recherche

        Returns:
            Dictionnaire avec analyse et plan
        """
        analysis = {
            "needs_web": self._needs_web_search(question),
            "complexity": self._assess_complexity(question),
            "sub_questions": self._break_down_question(question),
            "search_strategy": "single",  # single, sequential, parallel
            "estimated_searches": 1
        }

        # Déterminer la stratégie
        if len(analysis["sub_questions"]) > 1:
            if analysis["complexity"] > 7:
                analysis["search_strategy"] = "sequential"
            else:
                analysis["search_strategy"] = "parallel"
            analysis["estimated_searches"] = len(analysis["sub_questions"])

        logger.info(f"Analyse question: stratégie={analysis['search_strategy']}, "
                   f"recherches={analysis['estimated_searches']}")

        return analysis

    def _needs_web_search(self, question: str) -> bool:
        """Détermine si la question nécessite une recherche web"""

        # Mots-clés indiquant une recherche web
        web_indicators = [
            "aujourd'hui", "actuellement", "récemment", "dernier", "nouveau",
            "prix", "coût", "valeur", "statistique", "actualité", "news",
            "météo", "température", "prévision", "cours", "bourse",
            "site web", "internet", "online", "disponible"
        ]

        question_lower = question.lower()
        return any(indicator in question_lower for indicator in web_indicators)

    def _assess_complexity(self, question: str) -> int:
        """Évalue la complexité de la question (0-10)"""

        complexity = 0

        # Longueur de la question
        if len(question.split()) > 15:
            complexity += 2

        # Patterns de complexité
        for pattern_name, pattern in self.complexity_patterns.items():
            if pattern.search(question):
                complexity += 2

        # Questions multiples
        if question.count('?') > 1 or any(word in question.lower() for word in ['et', 'ou', 'mais']):
            complexity += 3

        return min(10, complexity)

    def _break_down_question(self, question: str) -> List[str]:
        """Décompose la question en sous-questions si nécessaire"""

        # Pour l'instant, logique simple
        sub_questions = [question]

        # Si question très longue, essayer de diviser
        if len(question.split()) > 20:
            # Diviser par les connecteurs logiques
            parts = re.split(r'(?:et|ou|mais|ainsi que|également)', question)
            if len(parts) > 1:
                sub_questions = [part.strip() + '?' for part in parts if part.strip()]

        return sub_questions

class WebAwareAgent:
    """
    Agent intelligent capable de recherches web multi-étapes
    """

    def __init__(self):
        self.planner = SearchPlanner()
        
        # Vérifier disponibilité des composants
        try:
            self.rag_pipeline = get_extended_rag_pipeline()
            self.web_search = get_web_search_engine()
            self.available = True
        except Exception as e:
            logger.error(f"Erreur initialisation agent: {e}")
            self.rag_pipeline = None
            self.web_search = None
            self.available = False

        # Statistiques
        self.stats = {
            "total_questions": 0,
            "web_searches_performed": 0,
            "sub_questions_generated": 0,
            "average_response_time": 0
        }

        logger.info(f"WebAwareAgent initialisé (available={self.available})")

    def answer_question(self, question: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Répond à une question en utilisant l'orchestration intelligente

        Args:
            question: Question de l'utilisateur
            max_depth: Profondeur maximale de recherche

        Returns:
            Réponse complète avec métadonnées
        """

        start_time = datetime.now()
        self.stats["total_questions"] += 1

        logger.info(f"🤖 Traitement question: '{question}'")

        try:
            if not self.available:
                return {
                    "answer": "Le système de recherche web n'est pas disponible actuellement. Veuillez vérifier que tous les composants sont installés.",
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "search_strategy": "unavailable"
                }

            # 1. Analyse et planification
            analysis = self.planner.analyze_question(question)

            # 2. Exécution selon la stratégie
            if analysis["search_strategy"] == "single":
                response = self._execute_single_search(question, analysis)

            elif analysis["search_strategy"] == "parallel":
                response = self._execute_parallel_search(analysis["sub_questions"], analysis)

            elif analysis["search_strategy"] == "sequential":
                response = self._execute_sequential_search(analysis["sub_questions"], analysis, max_depth)

            else:
                response = self._execute_single_search(question, analysis)

            # 3. Métriques finales
            processing_time = (datetime.now() - start_time).total_seconds()
            response["processing_time"] = processing_time
            response["search_strategy"] = analysis["search_strategy"]
            response["sub_questions_count"] = len(analysis["sub_questions"])

            # Mise à jour stats
            self.stats["web_searches_performed"] += analysis["estimated_searches"]
            self.stats["sub_questions_generated"] += len(analysis["sub_questions"])

            # Moyenne glissante du temps de réponse
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (self.stats["total_questions"] - 1)) +
                processing_time
            ) / self.stats["total_questions"]

            logger.info(f"✅ Réponse générée: {len(response.get('answer', ''))} caractères, "
                       f"stratégie={analysis['search_strategy']}, temps={processing_time:.2f}s")

            return response

        except Exception as e:
            logger.error(f"❌ Erreur agent: {e}")
            return {
                "answer": "Désolé, une erreur s'est produite lors du traitement de votre question.",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "search_strategy": "error"
            }

    def _execute_single_search(self, question: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Exécution d'une recherche simple"""

        use_web = analysis.get("needs_web", True)
        return self.rag_pipeline.ask_question(question, use_web=use_web)

    def _execute_parallel_search(self, sub_questions: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Exécution de recherches en parallèle"""

        logger.info(f"🔀 Recherche parallèle: {len(sub_questions)} sous-questions")

        # Effectuer les recherches en parallèle (simulation)
        sub_responses = []
        all_web_sources = []
        all_local_sources = 0

        for sub_q in sub_questions:
            response = self._execute_single_search(sub_q, analysis)
            sub_responses.append({
                "question": sub_q,
                "answer": response.get("answer", ""),
                "sources": response.get("sources", [])
            })

            # Collecter les sources
            all_web_sources.extend(response.get("web_sources", []))
            all_local_sources += response.get("local_sources", 0)

        # Synthèse des réponses
        combined_answer = self._synthesize_responses(sub_questions, sub_responses)

        return {
            "answer": combined_answer,
            "sources": self._merge_sources(sub_responses),
            "web_sources": list(set(all_web_sources)),
            "local_sources": all_local_sources,
            "sub_responses": sub_responses
        }

    def _execute_sequential_search(self, sub_questions: List[str], analysis: Dict[str, Any], max_depth: int) -> Dict[str, Any]:
        """Exécution de recherches séquentielles avec raffinement"""

        logger.info(f"🔗 Recherche séquentielle: {len(sub_questions)} étapes")

        current_context = ""
        all_responses = []

        for i, sub_q in enumerate(sub_questions):
            if i >= max_depth:
                break

            # Enrichir la question avec le contexte précédent
            enriched_question = sub_q
            if current_context:
                enriched_question = f"{sub_q} (Contexte: {current_context[:200]}...)"

            response = self._execute_single_search(enriched_question, analysis)
            all_responses.append({
                "step": i + 1,
                "question": sub_q,
                "enriched_question": enriched_question,
                "answer": response.get("answer", ""),
                "sources": response.get("sources", [])
            })

            # Mettre à jour le contexte pour l'étape suivante
            current_context += f" {response.get('answer', '')}"

        # Synthèse finale
        final_answer = self._synthesize_sequential_responses(sub_questions, all_responses)

        return {
            "answer": final_answer,
            "sources": self._merge_sources(all_responses),
            "sequential_steps": all_responses
        }

    def _synthesize_responses(self, sub_questions: List[str], sub_responses: List[Dict[str, Any]]) -> str:
        """Synthèse des réponses parallèles"""

        # Construction d'une réponse cohérente
        synthesis_parts = []

        synthesis_parts.append("Voici une synthèse des informations trouvées:")

        for i, resp in enumerate(sub_responses):
            question = resp["question"]
            answer = resp["answer"][:300] + "..." if len(resp["answer"]) > 300 else resp["answer"]

            synthesis_parts.append(f"\n**{question}**\n{answer}")

        synthesis_parts.append("\nCette réponse combine des informations provenant de sources multiples.")

        return "\n".join(synthesis_parts)

    def _synthesize_sequential_responses(self, sub_questions: List[str], step_responses: List[Dict[str, Any]]) -> str:
        """Synthèse des réponses séquentielles"""

        synthesis_parts = ["Voici le résultat de l'analyse étape par étape:"]

        for resp in step_responses:
            step = resp["step"]
            question = resp["question"]
            answer = resp["answer"]

            synthesis_parts.append(f"\n### Étape {step}: {question}")
            synthesis_parts.append(answer)

        synthesis_parts.append("\n**Conclusion:** Cette analyse progressive permet d'approfondir le sujet.")

        return "\n".join(synthesis_parts)

    def _merge_sources(self, responses: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Fusion des sources de toutes les réponses"""

        all_sources = []
        seen_urls = set()

        for resp in responses:
            for source in resp.get("sources", []):
                url = source.get("url", "")
                if url and url not in seen_urls:
                    all_sources.append(source)
                    seen_urls.add(url)

        return all_sources

    def get_agent_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'agent"""
        return {
            **self.stats,
            "planner_complexity_patterns": len(self.planner.complexity_patterns)
        }

# Instance globale
web_aware_agent = WebAwareAgent()

def get_web_aware_agent() -> WebAwareAgent:
    """Factory function pour l'instance globale"""
    return web_aware_agent

# Tests unitaires
if __name__ == "__main__":
    print("🧪 Test de l'Agent Orchestrator")
    print("=" * 50)

    # Initialisation
    agent = WebAwareAgent()

    # Tests avec différentes questions
    test_questions = [
        "Quel est le prix du Bitcoin aujourd'hui?",
        "Comparez les langages Python et JavaScript pour le développement web",
        "Quelles sont les actualités récentes sur l'IA et comment ça impacte le marché du travail?"
    ]

    for question in test_questions:
        print(f"\n🤖 Question: '{question}'")
        print("-" * 60)

        try:
            response = agent.answer_question(question)

            print("✅ Réponse générée:")
            print(f"   Stratégie: {response.get('search_strategy', 'unknown')}")
            print(f"   Temps: {response.get('processing_time', 0):.2f}s")
            print(f"   Sources: {len(response.get('sources', []))}")
            print(f"   Texte: {response.get('answer', '')[:200]}...")

        except Exception as e:
            print(f"❌ Erreur: {e}")

    # Statistiques finales
    print("\n📊 Statistiques de l'agent:")
    stats = agent.get_agent_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Tests terminés!")