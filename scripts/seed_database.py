import os
import sys
from datetime import datetime, timezone, timedelta

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.officer import Officer
from app.models.asset import InfrastructureAsset, AssetType, CriticalityLevel, AssetStatus
from app.models.sensor import Sensor, SensorReading, SensorType, DeviceType, SensorStatus
from app.models.project import GovernmentProject, ProjectStatus
from app.models.warning import Warning, WarningSeverity, WarningStatus
from app.models.precaution import Precaution, TargetAudience, PrecautionPriority
from app.models.prediction import Prediction, PredictionType
from app.models.maintenance import WorkOrder, WorkOrderStatus, WorkOrderPriority
from app.ingestion.opencity import OpenCityRoadsAdapter, OpenCitySewageAdapter, OpenCityFireStationsAdapter
from app.ingestion.water_leaks import WaterLeaksAdapter
from app.ingestion.government_projects import GovernmentProjectsAdapter
from app.ingestion.sensors import SensorRegistryAdapter
from app.core.logging import logger


def seed_database():
    """Seed comprehensive demo database for SmartInfra AI Pune."""
    logger.info("Initializing database schema...")
    init_db()
    db = SessionLocal()

    try:
        # 1. Create Demo Users
        users_data = [
            ("Admin User", "admin@smartinfra.pune.gov.in", "admin123", UserRole.ADMIN, "+91-20-2550-0001"),
            ("Officer Rajesh Patil", "officer.patil@punecorporation.org", "officer123", UserRole.OFFICER, "+91-20-2550-1100"),
            ("Engineer Sneha Deshmukh", "sneha.eng@punecorporation.org", "engineer123", UserRole.ENGINEER, "+91-20-2550-1205"),
            ("Tech Anil Shinde", "anil.field@punecorporation.org", "tech123", UserRole.FIELD_TECHNICIAN, "+91-98220-44550"),
            ("Citizen Rahul Sharma", "rahul.sharma@example.com", "citizen123", UserRole.CITIZEN, "+91-98900-11223"),
        ]

        user_map = {}
        for name, email, pwd, role, phone in users_data:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    name=name,
                    email=email,
                    password_hash=hash_password(pwd),
                    role=role,
                    phone=phone,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(user)
                db.flush()
            user_map[role] = user

        logger.info(f"Users verified/seeded: {len(user_map)}")

        # 2. Run Dataset Ingestion Adapters
        logger.info("Running municipal dataset ingestion adapters...")
        OpenCityRoadsAdapter().run(db)
        OpenCitySewageAdapter().run(db)
        OpenCityFireStationsAdapter().run(db)
        WaterLeaksAdapter().run(db)
        GovernmentProjectsAdapter().run(db)
        SensorRegistryAdapter().run(db)

        # 3. Create Seed Active Warning & Precaution for Hackathon Demo
        pipe_asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.asset_id == "PUN-PIPE-001").first()
        if pipe_asset:
            pipe_asset.health_score = 64.0
            pipe_asset.risk_score = 72.0
            pipe_asset.status = AssetStatus.CRITICAL

            existing_w = db.query(Warning).filter(Warning.asset_id == pipe_asset.id).first()
            if not existing_w:
                warn = Warning(
                    asset_id=pipe_asset.id,
                    warning_type="PRESSURE_ANOMALY",
                    severity=WarningSeverity.HIGH,
                    title="Abnormal Hydraulic Pressure Surge on Parvati-Swargate Feeder",
                    description="Sensor WP-001 telemetry recorded sustained 84.6 PSI pressure spike exceeding safety baseline (60 PSI).",
                    risk_score=72.0,
                    trigger="Pressure surge > 80 PSI detected by IoT telemetry node.",
                    recommended_action="Dispatch emergency maintenance technician to inspect pressure-reducing valve station at Parvati reservoir junction.",
                    status=WarningStatus.ACTIVE,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(warn)
                db.flush()

                # Precautions
                db.add(Precaution(
                    warning_id=warn.id,
                    title="Citizen Water Supply Advisory",
                    description="Pressure regulation underway. Minor supply fluctuations possible in Swargate / Parvati zones.",
                    priority=PrecautionPriority.MEDIUM,
                    action="Store sufficient water for domestic use; report surface water logging to PMC helpline 1800-1030-222.",
                    target_audience=TargetAudience.CITIZEN
                ))
                db.add(Precaution(
                    warning_id=warn.id,
                    title="Zonal Engineer Inspection Order",
                    description="Hydraulic pressure anomaly indicates potential joint stress.",
                    priority=PrecautionPriority.HIGH,
                    action="Verify telemetry sensor calibration, examine pressure release valve PRV-04, and inspect conduit chamber.",
                    target_audience=TargetAudience.ENGINEER
                ))
                db.add(Precaution(
                    warning_id=warn.id,
                    title="Field Technician Valve Check",
                    description="Physical valve actuation required.",
                    priority=PrecautionPriority.IMMEDIATE,
                    action="Inspect valve spindle, check acoustic leak logger readings, and verify bypass regulator status.",
                    target_audience=TargetAudience.FIELD_TECHNICIAN
                ))

                # Create associated Work Order
                wo = WorkOrder(
                    asset_id=pipe_asset.id,
                    warning_id=warn.id,
                    assigned_to=user_map.get(UserRole.FIELD_TECHNICIAN).id if user_map.get(UserRole.FIELD_TECHNICIAN) else None,
                    priority=WorkOrderPriority.HIGH,
                    description="Inspect and adjust PRV-04 at Parvati Water Works feeder line following 84.6 PSI surge.",
                    status=WorkOrderStatus.ASSIGNED,
                    due_date=datetime.now(timezone.utc) + timedelta(days=1),
                    created_at=datetime.now(timezone.utc)
                )
                db.add(wo)

                # Seed ML Prediction
                pred = Prediction(
                    asset_id=pipe_asset.id,
                    prediction_type=PredictionType.FAILURE,
                    probability=0.74,
                    confidence=0.82,
                    predicted_failure_window="Within 14 days",
                    estimated_rul_min=1.2,
                    estimated_rul_max=2.5,
                    model_version="v1.0-reliability-heuristic-ml",
                    features={"health_score": 64.0, "risk_score": 72.0, "pressure_spike_count": 3},
                    explanation=[
                        {"factor": "Pressure anomaly frequency", "impact": "HIGH", "detail": "3 pressure spikes recorded in 48h."},
                        {"factor": "Asset Age (14.5 years)", "impact": "MEDIUM", "detail": "DI pipe approaching mid-life fatigue."}
                    ],
                    created_at=datetime.now(timezone.utc)
                )
                db.add(pred)

        db.commit()
        logger.info("Database successfully seeded with demo users, assets, projects, warnings, and predictions!")

    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
