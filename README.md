# 🩺 Equiderma AI: Multimodal Skin Disease Prediction & Clinical Advisor

Equiderma AI is a local multimodal image-to-text clinical decision-support system designed to assess **dermatological conditions across diverse skin tones** (Fitzpatrick Phototypes I through VI).

The system integrates a **Flask REST API backend**, an interactive **Streamlit frontend dashboard**, a local **Ollama multimodal vision model** (`llama3.2-vision` / `llava`), and a **ChromaDB RAG vector database** to retrieve grounded clinical literature and assign confidence scores and severity risk ratings (**High**, **Medium**, **Low**).

> **Medical Disclaimer & Design Rule**: Strictly built **without OpenCV** (`cv2`). Image loading and processing are performed natively using Pillow and base64 strings passed directly into Ollama's vision API.

---

## 🌟 Key Features

1. **Multimodal Image-to-Text Analysis**:
   - Accepts lesion photographs (via file upload or camera capture) alongside patient symptom history.
   - Evaluates lesion morphology, margin irregularity, color variegation, and scaling.

2. **Melanin & Skin Tone Awareness**:
   - Categorizes skin phototypes according to the **Fitzpatrick Scale (Types I–VI)**.
   - Highlights critical clinical variations:
     - **Light Skin (Types I–III)**: Vivid pink/red erythema and classic inflammatory presentation.
     - **Melanin-Rich / Dark Skin (Types IV–VI)**: Subtle erythema, violaceous or slate-brown discoloration, follicular prominence, and high propensity for Post-Inflammatory Hyperpigmentation (PIH).

3. **Risk Stratification & Confidence Scoring**:
   - **Severity Level**:
     - 🚨 **High**: Suspected malignancies (Melanoma, invasive BCC) or acute severe infections (Herpes Zoster/Shingles) requiring urgent clinical care.
     - ⚠️ **Medium**: Chronic inflammatory conditions (Eczema, Psoriasis, Contact Dermatitis) requiring prescription regimens.
     - ✅ **Low**: Benign or mild conditions (Acne, Tinea Corporis, Rosacea, Vitiligo) manageable with routine or OTC care.
   - **Confidence Score**: Quantitative percentage score (0–100%) indicating visual and anamnesis confidence.

4. **ChromaDB RAG (Retrieval-Augmented Generation)**:
   - Clinical literature is chunked by condition, visual morphology, skin tone presentation, and management protocols.
   - Embeddings are indexed in ChromaDB to retrieve top matching clinical chunks that ground the Ollama advisor's diagnosis with verifiable evidence.

---

## 🏗️ Architecture

```
Equiderma AI/
├── backend/
│   ├── __init__.py
│   ├── config.py              # Ports, hosts, Ollama models, Fitzpatrick scale
│   ├── knowledge_data.py      # Curated dermatology dataset across skin tones & severities
│   ├── rag_engine.py          # ChromaDB chunking, vector indexing & semantic search
│   ├── clinical_advisor.py    # Multimodal Ollama integration, Pydantic schema, no OpenCV
│   └── server.py              # Flask REST API routes (/api/analyze, /api/health, /api/rag)
├── frontend/
│   ├── __init__.py
│   ├── components.py          # Severity badges, confidence gauge, tone & citation widgets
│   └── dashboard.py           # Streamlit clinical dashboard with image upload & camera
├── data/
│   └── chroma_db/             # Local persistent ChromaDB vector store
├── requirements.txt           # Clean dependencies (Flask, Streamlit, ChromaDB, Ollama, Pillow)
├── run_backend.py             # Launcher for Flask backend server
├── run_frontend.py            # Launcher for Streamlit frontend dashboard
└── test_system.py             # Automated verification suite
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Prepare Ollama (Local Multimodal Model)
Equiderma AI is designed to use local Ollama vision models:
```bash
# Pull a multimodal vision model (choose one):
ollama pull llama3.2-vision
# OR
ollama pull llava
```
*Note: If Ollama is offline or the vision model is still downloading, Equiderma AI automatically falls back to grounded ChromaDB RAG inference mode so you can continue testing without interruptions.*

### 3. Start the Flask Backend
In a terminal, start the Flask REST API:
```bash
python run_backend.py
```
Backend will start on `http://127.0.0.1:5000`.

### 4. Start the Streamlit Clinical Dashboard
In a second terminal, launch the Streamlit frontend:
```bash
streamlit run frontend/dashboard.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 System Verification

To run the automated verification test suite covering the knowledge base, ChromaDB vector indexing, pure base64 image encoding (no OpenCV), clinical advisor reasoning, and Flask endpoints:
```bash
python test_system.py
```

---

## 📡 Backend REST API Endpoints

- `GET /api/health`: Health status of Flask, Ollama connection, and ChromaDB chunk count.
- `POST /api/analyze`: Multimodal analysis accepting `{ "image": "<b64>", "symptoms": "...", "skin_tone_hint": "Type IV", "model": "llama3.2-vision" }`.
- `GET /api/conditions`: Query dermatological knowledge base records with optional `?q=` and `?severity=` filters.
- `POST /api/rag/search`: Semantic vector search into ChromaDB with `{ "query": "...", "n_results": 4, "tone": "dark_skin" }`.
- `POST /api/rag/reindex`: Re-chunk and re-embed all clinical knowledge records into ChromaDB.
