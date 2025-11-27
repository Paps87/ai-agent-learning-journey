# Phase 3: Ask-the-Web Agent 🌐

## 🎯 **Objectif**
Créer un agent IA capable d'aller chercher des informations sur le web comme Perplexity, en combinant recherche web, parsing de contenu, et génération de réponses intelligentes.

## 🧠 **Concepts Clés**

### **1. Agent Web-Aware**
Un agent capable de :
- **Comprendre** les questions complexes
- **Planifier** des recherches multi-étapes
- **Exécuter** des recherches sur le web
- **Synthétiser** l'information trouvée
- **Fournir** des réponses avec sources

### **2. Recherche Web**
Techniques pour trouver l'information pertinente :
- **APIs de recherche** : DuckDuckGo, Google, Bing
- **Web scraping** : BeautifulSoup, Scrapy
- **Parsing intelligent** : Extraction du contenu utile

### **3. Orchestration d'Agent**
Coordination des tâches :
- **Planification** : Décomposer la question en sous-recherches
- **Exécution** : Effectuer les recherches en parallèle/séquence
- **Synthèse** : Combiner les résultats
- **Validation** : Vérifier la cohérence

### **4. RAG Étendu**
Intégration des données web :
- **Indexation dynamique** : Ajouter du contenu web à la volée
- **Mémorisation** : Conserver le contexte des recherches
- **Mise à jour** : Actualiser les connaissances

## 📋 **Sous-Projets**

### **3.1 Recherche Web**
- APIs de recherche (DuckDuckGo, Google)
- Gestion des résultats
- Filtrage et ranking

### **3.2 Parsing HTML**
- Extraction de contenu textuel
- Nettoyage du HTML
- Chunking intelligent

### **3.3 Pipeline RAG Étendu**
- Intégration données web
- Gestion mémoire conversation
- Mise à jour dynamique

### **3.4 Agent Orchestration**
- Planification de recherches
- Exécution multi-étape
- Gestion d'erreurs

### **3.5 Interface Web-Aware**
- Affichage des sources
- Historique des recherches
- Paramètres avancés

## 🏗️ **Architecture**

```
Question Utilisateur
        ↓
   Agent Orchestrator
   ├── Analyse question
   ├── Planification recherche
   └── Coordination
        ↓
   Recherche Web (DuckDuckGo/Google)
        ↓
   Parsing + Chunking HTML
        ↓
   RAG Pipeline Étendu
   ├── Indexation dynamique
   ├── Recherche sémantique
   └── Génération réponse
        ↓
   Réponse avec Sources
   ├── Contenu synthétisé
   ├── Citations
   └── Liens sources
```

## 🎯 **Résultat Attendu**
Un agent capable de répondre à des questions complexes en allant chercher l'information sur le web, avec citations et raisonnement transparent.