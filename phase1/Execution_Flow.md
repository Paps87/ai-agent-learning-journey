# 🚀 Flux d'Exécution - LLM Playground

## Schéma ASCII Simplifié

```
┌─────────────────┐
│   UTILISATEUR   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  COLLECTE       │────▶│  TOKENISATION   │────▶│  ENTRAÎNEMENT   │
│  download_data  │     │  preprocess     │     │  training       │
│                 │     │                 │     │                 │
│ • Wikipedia API │     │ • SentencePiece │     │ • PyTorch       │
│ • Nettoyage     │     │ • BPE Training  │     │ • Next-Token    │
│ • Sauvegarde    │     │ • Tokenize      │     │ • Optimization  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
    data/raw/               data/processed/            models/
wikipedia_corpus.txt     tokenized_corpus.txt      gpt_model.pth
                                                            │
                                                            ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  INFERENCE      │◀────│  GÉNÉRATION     │◀────│  INTERFACE      │
│  GPTModel       │     │  Sampling       │     │  Streamlit      │
│                 │     │                 │     │                 │
│ • Forward pass  │     │ • Greedy        │     │ • Chat UI       │
│ • Causal mask   │     │ • Top-k         │     │ • Paramètres    │
│ • Logits        │     │ • Top-p         │     │ • Historique    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
    TOKENS IDS              TEXTE GÉNÉRÉ            UTILISATEUR
    [1523, 4871, ...]     "The AI model..."       Réponse finale
```

## Pipeline Étape par Étape

### 1. **PHASE DE DONNÉES** 📊
```
Internet → Wikipedia API → DataCollector → Nettoyage → Fichiers texte
```

**Fichiers générés :**
- `data/raw/wikipedia_corpus.txt` (articles concaténés)

### 2. **PHASE DE TOKENISATION** 🔤
```
Texte brut → SentencePiece → BPE Training → Tokenization → IDs numériques
```

**Fichiers générés :**
- `models/tokenizer.model` (modèle entraîné)
- `models/tokenizer.vocab` (vocabulaire)
- `data/processed/tokenized_corpus.txt` (séquence d'IDs)

### 3. **PHASE D'ENTRAÎNEMENT** 🧠
```
Tokens IDs → TextDataset → DataLoader → GPTModel → Loss → Optimization
```

**Fichiers générés :**
- `models/gpt_model.pth` (poids du modèle)
- Checkpoints intermédiaires (optionnel)

### 4. **PHASE D'INFERENCE** 🎯
```
Prompt → Tokenizer.encode() → GPTModel.generate() → Tokenizer.decode() → Réponse
```

**Composants utilisés :**
- Modèle chargé en mémoire
- Tokenizer pour conversion
- Stratégies de sampling

### 5. **PHASE INTERFACE** 🎨
```
Utilisateur → Streamlit UI → Paramètres → Génération → Affichage → Historique
```

**Composants UI :**
- Zone de chat
- Sliders (temperature, top-k, etc.)
- Boutons de contrôle
- Historique des messages

## États du Système

### État 0: Initial
```
📁 data/raw/          : Vide
📁 data/processed/    : Vide
📁 models/           : Vide
🚫 Interface         : Non disponible
```

### État 1: Après Collecte
```
📁 data/raw/          : ✅ wikipedia_corpus.txt
📁 data/processed/    : Vide
📁 models/           : ✅ tokenizer.model/.vocab
🚫 Interface         : Non disponible
```

### État 2: Après Tokenisation
```
📁 data/raw/          : ✅ wikipedia_corpus.txt
📁 data/processed/    : ✅ tokenized_corpus.txt
📁 models/           : ✅ tokenizer.model/.vocab
🚫 Interface         : Non disponible
```

### État 3: Après Entraînement
```
📁 data/raw/          : ✅ wikipedia_corpus.txt
📁 data/processed/    : ✅ tokenized_corpus.txt
📁 models/           : ✅ tokenizer.model/.vocab + gpt_model.pth
🟢 Interface         : Disponible !
```

## Flux de Données

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   STRING    │───▶│   TOKENS    │───▶│   TENSORS   │───▶│  LOGITS     │
│             │    │             │    │             │    │             │
│ "Hello AI"  │    │ [1, 452, 89]│    │ tensor[...] │    │ tensor[...] │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      ▲                    ▲                    ▲                    ▲
      │                    │                    │                    │
   Décode               Encode              Forward            Sample
   (Tokenizer)          (Tokenizer)        (GPTModel)       (generate)
```

## Gestion d'Erreurs

### Points de Contrôle
- ✅ Fichier de données existe ?
- ✅ Tokenizer entraîné ?
- ✅ Modèle existe ?
- ✅ Interface peut charger le modèle ?

### Récupération
- Si données manquent → Relancer collecte
- Si tokenizer cassé → Ré-entraîner
- Si modèle corrompu → Recharger depuis checkpoint
- Si interface plante → Vérifier chemins des fichiers

---

*Ce schéma montre le flux complet de données et d'exécution à travers toutes les phases du projet.*