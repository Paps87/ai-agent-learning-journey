#!/usr/bin/env python3
"""
Script to preprocess data: train tokenizer and tokenize corpus.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.tokenization import Tokenizer
from pathlib import Path

def main():
    # Paths
    raw_data_dir = Path("../data/raw")
    processed_data_dir = Path("../data/processed")
    processed_data_dir.mkdir(parents=True, exist_ok=True)

    corpus_file = raw_data_dir / "wikipedia_corpus.txt"
    if not corpus_file.exists():
        print(f"Corpus file not found: {corpus_file}")
        print("Run download_data.py first.")
        return

    # Train tokenizer
    print("Training tokenizer...")
    tokenizer = Tokenizer()
    tokenizer.train(str(corpus_file))

    # Load tokenizer
    tokenizer.load()

    # Tokenize the corpus
    tokenized_file = processed_data_dir / "tokenized_corpus.txt"
    print("Tokenizing corpus...")
    tokenizer.tokenize_file(str(corpus_file), str(tokenized_file))

    print("Preprocessing complete.")
    print(f"Vocab size: {tokenizer.get_vocab_size()}")

if __name__ == "__main__":
    main()