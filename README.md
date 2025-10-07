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
5. For GPU: Use Novita AI or local/cloud setup

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