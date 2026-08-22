"""
Smart City Predictive Infrastructure Maintenance - ML Training Pipeline
========================================================================
This module generates simulated hackathon datasets, builds preprocessing
pipelines, trains RandomForest models for delay and risk prediction,
evaluates metrics (MAE, RMSE, R2, Accuracy, F1), and serializes models.

Note: Dataset generated here is synthetic / simulated data for Smart City
hackathon demonstration and does not claim to be actual municipal sensor data.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DATA_PATH = DATA_DIR / "smart_city_data.csv"
DELAY_MODEL_PATH = MODELS_DIR / "smart_city_delay_model.pkl"
RISK_MODEL_PATH = MODELS_DIR / "smart_city_risk_model.pkl"

PROJECT_TYPES = [
    "Road Construction",
    "Metro Rail",
    "Bridge Repair",
    "Drainage Maintenance",
    "Pipeline Work",
    "Flyover Construction"
]

CONSTRUCTION_ACTIVITIES = [
    "Paving & Resurfacing",
    "Viaduct Segment Launching",
    "Excavation & Trenching",
    "Manhole Rehabilitation",
    "Desilting & Clearing",
    "Structural Pier Retrofit",
    "Signal & Junction Works"
]

def generate_synthetic_dataset(num_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic smart city infrastructure dataset.
    Follows urban planning physics and empirical delay factors.
    """
    np.random.seed(random_seed)
    
    project_ids = [f"PRJ-{1000 + i}" for i in range(num_samples)]
    
    # Pune / Smart city approximate bounds
    latitudes = np.random.uniform(18.45, 18.65, size=num_samples).round(4)
    longitudes = np.random.uniform(73.72, 73.96, size=num_samples).round(4)
    
    project_types = np.random.choice(PROJECT_TYPES, size=num_samples, p=[0.30, 0.20, 0.15, 0.15, 0.10, 0.10])
    activities = np.random.choice(CONSTRUCTION_ACTIVITIES, size=num_samples)
    
    planned_durations = np.random.choice([30, 45, 60, 90, 120, 180, 240, 365], size=num_samples)
    current_progresses = np.random.uniform(5, 95, size=num_samples).round(1)
    
    traffic_volumes = np.random.normal(950, 350, size=num_samples).clip(200, 2500).astype(int)
    average_speeds = (65 - (traffic_volumes / 2500) * 45 + np.random.normal(0, 4, size=num_samples)).clip(8, 60).round(1)
    
    rainfalls = np.random.exponential(scale=12.0, size=num_samples).clip(0, 140).round(1)
    temperatures = np.random.normal(28, 5, size=num_samples).clip(16, 42).round(1)
    humidities = (50 + (rainfalls * 0.35) + np.random.normal(0, 8, size=num_samples)).clip(25, 98).round(1)
    
    # Road condition: 1 (Excellent) to 5 (Severely Degraded)
    road_conditions = np.random.choice([1, 2, 3, 4, 5], size=num_samples, p=[0.15, 0.30, 0.30, 0.15, 0.10])
    workers_available = np.random.normal(25, 12, size=num_samples).clip(4, 90).astype(int)
    previous_delays = np.random.exponential(scale=4.0, size=num_samples).clip(0, 40).astype(int)
    nearby_projects = np.random.choice([0, 1, 2, 3, 4, 5], size=num_samples, p=[0.35, 0.30, 0.20, 0.10, 0.04, 0.01])
    
    # -------------------------------------------------------------
    # Domain equation for realistic delay calculation (ground truth):
    # -------------------------------------------------------------
    traffic_factor = (traffic_volumes / 1000) * (30 / np.maximum(average_speeds, 10)) * 2.2
    weather_factor = (rainfalls / 20) * (humidities / 80) * 3.0
    road_factor = (road_conditions - 1) * 1.5
    labor_deficit = np.maximum(0, (planned_durations / 10) - workers_available) * 0.35
    history_factor = previous_delays * 0.4
    nearby_factor = nearby_projects * 0.8
    
    # Expected progress vs actual progress discrepancy
    expected_progress = (planned_durations / 100.0) * np.random.uniform(0.8, 1.2, size=num_samples)
    progress_lag = np.maximum(0, (50 - current_progresses) * 0.1)
    
    noise = np.random.normal(0, 1.5, size=num_samples)
    
    raw_delay = (
        traffic_factor
        + weather_factor
        + road_factor
        + labor_deficit
        + history_factor
        + nearby_factor
        + progress_lag
        + noise
    )
    predicted_delay_days = np.maximum(0, raw_delay).round().astype(int)
    actual_durations = planned_durations + predicted_delay_days
    predicted_completion_days = actual_durations
    
    # Project status mapping
    statuses = []
    for delay in predicted_delay_days:
        if delay > 12:
            statuses.append("Delayed")
        elif delay > 0:
            statuses.append("In Progress")
        else:
            statuses.append(np.random.choice(["In Progress", "Completed", "Planned"], p=[0.7, 0.2, 0.1]))
            
    # Risk Classification (LOW, MEDIUM, HIGH, CRITICAL)
    # Composite risk score: 0 to 100
    composite_risk_score = (
        (traffic_volumes / 2500) * 25
        + (rainfalls / 140) * 25
        + ((road_conditions - 1) / 4) * 20
        + (np.minimum(predicted_delay_days, 30) / 30) * 20
        + (nearby_projects / 5) * 10
    ) * 100 / 100
    
    risk_levels = []
    for score in composite_risk_score:
        if score >= 68 or (score >= 50 and np.random.rand() > 0.65):
            risk_levels.append("CRITICAL")
        elif score >= 48:
            risk_levels.append("HIGH")
        elif score >= 28:
            risk_levels.append("MEDIUM")
        else:
            risk_levels.append("LOW")
            
    df = pd.DataFrame({
        "project_id": project_ids,
        "latitude": latitudes,
        "longitude": longitudes,
        "project_type": project_types,
        "project_status": statuses,
        "planned_duration": planned_durations,
        "current_progress": current_progresses,
        "traffic_volume": traffic_volumes,
        "average_speed": average_speeds,
        "rainfall": rainfalls,
        "temperature": temperatures,
        "humidity": humidities,
        "road_condition": road_conditions,
        "workers_available": workers_available,
        "previous_delay": previous_delays,
        "construction_activity": activities,
        "nearby_projects": nearby_projects,
        "actual_duration": actual_durations,
        "predicted_delay_days": predicted_delay_days,
        "predicted_completion_days": predicted_completion_days,
        "infrastructure_risk": risk_levels
    })
    
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes derived interaction features for ML models.
    """
    data = df.copy()
    data["traffic_congestion_index"] = data["traffic_volume"] / (data["average_speed"] + 1.0)
    data["weather_severity_index"] = data["rainfall"] * (data["humidity"] / 100.0)
    data["labor_density"] = data["workers_available"] / (data["planned_duration"] + 1.0)
    data["progress_rate"] = data["current_progress"] / (data["planned_duration"] + 1.0)
    return data

def build_preprocessing_pipeline(categorical_cols, numerical_cols):
    """
    Creates a scikit-learn ColumnTransformer for numerical and categorical preprocessing.
    """
    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, numerical_cols),
            ("cat", cat_transformer, categorical_cols)
        ]
    )
    return preprocessor

def train_models():
    """
    Executes the complete training pipeline:
    1. Loads or generates dataset.
    2. Performs feature engineering.
    3. Builds training pipelines for Delay Regressor and Risk Classifier.
    4. Evaluates performance metrics.
    5. Saves serialized models with joblib.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=================================================================")
    print("   Smart City Infrastructure AI - Model Training Pipeline        ")
    print("=================================================================")
    
    # 1. Load or generate dataset
    if not DATA_PATH.exists():
        print(f"[+] Dataset not found at {DATA_PATH}. Generating 1,500 synthetic samples...")
        df = generate_synthetic_dataset(num_samples=1500)
        df.to_csv(DATA_PATH, index=False)
        print(f"[✓] Dataset successfully generated and saved to {DATA_PATH}")
    else:
        print(f"[+] Loading dataset from {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH)
        
    print(f"    Total records: {len(df)}")
    print(f"    Columns: {list(df.columns)}")
    
    # 2. Feature Engineering
    df_feat = feature_engineering(df)
    
    categorical_features = ["project_type"]
    numerical_features = [
        "planned_duration",
        "current_progress",
        "traffic_volume",
        "average_speed",
        "rainfall",
        "temperature",
        "humidity",
        "road_condition",
        "workers_available",
        "previous_delay",
        "traffic_congestion_index",
        "weather_severity_index",
        "labor_density",
        "progress_rate"
    ]
    
    # Features matrix X
    X = df_feat[categorical_features + numerical_features]
    
    # Targets
    y_delay = df_feat["predicted_delay_days"]
    y_risk = df_feat["infrastructure_risk"]
    
    # 3. Train / Test Split
    X_train, X_test, y_del_train, y_del_test, y_risk_train, y_risk_test = train_test_split(
        X, y_delay, y_risk, test_size=0.20, random_state=42
    )
    
    print(f"\n[+] Training Set: {len(X_train)} samples | Test Set: {len(X_test)} samples")
    
    # -------------------------------------------------------------
    # 4. Train Delay Regressor Model (RandomForestRegressor)
    # -------------------------------------------------------------
    print("\n[+] Training Delay Prediction Regressor (RandomForestRegressor)...")
    delay_preprocessor = build_preprocessing_pipeline(categorical_features, numerical_features)
    delay_pipeline = Pipeline(steps=[
        ("preprocessor", delay_preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    delay_pipeline.fit(X_train, y_del_train)
    y_del_pred = delay_pipeline.predict(X_test)
    
    mae = mean_absolute_error(y_del_test, y_del_pred)
    rmse = np.sqrt(mean_squared_error(y_del_test, y_del_pred))
    r2 = r2_score(y_del_test, y_del_pred)
    
    print("\n--- Delay Prediction Model Evaluation ---")
    print(f"    Mean Absolute Error (MAE)  : {mae:.2f} days")
    print(f"    Root Mean Squared Error    : {rmse:.2f} days")
    print(f"    R² Score                   : {r2:.4f} ({r2*100:.1f}%)")
    
    # -------------------------------------------------------------
    # 5. Train Infrastructure Risk Classifier (RandomForestClassifier)
    # -------------------------------------------------------------
    print("\n[+] Training Infrastructure Risk Classifier (RandomForestClassifier)...")
    risk_preprocessor = build_preprocessing_pipeline(categorical_features, numerical_features)
    risk_pipeline = Pipeline(steps=[
        ("preprocessor", risk_preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=150, max_depth=10, class_weight="balanced", random_state=42, n_jobs=-1))
    ])
    
    risk_pipeline.fit(X_train, y_risk_train)
    y_risk_pred = risk_pipeline.predict(X_test)
    
    acc = accuracy_score(y_risk_test, y_risk_pred)
    prec = precision_score(y_risk_test, y_risk_pred, average="weighted", zero_division=0)
    rec = recall_score(y_risk_test, y_risk_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_risk_test, y_risk_pred, average="weighted", zero_division=0)
    
    print("\n--- Infrastructure Risk Model Evaluation ---")
    print(f"    Accuracy                   : {acc:.4f} ({acc*100:.1f}%)")
    print(f"    Precision (weighted)       : {prec:.4f}")
    print(f"    Recall (weighted)          : {rec:.4f}")
    print(f"    F1-Score (weighted)        : {f1:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_risk_test, y_risk_pred, digits=3))
    
    # -------------------------------------------------------------
    # 6. Save Model Artifacts
    # -------------------------------------------------------------
    print(f"[+] Serializing trained models to {MODELS_DIR}...")
    joblib.dump(delay_pipeline, DELAY_MODEL_PATH)
    joblib.dump(risk_pipeline, RISK_MODEL_PATH)
    print(f"    [✓] Delay Model saved: {DELAY_MODEL_PATH}")
    print(f"    [✓] Risk Model saved : {RISK_MODEL_PATH}")
    
    # Verification test with Hackathon Demo Scenario
    print("\n=================================================================")
    print("   Verifying Hackathon Demo Scenario: 'Road Expansion – Zone A'  ")
    print("=================================================================")
    sample_input = pd.DataFrame([{
        "project_type": "Road Construction",
        "planned_duration": 60,
        "current_progress": 55.0,
        "traffic_volume": 1120,
        "average_speed": 19.0,
        "rainfall": 8.0,
        "temperature": 27.0,
        "humidity": 80.0,
        "road_condition": 3,
        "workers_available": 18,
        "previous_delay": 5
    }])
    sample_feat = feature_engineering(sample_input)
    sample_X = sample_feat[categorical_features + numerical_features]
    
    pred_delay = delay_pipeline.predict(sample_X)[0]
    pred_risk = risk_pipeline.predict(sample_X)[0]
    
    print(f"Input: Traffic=1120 v/h, Speed=19 km/h, Rain=8 mm, Progress=55%, Workers=18, Planned=60d")
    print(f"Prediction -> Delay: {round(pred_delay)} days | Est. Completion: {60 + round(pred_delay)} days | Risk: {pred_risk}")
    print("=================================================================\n")

if __name__ == "__main__":
    train_models()
