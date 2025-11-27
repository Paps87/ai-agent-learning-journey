# Phase 1: LLM Playground

This project builds a mini local ChatGPT-like playground to understand LLM foundations.

## Components

- **Data Collection**: Collect and clean data from Wikipedia
- **Tokenization**: Implement BPE using SentencePiece
- **Transformer Model**: GPT-like architecture in PyTorch
- **Text Generation**: Greedy, top-k, top-p sampling
- **Fine-tuning**: Post-training on SFT dataset
- **Interface**: Streamlit app for inference and chat

## Project Structure

```
phase1/
├── data/
│   ├── raw/          # Raw collected data
│   └── processed/    # Cleaned and tokenized data
├── src/
│   ├── __init__.py
│   ├── data_collection.py
│   ├── tokenization.py
│   ├── model.py
│   ├── generation.py
│   ├── training.py
│   └── utils.py
├── models/           # Saved model checkpoints
├── notebooks/
│   └── experiments.ipynb
├── app/
│   ├── __init__.py
│   └── main.py       # Streamlit interface
├── scripts/
│   ├── download_data.py
│   └── preprocess.py
└── README.md
```

## Getting Started

1. Install dependencies: `pip install -r ../requirements.txt`
2. Run data collection: `python scripts/download_data.py`
3. Preprocess data: `python scripts/preprocess.py`
4. Train model: `python src/training.py`
5. Launch interface: `streamlit run app/main.py`