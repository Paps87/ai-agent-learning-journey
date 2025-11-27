#!/bin/bash
# Script de lancement simple pour Mini Perplexity avec Streamlit

echo "🚀 Lancement Mini Perplexity (Streamlit)"
echo "========================================"
echo ""

# Vérifier LM Studio
echo "🔍 Vérification LM Studio..."
if curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo "✅ LM Studio connecté"
else
    echo "⚠️  LM Studio non détecté sur localhost:1234"
    echo "   Assurez-vous que LM Studio est lancé"
fi

echo ""
echo "📡 Démarrage de l'interface Streamlit..."
echo "   URL: http://localhost:8501"
echo ""

# Activer venv et lancer Streamlit
cd "/home/paps/Projet ai"
source venv/bin/activate
streamlit run phase3/app/main.py
