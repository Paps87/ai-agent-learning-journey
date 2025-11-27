#!/usr/bin/env python3
"""
Script to download and collect training data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_collection import DataCollector

def main():
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
        "Philosophy",
        "Biology",
        "Chemistry"
    ]

    print("Starting data collection from Wikipedia...")
    texts = collector.collect_wikipedia_articles(topics, max_articles=10)
    collector.save_texts(texts)
    print(f"Data collection complete. Collected {len(texts)} articles.")

if __name__ == "__main__":
    main()