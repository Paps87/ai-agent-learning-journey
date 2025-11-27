import torch
import torch.nn.functional as F
from typing import Optional, List
from .model import GPTModel
from .tokenization import Tokenizer

class TextGenerator:
    def __init__(self, model: GPTModel, tokenizer: Tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()

    def generate_greedy(self, prompt: str, max_new_tokens: int = 50) -> str:
        """Generate text using greedy decoding (always pick most likely token)."""
        input_ids = torch.tensor([self.tokenizer.encode(prompt)], dtype=torch.long)

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=0.0  # Greedy
            )

        generated_text = self.tokenizer.decode(generated_ids[0].tolist())
        return generated_text[len(prompt):].strip()

    def generate_top_k(self, prompt: str, max_new_tokens: int = 50,
                       temperature: float = 1.0, top_k: int = 50) -> str:
        """Generate text using top-k sampling."""
        input_ids = torch.tensor([self.tokenizer.encode(prompt)], dtype=torch.long)

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k
            )

        generated_text = self.tokenizer.decode(generated_ids[0].tolist())
        return generated_text[len(prompt):].strip()

    def generate_top_p(self, prompt: str, max_new_tokens: int = 50,
                       temperature: float = 1.0, top_p: float = 0.9) -> str:
        """Generate text using nucleus (top-p) sampling."""
        input_ids = torch.tensor([self.tokenizer.encode(prompt)], dtype=torch.long)

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p
            )

        generated_text = self.tokenizer.decode(generated_ids[0].tolist())
        return generated_text[len(prompt):].strip()

    def generate(self, prompt: str, strategy: str = "greedy", **kwargs) -> str:
        """Unified generation method."""
        if strategy == "greedy":
            return self.generate_greedy(prompt, **kwargs)
        elif strategy == "top_k":
            return self.generate_top_k(prompt, **kwargs)
        elif strategy == "top_p":
            return self.generate_top_p(prompt, **kwargs)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

if __name__ == "__main__":
    # Test generation
    from .model import GPTModel

    # Dummy model and tokenizer for testing
    vocab_size = 1000
    model = GPTModel(vocab_size=vocab_size)
    tokenizer = Tokenizer()

    # Create dummy tokenizer model for testing
    import sentencepiece as spm
    # This would need actual trained model

    generator = TextGenerator(model, tokenizer)
    print("TextGenerator initialized. Ready for generation with trained models.")