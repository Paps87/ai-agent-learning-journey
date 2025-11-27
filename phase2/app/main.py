"""
Interface Streamlit pour le Chatbot RAG de Support Client - Phase 2
Interface utilisateur complète avec historique, paramètres et évaluation
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

# Import des modules RAG
from src.rag_pipeline import get_rag_pipeline
from src.prompt_engineering import get_prompt_engineer, RoleType, PromptStyle

# Configuration de la page
st.set_page_config(
    page_title="🤖 SupportBot RAG - TechCorp",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de l'état de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = get_rag_pipeline()
if "prompt_engineer" not in st.session_state:
    st.session_state.prompt_engineer = get_prompt_engineer()

class ChatInterface:
    """Interface de chat pour le chatbot RAG"""
    
    def __init__(self):
        self.rag_pipeline = st.session_state.rag_pipeline
        self.prompt_engineer = st.session_state.prompt_engineer
        
    def display_sidebar(self):
        """Affiche la sidebar avec les paramètres"""
        with st.sidebar:
            st.title("⚙️ Paramètres du Chatbot")
            
            # Paramètres de recherche
            st.subheader("🔍 Paramètres de Recherche")
            max_results = st.slider("Nombre max de résultats", 1, 10, 3)
            score_threshold = st.slider("Seuil de pertinence", 0.0, 1.0, 0.3, 0.05)
            
            # Paramètres de prompt engineering
            st.subheader("🎨 Engineering de Prompt")
            
            # Sélection manuelle du rôle
            role_options = {role.value: role for role in RoleType}
            selected_role = st.selectbox(
                "Rôle de l'assistant",
                options=list(role_options.keys()),
                index=0
            )
            
            # Sélection manuelle du style
            style_options = {style.value: style for style in PromptStyle}
            selected_style = st.selectbox(
                "Style de réponse",
                options=list(style_options.keys()),
                index=4  # Friendly par défaut
            )
            
            # Auto-détection
            auto_detect = st.checkbox("Auto-détection rôle/style", value=True)
            
            # Paramètres avancés
            with st.expander("Paramètres avancés"):
                show_context = st.checkbox("Afficher le contexte", value=False)
                show_prompt = st.checkbox("Afficher le prompt", value=False)
                enable_evaluation = st.checkbox("Évaluation des réponses", value=True)
            
            # Statistiques
            st.subheader("📊 Statistiques")
            st.info(f"💬 Messages: {len(st.session_state.messages)}")
            
            # Bouton reset
            if st.button("🔄 Réinitialiser la conversation"):
                st.session_state.messages = []
                st.rerun()
            
            return {
                "max_results": max_results,
                "score_threshold": score_threshold,
                "role": role_options[selected_role] if not auto_detect else None,
                "style": style_options[selected_style] if not auto_detect else None,
                "show_context": show_context,
                "show_prompt": show_prompt,
                "enable_evaluation": enable_evaluation,
                "auto_detect": auto_detect
            }
    
    def display_chat_interface(self):
        """Affiche l'interface principale de chat"""
        st.title("🤖 SupportBot RAG - Assistant de Support TechCorp")
        st.markdown("""
        **Posez vos questions sur:** 
        - 🖥️ Support IT (VPN, emails, mots de passe)
        - 👥 Ressources Humaines (congés, évaluations)
        - 🏢 Politiques d'entreprise
        - Et bien plus...
        """)
        
        # Affichage des messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Affichage des métadonnées si présentes
                if "metadata" in message:
                    with st.expander("📊 Détails techniques"):
                        st.json(message["metadata"])
    
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
            
            # Générer la réponse
            with st.chat_message("assistant"):
                with st.spinner("🔍 Recherche dans la documentation..."):
                    # Appel au pipeline RAG
                    result = self.rag_pipeline.ask_question(
                        user_input,
                        max_context_results=params["max_results"],
                        score_threshold=params["score_threshold"]
                    )
                
                # Afficher la réponse
                st.markdown(result["answer"])
                
                # Préparer les métadonnées
                metadata = {
                    "metrics": result["metrics"],
                    "timestamp": datetime.now().isoformat()
                }
                
                # Ajouter des informations de prompt engineering si demandé
                if params["show_prompt"]:
                    metadata["prompt_preview"] = result["prompt"][:500] + "..." if len(result["prompt"]) > 500 else result["prompt"]
                
                if params["show_context"]:
                    metadata["context_preview"] = result["context"][:500] + "..." if len(result["context"]) > 500 else result["context"]
                
                # Information de prompt engineering
                if params["auto_detect"]:
                    detected_role = self.prompt_engineer.detect_role_from_query(user_input)
                    detected_style = self.prompt_engineer.detect_style_from_query(user_input)
                    metadata["prompt_engineering"] = {
                        "detected_role": detected_role.value,
                        "detected_style": detected_style.value
                    }
                else:
                    metadata["prompt_engineering"] = {
                        "selected_role": params["role"].value,
                        "selected_style": params["style"].value
                    }
                
                # Évaluation si activée
                if params["enable_evaluation"]:
                    evaluation = self._evaluate_response(user_input, result["answer"], result["context"])
                    metadata["evaluation"] = evaluation
                
                # Ajouter le message assistant avec métadonnées
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata
                })
                
                # Afficher les détails techniques si demandés
                if params["show_context"] or params["show_prompt"]:
                    with st.expander("📊 Détails techniques"):
                        st.json(metadata)
        
        except Exception as e:
            error_msg = "❌ Désolé, une erreur s'est produite. Veuillez réessayer."
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
    
    def _evaluate_response(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """Évalue la qualité de la réponse"""
        # Métriques simples d'évaluation
        evaluation = {
            "question_length": len(question.split()),
            "answer_length": len(answer.split()),
            "context_length": len(context.split()),
            "has_context": "Aucune information" not in context,
            "response_time": datetime.now().isoformat(),
            "score": self._calculate_response_score(question, answer, context)
        }
        
        return evaluation
    
    def _calculate_response_score(self, question: str, answer: str, context: str) -> float:
        """Calcule un score de qualité pour la réponse"""
        score = 0.0
        
        # Points pour la présence de contexte
        if "Aucune information" not in context:
            score += 0.4
        
        # Points pour la longueur de la réponse (ni trop court ni trop long)
        answer_words = len(answer.split())
        if 10 <= answer_words <= 100:
            score += 0.3
        elif answer_words > 100:
            score += 0.2
        else:
            score += 0.1
        
        # Points pour la pertinence (vérification basique des mots-clés)
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        relevant_keywords = ["vpn", "congés", "évaluation", "portail", "email", "mot de passe"]
        matches = sum(1 for keyword in relevant_keywords if keyword in question_lower and keyword in answer_lower)
        
        if matches > 0:
            score += 0.3 * min(matches, 3)  # Max 0.9 pour les mots-clés
        
        return min(score, 1.0)  # Normaliser à 1.0 max

def main():
    """Fonction principale de l'application"""
    chat_interface = ChatInterface()
    
    # Afficher la sidebar et récupérer les paramètres
    params = chat_interface.display_sidebar()
    
    # Afficher l'interface de chat
    chat_interface.display_chat_interface()
    
    # Gestion de l'entrée utilisateur
    user_input = st.chat_input("💬 Posez votre question sur le support...")
    
    if user_input:
        chat_interface.process_user_input(user_input, params)

if __name__ == "__main__":
    main()