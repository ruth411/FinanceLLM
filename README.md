# FinanceLLM

## 🎯 Objective
Build a privacy-friendly personal finance dashboard that:
- Runs a **local LLM** (Ollama) inside GitHub Codespaces
- Exposes a **FastAPI** backend (CSV ingest, summaries, LLM bridge)
- Serves a **Streamlit** web UI (charts, tables)

Everything runs in **Docker** inside your Codespace (no external cloud inference).

---

## 🧱 Stack (current stage)
- **Ollama**: local LLM server (default model: `phi3:mini`)
- **FastAPI**: REST API (health, CSV ingest endpoints, summaries)
- **SQLite**: local DB (Docker volume)
- **Streamlit**: dashboard UI

**Ports**
- Ollama: `11434`
- API: `8000`
- UI: `8501`

**Services**
- ollama -> local LLM
- api -> FastAPI backend
- app -> Streamlit UI

### 🗂️ Repo layout (current)
```
.
├─ docker-compose.yml
├─ api/
│  ├─ Dockerfile
│  ├─ requirements.txt
│  ├─ main.py
│  ├─ llm.py
│  ├─ ingest.py
│  ├─ db.py
│  └─ models.py
└─ app/
   ├─ Dockerfile
   ├─ requirements.txt
   └─ streamlit_app.py
```
---

## 🚀 Quickstart (GitHub Codespaces)

### 0) Open in Codespaces
- Open this repo in **GitHub Codespaces**.
- If needed, add Docker-in-Docker support and rebuild:
  ```
  // .devcontainer/devcontainer.json
  { "features": { "ghcr.io/devcontainers/features/docker-in-docker:2": {} } }
  ```

### 1) Build & start all services

```
docker compose up -d --build
docker compose ps
```

### 2) Pull a compact CPU model for Ollama (first time only)
```
docker exec -it ollama ollama pull phi3:mini
```

### 3) (Optional) Sanity check the LLM
```
curl -s http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"phi3:mini","messages":[{"role":"user","content":"Say hi in one sentence."}]}'
```
### 4) Check the API health & docs
```
curl -s http://localhost:8000/health
# -> {"status":"ok"}
```
