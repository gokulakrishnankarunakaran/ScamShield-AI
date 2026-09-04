# ScamShield AI — Backend API

**Team CYBERTRON**  
**Core Principle:** *"VERIFY BEFORE YOU TRUST."*

ScamShield AI is an intelligent payment security and fraud prevention platform for UPI and QR/screenshot payments. It pairs **deterministic evidence** (authoritative payment identity registries and Actian Vector semantic matching) with **AI contextual explanation** (Google Gemini).

---

## 📁 Architecture & Directory Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # API server entrypoint (FastAPI / Multi-mode runner)
│   ├── config.py                # 12-factor configuration & environment manager
│   ├── schemas/                 # Pydantic data contracts & schemas
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── merchant.py
│   │   ├── qr.py
│   │   └── screenshot.py
│   ├── routers/                 # Modular API route controllers
│   │   ├── __init__.py
│   │   ├── health.py            # GET /health
│   │   ├── qr.py                # POST /check-qr (Scaffolded for Phase 2)
│   │   ├── screenshot.py        # POST /check-screenshot (Scaffolded for Phase 2)
│   │   └── demo.py              # GET /demo/merchants & POST /demo/reset
│   ├── services/                # Business logic & domain services
│   │   ├── __init__.py
│   │   ├── reputation_service.py # Deterministic VPA reputation lookup
│   │   └── vector_service.py    # Semantic & phonetic merchant name matching
│   └── database/                # Database clients & data stores
│       ├── __init__.py
│       ├── actian.py            # Actian VectorAI / Actian Vector client abstraction
│       └── mock_data.py         # Synthetic demo merchant registry
├── tests/                       # Comprehensive unit and integration test suite
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_config.py
│   ├── test_reputation.py
│   ├── test_vector_service.py
│   └── test_actian.py
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # Backend documentation
```

---

## ⚙️ Environment Setup & Python Guidelines

### Python Version Recommendation
* **Recommended for ML / Neural Vector Embeddings:** Python `3.11` or `3.12`.
* **Current Machine Default:** Python `3.14.7`.

### Quickstart
1. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

2. **Configure Environment:**
   ```bash
   copy .env.example .env
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Server:**
   ```bash
   python -m backend.app.main
   # Or using uvicorn:
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 🛡️ Database & Actian VectorAI

The backend features a resilient Actian Vector database client ([`ActianVectorClient`](file:///c:/Users/gokul/Videos/ScamShield%202.0/backend/app/database/actian.py)):
* **Status Telemetry:** Checks host socket/ODBC connection on startup and exposes status in `/health`.
* **Zero Crash Fallback:** When Actian Vector is offline or not installed, the system gracefully falls back to an in-memory sparse cosine vector index without interrupting service.

---

## 🧪 Running Tests

Execute the complete backend test suite:
```bash
python -m unittest discover -s backend/tests -p "test_*.py" -v
```

Or with `pytest`:
```bash
pytest backend/tests/ -v
```

---

## 🔌 API Endpoints (Phase 1)

| Method | Path | Description | Phase |
|---|---|---|---|
| `GET` | `/` | API Root and metadata | Phase 1 (Active) |
| `GET` | `/health` | Server health & Actian status | Phase 1 (Active) |
| `GET` | `/demo/merchants` | List demo verified/scam merchants | Phase 1 (Active) |
| `POST` | `/demo/reset` | Reset demo registry to baseline | Phase 1 (Active) |
| `POST` | `/check-qr` | QR Shield Verification | Phase 2 (Scaffolded) |
| `POST` | `/check-screenshot` | Screenshot Verifier | Phase 2 (Scaffolded) |

