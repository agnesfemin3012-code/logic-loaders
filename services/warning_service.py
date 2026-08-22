from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.warning import Warning, WarningSeverity, WarningStatus
from app.models.precaution import Precaution, TargetAudience, PrecautionPriority
from app.models.asset import InfrastructureAsset, AssetType, AssetStatus
from app.models.audit import AuditLog
from app.services.notification_service import notification_service
from app.core.logging import logger


class WarningService:
    """
    Automated Warning & Precaution Generation Engine.
    Translates detected anomalies, risk score surges, and environmental alerts
    into structured municipal warnings and role-targeted precautions.
    """

    async def create_warning_for_asset(
        self,
        db: Session,
        asset: InfrastructureAsset,
        warning_type: str,
        severity: WarningSeverity,
        title: str,
        description: str,
        trigger: str,
        recommended_action: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Warning:
        """
        Persist a warning in the database, attach standardized precautions, and broadcast.
        """
        warning = Warning(
            asset_id=asset.id,
            project_id=project_id,
            warning_type=warning_type,
            severity=severity,
            title=title,
            description=description,
            risk_score=asset.risk_score,
            trigger=trigger,
            recommended_action=recommended_action or "Initiate urgent engineering inspection and notify zonal division.",
            status=WarningStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        )
        db.add(warning)
        db.flush()

        # Generate role-specific precautions
        precautions = self._generate_precautions_for_warning(warning, asset)
        for p in precautions:
            db.add(p)

        # Update asset status
        if severity in (WarningSeverity.CRITICAL, WarningSeverity.HIGH):
            asset.status = AssetStatus.CRITICAL if severity == WarningSeverity.CRITICAL else AssetStatus.WARNING

        db.commit()
        db.refresh(warning)

        # Broadcast via WebSocket
        try:
            await notification_service.broadcast("NEW_WARNING", {
                "warning_id": warning.id,
                "asset_id": asset.asset_id,
                "asset_name": asset.name,
                "severity": warning.severity.value,
                "title": warning.title,
                "risk_score": warning.risk_score,
                "trigger": warning.trigger,
                "precautions_count": len(precautions)
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast warning over WS: {e}")

        return warning

    def _generate_precautions_for_warning(self, warning: Warning, asset: InfrastructureAsset) -> List[Precaution]:
        precautions = []
        is_crit = warning.severity == WarningSeverity.CRITICAL
        prio = PrecautionPriority.IMMEDIATE if is_crit else PrecautionPriority.HIGH

        if asset.asset_type in (AssetType.PIPELINE, AssetType.WATER_NETWORK):
            # Citizen
            precautions.append(Precaution(
                warning_id=warning.id,
                title="Possible Low Pressure / Water Supply Advisory",
                description="PMC water network maintenance underway. Citizens may experience minor pressure variations.",
                priority=PrecautionPriority.MEDIUM,
                action="Store sufficient water for essential needs; report any visible road surface water pooling to PMC helpline.",
                target_audience=TargetAudience.CITIZEN
            ))
            # Officer / Engineer
            precautions.append(Precaution(
                warning_id=warning.id,
                title="Immediate Pressure Valve & Feeder Inspection",
                description="Abnormal hydraulic pressure telemetry detected.",
                priority=prio,
                action="Dispatch field technician to verify pressure regulation station and inspect joint seals for leakage.",
                target_audience=TargetAudience.ENGINEER
            ))
            # Field Tech
            precautions.append(Precaution(
                warning_id=warning.id,
                title="Acoustic Leak Detection & Pressure Gauge Check",
                description="Inspect pipeline segment for structural fissure or air-pocket surges.",
                priority=prio,
                action="Check upstream booster valve, verify pressure transducer calibration, and check soil moisture.",
                target_audience=TargetAudience.FIELD_TECHNICIAN
            ))

        elif asset.asset_type in (AssetType.ROAD, AssetType.BRIDGE, AssetType.FOOTPATH):
            # Citizen
            precautions.append(Precaution(
                warning_id=warning.id,
                title="Commute Alert: Road Structural Caution",
                description="Elevated risk or ongoing repair observed near this route segment.",
                priority=PrecautionPriority.HIGH,
                action="Reduce vehicle speed, expect lane narrowing or diversions, and follow local traffic signage.",
                target_audience=TargetAudience.CITIZEN
            ))
            # Engineer
            precautions.append(Precaution(
                warning_id=warning.id,
                title="Structural Integrity & Load Inspection",
                description="Vibration / deformation indicators require engineering review.",
                priority=prio,
                action="Deploy structural engineer with ultrasonic testing tools to inspect deck slabs, bearings, and expansion joints.",
                target_audience=TargetAudience.ENGINEER
            ))

        elif asset.asset_type in (AssetType.DRAINAGE, AssetType.SEWAGE):
            # Citizen
            precautions.append(Precaution(
                warning_id=warning.id,
                title="Waterlogging & Overflow Hazard Warning",
                description="High drainage level / surcharge risk during active precipitation.",
                priority=PrecautionPriority.HIGH,
                action="Avoid walking or driving through standing water; do not open manholes.",
                target_audience=TargetAudience.CITIZEN
            ))
            # Field Tech
            precautions.append(Precaution(
                warning_id=warning.id,
                title="Suction & De-siltation Deployment",
                description="Culvert / main line obstruction detected.",
                priority=prio,
                action="Deploy jetting suction vehicle immediately to clear blockage at upstream chamber.",
                target_audience=TargetAudience.FIELD_TECHNICIAN
            ))
        else:
            # Generic
            precautions.append(Precaution(
                warning_id=warning.id,
                title="General Infrastructure Caution",
                description="Elevated risk metrics observed on this asset.",
                priority=PrecautionPriority.MEDIUM,
                action="Exercise caution in the vicinity and adhere to PMC advisory bulletins.",
                target_audience=TargetAudience.CITIZEN
            ))

        return precautions


warning_service = WarningService()
