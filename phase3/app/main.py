"""
Interface Streamlit pour l'Agent Web-Aware - Phase 3
Interface utilisateur pour l'agent capable de recherches web intelligentes
"""

import streamlit as st
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Any
import json

# Ajouter le répertoire parent au path pour imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import des modules Phase 3
from src.agent_orchestrator import get_web_aware_agent
from src.extended_rag_pipeline import get_extended_rag_pipeline

# Configuration de la page
st.set_page_config(
    page_title="🌐 WebAware Agent - Ask-the-Web",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de l'état de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "web_agent" not in st.session_state:
    st.session_state.web_agent = get_web_aware_agent()
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = get_extended_rag_pipeline()

class WebAwareChatInterface:
    """Interface de chat pour l'agent web-aware"""

    def __init__(self):
        self.web_agent = st.session_state.web_agent
        self.rag_pipeline = st.session_state.rag_pipeline

    def display_sidebar(self):
        """Affiche la sidebar avec les paramètres"""
        with st.sidebar:
            st.title("⚙️ Paramètres de l'Agent")

            # Mode de fonctionnement
            st.subheader("🎯 Mode de Recherche")
            search_mode = st.selectbox(
                "Stratégie de recherche",
                ["Auto (Recommandé)", "Recherche Web Seulement", "Base Locale Seulement", "RAG Étendu"],
                index=0
            )

            # Paramètres de recherche web
            st.subheader("🌐 Paramètres Web")
            max_web_results = st.slider("Résultats web max", 1, 10, 3)
            max_search_depth = st.slider("Profondeur max de recherche", 1, 5, 3)

            # Paramètres avancés
            with st.expander("🔧 Paramètres Avancés"):
                show_sources = st.checkbox("Afficher les sources détaillées", value=True)
                show_search_strategy = st.checkbox("Afficher la stratégie de recherche", value=True)
                show_processing_time = st.checkbox("Afficher le temps de traitement", value=True)
                enable_memory = st.checkbox("Activer la mémoire conversationnelle", value=True)

            # Statistiques de l'agent
            st.subheader("📊 Statistiques")
            agent_stats = self.web_agent.get_agent_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Questions traitées", agent_stats.get("total_questions", 0))
                st.metric("Recherches web", agent_stats.get("web_searches_performed", 0))
            with col2:
                st.metric("Temps moyen", f"{agent_stats.get('average_response_time', 0):.2f}s")
                st.metric("Sous-questions", agent_stats.get("sub_questions_generated", 0))

            # Bouton reset
            if st.button("🔄 Réinitialiser la conversation"):
                st.session_state.messages = []
                st.rerun()

            return {
                "search_mode": search_mode,
                "max_web_results": max_web_results,
                "max_search_depth": max_search_depth,
                "show_sources": show_sources,
                "show_search_strategy": show_search_strategy,
                "show_processing_time": show_processing_time,
                "enable_memory": enable_memory
            }

    def display_chat_interface(self):
        """Affiche l'interface principale de chat"""
        st.title("🌐 WebAware Agent - Votre Assistant Web Intelligent")
        st.markdown("""
        **Je peux répondre à vos questions en combinant :**
        - 📚 **Connaissances locales** (documents internes)
        - 🌐 **Recherche web** (informations actuelles)
        - 🧠 **Raisonnement intelligent** (analyse et synthèse)

        **Exemples de questions :**
        - "Quel est le prix du Bitcoin aujourd'hui ?"
        - "Comparez Python et JavaScript pour le développement web"
        - "Quelles sont les dernières actualités sur l'IA ?"
        """)

        # Affichage des messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Affichage des métadonnées si présentes
                if "metadata" in message:
                    self._display_message_metadata(message["metadata"])

    def _display_message_metadata(self, metadata: Dict[str, Any]):
        """Affiche les métadonnées d'un message"""
        with st.expander("📊 Détails de la réponse"):
            cols = st.columns(3)

            # Colonne 1: Stratégie et performance
            with cols[0]:
                if "search_strategy" in metadata:
                    st.metric("Stratégie", metadata["search_strategy"])
                if "processing_time" in metadata:
                    st.metric("Temps", f"{metadata['processing_time']:.2f}s")
                if "sub_questions_count" in metadata:
                    st.metric("Sous-questions", metadata["sub_questions_count"])

            # Colonne 2: Sources
            with cols[1]:
                if "web_sources" in metadata:
                    st.metric("Sources Web", len(metadata["web_sources"]))
                if "local_sources" in metadata:
                    st.metric("Sources Locales", metadata["local_sources"])
                if "sources" in metadata:
                    st.metric("Total Sources", len(metadata["sources"]))

            # Colonne 3: Contenu
            with cols[2]:
                if "context_chunks" in metadata:
                    st.metric("Chunks utilisés", metadata["context_chunks"])
                if "context_length" in metadata:
                    st.metric("Longueur contexte", metadata["context_length"])

            # Affichage des sources détaillées
            if st.checkbox("Voir les sources", key=f"sources_{metadata.get('timestamp', 'unknown')}"):
                self._display_sources(metadata)

            # Affichage des étapes séquentielles si présentes
            if "sequential_steps" in metadata:
                self._display_sequential_steps(metadata["sequential_steps"])

    def _display_sources(self, metadata: Dict[str, Any]):
        """Affiche la liste détaillée des sources"""
        sources = metadata.get("sources", [])

        if not sources:
            st.info("Aucune source disponible")
            return

        st.subheader("🔗 Sources utilisées")

        for i, source in enumerate(sources, 1):
            source_type = source.get("type", "unknown")
            title = source.get("title", "Sans titre")
            url = source.get("url", "")

            col1, col2 = st.columns([3, 1])
            with col1:
                if url:
                    st.markdown(f"**{i}.** [{title}]({url})")
                else:
                    st.markdown(f"**{i}.** {title}")
            with col2:
                if source_type == "web":
                    st.info("🌐 Web")
                else:
                    st.success("📚 Local")

    def _display_sequential_steps(self, steps: List[Dict[str, Any]]):
        """Affiche les étapes d'une recherche séquentielle"""
        st.subheader("🔗 Recherche étape par étape")

        for step in steps:
            with st.expander(f"Étape {step['step']}: {step['question']}", expanded=False):
                st.markdown(f"**Question enrichie:** {step['enriched_question']}")
                st.markdown(f"**Réponse:** {step['answer']}")
                if step.get("sources"):
                    st.markdown(f"**Sources ({len(step['sources'])}):**")
                    for source in step["sources"]:
                        url = source.get("url", "")
                        if url:
                            st.markdown(f"- [{source.get('title', url)}]({url})")
                        else:
                            st.markdown(f"- {source.get('title', 'Source locale')}")

    def process_user_input(self, user_input: str, params: Dict[str, Any]):
        """Traite l'entrée utilisateur et génère une réponse"""
        try:
            # Ajouter le message utilisateur
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })

            # Afficher le message utilisateur
            with st.chat_message("user"):
                st.markdown(user_input)

            # Générer la réponse selon le mode
            with st.chat_message("assistant"):
                with st.spinner("🧠 Analyse de la question..."):
                    response = self._generate_response(user_input, params)

                # Afficher la réponse
                st.markdown(response["answer"])

                # Préparer les métadonnées
                metadata = {
                    "search_strategy": response.get("search_strategy", "unknown"),
                    "processing_time": response.get("processing_time", 0),
                    "sub_questions_count": response.get("sub_questions_count", 0),
                    "web_sources": response.get("web_sources", []),
                    "local_sources": response.get("local_sources", 0),
                    "sources": response.get("sources", []),
                    "context_chunks": response.get("context_chunks", 0),
                    "context_length": response.get("context_length", 0),
                    "timestamp": datetime.now().isoformat()
                }

                # Ajouter les étapes séquentielles si présentes
                if "sequential_steps" in response:
                    metadata["sequential_steps"] = response["sequential_steps"]

                # Ajouter le message assistant avec métadonnées
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata
                })

                # Affichage des métadonnées selon les paramètres
                if params["show_sources"] or params["show_search_strategy"] or params["show_processing_time"]:
                    self._display_message_metadata(metadata)

        except Exception as e:
            error_msg = "❌ Désolé, une erreur s'est produite lors du traitement de votre question."
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })

    def _generate_response(self, user_input: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Génère une réponse selon le mode sélectionné"""

        mode = params["search_mode"]

        if mode == "Auto (Recommandé)":
            # Utiliser l'agent intelligent
            return self.web_agent.answer_question(
                user_input,
                max_depth=params["max_search_depth"]
            )

        elif mode == "Recherche Web Seulement":
            # Recherche web uniquement
            return self.rag_pipeline.ask_question(
                user_input,
                use_web=True,
                max_web_results=params["max_web_results"]
            )

        elif mode == "Base Locale Seulement":
            # Base locale uniquement
            return self.rag_pipeline.ask_question(
                user_input,
                use_web=False
            )

        elif mode == "RAG Étendu":
            # RAG étendu avec web
            return self.rag_pipeline.ask_question(
                user_input,
                use_web=True,
                max_web_results=params["max_web_results"]
            )

        else:
            # Par défaut, mode auto
            return self.web_agent.answer_question(user_input)

def main():
    """Fonction principale de l'application"""
    chat_interface = WebAwareChatInterface()

    # Afficher la sidebar et récupérer les paramètres
    params = chat_interface.display_sidebar()

    # Afficher l'interface de chat
    chat_interface.display_chat_interface()

    # Gestion de l'entrée utilisateur
    user_input = st.chat_input("💬 Posez votre question (je peux chercher sur le web si nécessaire)...")

    if user_input:
        chat_interface.process_user_input(user_input, params)

if __name__ == "__main__":
    main()