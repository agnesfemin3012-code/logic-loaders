import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class SensorType(str, enum.Enum):
    WATER_PRESSURE = "WATER_PRESSURE"
    FLOW = "FLOW"
    VIBRATION = "VIBRATION"
    STRAIN = "STRAIN"
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    RAINFALL = "RAINFALL"
    WATER_LEVEL = "WATER_LEVEL"
    OTHER = "OTHER"


class DeviceType(str, enum.Enum):
    ARDUINO = "ARDUINO"
    RASPBERRY_PI = "RASPBERRY_PI"
    ESP32 = "ESP32"
    INDUSTRIAL_IOT = "INDUSTRIAL_IOT"
    OTHER = "OTHER"


class SensorStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    WARNING = "WARNING"
    FAULTY = "FAULTY"


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), unique=True, index=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id", ondelete="CASCADE"), nullable=True, index=True)
    sensor_type = Column(Enum(SensorType), nullable=False, index=True)
    device_type = Column(Enum(DeviceType), default=DeviceType.OTHER, nullable=False)
    unit = Column(String(50), nullable=False)  # e.g., "psi", "L/min", "mm/s", "°C", "mm"
    status = Column(Enum(SensorStatus), default=SensorStatus.ONLINE, nullable=False)
    
    installed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    asset = relationship("InfrastructureAsset", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan", order_by="desc(SensorReading.timestamp)")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), ForeignKey("sensors.sensor_id", ondelete="CASCADE"), index=True, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    quality = Column(String(50), default="GOOD", nullable=False)  # GOOD, ANOMALOUS, SUSPICIOUS, CALIBRATION
    metadata_json = Column(JSON, nullable=True)

    # Relationships
    sensor = relationship("Sensor", back_populates="readings")

    __table_args__ = (
        Index("idx_sensor_reading_time", "sensor_id", "timestamp"),
    )
