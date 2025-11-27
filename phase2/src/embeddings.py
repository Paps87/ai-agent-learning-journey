"""
Système d'embeddings pour RAG - Phase 2
Conversion de texte en vecteurs numériques pour recherche sémantique
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """
    Gestionnaire d'embeddings utilisant Sentence Transformers
    Modèle recommandé : all-MiniLM-L6-v2 (384 dimensions, performant)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialise le modèle d'embeddings

        Args:
            model_name: Nom du modèle Sentence Transformers à utiliser
        """
        self.model_name = model_name
        self.model = None
        self.dimension = None

        logger.info(f"Initialisation EmbeddingManager avec modèle {model_name}")

    def load_model(self):
        """Charge le modèle d'embeddings"""
        try:
            self.model = SentenceTransformer(self.model_name)
            # Test avec un texte simple pour déterminer la dimension
            test_embedding = self.model.encode("test")
            self.dimension = len(test_embedding)

            logger.info(f"Modèle {self.model_name} chargé. Dimension: {self.dimension}")

        except Exception as e:
            logger.error(f"Erreur chargement modèle {self.model_name}: {e}")
            raise

    def encode_text(self, text: str) -> np.ndarray:
        """
        Convertit un texte en vecteur d'embedding

        Args:
            text: Texte à encoder

        Returns:
            Vecteur numpy de dimension fixe
        """
        if self.model is None:
            raise ValueError("Modèle non chargé. Appelez load_model() d'abord.")

        try:
            # Encode le texte
            embedding = self.model.encode(text, convert_to_numpy=True)

            # Normalisation L2 (recommandé pour similarité cosinus)
            embedding = embedding / np.linalg.norm(embedding)

            return embedding

        except Exception as e:
            logger.error(f"Erreur encodage texte: {e}")
            raise

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode un batch de textes pour optimisation

        Args:
            texts: Liste de textes à encoder
            batch_size: Taille du batch pour traitement

        Returns:
            Matrice numpy (n_texts, dimension)
        """
        if self.model is None:
            raise ValueError("Modèle non chargé. Appelez load_model() d'abord.")

        try:
            logger.info(f"Encodage de {len(texts)} textes en batches de {batch_size}")

            # Encode en batch
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalisation automatique
            )

            logger.info(f"Encodage terminé. Shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"Erreur encodage batch: {e}")
            raise

    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings

        Args:
            embedding1, embedding2: Vecteurs d'embeddings

        Returns:
            Score de similarité entre 0 et 1
        """
        try:
            # Similarité cosinus (déjà normalisés)
            similarity = np.dot(embedding1, embedding2)

            # Clamp entre 0 et 1 (au cas où)
            similarity = max(0.0, min(1.0, similarity))

            return float(similarity)

        except Exception as e:
            logger.error(f"Erreur calcul similarité: {e}")
            raise

    def get_dimension(self) -> int:
        """Retourne la dimension des embeddings"""
        if self.dimension is None:
            raise ValueError("Modèle non chargé")
        return self.dimension

    def chunk_text(self, text: str, chunk_size: int = 512,
                  overlap: int = 50) -> List[str]:
        """
        Découpe un long texte en chunks pour embedding

        Args:
            text: Texte à découper
            chunk_size: Taille maximale d'un chunk
            overlap: Chevauchement entre chunks

        Returns:
            Liste de chunks de texte
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = words[i:i + chunk_size]
            if chunk:  # Éviter chunks vides
                chunks.append(" ".join(chunk))

        logger.info(f"Texte découpé en {len(chunks)} chunks")
        return chunks

# Instance globale pour réutilisation
embedding_manager = EmbeddingManager()

def get_embedding_manager() -> EmbeddingManager:
    """Factory function pour obtenir l'instance globale"""
    return embedding_manager

# Tests unitaires
if __name__ == "__main__":
    # Test du système d'embeddings
    manager = EmbeddingManager()
    manager.load_model()

    # Test encodage simple
    text1 = "Comment configurer le VPN ?"
    text2 = "Setup VPN connection"

    emb1 = manager.encode_text(text1)
    emb2 = manager.encode_text(text2)

    similarity = manager.get_similarity(emb1, emb2)

    print(f"Texte 1: {text1}")
    print(f"Texte 2: {text2}")
    print(f"Similarité: {similarity:.3f}")
    print(f"Dimension: {manager.get_dimension()}")

    # Test batch
    texts = [
        "Mot de passe oublié VPN",
        "Configuration email Outlook",
        "Demande de congés",
        "Problème imprimante"
    ]

    embeddings = manager.encode_batch(texts)
    print(f"Batch encodage réussi. Shape: {embeddings.shape}")