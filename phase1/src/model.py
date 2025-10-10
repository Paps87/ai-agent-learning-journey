import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, q, k, v, mask=None):
        batch_size = q.size(0)

        # Linear transformations and reshape
        q = self.w_q(q).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        k = self.w_k(k).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        v = self.w_v(v).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)

        # Attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_k ** 0.5)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attn = F.softmax(scores, dim=-1)
        context = torch.matmul(attn, v)

        # Concatenate and linear
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.w_o(context)

class FeedForward(nn.Module):
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)

    def forward(self, x):
        return self.linear2(F.relu(self.linear1(x)))

class TransformerBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, n_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.feed_forward = FeedForward(d_model, d_ff)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Self-attention with residual connection
        attn_out = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))

        # Feed-forward with residual connection
        ff_out = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_out))

        return x

class GPTModel(nn.Module):
    def __init__(self, vocab_size: int, d_model: int = 512, n_heads: int = 8,
                 n_layers: int = 6, d_ff: int = 2048, max_seq_len: int = 1024,
                 dropout: float = 0.1):
        super().__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.max_seq_len = max_seq_len

        # Token and position embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_len, d_model)

        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])

        # Output layer
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

        # Tie weights
        self.token_embedding.weight = self.lm_head.weight

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, input_ids, targets=None):
        batch_size, seq_len = input_ids.size()

        # Create position ids
        position_ids = torch.arange(0, seq_len, dtype=torch.long, device=input_ids.device)
        position_ids = position_ids.unsqueeze(0).expand(batch_size, -1)

        # Embeddings
        tok_emb = self.token_embedding(input_ids)
        pos_emb = self.position_embedding(position_ids)
        x = tok_emb + pos_emb

        # Create causal mask
        causal_mask = torch.tril(torch.ones(seq_len, seq_len, device=input_ids.device)).bool()
        causal_mask = causal_mask.unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, seq_len)

        # Transformer blocks
        for block in self.blocks:
            x = block(x, causal_mask)

        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            # Shift logits and targets for next-token prediction
            shift_logits = logits[..., :-1, :].contiguous()
            shift_targets = targets[..., 1:].contiguous()
            loss = F.cross_entropy(shift_logits.view(-1, self.vocab_size),
                                 shift_targets.view(-1))

        return logits, loss

    def generate(self, input_ids, max_new_tokens: int = 50, temperature: float = 1.0,
                top_k: Optional[int] = None, top_p: Optional[float] = None):
        """Generate text autoregressively."""
        self.eval()
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Get logits for the last token
                logits, _ = self(input_ids)

                if temperature == 0.0:
                    # Greedy decoding: select the token with highest probability
                    next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
                else:
                    # Apply temperature
                    next_token_logits = logits[:, -1, :] / temperature

                    # Apply top-k sampling
                    if top_k is not None:
                        top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k, dim=-1)
                        next_token_logits = torch.full_like(next_token_logits, -float('inf'))
                        next_token_logits.scatter_(-1, top_k_indices, top_k_logits)

                    # Apply top-p (nucleus) sampling
                    if top_p is not None:
                        sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                        sorted_probs = F.softmax(sorted_logits, dim=-1)
                        cumulative_probs = torch.cumsum(sorted_probs, dim=-1)

                        # Find cutoff
                        cutoff_mask = cumulative_probs > top_p
                        # Set logits beyond cutoff to -inf
                        sorted_logits[cutoff_mask] = -float('inf')

                        # Re-sort to original order
                        next_token_logits.scatter_(-1, sorted_indices, sorted_logits)

                    # Sample next token
                    probs = F.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)

                # Append to sequence
                input_ids = torch.cat([input_ids, next_token], dim=-1)

        return input_ids

if __name__ == "__main__":
    # Test the model
    vocab_size = 1000
    model = GPTModel(vocab_size=vocab_size, d_model=256, n_heads=4, n_layers=4)

    # Dummy input
    x = torch.randint(0, vocab_size, (2, 10))
    logits, loss = model(x, x)
    print(f"Input shape: {x.shape}")
    print(f"Logits shape: {logits.shape}")
    print(f"Loss: {loss}")

    # Test generation
    generated = model.generate(x[:, :5], max_new_tokens=5)
    print(f"Generated shape: {generated.shape}")