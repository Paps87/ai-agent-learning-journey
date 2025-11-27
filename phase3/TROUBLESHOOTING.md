# 🔧 Dépannage Mini Perplexity

## ❌ Erreur: NetworkError when attempting to fetch resource

### Diagnostic

Le backend tourne et répond :
```bash
curl http://localhost:8000/api/health
# ✅ {"status":"healthy","lm_studio_connected":true}
```

Mais le frontend ne peut pas se connecter.

### Solutions

#### Solution 1 : Vérifier que le backend écoute sur toutes les interfaces

Le backend doit écouter sur `0.0.0.0` et non `127.0.0.1`

**Vérifier :**
```bash
ss -tlnp | grep 8000
```

**Attendu :**
```
LISTEN  0.0.0.0:8000  (pas 127.0.0.1:8000)
```

#### Solution 2 : Tester depuis le navigateur

Ouvrir la console du navigateur (F12) et tester :
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

#### Solution 3 : Vérifier CORS

Le backend a déjà CORS activé dans `api.py` :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

#### Solution 4 : Relancer le backend

```bash
# Arrêter le backend (Ctrl+C)
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

### Test Rapide

**Terminal 1 - Backend :**
```bash
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

**Terminal 2 - Test :**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Navigateur :**
- Ouvrir http://localhost:8080
- Ouvrir Console (F12)
- Vérifier les erreurs réseau
