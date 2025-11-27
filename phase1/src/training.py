import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.model import GPTModel
from src.tokenization import Tokenizer

class TextDataset(Dataset):
    def __init__(self, tokenized_file: str, seq_len: int = 512):
        self.seq_len = seq_len

        # Load tokenized data
        with open(tokenized_file, 'r') as f:
            tokens = [int(x) for x in f.read().split()]

        self.data = torch.tensor(tokens, dtype=torch.long)

    def __len__(self):
        return len(self.data) - self.seq_len

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.seq_len]
        y = self.data[idx + 1:idx + self.seq_len + 1]
        return x, y

def train_model(tokenized_file: str, vocab_size: int, epochs: int = 10,
                batch_size: int = 8, lr: float = 1e-4, save_path: str = "../models/gpt_model.pth"):
    # Create dataset and dataloader
    dataset = TextDataset(tokenized_file)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = GPTModel(vocab_size=vocab_size)
    model.train()

    # Optimizer
    optimizer = optim.AdamW(model.parameters(), lr=lr)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    print(f"Training on {device}")
    print(f"Dataset size: {len(dataset)}")
    print(f"Batch size: {batch_size}")

    for epoch in range(epochs):
        total_loss = 0
        for batch_idx, (x, y) in enumerate(dataloader):
            x, y = x.to(device), y.to(device)

            optimizer.zero_grad()
            logits, loss = model(x, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if batch_idx % 100 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx}, Loss: {loss.item():.4f}")

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs} completed. Average Loss: {avg_loss:.4f}")

        # Save checkpoint
        checkpoint_path = save_path.replace('.pth', f'_epoch_{epoch+1}.pth')
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_loss,
        }, checkpoint_path)
        print(f"Saved checkpoint: {checkpoint_path}")

    # Save final model
    torch.save(model.state_dict(), save_path)
    print(f"Training complete. Model saved to {save_path}")

if __name__ == "__main__":
    # Load tokenizer to get vocab size
    tokenizer = Tokenizer()
    tokenizer.load()

    vocab_size = tokenizer.get_vocab_size()
    tokenized_file = "../data/processed/tokenized_corpus.txt"

    if not Path(tokenized_file).exists():
        print(f"Tokenized file not found: {tokenized_file}")
        print("Run preprocess.py first.")
        sys.exit(1)

    train_model(tokenized_file, vocab_size, epochs=1, batch_size=2)