import wikipedia
import os
from pathlib import Path
import re
from typing import List

class DataCollector:
    def __init__(self, output_dir: str = "../data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def clean_text(self, text: str) -> str:
        """Clean Wikipedia text by removing references, tables, etc."""
        # Remove references like [1], [2]
        text = re.sub(r'\[\d+\]', '', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove empty lines
        text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        return text.strip()

    def collect_wikipedia_articles(self, topics: List[str], max_articles: int = 10) -> List[str]:
        """Collect articles from Wikipedia on given topics."""
        collected_texts = []

        for topic in topics:
            try:
                # Search for pages related to the topic
                search_results = wikipedia.search(topic, results=max_articles)
                print(f"Found {len(search_results)} pages for topic '{topic}': {search_results[:5]}...")

                for page_title in search_results[:max_articles]:
                    try:
                        page = wikipedia.page(page_title, auto_suggest=False)
                        content = page.content
                        cleaned_content = self.clean_text(content)

                        if len(cleaned_content) > 1000:  # Only keep substantial articles
                            collected_texts.append(cleaned_content)
                            print(f"Collected: {page_title} ({len(cleaned_content)} chars)")

                    except wikipedia.exceptions.DisambiguationError as e:
                        print(f"Disambiguation for {page_title}: {e.options[:3]}...")
                        continue
                    except Exception as e:
                        print(f"Error collecting {page_title}: {e}")
                        continue

            except Exception as e:
                print(f"Error searching topic '{topic}': {e}")
                continue

        return collected_texts

    def save_texts(self, texts: List[str], filename: str = "wikipedia_corpus.txt"):
        """Save collected texts to file."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            for text in texts:
                f.write(text + '\n\n')

        print(f"Saved {len(texts)} articles to {output_path}")
        return output_path

if __name__ == "__main__":
    collector = DataCollector()

    # Topics to collect
    topics = [
        "Artificial intelligence",
        "Machine learning",
        "Natural language processing",
        "Computer science",
        "Mathematics",
        "Physics",
        "History",
        "Philosophy"
    ]

    print("Starting data collection...")
    texts = collector.collect_wikipedia_articles(topics, max_articles=5)
    collector.save_texts(texts)
    print(f"Collected {len(texts)} articles total.")