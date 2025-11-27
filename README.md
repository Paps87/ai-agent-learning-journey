# AI Labs Project

This repository contains a series of AI projects following a structured learning path from basic LLM understanding to advanced multi-modal agents.

## Project Phases

### Phase 0 — Mise en place (Setup)
- ✅ Python 3.11/3.12 environment
- ✅ VSCode, Docker, Jupyter, Git
- ✅ GitHub repo setup
- GPU environment: Using Novita AI for computations during testing

### Phase 1 — Project 1: Build an LLM Playground 🧠
Objective: Understand LLM foundations and build a local "ChatGPT".

Sub-projects:
- Data collection and cleaning (Common Crawl or Wikipedia)
- Tokenization (BPE / SentencePiece)
- Transformer architecture (GPT-like model in PyTorch)
- Text generation (greedy / top-k / top-p)
- Post-training: Fine-tuning on simple SFT dataset
- Streamlit or FastAPI interface for testing

### Phase 2 — Project 2: Customer Support Chatbot (RAG + Prompt Engineering) 🗂️
Objective: Build a chatbot connected to internal documentation.

Sub-projects:
- Document indexing with embeddings (FAISS / ChromaDB)
- Contextual retrieval + generation (RAG pipeline)
- Advanced prompt engineering (role, chain-of-thought)
- Response evaluation (relevance, factuality)
- Web or terminal UI for tests

### Phase 3 — Project 3: Ask-the-Web Agent 🌐
Objective: Create an agent capable of web searching like Perplexity.

- Web search (DuckDuckGo / Google API / Tavily)
- HTML parsing + chunking
- RAG + reasoning + orchestration (ReAct / LangGraph)
- Tools: function calling, Python execution, multi-step planning

### Phase 4 — Project 4: Deep Research (Reasoning & Verifiers) 🔍
Objective: Master logical reasoning and automatic verification.

- Chain-of-Thought, Tree-of-Thought implementation
- Response verification and self-correction
- Light fine-tuning on reasoning datasets (STaR, PRM)
- Benchmark on GSM8K / MATH / QA tasks

### Phase 5 — Project 5: Multi-modal Agent 🎨
Objective: Generate images/videos from text.

- Diffusion introduction (Stable Diffusion, DiT)
- Simplified diffusion model training
- Image generation (txt2img) and videos (txt2vid)
- Integration with agent for text + visual combination

### Phase 6 — Capstone Project 🚀
Define and implement a custom AI project (e.g., DevOps architect AI, InfraGPT).

## Setup Instructions

1. Clone this repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. GPU environment: Use Novita AI for computations during testing phases

## Managing Secrets

API keys and sensitive data are stored in an encrypted vault using Ansible Vault.

1. Copy `secrets_template.yml` to `secrets.yml`
2. Edit `secrets.yml` with your actual keys
3. Encrypt it: `ansible-vault encrypt secrets.yml`
4. To edit: `ansible-vault edit secrets.yml`
5. To view: `ansible-vault view secrets.yml`

In Python code, load secrets like:

```python
import subprocess
import yaml

# Decrypt and load
result = subprocess.run(['ansible-vault', 'view', 'secrets.yml'], capture_output=True, text=True, input='your_vault_password\n')
secrets = yaml.safe_load(result.stdout)

API_KEY = secrets['novita_api_key']
```

Alternatively, use python-dotenv with a .env file (also gitignored).

## Using Novita AI for GPU Computations

Novita AI provides cloud GPU resources for running AI models. Sign up at [novita.ai](https://novita.ai), get your API key, and store it securely in the vault.

Example usage in Python:

```python
import requests

# Load API_KEY from secrets
API_KEY = secrets['novita_api_key']  # Assuming secrets loaded as above

url = "https://api.novita.ai/v1/text-to-image"  # Example endpoint for image generation

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "prompt": "A beautiful sunset over mountains",
    "width": 512,
    "height": 512
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    result = response.json()
    print("Generated image URL:", result['image_url'])
else:
    print("Error:", response.text)
```

For LLM inference, check their documentation for text generation endpoints. Replace the endpoint and data accordingly.

## Requirements
- Python 3.11+
- Git
- Docker (optional)
- Jupyter Notebook

## Notes
- Rhythm: 4-6 hours/week
- Each project: 2-3 weeks
- Method: Guided with ready-to-run code, iterate together on bugs/experiments/results
- End of each project: Report and demo
=======
# projet_ai
I plan to deep dive into AI, you will find all my prj here
>>>>>>> 6797304b865902f833abafae34dee42d527bcab8
