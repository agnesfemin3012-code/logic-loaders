# AI-Driven Predictive Infrastructure Maintenance for Smart Cities

An AI-powered Smart City Infrastructure Monitoring and Predictive Maintenance system developed for college hackathon demonstration.

---

## 🏙 System Architecture

```
Frontend (React.js + Tailwind + Leaflet/OpenStreetMap)
   │
   ▼ HTTP / REST
FastAPI Backend (:8000)
   ├── ML Models (RandomForestRegressor + RandomForestClassifier)
   ├── Weather Service (Modular: IMD API + Open-Meteo Fallback + Simulation)
   └── AI Chatbot (Google Gemini API with Verified Backend Tool Grounding)
```

---

## 📂 Project Structure

```
.
├── backend/
│   ├── main.py                     # FastAPI server entrypoint
│   ├── train_model.py              # ML training, preprocessing & evaluation
│   ├── predict.py                  # Standalone prediction engine & CLI
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   ├── .env                        # Local configuration
│   ├── data/
│   │   └── smart_city_data.csv     # Synthetic smart city dataset
│   ├── models/
│   │   ├── smart_city_delay_model.pkl   # Serialized delay regressor
│   │   └── smart_city_risk_model.pkl    # Serialized risk classifier
│   ├── routes/
│   │   ├── prediction.py           # POST /predict, POST /predict/batch
│   │   ├── projects.py             # GET /projects, GET /projects/{id}
│   │   ├── weather.py              # GET /weather/current, GET /weather/alerts
│   │   └── chatbot.py              # POST /chatbot/chat (Gemini AI)
│   └── services/
│       ├── ml_service.py           # ML inference & priority scoring
│       ├── weather_service.py      # Modular IMD / Open-Meteo provider
│       ├── gemini_service.py       # Google Gemini tool-grounded service
│       └── recommendation_service.py # Smart preventive action rules
│
├── src/                            # React.js Frontend
│   ├── components/                 # UI, Maps, Drawers, Metrics
│   ├── pages/                      # Dashboard, Projects, AI Intelligence, Assistant
│   ├── services/
│   │   └── api.ts                  # Frontend API client for FastAPI
│   └── ...
├── package.json
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Machine Learning & Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. (Optional) Create and activate a Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the ML Models & generate dataset
python train_model.py

# 5. (Optional) Test standalone prediction CLI on demo scenario
python predict.py --demo

# 6. Start the FastAPI Server
python main.py
# Or with uvicorn:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend server will run at:
- **API Base**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Alternative ReDoc**: `http://localhost:8000/redoc`

---

### 2. Frontend React Setup

```bash
# In the root directory:
npm install
npm run dev
```

The frontend dashboard will run at `http://localhost:5173`.

---

## 🧠 Machine Learning Details

### Input Features:
- `project_type`: Type of infrastructure (Road, Metro, Bridge, Drain, etc.)
- `planned_duration`: Duration in days
- `current_progress`: Progress percentage (0–100%)
- `traffic_volume`: Vehicles / hour
- `average_speed`: Speed in km/h
- `rainfall`: Precipitation in mm
- `temperature`: Temperature in °C
- `humidity`: Humidity percentage
- `road_condition`: Surface condition rating (1 to 5)
- `workers_available`: Workforce count
- `previous_delay`: Historical delay in days

### Feature Engineering:
- $\text{Traffic Congestion Index} = \frac{\text{traffic\_volume}}{\text{average\_speed} + 1}$
- $\text{Weather Severity Index} = \text{rainfall} \times \frac{\text{humidity}}{100}$
- $\text{Labor Density} = \frac{\text{workers\_available}}{\text{planned\_duration} + 1}$

### Output Predictions:
1. `predicted_delay_days`: Numerical regression via `RandomForestRegressor`
2. `predicted_completion_days`: `planned_duration + predicted_delay_days`
3. `risk_level`: Multi-class classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) via `RandomForestClassifier`
4. `traffic_level`: Congestion classification (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`)
5. `weather_impact`: Environmental severity (`NONE`, `LOW`, `MODERATE`, `SEVERE`)
6. `priority_analysis`: Composite score out of 100 based on Traffic + Road + Delay + Weather + Age.

---

## 🌦 Weather Integration

The weather service is modular:
1. **Official IMD API**: Used when `IMD_API_KEY` is provided in `.env`.
2. **Open-Meteo Live API**: Free open meteorological REST API used as live fallback.
3. **Calibrated City Feed**: High-fidelity offline simulation ensuring reliable demo execution during presentations.

---

## 🤖 Google Gemini AI Grounding Rule

**Core Rule**: Gemini **never invents numerical predictions**.
All numerical values (delays, completion days, failure risks, priority scores) originate strictly from the Scikit-learn ML models and verified backend tools. Gemini acts as an explainability and reasoning layer converting technical findings into clear municipal recommendations.

---

## 🎯 Hackathon Demo Benchmark

**Scenario: "Road Expansion – Zone A"**
- Inputs:
  - Traffic: 1120 vehicles/hour
  - Speed: 19 km/h
  - Rainfall: 8 mm
  - Progress: 55%
  - Workers: 18
  - Planned duration: 60 days
- ML Outputs:
  - `predicted_delay_days`: ~9 days
  - `predicted_completion_days`: ~69 days
  - `risk_level`: `HIGH`
  - `traffic_level`: `HIGH`
- Smart Action: *"Shift major construction activity to low-traffic night hours (22:00–06:00) and increase workforce allocation."*
