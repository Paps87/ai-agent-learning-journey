# Phase 2: Customer Support Chatbot (RAG + Prompt Engineering) 🗂️

## Objectif
Construire un chatbot de support client intelligent utilisant RAG (Retrieval-Augmented Generation) pour répondre aux questions basées sur la documentation interne de l'entreprise.

## Architecture RAG

### Composants Principaux
1. **Système d'Embeddings** : Conversion texte → vecteurs numériques
2. **Base Vectorielle Qdrant** : Stockage et recherche des embeddings
3. **Pipeline RAG** : Retrieval + Augmentation + Generation
4. **Prompt Engineering** : Techniques avancées pour améliorer les réponses
5. **Interface Chatbot** : Interface utilisateur moderne

### Flux de Fonctionnement
```
Documents → Chunks → Embeddings → Qdrant DB
                                    ↓
Question User → Embedding → Recherche → Contexte → Prompt Augmenté → LLM → Réponse
```

## Structure du Projet

```
phase2/
├── src/
│   ├── embeddings.py          # Gestion des embeddings (Sentence Transformers)
│   ├── vector_db.py           # Interface Qdrant (CRUD operations)
│   ├── rag_pipeline.py        # Pipeline RAG complet
│   ├── prompt_engineering.py  # Techniques de prompt avancées
│   └── evaluation.py          # Métriques d'évaluation
├── data/
│   └── documents/             # Documents de support client
├── scripts/
│   ├── setup_qdrant.py        # Installation et configuration Qdrant
│   ├── index_documents.py     # Indexation des documents
│   └── test_rag.py            # Tests du pipeline RAG
├── app/
│   └── chatbot.py             # Interface Streamlit du chatbot
└── README.md
```

## Dépendances
- `qdrant-client` : Client Python pour Qdrant
- `sentence-transformers` : Modèles d'embeddings
- `langchain` : Framework RAG (optionnel)
- `streamlit` : Interface utilisateur

## Démarrage Rapide

1. **Installer les dépendances :**
```bash
pip install qdrant-client sentence-transformers
```

2. **Démarrer Qdrant :**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

3. **Indexer les documents :**
```bash
python scripts/index_documents.py
```

4. **Lancer le chatbot :**
```bash
streamlit run app/chatbot.py
```

## Concepts Clés

### Embeddings
- Représentation vectorielle du sens des textes
- Mesure de similarité sémantique
- Modèle utilisé : `all-MiniLM-L6-v2` (384 dimensions)

### Base Vectorielle
- Stockage efficace des embeddings
- Recherche par similarité cosinus
- Métadonnées associées (source, titre, etc.)

### RAG Pipeline
1. **Retrieval** : Trouver documents pertinents
2. **Augmentation** : Enrichir le prompt avec contexte
3. **Generation** : Produire réponse basée sur faits

### Prompt Engineering
- Role-based prompting (assistant support)
- Chain-of-thought reasoning
- Few-shot examples
- Context compression

## Évaluation
- **Pertinence** : Le contexte trouvé est-il approprié ?
- **Factualité** : La réponse est-elle basée sur les documents ?
- **Utilité** : La réponse résout-elle le problème de l'utilisateur ?

## Prochaines Étapes
1. Implémentation des embeddings
2. Configuration Qdrant
3. Pipeline RAG
4. Interface utilisateur
5. Tests et optimisation