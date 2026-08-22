from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.ingestion.base import BaseIngestionAdapter
from app.models.asset import InfrastructureAsset, AssetType, CriticalityLevel, AssetStatus
from app.models.sensor import Sensor, SensorType, DeviceType, SensorStatus
from app.ml.health_score import asset_health_engine
from app.utils.geo import point_to_wkt


class WaterLeaksAdapter(BaseIngestionAdapter):
    """Ingests Pune Water Supply Network and Historical Leak Incidents dataset."""

    def __init__(self):
        super().__init__(
            source_name="PMC Water Supply & Leakage Telemetry Registry",
            source_url="https://punecorporation.org/water-supply"
        )

    def load_raw_data(self, filepath_or_url: Optional[str] = None) -> List[Dict[str, Any]]:
        return [
            {
                "asset_id": "PUN-PIPE-001",
                "name": "Parvati Water Works to Swargate Feeder Line",
                "type": "PIPELINE",
                "lat": 18.4975,
                "lng": 73.8510,
                "condition": "Fair",
                "material": "Ductile Iron (DI) 900mm",
                "age": 14.5,
                "criticality": "CRITICAL",
                "sensors": [
                    {"sensor_id": "WP-001", "type": "WATER_PRESSURE", "unit": "psi", "device": "ARDUINO"},
                    {"sensor_id": "FL-001", "type": "FLOW", "unit": "L/min", "device": "RASPBERRY_PI"}
                ]
            },
            {
                "asset_id": "PUN-PIPE-002",
                "name": "Warje Water Treatment Plant - Kothrud Main",
                "type": "PIPELINE",
                "lat": 18.4812,
                "lng": 73.8015,
                "condition": "Good",
                "material": "Mild Steel (MS) 1200mm",
                "age": 8.0,
                "criticality": "HIGH",
                "sensors": [
                    {"sensor_id": "WP-002", "type": "WATER_PRESSURE", "unit": "psi", "device": "ARDUINO"}
                ]
            },
            {
                "asset_id": "PUN-PIPE-003",
                "name": "Cantonment Water Works - Camp & Station Feeder",
                "type": "PIPELINE",
                "lat": 18.5142,
                "lng": 73.8790,
                "condition": "Poor",
                "material": "Cast Iron (CI) 600mm",
                "age": 28.0,
                "criticality": "CRITICAL",
                "sensors": [
                    {"sensor_id": "WP-003", "type": "WATER_PRESSURE", "unit": "psi", "device": "RASPBERRY_PI"}
                ]
            },
            {
                "asset_id": "PUN-PIPE-004",
                "name": "Hinjawadi Phase 1 MIDC Industrial Water Feeder",
                "type": "PIPELINE",
                "lat": 18.5913,
                "lng": 73.7389,
                "condition": "Fair",
                "material": "HDPE 500mm",
                "age": 6.5,
                "criticality": "HIGH",
                "sensors": [
                    {"sensor_id": "WP-004", "type": "WATER_PRESSURE", "unit": "psi", "device": "ARDUINO"},
                    {"sensor_id": "FL-004", "type": "FLOW", "unit": "L/min", "device": "ARDUINO"}
                ]
            }
        ]

    def validate_and_normalize(self, r: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not r.get("asset_id"):
            return None
        return {
            "asset_id": str(r["asset_id"]),
            "name": str(r["name"]),
            "asset_type": AssetType.PIPELINE,
            "latitude": float(r["lat"]),
            "longitude": float(r["lng"]),
            "condition": str(r.get("condition", "Good")),
            "material": str(r.get("material", "Ductile Iron")),
            "age": float(r.get("age", 10.0)),
            "criticality": CriticalityLevel(r.get("criticality", "HIGH")),
            "sensors": r.get("sensors", []),
            "source": self.source_name,
            "source_url": self.source_url
        }

    def persist_records(self, db: Session, records: List[Dict[str, Any]]) -> int:
        count = 0
        for data in records:
            asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.asset_id == data["asset_id"]).first()
            if not asset:
                asset = InfrastructureAsset(
                    asset_id=data["asset_id"],
                    name=data["name"],
                    asset_type=data["asset_type"],
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    geometry_wkt=point_to_wkt(data["latitude"], data["longitude"]),
                    condition=data["condition"],
                    material=data["material"],
                    age=data["age"],
                    criticality=data["criticality"],
                    source=data["source"],
                    source_url=data["source_url"]
                )
                db.add(asset)
                db.flush()
            else:
                asset.name = data["name"]
                asset.condition = data["condition"]
                asset.age = data["age"]
                asset.criticality = data["criticality"]

            health, _ = asset_health_engine.compute_health_score(asset.asset_type, asset.condition, asset.age)
            risk, _, _ = asset_health_engine.compute_risk_score(health, asset.criticality)
            asset.health_score = health
            asset.risk_score = risk

            # Register attached sensors
            for s in data.get("sensors", []):
                sensor = db.query(Sensor).filter(Sensor.sensor_id == s["sensor_id"]).first()
                if not sensor:
                    sensor = Sensor(
                        sensor_id=s["sensor_id"],
                        asset_id=asset.id,
                        sensor_type=SensorType(s.get("type", "WATER_PRESSURE")),
                        device_type=DeviceType(s.get("device", "ARDUINO")),
                        unit=s.get("unit", "psi"),
                        status=SensorStatus.ONLINE,
                        latitude=asset.latitude,
                        longitude=asset.longitude,
                        installed_at=datetime.now(timezone.utc),
                        last_seen=datetime.now(timezone.utc)
                    )
                    db.add(sensor)

            count += 1

        db.commit()
        return count
