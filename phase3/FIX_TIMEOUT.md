# 🔧 Fix: Timeout LM Studio

## Problème
La génération prend trop de temps et timeout après 60 secondes.

## Solutions Appliquées

### 1. Augmentation du Timeout
- **Avant :** 60 secondes
- **Après :** 120 secondes

### 2. Réduction des Tokens
- **Avant :** 2000 tokens max
- **Après :** 1000 tokens max (réponses plus courtes et rapides)

### 3. Redémarrer le Backend

```bash
# Arrêter le backend (Ctrl+C dans Terminal 1)
cd "/home/paps/Projet ai/phase3"
./run_backend.sh
```

### 4. Réessayer

1. Rafraîchir la page (F5)
2. Poser la question : "Quel est le prix du Bitcoin?"
3. Attendre ~30-60 secondes

## Temps Attendus Maintenant

- Recherche web : 1-3s
- Parsing : 0.5-1s
- **LLM : 10-30s** (au lieu de 60s+)
- **Total : 15-40s**

## Si Toujours Trop Lent

### Option A : Réduire encore max_tokens
Éditer `/home/paps/Projet ai/phase3/src/lmstudio_client.py` ligne 299 :
```python
max_tokens=500  # Réponses très courtes
```

### Option B : Vérifier LM Studio
1. Ouvrir LM Studio
2. Vérifier que le modèle est bien chargé
3. Tester la génération directement dans LM Studio

### Option C : Utiliser un modèle plus petit
Dans LM Studio, charger un modèle plus rapide (3B ou 7B au lieu de 8B)
