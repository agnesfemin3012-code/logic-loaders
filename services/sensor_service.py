from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.sensor import Sensor, SensorReading, SensorStatus
from app.models.asset import InfrastructureAsset, AssetStatus
from app.models.warning import WarningSeverity
from app.ml.anomaly_detection import anomaly_detector
from app.ml.health_score import asset_health_engine
from app.services.warning_service import warning_service
from app.services.notification_service import notification_service
from app.core.logging import logger
from app.schemas.sensor import ReadingCreate, ReadingIngestResponse


class SensorService:
    """
    Sensor telemetry processing pipeline:
    Sensor Ingestion -> Validation -> Anomaly Detection -> Health & Risk Recalculation -> Warning Generation -> WebSocket Broadcast.
    """

    async def ingest_reading(self, db: Session, payload: ReadingCreate) -> ReadingIngestResponse:
        # 1. Lookup Sensor
        sensor = db.query(Sensor).filter(Sensor.sensor_id == payload.sensor_id).first()
        if not sensor:
            # Auto-register sensor if new device arrives in dev/demo mode
            sensor = Sensor(
                sensor_id=payload.sensor_id,
                sensor_type="WATER_PRESSURE",
                unit=payload.unit or "psi",
                status=SensorStatus.ONLINE,
                last_seen=datetime.now(timezone.utc)
            )
            db.add(sensor)
            db.commit()
            db.refresh(sensor)

        # 2. Retrieve recent history for statistical evaluation
        recent_readings = (
            db.query(SensorReading.value)
            .filter(SensorReading.sensor_id == sensor.sensor_id)
            .order_by(desc(SensorReading.timestamp))
            .limit(10)
            .all()
        )
        recent_values = [r[0] for r in reversed(recent_readings)]

        # 3. Detect Anomalies
        unit_str = payload.unit or sensor.unit
        eval_result = anomaly_detector.detect_single_reading(
            sensor_type=sensor.sensor_type.value if hasattr(sensor.sensor_type, "value") else str(sensor.sensor_type),
            current_value=payload.value,
            recent_values=recent_values
        )

        is_anomaly = eval_result["is_anomaly"]
        anomaly_score = eval_result["anomaly_score"]
        quality_str = "ANOMALOUS" if is_anomaly else (payload.quality or "GOOD")

        # 4. Save reading
        reading = SensorReading(
            sensor_id=sensor.sensor_id,
            timestamp=payload.timestamp or datetime.now(timezone.utc),
            value=payload.value,
            unit=unit_str,
            quality=quality_str,
            metadata_json=payload.metadata
        )
        db.add(reading)
        sensor.last_seen = datetime.now(timezone.utc)
        sensor.status = SensorStatus.WARNING if is_anomaly else SensorStatus.ONLINE

        warning_generated = False
        warning_id = None
        asset_risk = None

        # 5. If attached to an Infrastructure Asset, update health and risk
        if sensor.asset_id:
            asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == sensor.asset_id).first()
            if asset:
                # Count recent anomalies for this asset
                anom_count = db.query(SensorReading).join(Sensor).filter(
                    Sensor.asset_id == asset.id,
                    SensorReading.quality == "ANOMALOUS"
                ).count()
                if is_anomaly:
                    anom_count += 1

                # Recompute health score
                new_health, factors = asset_health_engine.compute_health_score(
                    asset_type=asset.asset_type,
                    condition=asset.condition,
                    age_years=asset.age,
                    recent_anomalies_count=anom_count
                )
                asset.health_score = new_health

                # Recompute composite risk score
                new_risk, risk_cat, risk_factors = asset_health_engine.compute_risk_score(
                    health_score=new_health,
                    criticality=asset.criticality,
                    recent_anomalies_count=anom_count,
                    active_anomaly_score=anomaly_score if is_anomaly else 0.0
                )
                asset.risk_score = new_risk
                asset_risk = new_risk

                # 6. Check Warning Generation
                if is_anomaly or new_risk >= 60.0:
                    severity = WarningSeverity.CRITICAL if (new_risk >= 80 or eval_result["severity"] == "CRITICAL") else WarningSeverity.HIGH
                    title = f"Possible Hydraulic / Pressure Anomaly on {asset.name}"
                    trigger = eval_result.get("trigger") or f"Asset risk elevated to {new_risk:.1f}/100"
                    
                    warning = await warning_service.create_warning_for_asset(
                        db=db,
                        asset=asset,
                        warning_type="PRESSURE_ANOMALY" if sensor.sensor_type.value == "WATER_PRESSURE" else "TELEMETRY_ANOMALY",
                        severity=severity,
                        title=title,
                        description=f"Sensor '{sensor.sensor_id}' recorded {payload.value:.1f} {unit_str}. {trigger}. Anomaly score: {anomaly_score:.2f}.",
                        trigger=trigger,
                        recommended_action="Inspect pipeline segment valves, joints, and adjacent service corridors."
                    )
                    warning_generated = True
                    warning_id = warning.id

                # Broadcast Asset update
                try:
                    await notification_service.broadcast("ASSET_TELEMETRY_UPDATE", {
                        "asset_id": asset.asset_id,
                        "health_score": asset.health_score,
                        "risk_score": asset.risk_score,
                        "status": asset.status.value,
                        "sensor_id": sensor.sensor_id,
                        "latest_value": payload.value,
                        "is_anomaly": is_anomaly
                    })
                except Exception as e:
                    logger.warning(f"Error broadcasting telemetry: {e}")

        db.commit()

        # Broadcast raw sensor reading
        try:
            await notification_service.broadcast("SENSOR_READING", {
                "sensor_id": sensor.sensor_id,
                "value": payload.value,
                "unit": unit_str,
                "is_anomaly": is_anomaly,
                "quality": quality_str
            })
        except Exception:
            pass

        return ReadingIngestResponse(
            status="success",
            sensor_id=sensor.sensor_id,
            reading_id=reading.id,
            value=payload.value,
            unit=unit_str,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            warning_generated=warning_generated,
            warning_id=warning_id,
            asset_risk_score=asset_risk
        )


sensor_service = SensorService()
