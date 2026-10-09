# AI Incident Learning & Prevention Copilot

Autonomous Agentic RAG system for Telecom Core Incident Resolution, Real-Time Auditability, and Continuous Institutional Memory Ingestion.

---

## 🛠️ Architecture Overview

- **Vector Database**: ChromaDB (Collection: `jira_tickets`)
- **Embedding Model**: `embeddinggemma` (via Ollama)
- **Synthesis & Reasoning LLM**: `llama3` (via Ollama)
- **Backend API**: FastAPI (`http://localhost:8000`)
- **Frontend Dashboard**: Streamlit (`http://localhost:8501`)

---

## 📋 System Prerequisites

Before running this project on a new laptop, ensure you have:

1. **Python 3.10+** installed:
   ```bash
   python --version
   ```
2. **Ollama** installed from [https://ollama.com](https://ollama.com).
3. **Git** installed.

---

## 🚀 Setup & Installation (Step-by-Step)

### Step 1: Start Ollama & Download Required Models

Open your terminal and pull the two models used by the Copilot:

```bash
# 1. Pull the reasoning and extraction model (Llama 3 8B)
ollama pull llama3

# 2. Pull the dense embedding model
ollama pull embeddinggemma
```

> **Note**: Make sure the Ollama desktop application or service is running in the background (`ollama serve`).

---

### Step 2: Clone or Copy the Repository

```bash
git clone <your-repo-url>
cd codedoodle
```

---

### Step 3: Create & Activate Python Virtual Environment

#### On Windows (PowerShell):
```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1
```
*(If you encounter a script execution policy error on PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

#### On Windows (Command Prompt `cmd`):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 4: Install Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

---

### Step 5: Embed Knowledge Base Tickets into ChromaDB

Populate the official ChromaDB vector store (`jira_tickets`) with the 27 historical tickets from `tickets.json`:

```bash
python embed_tickets.py
```
*(This loads `tickets.json`, generates `embeddinggemma` vectors for all tickets, and stores them locally in `./chroma_db`).*

---

## 🖥️ Running the Application

You will run **two terminal windows** (with `venv` activated in both):

### Terminal 1: Start FastAPI Backend

```bash
# Windows / Linux / macOS:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- **Backend API URL**: `http://localhost:8000`
- **Swagger / OpenAPI Docs**: `http://localhost:8000/docs`

---

### Terminal 2: Start Streamlit Frontend

Open a new terminal tab/window in the project directory, activate `venv`, and run:

```bash
streamlit run app.py
```
- **Streamlit Web UI**: `http://localhost:8501`

---

## 🔄 Interaction Flow

1. **Input Query**: Paste raw alarm logs, symptoms, or proposed MOP execution script.
2. **Automatic Field Matching**: The agent extracts technical parameters:
   - `Component / Node`
   - `Build Version`
   - `RCA Category`
   - `Product Release`
3. **Pre-Search Gatekeeper (Slot Filling)**:
   - If any mandatory field (`*`) is missing, you fill or edit it directly.
4. **Execution**: Click **🚀 Run Hybrid Search & Synthesize Remediation**.
5. **Results & Autonomous Action**:
   - **Confidence $\ge$ 70%**: Displays matched historical tickets (with **Assignee** and **Reporter**), complete citation audit trail, and Llama 3 synthesized solution.
   - **Confidence < 70%**: Displays a clean prompt: *"This issue has not occurred before would you like to log it here."* with pre-filled mandatory fields to embed and register the incident into `jira_tickets`.

---

## 📁 Project Directory Structure

```text
├── tickets.json          # 27 Nokia Core incident tickets
├── embed_tickets.py      # Parses & embeds tickets.json into ChromaDB (jira_tickets)
├── ingestion_data.py     # Ingestion helper functions & vector insertion
├── match.py              # Agentic extraction, embeddinggemma query & hybrid search logic
├── recommendations.py    # Zero-hallucination Llama 3 resolution synthesis
├── main.py               # FastAPI backend with /match, /recommend, /feedback endpoints
├── app.py                # Streamlit enterprise NOC dashboard UI
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore file (excludes venv, pycache, etc.)
└── README.md             # Project documentation and run guide
```
