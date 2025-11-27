"""
Base de données vectorielle Qdrant pour RAG - Phase 2
Gestion du stockage et de la recherche d'embeddings
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import CollectionStatus
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import logging
import uuid

logger = logging.getLogger(__name__)

class VectorDatabase:
    """
    Interface pour la base de données vectorielle Qdrant
    Gère la création de collections, l'indexation et la recherche
    """

    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialise la connexion Qdrant

        Args:
            host: Adresse du serveur Qdrant
            port: Port du serveur Qdrant
        """
        self.host = host
        self.port = port
        self.client = None
        self.collection_name = "support_documents"

        logger.info(f"Initialisation VectorDatabase: {host}:{port}")

    def connect(self):
        """Établit la connexion avec Qdrant"""
        try:
            self.client = QdrantClient(host=self.host, port=self.port)

            # Test de connexion
            self.client.get_collections()

            logger.info("Connexion Qdrant établie avec succès")

        except Exception as e:
            logger.error(f"Erreur connexion Qdrant: {e}")
            raise

    def create_collection(self, vector_size: int, collection_name: Optional[str] = None):
        """
        Crée une nouvelle collection pour les embeddings

        Args:
            vector_size: Dimension des vecteurs d'embedding
            collection_name: Nom de la collection (optionnel)
        """
        if collection_name:
            self.collection_name = collection_name

        try:
            # Vérifier si collection existe déjà
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection {self.collection_name} existe déjà")
                return

            # Créer la collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE  # Similarité cosinus
                )
            )

            logger.info(f"Collection {self.collection_name} créée avec succès")

        except Exception as e:
            logger.error(f"Erreur création collection: {e}")
            raise

    def delete_collection(self, collection_name: Optional[str] = None):
        """Supprime une collection"""
        collection = collection_name or self.collection_name

        try:
            self.client.delete_collection(collection)
            logger.info(f"Collection {collection} supprimée")

        except Exception as e:
            logger.error(f"Erreur suppression collection {collection}: {e}")
            raise

    def add_documents(self, documents: List[Dict[str, Any]],
                     embeddings: np.ndarray) -> List[str]:
        """
        Ajoute des documents avec leurs embeddings

        Args:
            documents: Liste de dicts avec 'text', 'metadata', etc.
            embeddings: Matrice numpy des embeddings

        Returns:
            Liste des IDs des documents ajoutés
        """
        if len(documents) != len(embeddings):
            raise ValueError("Nombre de documents != nombre d'embeddings")

        points = []
        ids = []

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Générer un ID unique
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)

            # Préparer le point pour Qdrant
            point = models.PointStruct(
                id=doc_id,
                vector=embedding.tolist(),
                payload={
                    "text": doc["text"],
                    "source": doc.get("source", "unknown"),
                    "title": doc.get("title", ""),
                    "chunk_id": doc.get("chunk_id", i),
                    **doc.get("metadata", {})
                }
            )
            points.append(point)

        try:
            # Ajouter les points en batch
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"Ajouté {len(points)} documents à la collection")
            return ids

        except Exception as e:
            logger.error(f"Erreur ajout documents: {e}")
            raise

    def search_similar(self, query_embedding: np.ndarray,
                      limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche les documents les plus similaires

        Args:
            query_embedding: Embedding de la requête
            limit: Nombre maximum de résultats

        Returns:
            Liste des documents similaires avec scores
        """
        try:
            # Recherche vectorielle
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit,
                with_payload=True,
                with_vectors=False  # On ne récupère pas les vecteurs
            )

            # Formater les résultats
            results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload["text"],
                    "source": hit.payload.get("source", "unknown"),
                    "title": hit.payload.get("title", ""),
                    "metadata": {k: v for k, v in hit.payload.items()
                               if k not in ["text", "source", "title"]}
                }
                results.append(result)

            logger.info(f"Recherche réussie: {len(results)} résultats")
            return results

        except Exception as e:
            logger.error(f"Erreur recherche: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """Retourne les informations sur la collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,  # Nom direct
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status.value if hasattr(collection_info.status, 'value') else str(collection_info.status),
                "vector_size": collection_info.config.params.vectors.size
            }

        except Exception as e:
            logger.error(f"Erreur récupération info collection: {e}")
            raise

    def clear_collection(self):
        """Vide complètement la collection"""
        try:
            # Supprimer et recréer la collection
            collection_info = self.get_collection_info()
            vector_size = collection_info["vector_size"]

            self.delete_collection()
            self.create_collection(vector_size)

            logger.info("Collection vidée et recréée")

        except Exception as e:
            logger.error(f"Erreur vidage collection: {e}")
            raise

# Instance globale
vector_db = VectorDatabase()

def get_vector_db() -> VectorDatabase:
    """Factory function pour l'instance globale"""
    return vector_db

# Tests unitaires
if __name__ == "__main__":
    # Test de la base vectorielle
    print("=== Test VectorDatabase ===")

    # Simuler des données de test
    test_documents = [
        {
            "text": "Pour configurer le VPN, allez sur vpn.entreprise.com",
            "source": "it_faq",
            "title": "Configuration VPN"
        },
        {
            "text": "Les congés se demandent via le portail RH",
            "source": "hr_policies",
            "title": "Demande de congés"
        },
        {
            "text": "L'évaluation annuelle a lieu en décembre",
            "source": "hr_policies",
            "title": "Évaluation annuelle"
        }
    ]

    # Simuler des embeddings (en vrai, utiliserait EmbeddingManager)
    np.random.seed(42)
    test_embeddings = np.random.rand(len(test_documents), 384)
    # Normaliser
    test_embeddings = test_embeddings / np.linalg.norm(test_embeddings, axis=1, keepdims=True)

    try:
        # Initialiser
        db = VectorDatabase()
        db.connect()

        # Créer collection
        db.create_collection(vector_size=384)

        # Ajouter documents
        ids = db.add_documents(test_documents, test_embeddings)
        print(f"Documents ajoutés: {ids}")

        # Tester recherche
        query_embedding = test_embeddings[0]  # Chercher comme le premier doc
        results = db.search_similar(query_embedding, limit=2)

        print(f"\\nRecherche pour '{test_documents[0]['text'][:50]}...':")
        for i, result in enumerate(results):
            print(f"{i+1}. Score: {result['score']:.3f} - {result['text'][:50]}...")

        # Info collection
        info = db.get_collection_info()
        print(f"\\nInfo collection: {info}")

        print("\\n✅ Tests VectorDatabase réussis !")

    except Exception as e:
        print(f"❌ Erreur test: {e}")
        print("Note: Qdrant doit être démarré avec 'docker run -p 6333:6333 qdrant/qdrant'")