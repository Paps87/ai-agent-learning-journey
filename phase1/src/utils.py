import torch
from pathlib import Path
import json

def save_config(config: dict, path: str):
    """Save configuration to JSON file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)

def load_config(path: str) -> dict:
    """Load configuration from JSON file."""
    with open(path, 'r') as f:
        return json.load(f)

def count_parameters(model: torch.nn.Module) -> int:
    """Count total parameters in a PyTorch model."""
    return sum(p.numel() for p in model.parameters())

def count_trainable_parameters(model: torch.nn.Module) -> int:
    """Count trainable parameters in a PyTorch model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def get_device() -> torch.device:
    """Get the best available device (CUDA if available, else CPU)."""
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def set_seed(seed: int = 42):
    """Set random seed for reproducibility."""
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)