from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.ingestion.base import BaseIngestionAdapter
from app.models.sensor import Sensor, SensorType, DeviceType, SensorStatus
from app.models.asset import InfrastructureAsset


class SensorRegistryAdapter(BaseIngestionAdapter):
    """Ingests IoT sensor hardware registry deployed across Pune infrastructure."""

    def __init__(self):
        super().__init__(
            source_name="Pune Smart City IoT Telemetry Registry",
            source_url="https://punesmartcity.in/iot-registry"
        )

    def load_raw_data(self, filepath_or_url: Optional[str] = None) -> List[Dict[str, Any]]:
        return [
            {"sensor_id": "WP-001", "asset_id_code": "PUN-PIPE-001", "type": "WATER_PRESSURE", "unit": "psi", "device": "ARDUINO"},
            {"sensor_id": "FL-001", "asset_id_code": "PUN-PIPE-001", "type": "FLOW", "unit": "L/min", "device": "RASPBERRY_PI"},
            {"sensor_id": "WP-002", "asset_id_code": "PUN-PIPE-002", "type": "WATER_PRESSURE", "unit": "psi", "device": "ARDUINO"},
            {"sensor_id": "WP-003", "asset_id_code": "PUN-PIPE-003", "type": "WATER_PRESSURE", "unit": "psi", "device": "RASPBERRY_PI"},
            {"sensor_id": "WP-004", "asset_id_code": "PUN-PIPE-004", "type": "WATER_PRESSURE", "unit": "psi", "device": "ARDUINO"},
            {"sensor_id": "VIB-001", "asset_id_code": "PUN-BRG-001", "type": "VIBRATION", "unit": "mm/s", "device": "RASPBERRY_PI"},
            {"sensor_id": "STR-001", "asset_id_code": "PUN-BRG-001", "type": "STRAIN", "unit": "µε", "device": "ARDUINO"},
            {"sensor_id": "WL-001", "asset_id_code": "PUN-DRN-001", "type": "WATER_LEVEL", "unit": "m", "device": "ARDUINO"},
            {"sensor_id": "TMP-001", "asset_id_code": "PUN-STP-001", "type": "TEMPERATURE", "unit": "°C", "device": "RASPBERRY_PI"}
        ]

    def validate_and_normalize(self, r: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return r

    def persist_records(self, db: Session, records: List[Dict[str, Any]]) -> int:
        count = 0
        for data in records:
            asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.asset_id == data["asset_id_code"]).first()
            sensor = db.query(Sensor).filter(Sensor.sensor_id == data["sensor_id"]).first()
            if not sensor:
                sensor = Sensor(
                    sensor_id=data["sensor_id"],
                    asset_id=asset.id if asset else None,
                    sensor_type=SensorType(data["type"]),
                    device_type=DeviceType(data.get("device", "OTHER")),
                    unit=data["unit"],
                    status=SensorStatus.ONLINE,
                    latitude=asset.latitude if asset else 18.5204,
                    longitude=asset.longitude if asset else 73.8567,
                    installed_at=datetime.now(timezone.utc),
                    last_seen=datetime.now(timezone.utc)
                )
                db.add(sensor)
            else:
                if asset:
                    sensor.asset_id = asset.id
                sensor.status = SensorStatus.ONLINE
            count += 1

        db.commit()
        return count
