from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from app.models.project import GovernmentProject, ProjectStatus
from app.models.asset import InfrastructureAsset
from app.models.warning import Warning, WarningStatus
from app.utils.geo import haversine_distance, get_bounding_box


class ProjectService:
    """
    Project intelligence service providing project tracking, responsible officer attribution,
    and geospatial cross-referencing with adjacent municipal assets.
    """

    def get_project_with_details(self, db: Session, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve project details with verified officer attribution and adjacent infrastructure.
        """
        project = (
            db.query(GovernmentProject)
            .options(joinedload(GovernmentProject.officer), joinedload(GovernmentProject.warnings))
            .filter((GovernmentProject.project_id == project_id) | (GovernmentProject.id == int(project_id) if project_id.isdigit() else False))
            .first()
        )
        if not project:
            return None

        # Find nearby infrastructure assets (within 1000m)
        min_lat, max_lat, min_lon, max_lon = get_bounding_box(project.latitude, project.longitude, 1000.0)
        nearby_candidates = db.query(InfrastructureAsset).filter(
            InfrastructureAsset.latitude.between(min_lat, max_lat),
            InfrastructureAsset.longitude.between(min_lon, max_lon)
        ).all()

        nearby_assets = []
        for asset in nearby_candidates:
            dist = haversine_distance(project.latitude, project.longitude, asset.latitude, asset.longitude)
            if dist <= 1000.0:
                nearby_assets.append({
                    "asset_id": asset.asset_id,
                    "name": asset.name,
                    "asset_type": asset.asset_type.value,
                    "health_score": asset.health_score,
                    "risk_score": asset.risk_score,
                    "distance_meters": round(dist, 1)
                })

        return {
            "project": project,
            "nearby_assets": nearby_assets,
            "nearby_assets_count": len(nearby_assets),
        }

    def get_projects_nearby(self, db: Session, lat: float, lng: float, radius_meters: float = 2000.0) -> List[GovernmentProject]:
        """
        Geospatial radius search for government projects.
        """
        min_lat, max_lat, min_lon, max_lon = get_bounding_box(lat, lng, radius_meters)
        candidates = db.query(GovernmentProject).filter(
            GovernmentProject.latitude.between(min_lat, max_lat),
            GovernmentProject.longitude.between(min_lon, max_lon)
        ).all()

        results = []
        for proj in candidates:
            dist = haversine_distance(lat, lng, proj.latitude, proj.longitude)
            if dist <= radius_meters:
                results.append(proj)

        return results


project_service = ProjectService()
