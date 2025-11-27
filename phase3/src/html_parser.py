#!/usr/bin/env python3
"""
Module de parsing HTML pour Phase 3 - Ask-the-Web Agent
Extrait le contenu textuel des pages web pour l'intégration RAG
"""

from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Any, Optional
import re
import logging
from urllib.parse import urlparse

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTMLParser:
    """
    Parseur HTML pour extraire le contenu textuel des pages web
    Optimisé pour le contenu informatif (articles, documentation, etc.)
    """

    def __init__(self, timeout: int = 10, user_agent: str = None):
        """
        Initialise le parseur HTML

        Args:
            timeout: Timeout pour les requêtes HTTP (secondes)
            user_agent: User-Agent pour les requêtes
        """
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (compatible; WebScraper/1.0; +https://example.com/bot)"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        logger.info("HTMLParser initialisé")

    def parse_url(self, url: str) -> Optional[str]:
        """
        Télécharge et parse une URL pour extraire le texte principal

        Args:
            url: URL de la page à parser

        Returns:
            Texte extrait et nettoyé, ou None si erreur
        """
        try:
            logger.info(f"Téléchargement: {url}")

            # Validation URL
            if not self._is_valid_url(url):
                logger.warning(f"URL invalide: {url}")
                return None

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )

            response.raise_for_status()

            # Vérification du type de contenu
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Type de contenu non HTML: {content_type}")
                return None

            # Parsing HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraction du texte
            text = self._extract_main_content(soup)

            # Nettoyage
            clean_text = self._clean_text(text)

            if len(clean_text) < 100:  # Texte trop court
                logger.warning(f"Texte extrait trop court: {len(clean_text)} caractères")
                return None

            logger.info(f"Texte extrait: {len(clean_text)} caractères")
            return clean_text

        except requests.exceptions.Timeout:
            logger.error(f"Timeout pour {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur HTTP pour {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur parsing {url}: {e}")
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Valide qu'une URL est bien formée et sûre"""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc]) and parsed.scheme in ['http', 'https']
        except:
            return False

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extrait le contenu principal de la page HTML
        Stratégie multi-niveaux pour maximiser la qualité
        """

        # 1. Supprimer les éléments indésirables
        self._remove_unwanted_elements(soup)

        # 2. Chercher le contenu principal avec différents sélecteurs
        main_content = self._find_main_content(soup)

        # 3. Extraire le texte avec structure
        text = self._extract_text_with_structure(main_content)

        return text

    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """Supprime les éléments HTML indésirables"""

        # Éléments à supprimer complètement
        unwanted_tags = [
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            'noscript', 'iframe', 'object', 'embed', 'form',
            'button', 'input', 'select', 'textarea'
        ]

        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Supprimer les éléments avec classes indésirables
        unwanted_classes = [
            'advertisement', 'ads', 'sidebar', 'menu', 'navigation',
            'footer', 'header', 'popup', 'modal', 'cookie', 'gdpr',
            'social', 'share', 'comment', 'related'
        ]

        for class_name in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()

        # Supprimer les éléments avec IDs indésirables
        unwanted_ids = [
            'header', 'footer', 'sidebar', 'menu', 'nav',
            'advertisement', 'ads', 'popup', 'modal'
        ]

        for id_name in unwanted_ids:
            element = soup.find(id=id_name)
            if element:
                element.decompose()

    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Trouve le contenu principal en essayant différents sélecteurs
        par ordre de priorité
        """

        # Sélecteurs de contenu principal (par priorité décroissante)
        content_selectors = [
            # Sélecteurs sémantiques HTML5
            'main',
            'article',

            # Classes et IDs courants
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]',
            '[class*="entry"]',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#main-content',
            '#content',
            '#main',

            # Conteneurs génériques
            '[class*="container"]',
            '[class*="wrapper"]',

            # Fallback: body
            'body'
        ]

        for selector in content_selectors:
            try:
                element = soup.select_one(selector)
                if element and self._is_content_rich(element):
                    logger.debug(f"Contenu trouvé avec sélecteur: {selector}")
                    return element
            except:
                continue

        # Fallback final: tout le body
        logger.debug("Fallback: utilisation du body complet")
        return soup.body or soup

    def _is_content_rich(self, element) -> bool:
        """Vérifie si un élément contient du contenu textuel riche"""

        if not element:
            return False

        # Compter les mots
        text = element.get_text()
        word_count = len(text.split())

        # Critères de qualité
        min_words = 50
        max_density = 0.8  # Éviter les éléments avec trop de liens

        # Compter les liens
        link_count = len(element.find_all('a'))
        link_density = link_count / max(word_count, 1)

        return word_count >= min_words and link_density <= max_density

    def _extract_text_with_structure(self, element) -> str:
        """Extrait le texte en préservant la structure logique"""

        if not element:
            return ""

        # Extraire le texte avec séparateurs logiques
        text_parts = []
        seen_texts = set()  # Éviter les doublons

        for child in element.descendants:
            if child.name in ['p', 'div', 'section', 'article']:
                # Nouveau paragraphe
                para_text = child.get_text(separator=' ', strip=True)
                if para_text and len(para_text.split()) > 3 and para_text not in seen_texts:
                    text_parts.append(para_text)
                    seen_texts.add(para_text)

            elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Titre
                title_text = child.get_text(strip=True)
                if title_text and title_text not in seen_texts:
                    text_parts.append(f"\n## {title_text}\n")
                    seen_texts.add(title_text)

            elif child.name == 'li':
                # Élément de liste
                li_text = child.get_text(strip=True)
                if li_text and li_text not in seen_texts:
                    text_parts.append(f"• {li_text}")
                    seen_texts.add(li_text)

        # Si aucun texte structuré trouvé, fallback sur get_text()
        if not text_parts:
            logger.debug("Fallback: utilisation de get_text() simple")
            text = element.get_text(separator='\n', strip=True)
            return text

        # Joindre avec des sauts de ligne
        text = '\n\n'.join(text_parts)

        return text

    def _clean_text(self, text: str) -> str:
        """Nettoie et normalise le texte extrait"""

        if not text:
            return ""

        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        # Normaliser les espaces
        text = re.sub(r' +', ' ', text)

        # Supprimer les lignes vides multiples
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        # Nettoyer les fins de lignes
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        # Supprimer les caractères spéciaux indésirables (mais garder la ponctuation)
        text = re.sub(r'[^\w\s\n.,!?\-()\[\]{}:;"\'/\\]', '', text)

        # Supprimer les URLs longues
        text = re.sub(r'https?://[^\s]{50,}', '[URL]', text)

        # Limiter les répétitions de caractères
        text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)

        return text.strip()

class TextChunker:
    """
    Découpeur de texte en chunks optimisé pour le RAG
    Gère les chevauchements et préserve le contexte
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50, min_chunk_size: int = 100):
        """
        Args:
            chunk_size: Taille maximale d'un chunk (en mots)
            overlap: Chevauchement entre chunks (en mots)
            min_chunk_size: Taille minimale d'un chunk (en mots)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

        logger.info(f"TextChunker initialisé: chunk_size={chunk_size}, overlap={overlap}")

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Découpe le texte en chunks avec chevauchement

        Args:
            text: Texte à découper
            metadata: Métadonnées à ajouter à chaque chunk

        Returns:
            Liste de chunks avec métadonnées
        """

        if not text or len(text.strip()) < self.min_chunk_size:
            return []

        words = text.split()
        chunks = []

        if metadata is None:
            metadata = {}

        # Découpage avec chevauchement
        step = self.chunk_size - self.overlap

        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)

            # Vérifier la taille minimale
            if len(chunk_words) < self.min_chunk_size // 2:  # Chunk trop petit
                continue

            chunk_data = {
                "text": chunk_text,
                "chunk_id": len(chunks),
                "start_word": i,
                "end_word": min(i + self.chunk_size, len(words)),
                "word_count": len(chunk_words),
                "source": "web_parsed",
                **metadata
            }

            chunks.append(chunk_data)

        logger.info(f"Texte découpé: {len(words)} mots → {len(chunks)} chunks")
        return chunks

    def chunk_by_sections(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Découpage intelligent par sections (titres, paragraphes)
        """

        if not text:
            return []

        # Diviser par sections (détecter les titres ##)
        sections = re.split(r'\n##\s+', text)
        chunks = []

        if metadata is None:
            metadata = {}

        for section_id, section in enumerate(sections):
            if not section.strip():
                continue

            # Découper la section si elle est trop longue
            section_chunks = self.chunk_text(section, {
                **metadata,
                "section_id": section_id,
                "section_type": "section"
            })

            chunks.extend(section_chunks)

        return chunks

class WebContentProcessor:
    """
    Processeur complet de contenu web
    Combine parsing HTML et chunking pour l'intégration RAG
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Args:
            chunk_size: Taille des chunks
            overlap: Chevauchement entre chunks
        """
        self.parser = HTMLParser()
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)

        logger.info("WebContentProcessor initialisé")

    def process_search_result(self, search_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Traite un résultat de recherche complet

        Args:
            search_result: Résultat de recherche avec URL, title, etc.

        Returns:
            Liste de chunks prêts pour le RAG
        """

        url = search_result.get("url")
        if not url:
            logger.warning("URL manquante dans le résultat de recherche")
            return []

        logger.info(f"Traitement de l'URL: {url}")

        # Parser l'URL
        text = self.parser.parse_url(url)
        if not text:
            logger.warning(f"Impossible de parser l'URL: {url}")
            return []

        # Préparer les métadonnées
        metadata = {
            "source": "web",
            "url": url,
            "title": search_result.get("title", ""),
            "search_query": search_result.get("query", ""),
            "timestamp": search_result.get("timestamp", 0),
            "source_type": "web_page"
        }

        # Découper en chunks
        chunks = self.chunker.chunk_text(text, metadata)

        logger.info(f"Page traitée: {url} → {len(chunks)} chunks")
        return chunks

    def process_multiple_results(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Traite plusieurs résultats de recherche

        Args:
            search_results: Liste de résultats de recherche

        Returns:
            Liste complète de chunks
        """

        all_chunks = []
        successful_parses = 0

        for result in search_results:
            chunks = self.process_search_result(result)
            if chunks:  # Seulement si parsing réussi
                all_chunks.extend(chunks)
                successful_parses += 1

        logger.info(f"Traitement complet: {len(search_results)} URLs → {successful_parses} réussis → {len(all_chunks)} chunks")
        return all_chunks

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du processeur"""
        return {
            "parser_timeout": self.parser.timeout,
            "chunk_size": self.chunker.chunk_size,
            "chunk_overlap": self.chunker.overlap
        }

# Instance globale
web_processor = WebContentProcessor()

def get_web_processor() -> WebContentProcessor:
    """Factory function pour l'instance globale"""
    return web_processor

# Tests unitaires
if __name__ == "__main__":
    print("🧪 Test du WebContentProcessor")
    print("=" * 50)

    # Initialisation
    processor = WebContentProcessor()

    # Test avec une URL simple
    test_url = "https://httpbin.org/html"  # Service de test

    print(f"🔍 Test parsing URL: {test_url}")

    try:
        text = processor.parser.parse_url(test_url)
        if text:
            print(f"✅ Texte extrait: {len(text)} caractères")
            print(f"📄 Aperçu: {text[:200]}...")

            # Test chunking
            chunks = processor.chunker.chunk_text(text, {"test": True})
            print(f"✅ Découpage: {len(chunks)} chunks")

            if chunks:
                print(f"📝 Premier chunk: {chunks[0]['text'][:100]}...")

        else:
            print("❌ Échec du parsing")

    except Exception as e:
        print(f"💥 Erreur: {e}")

    print("\n✅ Tests terminés!")