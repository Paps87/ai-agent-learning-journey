#!/usr/bin/env python3
"""
Backend FastAPI pour Mini Perplexity
Expose les fonctionnalités de recherche web + LLM via API REST
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Imports Phase 3
from src.agent_orchestrator import get_web_aware_agent
from src.lmstudio_client import get_lm_studio_client
from src.web_search import get_web_search_engine

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation FastAPI
app = FastAPI(
    title="Mini Perplexity API",
    description="API de recherche web intelligente avec LLM",
    version="1.0.0"
)

# Configuration CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class AskRequest(BaseModel):
    """Requête pour /api/ask"""
    query: str
    max_results: Optional[int] = 5
    use_web: Optional[bool] = True

class Source(BaseModel):
    """Source d'information"""
    title: str
    url: str
    type: str

class AskResponse(BaseModel):
    """Réponse de /api/ask"""
    answer: str
    sources: List[Source]
    processing_time: float
    search_strategy: Optional[str] = None
    web_sources_count: int = 0
    local_sources_count: int = 0

class HealthResponse(BaseModel):
    """Réponse de /api/health"""
    status: str
    lm_studio_connected: bool
    timestamp: str

# Initialisation des composants
try:
    agent = get_web_aware_agent()
    llm_client = get_lm_studio_client()
    search_engine = get_web_search_engine()
    logger.info("✅ Composants initialisés avec succès")
except Exception as e:
    logger.error(f"❌ Erreur initialisation: {e}")
    agent = None
    llm_client = None
    search_engine = None

# Routes

@app.get("/")
async def root():
    """Page d'accueil - Servir le frontend"""
    frontend_path = os.path.join(parent_dir, "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        return {
            "name": "Mini Perplexity API",
            "version": "1.0.0",
            "endpoints": {
                "ask": "/api/ask",
                "health": "/api/health",
                "docs": "/docs"
            }
        }

# Servir les fichiers statiques du frontend
frontend_dir = os.path.join(parent_dir, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Vérifier l'état de santé de l'API
    Teste la connexion à LM Studio
    """
    lm_studio_ok = False
    
    if llm_client:
        try:
            lm_studio_ok = llm_client.test_connection()
        except:
            pass
    
    return HealthResponse(
        status="healthy" if lm_studio_ok else "degraded",
        lm_studio_connected=lm_studio_ok,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Endpoint principal : poser une question
    
    Workflow:
    1. Recherche web (DuckDuckGo)
    2. Extraction et chunking du contenu
    3. Génération réponse avec LM Studio
    4. Retour avec sources et citations
    """
    
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Service non disponible. Composants non initialisés."
        )
    
    try:
        logger.info(f"📥 Question reçue: '{request.query}'")
        
        # Utiliser l'agent pour répondre
        response = agent.answer_question(
            question=request.query,
            max_depth=3
        )
        
        # Formater les sources
        sources = []
        for source in response.get("sources", []):
            sources.append(Source(
                title=source.get("title", "Sans titre"),
                url=source.get("url", ""),
                type=source.get("type", "web")
            ))
        
        # Compter les sources par type
        web_count = len([s for s in response.get("web_sources", [])])
        local_count = response.get("local_sources", 0)
        
        logger.info(f"✅ Réponse générée: {len(response.get('answer', ''))} caractères")
        
        return AskResponse(
            answer=response.get("answer", "Aucune réponse générée"),
            sources=sources,
            processing_time=response.get("processing_time", 0),
            search_strategy=response.get("search_strategy", "unknown"),
            web_sources_count=web_count,
            local_sources_count=local_count
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement: {str(e)}"
        )

@app.get("/api/stats")
async def get_stats():
    """Statistiques de l'agent"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent non disponible")
    
    try:
        stats = agent.get_agent_stats()
        return {
            "agent_stats": stats,
            "lm_studio_connected": llm_client.test_connection() if llm_client else False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Point d'entrée
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Lancement Mini Perplexity Backend")
    print("=" * 60)
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🤖 LM Studio: http://localhost:1234")
    print("=" * 60)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
