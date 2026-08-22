# SMARTINFRA AI - System Architecture

## 1. Executive Summary
**SmartInfra AI** is a Pune-centric, AI-powered predictive infrastructure maintenance and smart-city intelligence platform. It bridges IoT telemetry, OpenCity geospatial municipal datasets, engineering reliability models, and generative conversational AI to provide actionable foresight to city authorities and smart commute intelligence to citizens.

---

## 2. Architectural Blueprint

```
+----------------------------------------------------------------------------------------------------+
|                                    SMARTINFRA AI - PLATFORM LAYERS                                 |
+----------------------------------------------------------------------------------------------------+

 [ CITIZEN & OFFICER FRONTENDS ]
     │               │
     │ REST API      │ WebSockets (/ws/dashboard, /ws/sensors)
     ▼               ▼
+────────────────────────────────────────────────────────────────────────────────────────────────----+
|                                       FASTAPI APPLICATION LAYER                                    |
|                                                                                                    |
|  • /api/auth          - JWT authentication & role-based authorization (Admin, Officer, Engineer)  |
|  • /api/dashboard     - Consolidated smart city command summary & incident counts                  |
|  • /api/assets        - Infrastructure catalog & explainable health scoring                        |
|  • /api/sensors       - IoT telemetry ingestion & time-series stream endpoints                     |
|  • /api/projects      - Verified PMC & PMRDA government project tracker with officer attribution   |
|  • /api/warnings      - Automated anomaly alerts, threshold warnings & acknowledgement workflows   |
|  • /api/precautions   - Targeted role-based safety precautions (Citizen, Officer, Engineer, Tech)  |
|  • /api/predictions   - ML failure probability, failure windows & Remaining Useful Life (RUL)      |
|  • /api/maintenance   - Work order dispatch, field repair tickets & verification logs              |
|  • /api/commute       - Multi-modal route corridor safety & active project risk engine             |
|  • /api/chat          - Grounded Google Gemini natural language smart city assistant               |
|  • /api/weather       - Real-time IMD / Open-Meteo precipitation & flood alert normalizer          |
|  • /api/maps          - Geocoding & route geometry provider with Pune landmark registry            |
+────────────────────────────────────────────────────────────────────────────────────────────────----+
                                    │                           │
                   ┌────────────────┴───────────────┐           │
                   ▼                                ▼           ▼
+──────────────────────────────────────+  +─────────────────────────────────────────+
|         AI & ML ENGINES              |  |         EXTERNAL INTEGRATIONS           |
|                                      |  |                                         |
| • Anomaly Detector (Z-score & rules) |  | • Google Gemini 1.5 Flash (REST Grounded)|
| • Health Score Engine (0-100)        |  | • Google Maps Platform (Directions/Geo) |
| • Composite Risk Engine (0-100)      |  | • India Meteorological Dept (IMD) API   |
| • Reliability Failure Predictor      |  | • Open-Meteo Live Precipitation API     |
| • Remaining Useful Life (RUL) Model  |  +─────────────────────────────────────────+
+──────────────────────────────────────+
                   │
                   ▼
+────────────────────────────────────────────────────────────────────────────────────────────────----+
|                                DATA ACCESS & PERSISTENCE LAYER                                     |
|                                                                                                    |
| • SQLAlchemy 2.0 ORM with Spatial Geometries (WKT + GeoAlchemy2)                                   |
| • PostgreSQL 16 + PostGIS (Production) / SQLite with Spatialite & Shapely (Development & Testing)  |
| • Alembic Database Migrations & Version Tracking                                                   |
+────────────────────────────────────────────────────────────────────────────────────────────────----+
                                    ▲
                                    │ Ingestion Adapters
+────────────────────────────────────────────────────────────────────────────────────────────────----+
|                                    DATA INGESTION PIPELINES                                        |
|                                                                                                    |
| • OpenCity Pune Roads & Footpaths         • OpenCity Pune Fire Stations                            |
| • OpenCity Pune Sewage & STP Network      • PMC Water Supply & Pipeline Telemetry                  |
| • OpenCity Pune Metro DPR                 • PMRDA & PMC Government Project Cell                    |
| • OpenCity Pune PMPML Annual Transit      • IoT Hardware Telemetry Registry (Arduino / RPi / ESP32)|
+────────────────────────────────────────────────────────────────────────────────────────────────----+
```

---

## 3. Data Flow & Core Workflows

### 3.1 Predictive Telemetry Pipeline
1. **Sensor Ingestion:** IoT devices (Arduino/Raspberry Pi) push telemetry to `POST /api/sensors/readings`.
2. **Real-time Anomaly Detection:** `AnomalyDetector` evaluates value thresholds, rate-of-change, and rolling statistical Z-scores.
3. **Dynamic Re-Scoring:** `AssetHealthEngine` recalculates asset health (0-100) and composite risk index (0-100).
4. **Warning & Precaution Generation:** If risk $\ge 60$ or anomaly detected, `WarningService` persists a warning and generates targeted precautions for citizens, engineers, and technicians.
5. **WebSocket Dispatch:** Broadcasts update over `/ws/dashboard` and `/ws/sensors`.

### 3.2 Citizen Commute & Anti-Hallucination Chatbot Pipeline
1. **User Prompt:** Citizen submits query (e.g., *"I want to go from Hinjawadi to Pune Station. What should I know?"*).
2. **Intent & Corridor Extraction:** Backend identifies `COMMUTE_QUERY` and extracts origin & destination.
3. **Spatial Query:** `CommuteService` retrieves route geometry from `MapsService` and queries database for intersecting PMC projects, high-risk assets, and active warnings within a 500m buffer.
4. **Weather Correlation:** `WeatherService` fetches current precipitation and flood alerts.
5. **Verified Grounding:** Structured context is passed to `AIService` (Google Gemini). Gemini is constrained by system prompts to use *only* verified facts.

---

## 4. Security & Role Matrix

| Role | Permissions |
|---|---|
| **ADMIN** | Full system access, user management, audit logs, configuration. |
| **OFFICER** | Manage projects, acknowledge warnings, dispatch work orders, view city risk overview. |
| **ENGINEER** | View technical diagnostics, trigger ML failure predictions, inspect sensor telemetry. |
| **FIELD_TECHNICIAN** | Update assigned work orders, log physical repair verification notes. |
| **CITIZEN** | Public commute intelligence, AI chatbot, public warnings, active road advisory. |
