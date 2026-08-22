from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.asset import InfrastructureAsset
from app.models.project import GovernmentProject, ProjectStatus
from app.models.warning import Warning, WarningSeverity, WarningStatus
from app.schemas.commute import (
    CommuteAnalyzeRequest,
    CommuteAnalyzeResponse,
    RouteGeometry,
    CommuteRiskLevel,
)
from app.schemas.asset import AssetOut
from app.schemas.project import ProjectOut
from app.schemas.warning import WarningOut
from app.schemas.precaution import PrecautionOut
from app.services.maps_service import maps_service
from app.services.weather_service import weather_service
from app.utils.geo import is_point_near_polyline, haversine_distance


class CommuteService:
    """
    Pune Smart Commute Intelligence Engine.
    Combines route geometries, corridor spatial buffers, active infrastructure warnings,
    PMC government road/metro construction works, and meteorological alerts.
    """

    async def analyze_commute(self, db: Session, request: CommuteAnalyzeRequest) -> CommuteAnalyzeResponse:
        # 1. Route geometry from Maps Service
        route_data = await maps_service.get_route(
            origin=request.origin,
            destination=request.destination,
            mode=request.mode
        )
        coords = route_data.get("coordinates", [])

        # 2. Real-time Weather
        weather = await weather_service.get_current_weather()

        # 3. Retrieve Candidate Infrastructure Assets near route
        all_assets = db.query(InfrastructureAsset).all()
        near_assets: List[InfrastructureAsset] = []
        for asset in all_assets:
            if is_point_near_polyline(asset.latitude, asset.longitude, coords, buffer_meters=request.buffer_radius_meters):
                near_assets.append(asset)

        # 4. Retrieve Candidate Government Projects near route
        all_projects = db.query(GovernmentProject).filter(
            GovernmentProject.status.in_([ProjectStatus.ONGOING, ProjectStatus.DELAYED, ProjectStatus.UPCOMING])
        ).all()
        near_projects: List[GovernmentProject] = []
        for proj in all_projects:
            if is_point_near_polyline(proj.latitude, proj.longitude, coords, buffer_meters=request.buffer_radius_meters):
                near_projects.append(proj)

        # 5. Retrieve Active Warnings for Near Assets and Projects
        near_asset_ids = [a.id for a in near_assets]
        near_proj_ids = [p.id for p in near_projects]
        
        active_warnings = []
        if near_asset_ids or near_proj_ids:
            active_warnings = (
                db.query(Warning)
                .options(joinedload(Warning.precautions))
                .filter(
                    Warning.status.in_([WarningStatus.ACTIVE, WarningStatus.ACKNOWLEDGED]),
                    (Warning.asset_id.in_(near_asset_ids) if near_asset_ids else False) |
                    (Warning.project_id.in_(near_proj_ids) if near_proj_ids else False)
                )
                .all()
            )

        # 6. Calculate Composite Commute Risk Score
        risk_score = 15.0  # baseline clear commute
        concerns = []

        # Weather factor
        if weather.risk == "SEVERE":
            risk_score += 35.0
            concerns.append("Severe rainfall and potential road waterlogging in low-lying corridors.")
        elif weather.risk == "HIGH":
            risk_score += 20.0
            concerns.append("Heavy monsoon showers causing reduced visibility and wet road surfaces.")
        elif weather.risk == "MODERATE":
            risk_score += 10.0
            concerns.append("Scattered rainfall on the travel corridor.")

        # Construction projects factor
        if near_projects:
            risk_score += min(30.0, len(near_projects) * 12.0)
            proj_names = ", ".join([p.name for p in near_projects[:2]])
            concerns.append(f"Active infrastructure works on route: {proj_names}.")

        # Critical / High Warnings factor
        crit_warns = [w for w in active_warnings if w.severity in (WarningSeverity.CRITICAL, WarningSeverity.HIGH)]
        if crit_warns:
            risk_score += min(40.0, len(crit_warns) * 20.0)
            concerns.append(f"{len(crit_warns)} high-severity municipal warning(s) active in corridor.")

        risk_score = min(100.0, risk_score)

        if risk_score >= 75.0:
            risk_level = "CRITICAL"
        elif risk_score >= 50.0:
            risk_level = "HIGH"
        elif risk_score >= 25.0:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # 7. Generate Citizen Recommendations
        recommendations = []
        if risk_level in ("CRITICAL", "HIGH"):
            recommendations.append("Consider leaving 15-25 minutes earlier due to construction-related slowdowns.")
        if near_projects:
            recommendations.append("Follow designated PMC detour lanes and watch for heavy machinery near project zones.")
        if weather.rainfall > 5.0:
            recommendations.append("Drive with headlights on; maintain safe braking distance on wet tarmac.")
        if not recommendations:
            recommendations.append("Route conditions are clear with standard Pune peak-hour transit flow.")

        # 8. Assemble response schemas
        route_geom = RouteGeometry(
            summary=route_data["summary"],
            distance_meters=route_data["distance_meters"],
            duration_seconds=route_data["duration_seconds"],
            polyline=route_data.get("polyline"),
            start_address=route_data.get("start_address"),
            end_address=route_data.get("end_address"),
            start_coords=route_data["start_coords"],
            end_coords=route_data["end_coords"]
        )

        infra_out = [AssetOut.model_validate(a) for a in near_assets]
        proj_out = [ProjectOut.model_validate(p) for p in near_projects]
        warn_out = []
        for w in active_warnings:
            wo = WarningOut(
                id=w.id,
                asset_id=w.asset_id,
                project_id=w.project_id,
                warning_type=w.warning_type,
                severity=w.severity,
                title=w.title,
                description=w.description,
                risk_score=w.risk_score,
                trigger=w.trigger,
                recommended_action=w.recommended_action,
                status=w.status,
                created_at=w.created_at,
                acknowledged_by=w.acknowledged_by,
                acknowledged_at=w.acknowledged_at,
                precautions=[PrecautionOut.model_validate(p) for p in w.precautions]
            )
            warn_out.append(wo)

        return CommuteAnalyzeResponse(
            route=route_geom,
            risk=CommuteRiskLevel(
                level=risk_level,
                score=round(risk_score, 1),
                primary_concerns=concerns
            ),
            weather=weather,
            infrastructure=infra_out,
            projects=proj_out,
            warnings=warn_out,
            recommendations=recommendations,
            data_sources=["PMC OpenCity", "Google Maps Directions", "IMD Pune Weather", "SmartInfra IoT Network"]
        )


commute_service = CommuteService()
