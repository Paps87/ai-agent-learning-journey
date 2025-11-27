#!/bin/bash
# Script de lancement du frontend Mini Perplexity

echo "🎨 Lancement Mini Perplexity Frontend"
echo "====================================="
echo ""
echo "🌐 Frontend: http://localhost:8080"
echo "📡 Backend: http://localhost:8000 (doit être lancé séparément)"
echo ""
echo "💡 Ouvrez votre navigateur sur http://localhost:8080"
echo ""

# Lancer le serveur HTTP
cd frontend
python3 -m http.server 8080
