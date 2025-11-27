# 🚀 Mini Perplexity - Guide de Démarrage Rapide

## ✅ Prérequis

1. **LM Studio lancé** sur port 1234
2. **Modèle chargé** (GPT 8B recommandé)
3. **Venv activé**

## 🎯 Lancement en 2 Étapes

### Terminal 1 - Backend

```bash
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

**Attendu :**
```
✅ LM Studio connecté
📡 Démarrage du serveur FastAPI...
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Frontend

```bash
cd "/home/paps/Projet ai/phase3"
./run_frontend.sh
```

**Attendu :**
```
🌐 Frontend: http://localhost:8080
Serving HTTP on 0.0.0.0 port 8080
```

### Navigateur

Ouvrir : **http://localhost:8080**

---

## 💡 Utilisation

1. Taper une question : "Quel est le prix du Bitcoin?"
2. Cliquer sur Rechercher ou appuyer sur Entrée
3. Attendre 5-15 secondes
4. Voir la réponse avec citations [1], [2], [3]
5. Cliquer sur les sources en bas

---

## 🐛 Dépannage

### Backend ne démarre pas

**Erreur Qdrant :**
✅ **Normal !** Le backend fonctionne en mode web-only sans Qdrant

**LM Studio non connecté :**
1. Ouvrir LM Studio
2. Charger un modèle
3. Cliquer "Start Server"

### Frontend ne charge pas

1. Vérifier backend sur http://localhost:8000/docs
2. Ouvrir console navigateur (F12)
3. Vérifier erreurs CORS

---

## 📊 Architecture

```
Question → Frontend (8080)
    ↓
Backend API (8000)
    ↓
Web Search (DuckDuckGo)
    ↓
HTML Parsing + Chunking
    ↓
LM Studio (1234) → Génération
    ↓
Réponse avec citations [1], [2]
```

---

**Mode actuel : Web-Only** (pas besoin de Qdrant)
