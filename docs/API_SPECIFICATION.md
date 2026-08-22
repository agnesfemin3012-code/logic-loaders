# SMARTINFRA AI - REST API Specification

Base URL: `/api` (or `/api/v1`)
Interactive OpenAPI Docs: `http://localhost:8000/docs`
Interactive Redoc: `http://localhost:8000/redoc`

---

## 1. Authentication & Users (`/api/auth`)

### `POST /api/auth/register`
- **Request Body:**
  ```json
  {
    "name": "Rajesh Patil",
    "email": "rajesh@punecorporation.org",
    "password": "SecurePassword123",
    "role": "OFFICER",
    "phone": "+91-20-2550-1100"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Rajesh Patil",
      "email": "rajesh@punecorporation.org",
      "role": "OFFICER",
      "phone": "+91-20-2550-1100",
      "is_active": true,
      "created_at": "2026-08-22T06:00:00Z",
      "updated_at": "2026-08-22T06:00:00Z"
    }
  }
  ```

### `POST /api/auth/login`
- **Request Body:**
  ```json
  {
    "email": "admin@smartinfra.pune.gov.in",
    "password": "admin123"
  }
  ```
- **Response (200 OK):** Returns JWT access token and user profile.

### `GET /api/auth/me`
- **Headers:** `Authorization: Bearer <JWT_TOKEN>`
- **Response (200 OK):** Current authenticated user profile.

---

## 2. Dashboard Command Center (`/api/dashboard`)

### `GET /api/dashboard/summary`
- **Description:** Aggregates asset counts, active warnings, delayed projects, 7-day predictive failures, situation overview, and Pune weather into a single response.
- **Response (200 OK):**
  ```json
  {
    "assets": {
      "total": 15,
      "healthy": 11,
      "at_risk": 3,
      "critical": 1,
      "by_type": {
        "PIPELINE": 4,
        "ROAD": 3,
        "BRIDGE": 1,
        "FOOTPATH": 1,
        "STP": 1,
        "SEWAGE": 1,
        "DRAINAGE": 1,
        "FIRE_STATION": 3
      }
    },
    "warnings": {
      "critical": 0,
      "high": 1,
      "moderate": 0,
      "low": 0,
      "info": 0,
      "total_active": 1
    },
    "projects": {
      "ongoing": 3,
      "delayed": 0,
      "planned": 0,
      "completed": 1,
      "total": 4
    },
    "predictions": {
      "next_7_days": 1,
      "next_30_days": 1,
      "high_probability_failures": 1
    },
    "situation": {
      "city": "Pune",
      "overall_risk": "HIGH",
      "alert_level": "ELEVATED",
      "active_incidents": 1,
      "high_risk_zones": ["Shivaji Nagar Corridor", "Hinjawadi Phase 1", "Swargate Junction"]
    }
  }
  ```

---

## 3. Infrastructure Assets (`/api/assets`)

### `GET /api/assets`
- **Query Params:** `page`, `page_size`, `asset_type`, `status`, `min_risk`, `max_health`, `search`.
- **Response (200 OK):** List of assets matching filters.

### `GET /api/assets/{id}`
- **Param:** Internal integer ID or string asset code (e.g. `PUN-PIPE-001`).

### `GET /api/assets/{id}/health`
- **Description:** Returns explainable factor breakdown for asset health (0-100) and risk score (0-100).
- **Response (200 OK):**
  ```json
  {
    "asset_id": "PUN-PIPE-001",
    "name": "Parvati Water Works to Swargate Feeder Line",
    "asset_type": "PIPELINE",
    "health_score": 64.0,
    "risk_score": 72.0,
    "status": "CRITICAL",
    "condition": "Fair",
    "age_years": 14.5,
    "factors": [
      {
        "factor": "Physical Condition",
        "impact": "NEUTRAL",
        "description": "Visual inspection status: 'Fair' yields base score 68/100."
      },
      {
        "factor": "Sensor Anomaly Frequency",
        "impact": "HIGH",
        "description": "3 telemetry anomalies recorded in recent operating window."
      }
    ]
  }
  ```

### `GET /api/assets/nearby`
- **Query Params:** `lat=18.5204&lng=73.8567&radius=1500`

---

## 4. IoT Sensors & Ingestion (`/api/sensors`)

### `POST /api/sensors/readings`
- **Request Body:**
  ```json
  {
    "sensor_id": "WP-001",
    "value": 88.5,
    "unit": "psi",
    "quality": "GOOD"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "status": "success",
    "sensor_id": "WP-001",
    "reading_id": 42,
    "value": 88.5,
    "unit": "psi",
    "is_anomaly": true,
    "anomaly_score": 0.643,
    "warning_generated": true,
    "warning_id": 8,
    "asset_risk_score": 72.0
  }
  ```

---

## 5. Government Projects (`/api/projects`)

### `GET /api/projects/{id}`
- **Description:** Returns project details with verified officer attribution and nearby assets.
- **Response (200 OK):**
  ```json
  {
    "project_id": "PUN-METRO-L3",
    "name": "Pune Metro Line 3 (Hinjawadi to Shivajinagar Elevated Corridor)",
    "department": "Pune Metropolitan Region Development Authority (PMRDA)",
    "status": "ONGOING",
    "progress": 78.5,
    "officer": {
      "employee_id": "PMRDA-ENG-4021",
      "department": "PMRDA Transit Wing",
      "designation": "Executive Engineer (Metro Infrastructure)",
      "public_contact": "+91-20-2593-3300",
      "email": "sanjay.shinde@pmrda.gov.in"
    },
    "warnings": [],
    "nearby_assets_count": 4
  }
  ```

---

## 6. Commute Intelligence (`/api/commute`)

### `POST /api/commute/analyze`
- **Request Body:**
  ```json
  {
    "origin": "Hinjawadi",
    "destination": "Pune Station",
    "mode": "driving",
    "buffer_radius_meters": 1000.0
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "route": {
      "summary": "Hinjawadi to Pune Station via Pune Primary Arterial Network",
      "distance_meters": 21850.0,
      "duration_seconds": 2623.0,
      "start_coords": {"lat": 18.5913, "lng": 73.7389},
      "end_coords": {"lat": 18.5289, "lng": 73.8744}
    },
    "risk": {
      "level": "HIGH",
      "score": 67.0,
      "primary_concerns": [
        "Active infrastructure works on route: Pune Metro Line 3, Wakad-Hinjawadi Flyover.",
        "1 high-severity municipal warning(s) active in corridor."
      ]
    },
    "weather": {
      "location": "Pune",
      "temperature": 27.4,
      "rainfall": 2.5,
      "condition": "Scattered Showers",
      "risk": "MODERATE"
    },
    "projects": [...],
    "warnings": [...],
    "recommendations": [
      "Consider leaving 15-25 minutes earlier due to construction-related slowdowns.",
      "Follow designated PMC detour lanes and watch for heavy machinery near project zones."
    ]
  }
  ```

---

## 7. Citizen Chatbot (`/api/chat`)

### `POST /api/chat`
- **Request Body:**
  ```json
  {
    "message": "I want to go from Hinjawadi to Pune Station. What should I know?"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "response": "Commute Summary (Hinjawadi -> Pune Station):\n• Distance & Time: Approx. 21.9 km (43 mins via primary arterial road).\n• Overall Corridor Risk: HIGH\n• Weather Conditions: Scattered Showers, 27.4°C (Rainfall: 2.5 mm).\n\nActive Government Infrastructure Works on Route:\n  - Pune Metro Line 3 (PMRDA): 78% completed (Status: ONGOING).\n  - Wakad-Hinjawadi Flyover (PMC): 62% completed (Status: ONGOING).\n\nCitizen Precautions & Recommendations:\n• Allow an extra 15–20 minutes travel buffer due to ongoing works.\n• For road emergencies, contact PMC Smart City Helpline at 1800-1030-222.",
    "intent": "COMMUTE_QUERY",
    "conversation_id": "3b29db42-990a-4fb7-84ee-87612f00e991",
    "precautions": [...]
  }
  ```

---

## 8. WebSockets

- **`/ws/dashboard`**: Telemetry and warning broadcast channel.
- **`/ws/sensors`**: Live sensor stream channel.
