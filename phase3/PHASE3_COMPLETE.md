# 📚 Phase 3 - Ask-the-Web Agent : Documentation Complète

## 🎯 Objectif de la Phase 3

Créer un **agent IA capable de rechercher sur le web** et de générer des réponses intelligentes avec citations, similaire à Perplexity AI.

---

## ✅ Ce qui a été réalisé

### 1. **Recherche Web Intelligente** 🔍

**Module :** `web_search.py`

**Fonctionnalités :**
- Recherche via DuckDuckGo (API gratuite)
- **Circuit Breaker Pattern** pour la résilience
- Retry automatique avec backoff exponentiel
- Validation et nettoyage des résultats
- Support multi-requêtes

**Points clés :**
```python
# Circuit Breaker : 3 états (CLOSED, OPEN, HALF_OPEN)
# Évite de surcharger l'API en cas d'erreurs répétées
# Retry : 3 tentatives max avec délai exponentiel
```

**Test validé :** ✅ 5 résultats pour "OpenAI GPT" en 1-2s

---

### 2. **Parsing HTML et Chunking** 📄

**Module :** `html_parser.py`

**Fonctionnalités :**
- Extraction du contenu principal (BeautifulSoup)
- Suppression des éléments indésirables (ads, nav, footer)
- **TextChunker** : découpage intelligent avec chevauchement
- Préservation de la structure logique (titres, paragraphes)

**Points clés :**
```python
# Chunking : 500 mots par chunk, 50 mots de chevauchement
# Préserve le contexte entre les chunks
# Fallback si parsing échoue (sites protégés)
```

**Limitation :** Certains sites bloquent le scraping (Wikipedia, OpenAI)

---

### 3. **Pipeline RAG Étendu** 🧠

**Module :** `extended_rag_pipeline.py`

**Fonctionnalités :**
- **Fusion Local + Web** : Combine documents locaux (Phase 2) et web
- **Mémoire conversationnelle** : Historique des 10 dernières questions
- **Cache de recherches** : Évite les recherches redondantes (24h TTL)
- **Scoring de pertinence** : Classe les résultats par score
- **Diversification des sources** : Évite les doublons

**Points clés :**
```python
# Mode web-only : Fonctionne sans Qdrant (Phase 2 optionnelle)
# Indexation temporaire : Chunks web indexés pour 24h
# Fusion intelligente : Combine local (si dispo) + web
```

**Correction importante :** Attribut `local_available` ajouté pour gérer l'absence de Qdrant

---

### 4. **Orchestrateur d'Agent** 🤖

**Module :** `agent_orchestrator.py`

**Fonctionnalités :**
- **Analyse de complexité** : Évalue si question simple ou complexe
- **Décomposition en sous-questions** : Pour questions complexes
- **3 stratégies de recherche** :
  - **Single** : Question simple
  - **Parallel** : Plusieurs sous-questions en parallèle
  - **Sequential** : Sous-questions dépendantes
- **Synthèse multi-sources** : Agrège les réponses

**Points clés :**
```python
# SearchPlanner : Analyse la question et choisit la stratégie
# Max depth : 3 niveaux de décomposition
# Synthèse finale : Combine toutes les réponses
```

**Correction importante :** Attribut `available` ajouté pour vérifier les composants

---

### 5. **Intégration LM Studio** 🎨

**Module :** `lmstudio_client.py` (créé durant cette phase)

**Fonctionnalités :**
- Client OpenAI-compatible pour LM Studio
- **Génération avec contexte et sources**
- **Citations automatiques** [1], [2], [3]
- Timeout configurable (120s)
- Fallback si LM Studio offline

**Points clés :**
```python
# Modèle : gad-gpt-5-chat-llama-3.1-8b-instruct-i1
# Temperature : 0.3 (précision)
# Max tokens : 1000 (réponses rapides)
# Timeout : 120s (augmenté pour éviter timeouts)
```

**Optimisations appliquées :**
- Timeout augmenté : 60s → 120s
- Max tokens réduit : 2000 → 1000 (réponses plus rapides)

---

### 6. **Interface Utilisateur** 🖥️

**Solution finale :** **Streamlit** (`app/main.py`)

**Pourquoi Streamlit ?**
- ✅ Pas de problèmes CORS
- ✅ Interface déjà prête
- ✅ Une seule commande pour lancer
- ✅ Rechargement automatique

**Tentatives abandonnées :**
- ❌ Backend FastAPI + Frontend HTML/JS : Problèmes CORS insurmontables
- ❌ Servir frontend depuis backend : Problèmes de cache navigateur

**Fonctionnalités de l'interface :**
- Recherche web en temps réel
- Affichage des réponses avec citations
- Sources détaillées (titre, URL, type)
- Statistiques (temps, stratégie, nombre de sources)
- Paramètres configurables (mode recherche, profondeur)

---

## 🔧 Corrections et Optimisations

### Problèmes Résolus

1. **Qdrant non disponible**
   - **Problème :** Backend crashait si Qdrant non lancé
   - **Solution :** Mode web-only avec flag `PHASE2_AVAILABLE`
   - **Impact :** Fonctionne sans Phase 2

2. **Timeout LM Studio**
   - **Problème :** Génération prenait >60s, timeout
   - **Solution :** Timeout 120s + max_tokens 1000
   - **Impact :** Réponses en 15-50s au lieu de timeout

3. **Attributs manquants**
   - **Problème :** `local_available` et `available` non définis
   - **Solution :** Initialisation dans `__init__`
   - **Impact :** Pas d'AttributeError

4. **Métriques Streamlit**
   - **Problème :** Affichage littéral ".2f" au lieu de valeurs
   - **Solution :** Formatage correct avec f-strings
   - **Impact :** Affichage propre des statistiques

5. **CORS Frontend/Backend**
   - **Problème :** Navigateur bloquait requêtes cross-origin
   - **Solution :** Abandon FastAPI, utilisation Streamlit
   - **Impact :** Plus de problèmes CORS

---

## 📊 Architecture Finale

```
┌─────────────────────────────────────┐
│   Interface Streamlit (port 8501)  │
│   - Questions / Réponses            │
│   - Sources et citations            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Agent Orchestrator                │
│   - Analyse complexité              │
│   - Décomposition questions         │
│   - Choix stratégie                 │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼──────────┐
│ Web Search │    │ Extended RAG    │
│ (DuckDuckGo│    │ Pipeline        │
└───┬────────┘    └──────┬──────────┘
    │                    │
┌───▼────────┐    ┌──────▼──────────┐
│ HTML Parser│    │ LM Studio       │
│ + Chunking │    │ (GPT 8B)        │
└────────────┘    └─────────────────┘
```

---

## 🚀 Utilisation

### Lancement Simple

```bash
cd "/home/paps/Projet ai/phase3"
./run_streamlit.sh
```

**Ou :**
```bash
cd "/home/paps/Projet ai"
source venv/bin/activate
streamlit run phase3/app/main.py
```

### Prérequis

1. **LM Studio lancé** sur port 1234
2. **Modèle chargé** (GPT 8B recommandé)
3. **Venv activé** avec dépendances installées

### Workflow Utilisateur

1. Ouvrir http://localhost:8501
2. Taper question : "Quel est le prix du Bitcoin?"
3. Cliquer "Rechercher"
4. Attendre 15-60 secondes
5. Voir réponse avec citations [1], [2], [3]
6. Consulter sources en bas

---

## 📈 Performance

**Temps de traitement typique :**
- Recherche web : 1-3s
- Parsing HTML : 0.5-1s
- Génération LLM : 10-40s
- **Total : 15-50s**

**Optimisations :**
- Circuit Breaker : Évite surcharge API
- Cache 24h : Évite recherches redondantes
- Chunking intelligent : Préserve contexte
- Max tokens réduit : Réponses plus rapides

---

## 📁 Structure des Fichiers

```
phase3/
├── src/
│   ├── web_search.py              # ✅ Recherche DuckDuckGo
│   ├── html_parser.py             # ✅ Parsing + Chunking
│   ├── extended_rag_pipeline.py   # ✅ RAG Local+Web
│   ├── agent_orchestrator.py      # ✅ Orchestration
│   └── lmstudio_client.py         # 🆕 Client LM Studio
│
├── app/
│   └── main.py                    # ✅ Interface Streamlit
│
├── backend/                       # ❌ Non utilisé (CORS)
├── frontend/                      # ❌ Non utilisé (CORS)
│
├── run_streamlit.sh               # 🆕 Script lancement
├── PHASE3_COMPLETE.md             # 🆕 Cette doc
└── README.md                      # Doc originale
```

---

## 🎓 Apprentissages Clés

### Techniques Maîtrisées

1. **Web Scraping** avec BeautifulSoup
2. **Circuit Breaker Pattern** pour résilience
3. **RAG hybride** (local + web)
4. **Chunking intelligent** avec chevauchement
5. **Orchestration multi-stratégies**
6. **Intégration LLM local** (LM Studio)
7. **Gestion d'erreurs robuste** (retry, fallback)

### Défis Surmontés

1. **CORS** : Résolu en utilisant Streamlit
2. **Timeout LLM** : Résolu en augmentant timeout + réduisant tokens
3. **Dépendances optionnelles** : Mode web-only sans Qdrant
4. **Sites protégés** : Fallback gracieux si parsing échoue

### Bonnes Pratiques

1. **Factory Pattern** : `get_web_search_engine()`, `get_lm_studio_client()`
2. **Logging complet** : Tous les modules loggent leurs actions
3. **Gestion d'erreurs** : Try/except avec messages clairs
4. **Configuration centralisée** : Timeouts, max_results, etc.
5. **Tests unitaires** : Chaque module testable indépendamment

---

## 🔍 Tests de Validation

### Test 1 : Recherche Web
```bash
cd phase3/src
python web_search.py
```
**Résultat :** ✅ 3 résultats pour "prix bitcoin"

### Test 2 : LM Studio
```bash
cd phase3/src
python lmstudio_client.py
```
**Résultat :** ✅ Génération avec citations [1], [2]

### Test 3 : Workflow Complet
```bash
cd phase3
python test_validation.py
```
**Résultat :** ✅ Pipeline OK (local_available=False)

### Test 4 : Interface Streamlit
```bash
streamlit run phase3/app/main.py
```
**Résultat :** ✅ Réponse "pancakes" en 28.37s avec sources

---

## 💡 Recommandations pour Production

### Améliorations Possibles

1. **Streaming des réponses** : SSE pour affichage progressif
2. **Cache persistant** : Redis au lieu de mémoire
3. **API officielle** : Remplacer DuckDuckGo par API payante
4. **Modèle plus rapide** : 3B ou 7B au lieu de 8B
5. **Historique permanent** : Base de données pour conversations
6. **Export PDF** : Sauvegarder réponses avec sources

### Sécurité

1. **Rate limiting** : Limiter requêtes par utilisateur
2. **Validation input** : Sanitize questions utilisateur
3. **HTTPS** : En production
4. **API keys** : Pour services externes

---

## 📊 Statistiques du Projet

**Lignes de code :**
- `web_search.py` : ~300 lignes
- `html_parser.py` : ~520 lignes
- `extended_rag_pipeline.py` : ~590 lignes
- `agent_orchestrator.py` : ~390 lignes
- `lmstudio_client.py` : ~260 lignes
- `main.py` (Streamlit) : ~320 lignes
- **Total : ~2380 lignes**

**Dépendances ajoutées :**
- `ddgs` (DuckDuckGo)
- `beautifulsoup4` (Parsing HTML)
- `streamlit` (Interface)
- `requests` (HTTP)

**Temps de développement :** ~8-10 heures (avec débogage)

---

## 🎉 Conclusion Phase 3

**Objectif atteint :** ✅ Agent web-aware fonctionnel

**Points forts :**
- ✅ Recherche web en temps réel
- ✅ Génération LLM locale (gratuit, privé)
- ✅ Citations automatiques [1], [2], [3]
- ✅ Interface simple et efficace
- ✅ Architecture modulaire et extensible

**Limitations :**
- ⚠️ Parsing échoue sur sites protégés
- ⚠️ Génération lente (15-50s)
- ⚠️ Pas de streaming
- ⚠️ Cache en mémoire (non persistant)

**Prêt pour Phase 4 !** 🚀

---

**Fichiers importants :**
- [run_streamlit.sh](file:///home/paps/Projet%20ai/phase3/run_streamlit.sh) - Lancement
- [main.py](file:///home/paps/Projet%20ai/phase3/app/main.py) - Interface
- [lmstudio_client.py](file:///home/paps/Projet%20ai/phase3/src/lmstudio_client.py) - LLM
- [agent_orchestrator.py](file:///home/paps/Projet%20ai/phase3/src/agent_orchestrator.py) - Orchestration
