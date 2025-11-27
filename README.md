# 🤖 AI Agent Learning Journey

A comprehensive, hands-on project to master **Retrieval-Augmented Generation (RAG)**, **Web-Aware Agents**, and **Advanced Reasoning** using local LLMs.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-Compatible-green.svg)](https://lmstudio.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Overview

This project implements a **4-phase learning path** to build production-ready AI agents, from basic RAG to advanced reasoning systems. Each phase builds upon the previous one, creating a complete AI assistant ecosystem.

### 🚀 What You'll Build

- **Phase 1**: Document-based Q&A with semantic search
- **Phase 2**: Production RAG pipeline with vector databases
- **Phase 3**: Web-aware agent (like Perplexity AI)
- **Phase 4**: Advanced reasoning with Chain-of-Thought *(coming soon)*

---

## ✨ Key Features

### Phase 1: RAG Fundamentals ✅
- 📄 PDF document processing
- 🔍 Semantic search with embeddings
- 💬 Context-aware Q&A
- 🎨 Streamlit interface

### Phase 2: Production RAG ✅
- 🗄️ Qdrant vector database integration
- 🧩 Intelligent text chunking
- 📊 Similarity search optimization
- 🔄 Document management system

### Phase 3: Web-Aware Agent ✅
- 🌐 Real-time web search (DuckDuckGo)
- 🔗 HTML parsing & content extraction
- 🤖 LM Studio integration (local LLM)
- 📚 Automatic citations [1], [2], [3]
- 🧠 Multi-strategy orchestration (single/parallel/sequential)
- 💾 Conversation memory & caching

### Phase 4: Deep Reasoning 🚧
- 🧩 Chain-of-Thought (CoT) implementation
- 🌳 Tree-of-Thought exploration
- ✅ Response verification & self-correction
- 📈 Benchmarking on GSM8K/MATH datasets

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | LM Studio (local), OpenAI-compatible API |
| **Embeddings** | Sentence-Transformers (all-MiniLM-L6-v2) |
| **Vector DB** | Qdrant |
| **Web Search** | DuckDuckGo (ddgs) |
| **Parsing** | BeautifulSoup4 |
| **Interface** | Streamlit |
| **Framework** | Python 3.10+ |

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- [LM Studio](https://lmstudio.ai/) (for local LLM)
- Docker (for Qdrant)

### Quick Start

```bash
# Clone repository
git clone https://github.com/Paps87/projet_ai.git
cd ai-agent-journey

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Qdrant (Phase 2+)
docker run -p 6333:6333 qdrant/qdrant

# Start LM Studio server (Phase 3+)
# Open LM Studio → Load model → Start Server (port 1234)
```

---

## 🚀 Usage

### Phase 1: Basic RAG

```bash
cd phase1
streamlit run app/main.py
```

Upload a PDF and start asking questions!

### Phase 2: Production RAG

```bash
cd phase2
streamlit run app/main.py
```

Manage documents, search with vector similarity, and get context-aware answers.

### Phase 3: Web-Aware Agent

```bash
cd phase3
./run_streamlit.sh
# Or: streamlit run app/main.py
```

Ask questions that require web research:
- *"What's the current Bitcoin price?"*
- *"Latest AI news?"*
- *"Compare Python vs JavaScript"*

**Response time:** 15-50 seconds (includes web search + LLM generation)

---

## 📊 Performance

### Phase 3 Benchmarks

| Metric | Value |
|--------|-------|
| **Web Search** | 1-3s |
| **HTML Parsing** | 0.5-1s |
| **LLM Generation** | 10-40s |
| **Total Response** | 15-50s |
| **Accuracy** | High (with citations) |

---

## 🏗️ Architecture

### Phase 3: Web-Aware Agent

```
┌─────────────────────────────────────┐
│   Streamlit Interface (port 8501)  │
│   - Questions / Answers             │
│   - Sources & Citations             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Agent Orchestrator                │
│   - Complexity analysis             │
│   - Question decomposition          │
│   - Strategy selection              │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼──────────┐
│ Web Search │    │ Extended RAG    │
│ (DuckDuckGo│    │ Pipeline        │
└───┬────────┘    └──────┬──────────┘
    │                    │
┌───▼────────┐    ┌──────▼──────────┐
│ HTML Parser│    │ LM Studio       │
│ + Chunking │    │ (Local LLM)     │
└────────────┘    └─────────────────┘
```

---

## 📚 Project Structure

```
ai-agent-journey/
├── phase1/                 # RAG Fundamentals
│   ├── src/               # Core modules
│   ├── app/               # Streamlit UI
│   └── data/              # Sample documents
│
├── phase2/                 # Production RAG
│   ├── src/               # Vector DB, embeddings
│   ├── app/               # Document management UI
│   └── tests/             # Unit tests
│
├── phase3/                 # Web-Aware Agent
│   ├── src/
│   │   ├── web_search.py          # DuckDuckGo integration
│   │   ├── html_parser.py         # Content extraction
│   │   ├── lmstudio_client.py     # LLM client
│   │   ├── extended_rag_pipeline.py
│   │   └── agent_orchestrator.py
│   ├── app/               # Streamlit interface
│   └── PHASE3_COMPLETE.md # Full documentation
│
└── phase4/                 # Deep Reasoning (WIP)
    ├── src/
    │   ├── reasoning/     # CoT, ToT implementations
    │   └── verification/  # Response verification
    └── PHASE4_RECOMMENDATIONS.md
```

---

## 🎓 Learning Path

### Phase 1: Foundations (1-2 weeks)
- ✅ Understand RAG basics
- ✅ Implement semantic search
- ✅ Build simple Q&A system

### Phase 2: Production (1-2 weeks)
- ✅ Vector database integration
- ✅ Optimize chunking strategies
- ✅ Document management

### Phase 3: Web Integration (2-3 weeks)
- ✅ Web scraping & parsing
- ✅ Multi-source orchestration
- ✅ Citation generation
- ✅ Local LLM integration

### Phase 4: Advanced Reasoning (4-6 weeks)
- 🚧 Chain-of-Thought prompting
- 🚧 Self-consistency & verification
- 🚧 Benchmark on GSM8K/MATH
- 🚧 Optional: Fine-tuning with LoRA

---

## 🔧 Configuration

### LM Studio Settings (Phase 3+)

```python
# Recommended configuration
MODEL = "gad-gpt-5-chat-llama-3.1-8b-instruct-i1"
TEMPERATURE = 0.3  # For accuracy
MAX_TOKENS = 1000  # For faster responses
TIMEOUT = 120      # Seconds
```

### Environment Variables

```bash
# Optional: Custom ports
export QDRANT_PORT=6333
export LMSTUDIO_PORT=1234
export STREAMLIT_PORT=8501
```

---

## 🧪 Testing

```bash
# Phase 1
cd phase1
python test_phase1.py

# Phase 2
cd phase2
python test_phase2.py

# Phase 3
cd phase3
python test_validation.py
```

---

## 📖 Documentation

- **Phase 1**: [README.md](phase1/README.md)
- **Phase 2**: [README.md](phase2/README.md)
- **Phase 3**: [PHASE3_COMPLETE.md](phase3/PHASE3_COMPLETE.md)
- **Phase 4**: [PHASE4_RECOMMENDATIONS.md](phase4/PHASE4_RECOMMENDATIONS.md)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LM Studio** for local LLM inference
- **Qdrant** for vector database
- **Sentence-Transformers** for embeddings
- **Streamlit** for rapid UI development
- **DuckDuckGo** for web search API

---

## 📧 Contact

**Your Name** - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/Paps87/projet_ai](https://github.com/Paps87/projet_ai)

---

## 🗺️ Roadmap

- [x] Phase 1: RAG Fundamentals
- [x] Phase 2: Production RAG
- [x] Phase 3: Web-Aware Agent
- [ ] Phase 4: Deep Reasoning
- [ ] Phase 5: Multi-Agent Systems
- [ ] Phase 6: Production Deployment

---

**⭐ Star this repo if you find it helpful!**
