from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.asset import InfrastructureAsset, AssetType, AssetStatus, CriticalityLevel
from app.models.user import UserRole
from app.schemas.asset import AssetCreate, AssetOut, AssetHealthOut, AssetHealthFactor
from app.ml.health_score import asset_health_engine
from app.utils.geo import haversine_distance, get_bounding_box, point_to_wkt
from app.api.deps import require_roles

router = APIRouter(prefix="/assets", tags=["Infrastructure Assets"])


@router.get("", response_model=List[AssetOut], summary="List infrastructure assets with filtering & pagination")
def get_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    min_risk: Optional[float] = Query(None, ge=0.0, le=100.0),
    max_health: Optional[float] = Query(None, ge=0.0, le=100.0),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve paginated infrastructure assets with flexible filtering criteria."""
    query = db.query(InfrastructureAsset)

    if asset_type:
        query = query.filter(InfrastructureAsset.asset_type == asset_type)
    if status:
        query = query.filter(InfrastructureAsset.status == status)
    if min_risk is not None:
        query = query.filter(InfrastructureAsset.risk_score >= min_risk)
    if max_health is not None:
        query = query.filter(InfrastructureAsset.health_score <= max_health)
    if search:
        query = query.filter(
            InfrastructureAsset.name.ilike(f"%{search}%") |
            InfrastructureAsset.asset_id.ilike(f"%{search}%") |
            InfrastructureAsset.description.ilike(f"%{search}%")
        )

    offset = (page - 1) * page_size
    assets = query.order_by(InfrastructureAsset.risk_score.desc()).offset(offset).limit(page_size).all()
    return assets


@router.get("/nearby", response_model=List[AssetOut], summary="Find assets within geographical radius")
def get_nearby_assets(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude (e.g. 18.5204)"),
    lng: float = Query(..., ge=-180.0, le=180.0, description="Longitude (e.g. 73.8567)"),
    radius: float = Query(1000.0, ge=50.0, le=50000.0, description="Radius in meters"),
    asset_type: Optional[AssetType] = None,
    min_risk: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Spatial proximity search for infrastructure assets within specified radius in meters."""
    min_lat, max_lat, min_lon, max_lon = get_bounding_box(lat, lng, radius)
    query = db.query(InfrastructureAsset).filter(
        InfrastructureAsset.latitude.between(min_lat, max_lat),
        InfrastructureAsset.longitude.between(min_lon, max_lon)
    )

    if asset_type:
        query = query.filter(InfrastructureAsset.asset_type == asset_type)
    if min_risk is not None:
        query = query.filter(InfrastructureAsset.risk_score >= min_risk)

    candidates = query.all()
    results = []
    for asset in candidates:
        dist = haversine_distance(lat, lng, asset.latitude, asset.longitude)
        if dist <= radius:
            results.append(asset)

    results.sort(key=lambda a: haversine_distance(lat, lng, a.latitude, a.longitude))
    return results


@router.get("/{id}", response_model=AssetOut, summary="Get asset by ID or asset_id code")
def get_asset_by_id(id: str, db: Session = Depends(get_db)):
    """Retrieve single asset by internal integer ID or PMC asset code (e.g., 'PUN-PIPE-001')."""
    asset = None
    if id.isdigit():
        asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == int(id)).first()
    if not asset:
        asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.asset_id == id).first()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset '{id}' not found.")
    return asset


@router.get("/{id}/health", response_model=AssetHealthOut, summary="Get explainable health score breakdown")
def get_asset_health_breakdown(id: str, db: Session = Depends(get_db)):
    """Retrieve asset health, risk score, and detailed explainability breakdown factors."""
    asset = None
    if id.isdigit():
        asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == int(id)).first()
    if not asset:
        asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.asset_id == id).first()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset '{id}' not found.")

    health_score, factors = asset_health_engine.compute_health_score(
        asset_type=asset.asset_type,
        condition=asset.condition,
        age_years=asset.age,
        recent_anomalies_count=len([s for s in asset.sensors if s.status.value == "WARNING"])
    )

    factors_out = [
        AssetHealthFactor(
            factor=f["factor"],
            impact=f["impact"],
            description=f["description"]
        ) for f in factors
    ]

    return AssetHealthOut(
        asset_id=asset.asset_id,
        name=asset.name,
        asset_type=asset.asset_type,
        health_score=asset.health_score,
        risk_score=asset.risk_score,
        status=asset.status,
        condition=asset.condition,
        age_years=asset.age,
        factors=factors_out
    )


@router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED, summary="Create new asset", dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.OFFICER, UserRole.ENGINEER]))])
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    """Register a new infrastructure asset in the municipal inventory."""
    existing = db.query(InfrastructureAsset).filter(InfrastructureAsset.asset_id == payload.asset_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset ID '{payload.asset_id}' already exists.")

    asset = InfrastructureAsset(
        asset_id=payload.asset_id,
        name=payload.name,
        asset_type=payload.asset_type,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        geometry_wkt=point_to_wkt(payload.latitude, payload.longitude),
        installation_date=payload.installation_date,
        material=payload.material,
        age=payload.age,
        criticality=payload.criticality,
        condition=payload.condition,
        source=payload.source,
        source_url=payload.source_url
    )

    # Initial score calculation
    health, _ = asset_health_engine.compute_health_score(asset.asset_type, asset.condition, asset.age)
    risk, _, _ = asset_health_engine.compute_risk_score(health, asset.criticality)
    asset.health_score = health
    asset.risk_score = risk

    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
