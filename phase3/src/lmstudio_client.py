#!/usr/bin/env python3
"""
Client LM Studio pour Phase 3 - Mini Perplexity
Communique avec LM Studio via l'API OpenAI-compatible
"""

import requests
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class LMStudioClient:
    """
    Client pour communiquer avec LM Studio
    Compatible avec l'API OpenAI
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = "gad-gpt-5-chat-llama-3.1-8b-instruct-i1",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 120  # Augmenté à 120s pour LM Studio
    ):
        """
        Initialise le client LM Studio
        
        Args:
            base_url: URL de base de LM Studio
            model: Nom du modèle à utiliser
            temperature: Température de génération (0-1)
            max_tokens: Nombre maximum de tokens
            timeout: Timeout en secondes
        """
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        logger.info(f"LMStudioClient initialisé: {base_url}, modèle={model}")
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à LM Studio
        
        Returns:
            True si connecté, False sinon
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=5
            )
            response.raise_for_status()
            
            models = response.json().get("data", [])
            logger.info(f"✅ LM Studio connecté: {len(models)} modèles disponibles")
            return True
            
        except Exception as e:
            logger.error(f"❌ LM Studio non accessible: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Génère une réponse avec LM Studio
        
        Args:
            prompt: Prompt utilisateur
            system_prompt: Prompt système (optionnel)
            temperature: Override température
            max_tokens: Override max_tokens
            
        Returns:
            Réponse générée
        """
        try:
            # Construire les messages
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Paramètres de génération
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            logger.debug(f"Génération LM Studio: {len(prompt)} caractères")
            
            # Appel API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Extraire la réponse
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            logger.info(f"✅ Réponse générée: {len(answer)} caractères")
            return answer
            
        except requests.exceptions.Timeout:
            logger.error("⏰ Timeout lors de la génération")
            return "Désolé, la génération a pris trop de temps. Veuillez réessayer."
            
        except requests.exceptions.ConnectionError:
            logger.error("🌐 LM Studio non accessible")
            return "Erreur: LM Studio n'est pas accessible. Vérifiez qu'il est bien lancé sur le port 1234."
            
        except Exception as e:
            logger.error(f"💥 Erreur génération: {e}")
            return f"Erreur lors de la génération: {str(e)}"
    
    def generate_with_context(
        self,
        question: str,
        context: str,
        sources: List[Dict[str, str]]
    ) -> str:
        """
        Génère une réponse avec contexte et sources
        Format optimisé pour Mini Perplexity
        
        Args:
            question: Question de l'utilisateur
            context: Contexte extrait des recherches
            sources: Liste des sources avec titre et URL
            
        Returns:
            Réponse avec citations [1], [2], etc.
        """
        
        # Construire le prompt système
        system_prompt = """Tu es un assistant de recherche intelligent et précis.

RÈGLES IMPORTANTES:
1. Réponds UNIQUEMENT avec les informations fournies dans les sources
2. Cite TOUJOURS tes sources avec [1], [2], [3], etc.
3. Sois précis, factuel et concis
4. Si l'information n'est pas dans les sources, dis-le clairement
5. Structure ta réponse de manière claire avec des paragraphes
6. N'invente JAMAIS d'informations"""

        # Construire le prompt utilisateur avec sources numérotées
        sources_text = "\n\n".join([
            f"[{i+1}] {source.get('title', 'Sans titre')}\n"
            f"URL: {source.get('url', 'N/A')}\n"
            f"Contenu: {source.get('snippet', '')}"
            for i, source in enumerate(sources)
        ])
        
        user_prompt = f"""SOURCES DISPONIBLES:
{sources_text}

CONTEXTE ADDITIONNEL:
{context[:1000]}

QUESTION: {question}

Réponds à la question en citant tes sources avec [1], [2], etc."""

        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Plus bas pour plus de précision
            max_tokens=1000  # Réduit pour réponses plus rapides
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du client"""
        return {
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout
        }

# Instance globale
lm_studio_client = LMStudioClient()

def get_lm_studio_client() -> LMStudioClient:
    """Factory function pour l'instance globale"""
    return lm_studio_client

# Tests
if __name__ == "__main__":
    print("🧪 Test du LM Studio Client")
    print("=" * 60)
    
    # Initialisation
    client = LMStudioClient()
    
    # Test connexion
    print("\n1. Test de connexion...")
    if client.test_connection():
        print("   ✅ Connexion réussie")
    else:
        print("   ❌ Connexion échouée")
        print("   💡 Vérifiez que LM Studio est lancé sur le port 1234")
        exit(1)
    
    # Test génération simple
    print("\n2. Test de génération simple...")
    response = client.generate("Dis bonjour en français")
    print(f"   Réponse: {response[:100]}...")
    
    # Test avec contexte
    print("\n3. Test avec contexte et sources...")
    sources = [
        {
            "title": "Bitcoin Price Today",
            "url": "https://coinmarketcap.com/currencies/bitcoin/",
            "snippet": "The live Bitcoin price is $87,426.84 USD"
        },
        {
            "title": "Bitcoin Analysis",
            "url": "https://example.com/btc",
            "snippet": "Bitcoin shows strong momentum in Q4 2024"
        }
    ]
    
    response = client.generate_with_context(
        question="Quel est le prix du Bitcoin?",
        context="Bitcoin est une cryptomonnaie populaire.",
        sources=sources
    )
    
    print(f"   Réponse: {response[:200]}...")
    
    # Statistiques
    print("\n4. Statistiques:")
    stats = client.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Tests terminés!")
