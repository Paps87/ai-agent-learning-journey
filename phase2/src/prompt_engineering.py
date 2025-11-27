"""
Techniques avancées de Prompt Engineering pour RAG - Phase 2
Amélioration des prompts pour des réponses plus précises et contextuelles
"""

from typing import List, Dict, Any, Optional
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class PromptStyle(Enum):
    """Styles de prompts disponibles"""
    CONCISE = "concise"  # Réponses courtes et directes
    DETAILED = "detailed"  # Réponses détaillées avec explications
    TECHNICAL = "technical"  # Langage technique pour experts
    FRIENDLY = "friendly"  # Ton amical et accessible
    FORMAL = "formal"  # Langage formel professionnel

class RoleType(Enum):
    """Types de rôles pour le prompt engineering"""
    IT_SUPPORT = "it_support"
    HR_ASSISTANT = "hr_assistant"
    GENERAL_ASSISTANT = "general_assistant"
    TECHNICAL_EXPERT = "technical_expert"

class PromptEngineer:
    """
    Gestionnaire de prompt engineering avancé
    Techniques: role-playing, chain-of-thought, few-shot learning, etc.
    """

    def __init__(self):
        self.role_templates = self._initialize_role_templates()
        self.style_templates = self._initialize_style_templates()
        logger.info("PromptEngineer initialisé")

    def _initialize_role_templates(self) -> Dict[RoleType, str]:
        """Initialise les templates de rôles"""
        return {
            RoleType.IT_SUPPORT: """
Tu es un expert en support informatique chez TechCorp. Ton rôle est d'aider les employés avec:
- Problèmes techniques et configurations
- Accès aux systèmes et authentification
- Matériel informatique et logiciels
- Sécurité et bonnes pratiques

Ton expertise: réseaux, VPN, emails, imprimantes, mots de passe, Active Directory.
""",

            RoleType.HR_ASSISTANT: """
Tu es un assistant RH chez TechCorp. Ton rôle est d'aider avec:
- Demandes de congés et absences
- Processus d'évaluation et développement
- Avantages sociaux et rémunération
- Politiques d'entreprise et procédures

Ton expertise: portail RH, congés payés, évaluations, formations.
""",

            RoleType.TECHNICAL_EXPERT: """
Tu es un expert technique senior chez TechCorp. Ton public est technique:
- Développeurs, DevOps, ingénieurs système
- Langage technique précis et détaillé
- Solutions complexes et architectures
- Bonnes pratiques et optimisations
""",

            RoleType.GENERAL_ASSISTANT: """
Tu es un assistant général chez TechCorp. Ton rôle est d'aider avec:
- Questions générales sur l'entreprise
- Orientation vers les bons services
- Informations de base et procédures
- Support polyvalent et bienveillant
"""
        }

    def _initialize_style_templates(self) -> Dict[PromptStyle, str]:
        """Initialise les templates de styles"""
        return {
            PromptStyle.CONCISE: "Réponds de manière concise et directe. Maximum 2-3 phrases.",
            PromptStyle.DETAILED: """
Fournis une réponse détaillée avec:
- Explications étape par étape
- Contextes et raisons
- Exemples concrets si pertinent
- Alternatives possibles
""",
            PromptStyle.TECHNICAL: """
Utilise un langage technique précis:
- Terminologie spécifique au domaine
- Détails techniques approfondis
- Références aux systèmes internes
- Codes d'erreur et solutions techniques
""",
            PromptStyle.FRIENDLY: """
Adopte un ton amical et accessible:
- Langage simple et clair
- Empathie et encouragement
- Emojis occasionnels si approprié 😊
- Phrases courtes et positives
""",
            PromptStyle.FORMAL: """
Utilise un langage formel professionnel:
- Structure officielle et polie
- Termes précis et complets
- Formulations diplomatiques
- Respect des protocoles d'entreprise
"""
        }

    def detect_role_from_query(self, query: str) -> RoleType:
        """
        Détecte automatiquement le rôle approprié basé sur la requête

        Args:
            query: Question de l'utilisateur

        Returns:
            RoleType approprié
        """
        query_lower = query.lower()
        
        # Détection basée sur les mots-clés
        it_keywords = ['vpn', 'mot de passe', 'email', 'imprimante', 'réseau', 'configurer', 'technique']
        hr_keywords = ['congés', 'rh', 'évaluation', 'formation', 'salaire', 'avantages', 'absences']
        technical_keywords = ['api', 'code', 'déploiement', 'git', 'docker', 'kubernetes', 'database']
        
        if any(keyword in query_lower for keyword in it_keywords):
            return RoleType.IT_SUPPORT
        elif any(keyword in query_lower for keyword in hr_keywords):
            return RoleType.HR_ASSISTANT
        elif any(keyword in query_lower for keyword in technical_keywords):
            return RoleType.TECHNICAL_EXPERT
        else:
            return RoleType.GENERAL_ASSISTANT

    def detect_style_from_query(self, query: str) -> PromptStyle:
        """
        Détecte automatiquement le style approprié

        Args:
            query: Question de l'utilisateur

        Returns:
            PromptStyle approprié
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['détaillé', 'explication', 'comment', 'pourquoi']):
            return PromptStyle.DETAILED
        elif any(word in query_lower for word in ['technique', 'expert', 'avancé', 'config']):
            return PromptStyle.TECHNICAL
        elif any(word in query_lower for word in ['simple', 'rapide', 'court', 'résumé']):
            return PromptStyle.CONCISE
        elif any(word in query_lower for word in ['urgence', 'important', 'officiel']):
            return PromptStyle.FORMAL
        else:
            return PromptStyle.FRIENDLY

    def build_enhanced_prompt(self, query: str, context: str, 
                           role: Optional[RoleType] = None,
                           style: Optional[PromptStyle] = None) -> str:
        """
        Construit un prompt avancé avec engineering

        Args:
            query: Question de l'utilisateur
            context: Contexte RAG
            role: Rôle spécifique (optionnel, auto-détecté sinon)
            style: Style spécifique (optionnel, auto-détecté sinon)

        Returns:
            Prompt optimisé
        """
        # Auto-détection si non spécifié
        detected_role = role or self.detect_role_from_query(query)
        detected_style = style or self.detect_style_from_query(query)
        
        # Récupérer les templates
        role_template = self.role_templates[detected_role]
        style_template = self.style_templates[detected_style]
        
        prompt = f"""
# RÔLE ET CONTEXTE
{role_template}

# STYLE DE RÉPONSE
{style_template}

# CONTRAINTES IMPORTANTES
- Utilise EXCLUSIVEMENT le contexte fourni pour répondre
- Si l'information n'est pas dans le contexte, dis clairement que tu ne sais pas
- Ne invente jamais d'information
- Cite tes sources quand c'est pertinent
- Sois précis et factuel

# CONTEXTE DOCUMENTAIRE
{context}

# QUESTION UTILISATEUR
{query}

# RÉPONSE (en français):
"""
        logger.info(f"Prompt construit - Rôle: {detected_role.value}, Style: {detected_style.value}")
        return prompt.strip()

    def add_chain_of_thought(self, prompt: str) -> str:
        """
        Ajoute un raisonnement étape par étape au prompt

        Args:
            prompt: Prompt original

        Returns:
            Prompt avec chain-of-thought
        """
        cot_addition = """

# PROCESSUS DE RAISONNEMENT
Avant de répondre, réfléchis étape par étape:
1. Analyse la question et identifie le besoin principal
2. Examine le contexte pour trouver les informations pertinentes  
3. Vérifie la cohérence et la complétude des informations
4. Structure ta réponse de manière logique
5. Valide que la réponse est basée uniquement sur le contexte

Maintenant, fournis ta réponse:
"""
        return prompt + cot_addition

    def add_few_shot_examples(self, prompt: str, examples: List[Dict[str, str]]) -> str:
        """
        Ajoute des exemples few-shot au prompt

        Args:
            prompt: Prompt original
            examples: Liste d'exemples {question: ..., réponse: ...}

        Returns:
            Prompt avec exemples
        """
        examples_section = "\n\n# EXEMPLES DE RÉPONSES (à suivre comme modèle):\n"
        
        for i, example in enumerate(examples, 1):
            examples_section += f"""
Exemple {i}:
Question: {example['question']}
Réponse: {example['answer']}
"""
        
        return prompt + examples_section

    def add_validation_check(self, prompt: str) -> str:
        """
        Ajoute une vérification de validation de réponse

        Args:
            prompt: Prompt original

        Returns:
            Prompt avec validation
        """
        validation_add = """

# VALIDATION FINALE
Avant de soumettre ta réponse, vérifie:
✅ La réponse est basée à 100% sur le contexte fourni
✅ Aucune information n'est inventée ou extrapolée  
✅ Le ton et le style correspondent au rôle
✅ La réponse est complète mais concise
✅ Les sources sont citées si nécessaire

Réponse finale:
"""
        return prompt + validation_add

# Instance globale
prompt_engineer = PromptEngineer()

def get_prompt_engineer() -> PromptEngineer:
    """Factory function pour l'instance globale"""
    return prompt_engineer

# Tests unitaires
if __name__ == "__main__":
    print("=== Test Prompt Engineering ===")
    
    try:
        engineer = PromptEngineer()
        
        # Test questions variées
        test_queries = [
            "Comment configurer le VPN ?",
            "Je veux comprendre le processus d'évaluation annuelle en détail",
            "Problème technique urgent avec mon email",
            "Simple rappel sur les congés"
        ]
        
        context = "[Document 1]\nConfiguration VPN: vpn.entreprise.com\n[Document 2]\nCongés: portail RH\n[Document 3]\nÉvaluation: décembre"
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            
            # Auto-détection
            role = engineer.detect_role_from_query(query)
            style = engineer.detect_style_from_query(query)
            
            print(f"🤖 Rôle détecté: {role.value}")
            print(f"🎨 Style détecté: {style.value}")
            
            # Construction prompt
            prompt = engineer.build_enhanced_prompt(query, context)
            print(f"📝 Prompt length: {len(prompt)} caractères")
            print(f"📋 Preview: {prompt[:200]}...")
        
        print("\n✅ Tests Prompt Engineering réussis !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()