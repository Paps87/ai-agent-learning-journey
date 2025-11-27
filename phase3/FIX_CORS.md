# 🔧 Fix CORS - Mini Perplexity

## Problème Identifié

**Erreur dans la console du navigateur :**
```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading 
the remote resource at http://localhost:8000/api/ask
(Reason: CORS request did not succeed)
```

## Cause

Le navigateur bloque les requêtes du frontend (localhost:8080) vers le backend (localhost:8000) à cause de la politique CORS (Cross-Origin Resource Sharing).

## Solution

### Étape 1 : CORS déjà configuré ✅

Le fichier `backend/api.py` a déjà CORS activé :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Étape 2 : Redémarrer le Backend

**IMPORTANT :** Le backend doit être redémarré pour que CORS fonctionne.

**Terminal 1 (Backend) :**
```bash
# Appuyer sur Ctrl+C pour arrêter le backend actuel
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

**Attendu :**
```
🚀 Lancement Mini Perplexity Backend
====================================
✅ LM Studio connecté
📡 Démarrage du serveur FastAPI...
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Étape 3 : Rafraîchir le Frontend

**Dans le navigateur :**
- Appuyer sur **Ctrl+Shift+R** (rafraîchissement forcé)
- Ou **F5**

### Étape 4 : Tester

1. Poser la question : "test"
2. Vérifier dans la console (F12) qu'il n'y a plus d'erreur CORS
3. Attendre la réponse

## Vérification

### Test 1 : Backend Health

```bash
curl http://localhost:8000/api/health
```

**Attendu :**
```json
{"status":"healthy","lm_studio_connected":true}
```

### Test 2 : CORS Headers

```bash
curl -I -X OPTIONS http://localhost:8000/api/ask \
  -H "Origin: http://localhost:8080" \
  -H "Access-Control-Request-Method: POST"
```

**Attendu :**
```
access-control-allow-origin: *
access-control-allow-methods: *
```

### Test 3 : Frontend

1. Ouvrir http://localhost:8080
2. F12 → Console
3. Tester :
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(console.log)
```

**Attendu :** Pas d'erreur CORS, réponse JSON affichée

## Si Toujours Bloqué

### Option A : Utiliser un Proxy

Modifier `frontend/app.js` ligne 3 :
```javascript
const API_URL = '';  // Utiliser le même domaine
```

Puis lancer le frontend avec un proxy.

### Option B : Ouvrir le HTML directement

Au lieu de `http://localhost:8080`, ouvrir :
```
file:///home/paps/Projet ai/phase3/frontend/index.html
```

⚠️ Mais cela peut causer d'autres problèmes CORS.

### Option C : Vérifier le Firewall

```bash
sudo ufw status
```

Si actif, autoriser le port 8000.

## Résumé

**Action requise :**
1. ✅ CORS déjà configuré dans le code
2. 🔄 **Redémarrer le backend** (Ctrl+C puis `./run_backend.sh`)
3. 🔄 **Rafraîchir le navigateur** (Ctrl+Shift+R)
4. ✅ Tester la requête

**Le problème devrait être résolu après le redémarrage du backend.**
