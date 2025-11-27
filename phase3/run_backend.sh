#!/bin/bash
# Script de lancement du backend Mini Perplexity

echo "🚀 Lancement Mini Perplexity Backend"
echo "===================================="

# Activer venv
source ../venv/bin/activate

# Vérifier LM Studio
echo "🔍 Vérification LM Studio..."
if curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo "✅ LM Studio connecté"
else
    echo "⚠️  LM Studio non détecté sur localhost:1234"
    echo "   Assurez-vous que LM Studio est lancé"
fi

echo ""
echo "📡 Démarrage du serveur FastAPI..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Lancer le backend
cd backend
python api.py
