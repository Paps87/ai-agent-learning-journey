import sentencepiece as spm
from pathlib import Path
import os
from typing import List, Optional

class Tokenizer:
    def __init__(self, model_prefix: str = "../models/tokenizer", vocab_size: int = 8000):
        self.model_prefix = Path(model_prefix)
        self.vocab_size = vocab_size
        self.model_prefix.parent.mkdir(parents=True, exist_ok=True)
        self.sp = None

    def train(self, input_file: str, model_type: str = "bpe"):
        """Train SentencePiece tokenizer on input text file."""
        model_path = str(self.model_prefix)

        spm.SentencePieceTrainer.train(
            input=input_file,
            model_prefix=model_path,
            vocab_size=self.vocab_size,
            model_type=model_type,  # 'bpe' or 'unigram'
            character_coverage=1.0,  # For multilingual
            unk_id=0,
            bos_id=1,
            eos_id=2,
            pad_id=3,
            unk_piece="<unk>",
            bos_piece="<s>",
            eos_piece="</s>",
            pad_piece="<pad>",
            user_defined_symbols=["<mask>"]  # For potential masked LM
        )

        print(f"Trained tokenizer saved to {model_path}.model and {model_path}.vocab")

    def load(self, model_file: Optional[str] = None):
        """Load trained tokenizer."""
        if model_file is None:
            model_file = str(self.model_prefix) + ".model"

        if not Path(model_file).exists():
            raise FileNotFoundError(f"Tokenizer model not found: {model_file}")

        self.sp = spm.SentencePieceProcessor()
        self.sp.load(model_file)
        print(f"Loaded tokenizer with vocab size: {self.sp.get_piece_size()}")

    def encode(self, text: str) -> List[int]:
        """Encode text to token ids."""
        if self.sp is None:
            raise ValueError("Tokenizer not loaded. Call load() first.")
        return self.sp.encode_as_ids(text)

    def decode(self, token_ids: List[int]) -> str:
        """Decode token ids to text."""
        if self.sp is None:
            raise ValueError("Tokenizer not loaded. Call load() first.")
        return self.sp.decode_ids(token_ids)

    def get_vocab_size(self) -> int:
        """Get vocabulary size."""
        if self.sp is None:
            raise ValueError("Tokenizer not loaded. Call load() first.")
        return self.sp.get_piece_size()

    def tokenize_file(self, input_file: str, output_file: str):
        """Tokenize a text file and save token ids."""
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        token_ids = self.encode(text)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(' '.join(map(str, token_ids)))

        print(f"Tokenized {input_file} -> {output_file}")

if __name__ == "__main__":
    # Example usage
    tokenizer = Tokenizer()

    # Train on sample data (you would use the collected corpus)
    # For demo, create a small sample
    sample_text = """Artificial intelligence is intelligence demonstrated by machines.
    Machine learning is a subset of AI that enables systems to learn from data.
    Natural language processing deals with the interaction between computers and human language."""

    sample_file = "../data/raw/sample.txt"
    Path(sample_file).parent.mkdir(parents=True, exist_ok=True)
    with open(sample_file, 'w') as f:
        f.write(sample_text)

    # Train tokenizer
    tokenizer.train(sample_file)

    # Load and test
    tokenizer.load()
    test_text = "AI and machine learning"
    tokens = tokenizer.encode(test_text)
    decoded = tokenizer.decode(tokens)

    print(f"Original: {test_text}")
    print(f"Tokens: {tokens}")
    print(f"Decoded: {decoded}")