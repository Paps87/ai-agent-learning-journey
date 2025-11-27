# 🎉 Mini Perplexity - Guide de Lancement

## 🚀 Démarrage Rapide

### Prérequis

1. **LM Studio** doit être lancé sur le port 1234
   - Ouvrir LM Studio
   - Charger le modèle GPT 8B
   - Démarrer le serveur local

2. **Dépendances Python** installées
   ```bash
   source venv/bin/activate
   pip install fastapi uvicorn python-multipart
   ```

### Lancement

**Terminal 1 - Backend :**
```bash
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

**Terminal 2 - Frontend :**
```bash
cd "/home/paps/Projet ai/phase3"
./run_frontend.sh
```

**Ouvrir le navigateur :**
- Frontend : http://localhost:8080
- API Docs : http://localhost:8000/docs

---

## 📁 Structure du Projet

```
phase3/
├── src/                          # Modules Phase 3 existants
│   ├── web_search.py            # ✅ Recherche DuckDuckGo
│   ├── html_parser.py           # ✅ Parsing HTML
│   ├── extended_rag_pipeline.py # ✅ RAG + LM Studio
│   ├── agent_orchestrator.py    # ✅ Orchestrateur
│   └── lmstudio_client.py       # 🆕 Client LM Studio
│
├── backend/                      # 🆕 API FastAPI
│   └── api.py                   # Endpoints REST
│
├── frontend/                     # 🆕 Interface Web
│   ├── index.html               # Interface moderne
│   ├── style.css                # Dark mode Perplexity
│   └── app.js                   # Logique frontend
│
├── app/                          # Interface Streamlit (conservée)
│   └── main.py
│
├── run_backend.sh               # 🆕 Script backend
├── run_frontend.sh              # 🆕 Script frontend
└── test_*.py                    # Tests de validation
```

---

## 🧪 Test Rapide

### 1. Tester LM Studio

```bash
cd "/home/paps/Projet ai/phase3/src"
source ../../venv/bin/activate
python lmstudio_client.py
```

**Attendu :** ✅ Connexion réussie + génération avec citations

### 2. Tester le Backend

```bash
# Terminal 1: Lancer backend
cd "/home/paps/Projet ai/phase3"
./run_backend.sh

# Terminal 2: Tester API
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "prix bitcoin"}'
```

**Attendu :** JSON avec `answer`, `sources`, `processing_time`

### 3. Tester le Frontend

1. Lancer backend (voir ci-dessus)
2. Lancer frontend : `./run_frontend.sh`
3. Ouvrir http://localhost:8080
4. Poser question : "Quel est le prix du Bitcoin?"

**Attendu :**
- Réponse avec citations [1], [2]
- Sources affichées en bas
- Liens cliquables

---

## 🎯 Fonctionnalités

### Backend API

**Endpoints :**
- `POST /api/ask` - Poser une question
- `GET /api/health` - Vérifier statut
- `GET /api/stats` - Statistiques agent
- `GET /docs` - Documentation interactive

**Workflow :**
1. Recherche web (DuckDuckGo)
2. Parsing HTML + chunking
3. Génération LLM (LM Studio)
4. Réponse avec citations

### Frontend

**Features :**
- 🎨 Dark mode style Perplexity
- 🔍 Recherche en temps réel
- 📚 Citations inline [1], [2], [3]
- 🔗 Sources cliquables
- ⚡ Animations smooth
- 📱 Responsive design

---

## 🔧 Configuration

### LM Studio

**Modèle utilisé :** `gad-gpt-5-chat-llama-3.1-8b-instruct-i1`

**Paramètres :**
- Temperature : 0.3 (précision)
- Max tokens : 2000
- Timeout : 60s

### Backend

**Port :** 8000
**CORS :** Activé pour localhost:8080

### Frontend

**Port :** 8080
**API URL :** http://localhost:8000

---

## 💡 Utilisation

### Questions Suggérées

- "Quel est le prix du Bitcoin aujourd'hui?"
- "Quelles sont les dernières actualités sur l'IA?"
- "Comparer Python et JavaScript pour le développement web"

### Citations

Les réponses incluent des citations numérotées :
- `[1]`, `[2]`, `[3]` dans le texte
- Cliquables pour scroller vers la source
- Sources affichées en bas avec titre + URL

---

## 🐛 Dépannage

### Backend ne démarre pas

```bash
# Vérifier que le venv est activé
source venv/bin/activate

# Réinstaller dépendances
pip install fastapi uvicorn
```

### LM Studio non connecté

1. Ouvrir LM Studio
2. Charger un modèle
3. Cliquer "Start Server"
4. Vérifier : http://localhost:1234/v1/models

### Frontend ne charge pas

1. Vérifier que le backend tourne (port 8000)
2. Ouvrir la console du navigateur (F12)
3. Vérifier les erreurs CORS

---

## 📊 Performance

**Temps de réponse typique :**
- Recherche web : 1-2s
- Parsing HTML : 0.5-1s
- Génération LLM : 3-10s
- **Total : 5-15s**

---

## 🎉 Prochaines Étapes

- [ ] Ajouter streaming des réponses (SSE)
- [ ] Historique des conversations
- [ ] Export PDF des réponses
- [ ] Mode comparaison (2 sources)
- [ ] Support images dans réponses

---

**Créé avec ❤️ - Phase 3 Mini Perplexity**
