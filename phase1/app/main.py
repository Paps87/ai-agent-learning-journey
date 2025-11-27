import streamlit as st
import torch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.model import GPTModel
from src.tokenization import Tokenizer

# Page config
st.set_page_config(
    page_title="LLM Playground",
    page_icon="🧠",
    layout="wide"
)

@st.cache_resource
def load_model_and_tokenizer():
    """Load the trained model and tokenizer."""
    try:
        # Load tokenizer
        tokenizer = Tokenizer()
        tokenizer.load()

        # Load model
        vocab_size = tokenizer.get_vocab_size()
        # Use same parameters as the saved test model
        model = GPTModel(
            vocab_size=vocab_size,
            d_model=128,      # Match saved model
            n_heads=4,
            n_layers=2,       # Match saved model
            max_seq_len=256   # Match saved model
        )

        model_path = "../models/gpt_model.pth"
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location='cpu'))
            st.success("Loaded trained model!")
        else:
            st.warning("No trained model found. Using untrained model for demonstration.")

        model.eval()
        return model, tokenizer

    except Exception as e:
        st.error(f"Error loading model/tokenizer: {e}")
        return None, None

def generate_text(model, tokenizer, prompt, max_tokens=50, temperature=1.0,
                 top_k=None, top_p=None, strategy="greedy"):
    """Generate text using the model."""
    try:
        # Encode prompt
        input_ids = torch.tensor([tokenizer.encode(prompt)], dtype=torch.long)

        # Set sampling parameters based on strategy
        if strategy == "greedy":
            temperature = 0.0
            top_k = None
            top_p = None
        elif strategy == "top_k":
            temperature = temperature
            top_p = None
        elif strategy == "top_p":
            temperature = temperature
            top_k = None

        # Generate
        with torch.no_grad():
            generated_ids = model.generate(
                input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p
            )

        # Decode
        generated_text = tokenizer.decode(generated_ids[0].tolist())

        # Remove the prompt from the beginning
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()

        return generated_text

    except Exception as e:
        return f"Error generating text: {e}"

def main():
    st.title("🧠 LLM Playground")
    st.markdown("A mini ChatGPT-like interface for text generation")

    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer()

    if model is None or tokenizer is None:
        st.error("Failed to load model and tokenizer. Please train the model first.")
        return

    # Sidebar for parameters
    st.sidebar.header("Generation Parameters")

    strategy = st.sidebar.selectbox(
        "Sampling Strategy",
        ["greedy", "top_k", "top_p"],
        help="Greedy: always pick most likely token\nTop-k: sample from top k tokens\nTop-p: nucleus sampling"
    )

    max_tokens = st.sidebar.slider("Max New Tokens", 10, 200, 50)
    temperature = st.sidebar.slider("Temperature", 0.1, 2.0, 1.0, 0.1,
                                   help="Higher = more random, Lower = more deterministic")

    if strategy == "top_k":
        top_k = st.sidebar.slider("Top-k", 1, 100, 50)
    else:
        top_k = None

    if strategy == "top_p":
        top_p = st.sidebar.slider("Top-p", 0.1, 1.0, 0.9, 0.05)
    else:
        top_p = None

    # Main interface
    st.header("Text Generation")

    # Chat-like interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Enter your prompt..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response = generate_text(
                    model, tokenizer, prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    strategy=strategy
                )
            st.markdown(response)

        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("*Built with PyTorch and Streamlit*")

if __name__ == "__main__":
    main()