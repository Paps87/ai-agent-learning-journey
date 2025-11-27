# 🎉 Solution CORS - Servir Frontend depuis Backend

## Problème

CORS ne fonctionne pas, même après configuration correcte. Le navigateur bloque toutes les requêtes.

## Solution

**Servir le frontend DEPUIS le backend** pour éviter complètement CORS !

Au lieu de :
- Frontend : http://localhost:8080
- Backend : http://localhost:8000
- ❌ Problème CORS

Maintenant :
- **Tout sur http://localhost:8000** ✅
- Pas de CORS !

## Changements Appliqués

### 1. Backend (`api.py`)
- ✅ Ajout `StaticFiles` pour servir le frontend
- ✅ Route `/` retourne `index.html`
- ✅ Route `/static/*` sert CSS et JS

### 2. Frontend (`app.js`)
- ✅ `API_URL = ''` (même domaine)

### 3. Frontend (`index.html`)
- ✅ `href="/static/style.css"`
- ✅ `src="/static/app.js"`

## Utilisation

### Étape 1 : Arrêter les Deux Serveurs

**Terminal 1 (Backend) :**
- Ctrl+C

**Terminal 2 (Frontend) :**
- Ctrl+C (plus besoin !)

### Étape 2 : Lancer UNIQUEMENT le Backend

```bash
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

### Étape 3 : Ouvrir le Navigateur

**URL : http://localhost:8000** (pas 8080 !)

Le backend sert maintenant :
- `/` → Frontend (index.html)
- `/static/*` → CSS et JS
- `/api/*` → API REST
- `/docs` → Documentation

## Test

1. Ouvrir http://localhost:8000
2. Poser question : "test"
3. ✅ Pas d'erreur CORS !
4. Réponse affichée

## Avantages

- ✅ Pas de CORS
- ✅ Un seul serveur à lancer
- ✅ Plus simple
- ✅ Prêt pour production

## Commandes

**Lancer :**
```bash
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

**Accéder :**
- Frontend : http://localhost:8000
- API Docs : http://localhost:8000/docs
- Health : http://localhost:8000/api/health

**Plus besoin de `run_frontend.sh` !**
