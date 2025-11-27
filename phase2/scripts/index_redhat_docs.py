#!/usr/bin/env python3
"""
Script d'indexation de documentation RedHat (OpenStack, Ansible)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings import EmbeddingManager
from src.vector_db import VectorDatabase
from pathlib import Path
import re

def chunk_markdown(text: str, max_chunk_size: int = 500) -> list:
    """Découpe markdown par sections"""
    sections = re.split(r'\n#{1,3}\s+', text)
    chunks = []
    for section in sections:
        if len(section) > max_chunk_size:
            words = section.split()
            for i in range(0, len(words), max_chunk_size):
                chunk = ' '.join(words[i:i+max_chunk_size])
                if chunk.strip():
                    chunks.append(chunk.strip())
        elif section.strip():
            chunks.append(section.strip())
    return chunks

def index_documents(docs_directory: str):
    """Indexe les documents dans Qdrant"""
    print(f"📁 Indexation depuis: {docs_directory}")
    
    # Init
    emb_mgr = EmbeddingManager()
    emb_mgr.load_model()
    
    db = VectorDatabase()
    db.connect()
    db.create_collection(vector_size=384)
    
    # Parcourir les fichiers
    docs_path = Path(docs_directory)
    all_chunks = []
    all_metadata = []
    
    for file_path in docs_path.glob("**/*.md"):
        print(f"📄 Traitement: {file_path.name}")
        text = file_path.read_text(encoding='utf-8')
        
        chunks = chunk_markdown(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadata.append({
                "text": chunk,
                "source": file_path.name,
                "title": file_path.stem,
                "chunk_id": i
            })
    
    print(f"📊 Total: {len(all_chunks)} chunks")
    
    if len(all_chunks) == 0:
        print("⚠️  Aucun document trouvé à indexer")
        return
    
    # Encoder et indexer
    print("🧮 Encodage...")
    embeddings = emb_mgr.encode_batch(all_chunks, batch_size=32)
    
    print("💾 Indexation dans Qdrant...")
    db.add_documents(all_metadata, embeddings)
    
    print(f"✅ Indexation terminée: {len(all_chunks)} documents")
    
    # Info
    info = db.get_collection_info()
    print(f"📊 Collection: {info['name']}, Status: {info['status']}")

if __name__ == "__main__":
    # Indexer les documents RedHat
    docs_dir = "../data/documents"

    # Créer un dossier pour docs RedHat si besoin
    redhat_dir = Path(docs_dir) / "redhat"
    redhat_dir.mkdir(parents=True, exist_ok=True)

    print("""
📚 INSTRUCTIONS POUR AJOUTER LA DOC REDHAT:

1. Télécharger docs depuis:
   - OpenStack: https://docs.openstack.org/
   - Ansible: https://docs.ansible.com/

2. Placer les fichiers .md dans: phase2/data/documents/redhat/

3. Lancer ce script: python scripts/index_redhat_docs.py

4. Qdrant doit tourner: docker run -p 6333:6333 qdrant/qdrant
""")

    # Indexer spécifiquement le dossier redhat
    redhat_docs_dir = str(redhat_dir)
    print(f"🔍 Recherche de docs dans: {redhat_docs_dir}")

    # Vérifier si le dossier existe et contient des fichiers
    if redhat_dir.exists():
        md_files = list(redhat_dir.glob("*.md"))
        print(f"📄 Fichiers .md trouvés: {len(md_files)}")
        for f in md_files:
            print(f"  - {f.name} ({f.stat().st_size} bytes)")
    else:
        print(f"❌ Dossier {redhat_docs_dir} n'existe pas")

    # Utiliser le bon chemin relatif depuis le script
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    redhat_path = project_root / "data" / "documents" / "redhat"
    print(f"📂 Chemin absolu: {redhat_path}")

    index_documents(str(redhat_path))