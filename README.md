# SmartInfra AI - Backend Service

FastAPI-powered backend for AI-driven predictive infrastructure maintenance and smart-city intelligence in Pune.

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+ (Tested and verified on **Python 3.14.4**)
- pip

### 2. Setup Virtual Environment & Install Dependencies
```bash
cd backend
python -m pip install -r ../requirements.txt
```

### 3. Initialize & Seed Database
```bash
# Applies migrations and seeds demo data (users, assets, projects, sensors)
python scripts/seed_database.py
```

### 4. Start Backend Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Swagger UI Documentation: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

## Running Tests
```bash
python -m pytest tests -v
```

---

## Running the IoT Sensor Simulator
To simulate live Arduino / Raspberry Pi sensor readings with automatic anomaly detection and warning generation:
```bash
python scripts/simulate_sensors.py
```
