# Implementation Plan - SMARTINFRA AI Backend Platform

## Overview
**SmartInfra AI** is an AI-driven predictive infrastructure maintenance and smart-city intelligence platform tailored specifically for Pune, Maharashtra. It serves government officers, infrastructure authorities, engineers, field technicians, and citizens by combining:
1. Normalized Pune municipal infrastructure datasets (roads, footpaths, sewage, water pipelines, metro DPR, fire stations, PMPML transit, construction bye-laws).
2. Live & simulated IoT sensor ingestion (water pressure, flow, vibration, strain, water levels).
3. Geospatial PostGIS engines for corridor, radius, and route-proximity analysis.
4. AI/ML predictive engines (statistical anomaly detection, Isolation Forest, health score 0-100, risk score 0-100, failure probability estimation, Remaining Useful Life ranges, feature explainability).
5. Automated Warning & Precaution Engine with role-based routing and work-order management.
6. Commute Intelligence Engine calculating route safety, active projects, warnings, and weather risks.
7. Citizen Chatbot powered by Google Gemini (with strict factual anchoring to verified backend context to prevent hallucinations).
8. Real-time WebSocket broadcasting and dashboard aggregation APIs.

---

## User Review Required
> [!NOTE]
> Python 3.14.4 compatibility has been verified. Core dependencies (`fastapi`, `uvicorn`, `sqlalchemy 2.0`, `alembic`, `pydantic v2`, `pydantic-settings`, `pyjwt`, `argon2-cffi`, `shapely`, `geoalchemy2`, `scikit-learn`, `httpx`, `websockets`, `pytest`) are supported.
> SQLite with SpatiaLite / pure-Python Shapely spatial fallback is provided alongside PostgreSQL + PostGIS to allow seamless execution and testing both in local zero-config environments and in full Docker/PostgreSQL+PostGIS production deployments.

---

## Architecture & Directory Structure

```
smartinfra-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── assets.py
│   │   │   ├── sensors.py
│   │   │   ├── projects.py
│   │   │   ├── officers.py
│   │   │   ├── warnings.py
│   │   │   ├── precautions.py
│   │   │   ├── predictions.py
│   │   │   ├── maintenance.py
│   │   │   ├── commute.py
│   │   │   ├── chatbot.py
│   │   │   ├── weather.py
│   │   │   ├── maps.py
│   │   │   └── websocket.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── officer.py
│   │   │   ├── asset.py
│   │   │   ├── sensor.py
│   │   │   ├── project.py
│   │   │   ├── warning.py
│   │   │   ├── precaution.py
│   │   │   ├── prediction.py
│   │   │   ├── maintenance.py
│   │   │   └── audit.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── asset.py
│   │   │   ├── sensor.py
│   │   │   ├── project.py
│   │   │   ├── officer.py
│   │   │   ├── warning.py
│   │   │   ├── precaution.py
│   │   │   ├── prediction.py
│   │   │   ├── maintenance.py
│   │   │   ├── commute.py
│   │   │   ├── chatbot.py
│   │   │   ├── dashboard.py
│   │   │   └── weather.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── chatbot_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── prediction_service.py
│   │   │   ├── sensor_service.py
│   │   │   ├── project_service.py
│   │   │   ├── weather_service.py
│   │   │   ├── maps_service.py
│   │   │   ├── commute_service.py
│   │   │   ├── warning_service.py
│   │   │   └── notification_service.py
│   │   ├── ml/
│   │   │   ├── anomaly_detection.py
│   │   │   ├── health_score.py
│   │   │   ├── failure_prediction.py
│   │   │   └── rul_prediction.py
│   │   ├── ingestion/
│   │   │   ├── base.py
│   │   │   ├── opencity.py
│   │   │   ├── water_leaks.py
│   │   │   ├── government_projects.py
│   │   │   └── sensors.py
│   │   └── utils/
│   │       ├── geo.py
│   │       ├── time.py
│   │       └── serializers.py
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── alembic.ini
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_assets.py
│   │   ├── test_sensors.py
│   │   ├── test_projects.py
│   │   ├── test_warnings.py
│   │   ├── test_commute.py
│   │   ├── test_chatbot.py
│   │   ├── test_ml_pipeline.py
│   │   └── test_dashboard.py
│   ├── scripts/
│   │   ├── seed_database.py
│   │   ├── simulate_sensors.py
│   │   └── import_datasets.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_SPECIFICATION.md
│   └── DATASETS.md
└── README.md
```

---

## Phased Implementation Roadmap

### Phase 1: Configuration, Core Infrastructure & Database Engine
- `backend/app/core/config.py`: Pydantic BaseSettings loading `.env` with validated defaults.
- `backend/app/core/database.py`: SQLAlchemy 2.0 Async/Sync engine, PostGIS/Geometry support with graceful Spatialite/Shapely spatial function fallbacks.
- `backend/app/core/security.py`: Argon2/bcrypt password hashing, JWT encoding/decoding with expiry and role validation.
- `backend/app/core/logging.py`: Structured JSON and formatted logging without leaking credentials.
- `backend/app/core/exceptions.py`: Centralized exception classes & global FastAPI error handlers.

### Phase 2: SQLAlchemy Models & Database Layer
- All 10 entity models: User, Officer, InfrastructureAsset, Sensor, SensorReading, GovernmentProject, Warning, Precaution, Prediction, WorkOrder, AuditLog.
- Foreign keys, cascading behaviors, spatial geometry columns, composite indexes.
- Alembic configuration and migration baseline.

### Phase 3: Pydantic v2 Schemas & Data Contracts
- Request and Response schemas for all models with validation, pagination, query filters, spatial coordinate models, and ISO 8601 formatting.

### Phase 4: AI & ML Engine
- **Health Score Engine (0-100)**: Configurable multi-criteria evaluation (age, condition, sensor anomalies, maintenance, criticality, environment).
- **Risk Score Engine (0-100)**: Heuristic + statistical weighting (condition 30%, anomalies 25%, criticality 20%, failure history 15%, weather 10%). Categories: LOW (0-30), MODERATE (31-60), HIGH (61-80), CRITICAL (81-100).
- **Anomaly Detection**: Rolling z-score, rate-of-change, Isolation Forest anomaly detector for multi-sensor time-series.
- **Failure Probability & RUL Predictor**: Survival/degradation curve estimator outputting confidence ranges (`estimated_rul_min`, `estimated_rul_max`) and explainability factor breakdown.

### Phase 5: External Services & Smart City Integrations
- **Maps Service**: Geocoding, reverse geocoding, route generation with polyline decoding and spatial corridor query support. Robust mock fallback when API key is not supplied.
- **Weather / IMD Service**: IMD/OpenMeteo endpoint integration returning normalized temperature, precipitation, flood risk, and weather alerts for Pune zones.
- **Sensor Ingestion Service**: Real-time reading processor, trigger evaluation, automatic asset risk recalculation, and warning emitter.
- **Warning & Precaution Engine**: Automatic threshold-based warning generator with actionable engineering and citizen precautions.
- **Commute Intelligence Service**: Multi-modal route risk analyzer evaluating route intersections with active road works, sewage overflows, pipeline pressure alerts, and weather risks.

### Phase 6: Gemini Conversational AI Service
- Intent classification (`COMMUTE_QUERY`, `INFRASTRUCTURE_QUERY`, `PROJECT_QUERY`, `WARNING_QUERY`, `WEATHER_QUERY`, `MAINTENANCE_QUERY`, `GENERAL_CITY_QUERY`).
- Origin/Destination and Entity extraction.
- **Strict Context Injection**: Gemini is supplied ONLY verified database/API context. Prompt enforces never hallucinating officers, projects, sensor readings, or fake risks. Clean mock/fallback responses when GEMINI_API_KEY is not configured.

### Phase 7: REST API Layer & WebSockets
- Full set of REST routes with OpenAPI documentation, dependency injection, and role-based access control.
- WebSocket broadcaster (`/ws/dashboard`, `/ws/sensors`) for live telemetry and warning streaming.

### Phase 8: Data Ingestion Adapters & Seeders
- Ingestion pipelines for OpenCity Pune datasets (bye-laws, transport, footpaths/roads, metro DPR, PMPML, sewage network, fire stations, sewage treatment plants) and water leaks dataset.
- Robust data normalizer preserving source attribution.
- Database seed script with verified Pune demo data.
- Sensor simulator script (`scripts/simulate_sensors.py`) generating live telemetry with anomaly events.

### Phase 9: Verification, Testing & Dockerization
- Comprehensive pytest test suite covering authentication, assets, projects, sensors, anomaly detection, warnings, commute analysis, weather, and chatbot.
- `Dockerfile` & `docker-compose.yml` (backend + PostGIS).
- Complete documentation (`README.md`, API specification, runbooks).

---

## Verification Plan
1. **Automated Unit & Integration Tests**: Run `pytest` on all API endpoints, ML modules, geospatial logic, and external services.
2. **End-to-End Simulation**: Run `simulate_sensors.py` to verify:
   - High pressure -> Anomaly detected -> Asset risk updated -> Critical Warning generated -> Precaution linked -> WebSocket broadcasted.
3. **Citizen Commute Scenario**: Test `POST /api/commute/analyze` with Hinjawadi to Pune Station, validating active road projects, high-risk warnings, and weather risks.
4. **Chatbot Scenario**: Test `POST /api/chat` for "I want to go from Hinjawadi to Pune Station. What should I know?", verifying structured context retrieval and accurate AI response.
5. **OpenAPI / Swagger Inspection**: Ensure `/docs` and `/openapi.json` are fully populated and valid.
