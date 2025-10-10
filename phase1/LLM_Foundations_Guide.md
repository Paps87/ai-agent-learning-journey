# 🧠 Guide des Fondations des LLMs

## Vue d'ensemble

Ce guide explique les concepts fondamentaux implémentés dans notre LLM Playground, en se concentrant sur la compréhension plutôt que sur les détails techniques.

## 1. Tokenisation : Convertir le texte en tokens

### Le problème
Les LLMs ne comprennent pas le texte brut. Ils travaillent avec des nombres (tokens). Comment découper intelligemment le texte pour maximiser l'efficacité du modèle ?

### Solution : BPE (Byte Pair Encoding)

BPE apprend des "sous-mots" optimaux en analysant la fréquence des paires de caractères dans le corpus d'entraînement.

#### Exemple concret :
```
Texte d'entrée : "artificial intelligence is amazing"

1. Découpage initial (caractères) :
   ['a','r','t','i','f','i','c','i','a','l',' ','i','n','t','e','l','l','i','g','e','n','c','e',' ','i','s',' ','a','m','a','z','i','n','g']

2. BPE apprend les paires fréquentes :
   - "in" apparaît souvent → devient un token
   - "ti" apparaît souvent → devient un token
   - "ing" apparaît souvent → devient un token
   - etc.

3. Résultat final :
   "artificial intelligence is amazing"
   → ["art", "ificial", " intelligence", " is", " amazing"]
   → [1523, 4871, 284, 318, 4673] (IDs numériques)
```

#### Pourquoi BPE est optimal :
- **Gère les mots inconnus** : "tokenization" → "token", "ization" (même si "ization" n'était pas dans le vocabulaire d'entraînement)
- **Équilibre optimal** : Entre caractères (trop granulaire, vocabulaire énorme) et mots complets (mots rares non gérables)
- **Apprentissage automatique** : La segmentation optimale est apprise statistiquement du corpus

#### Dans notre implémentation :
- Utilise SentencePiece (implémentation Google)
- Vocabulaire de 8000 tokens
- Entraîné sur notre corpus Wikipedia

## 2. Architecture Transformer : Attention + Causal Masking

### Le problème
Comment un modèle peut-il comprendre les relations complexes entre mots distants dans une phrase ?

### Solution : Multi-Head Attention avec Causal Masking

#### Mécanisme d'attention :
Pour chaque mot (token), le modèle regarde tous les autres mots et calcule un "score d'attention" : "combien ce mot m'aide-t-il à comprendre celui-ci ?"

#### Exemple pratique :
**Phrase :** "Le chat noir dort sur le canapé rouge"

Quand le modèle traite le mot "dort" :
- Il regarde "chat" avec un score élevé (qui dort ?)
- Il regarde "canapé" avec un score élevé (où dort-il ?)
- Il regarde "noir" avec un score moyen (contexte descriptif)
- Il ignore presque "rouge" (peu pertinent pour l'action de dormir)

#### Causal Masking (CRUCIAL pour la génération) :
- **Principe** : Un token ne peut voir que les tokens qui le précèdent
- **Pourquoi** : Permet la génération autoregressive (prédire le prochain token à partir des précédents)
- **Implémentation** : Masque triangulaire inférieur

```
Position:  0    1    2    3    4    5
Tokens:   [BOS] Le   chat noir dort
Mask:     [1,   0,   0,   0,   0,   0]  ← BOS ne voit rien (pas de passé)
          [1,   1,   0,   0,   0,   0]  ← "Le" voit BOS
          [1,   1,   1,   0,   0,   0]  ← "chat" voit BOS + "Le"
          [1,   1,   1,   1,   0,   0]  ← "noir" voit BOS + "Le" + "chat"
          etc.
```

#### Dans notre modèle :
- 4 couches de transformer
- 4 têtes d'attention par couche
- Dimension d'attention : 256
- Causal masking activé pour la génération

## 3. Génération de texte : Greedy vs Sampling

### Le problème
Le modèle prédit des probabilités pour chaque token possible suivant. Comment choisir lequel utiliser pour générer du texte ?

### Stratégies de génération :

#### a) Greedy (déterministe)
- **Principe** : Toujours choisir le token le plus probable
- **Avantages** : Cohérent, reproductible, rapide
- **Inconvénients** : Répétitif, manque de créativité, peut rester bloqué

**Exemple :**
```
Probabilités pour le prochain token :
"the": 0.4, "a": 0.3, "an": 0.2, "this": 0.1

Greedy choisit : "the" (toujours)
```

#### b) Top-k Sampling
- **Principe** : Garde seulement les k tokens les plus probables, ré-échantillonne parmi eux
- **Avantages** : Contrôle la diversité, évite les absurdités
- **Paramètre** : k (typiquement 40-60)

**Exemple (k=3) :**
```
Probabilités originales :
"the": 0.4, "a": 0.3, "an": 0.2, "this": 0.1, "dog": 0.05, ...

Top-3 gardés : "the": 0.4, "a": 0.3, "an": 0.2
Ré-normalisé : "the": 0.57, "a": 0.43, "an": 0.29
```

#### c) Top-p (Nucleus) Sampling
- **Principe** : Garde les tokens jusqu'à ce que leur probabilité cumulée atteigne p
- **Avantages** : Plus adaptatif que top-k, s'ajuste à la distribution
- **Paramètre** : p (typiquement 0.9-0.95)

**Exemple (p=0.9) :**
```
Probabilités triées :
"the": 0.4 (cumul: 0.4)
"a": 0.3 (cumul: 0.7)
"an": 0.2 (cumul: 0.9) ← Stop ici
"this": 0.1 (cumul: 1.0) ← Exclu
```

#### Temperature
- **Rôle** : Contrôle l'aléatoire de la distribution
- **Formule** : `probabilities = softmax(logits / temperature)`
- **Effets** :
  - T = 0.0 : Greedy (déterministe)
  - T = 1.0 : Distribution originale
  - T > 1.0 : Plus aléatoire (créatif)
  - T < 1.0 : Plus concentré (conservateur)

## 4. Entraînement : Next-Token Prediction

### Le problème
Comment entraîner un modèle à générer du texte cohérent et contextuellement approprié ?

### Solution : Next-Token Prediction (NTP)

#### Principe :
- **Objectif** : Prédire le token suivant à partir de tous les précédents
- **Loss** : Cross-entropy entre prédiction du modèle et token réel
- **Architecture** : GPT-like (décoder-only transformer)

#### Exemple d'entraînement :
```
Texte : "Le chat noir dort"

Création des exemples d'entraînement :
1. [BOS] → "Le"           (apprendre à prédire "Le")
2. [BOS] "Le" → "chat"    (apprendre à prédire "chat")
3. [BOS] "Le" "chat" → "noir"  (apprendre à prédire "noir")
4. [BOS] "Le" "chat" "noir" → "dort"  (apprendre à prédire "dort")
5. [BOS] "Le" "chat" "noir" "dort" → [EOS]  (apprendre à finir)
```

#### Pourquoi ça marche :
- **Apprentissage statistique** : Le modèle apprend les patterns du langage
- **Causal masking** : Force l'apprentissage de dépendances séquentielles
- **Scaling** : Plus de données = meilleur modèle
- **Transfer learning** : Fine-tuning possible pour des tâches spécifiques

#### Dans notre implémentation :
- Entraînement sur corpus Wikipedia tokenisé
- Loss cross-entropy
- Optimiseur AdamW
- Learning rate scheduling

## Synthèse : Comment fonctionne un LLM ?

Un LLM est essentiellement un **prédicteur de token suivant sophistiqué** qui :

1. **Convertit le texte en tokens** via BPE (tokenization)
2. **Comprends les relations contextuelles** via attention mechanism
3. **Prédit le prochain token** de manière contrôlée (greedy/sampling)
4. **S'entraîne par NTP** sur de gros corpus de texte

### Pipeline complet :
```
Texte brut → Tokenisation BPE → Embeddings → Transformer Blocks → Prédictions → Dé-tokenisation → Texte généré
```

### Points clés pour la compréhension :
- **Pas de "compréhension" magique** : Tout est statistique
- **Causal masking = génération possible** : Le modèle apprend à prédire séquentiellement
- **Sampling = créativité contrôlée** : Entre déterminisme et chaos
- **Scale matters** : Plus de données/paramètres = meilleurs résultats

---

*Ce guide fait partie du projet AI Labs - Phase 1 : LLM Playground*