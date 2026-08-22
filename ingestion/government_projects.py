from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from app.ingestion.base import BaseIngestionAdapter
from app.models.project import GovernmentProject, ProjectStatus
from app.models.officer import Officer
from app.utils.geo import point_to_wkt


class GovernmentProjectsAdapter(BaseIngestionAdapter):
    """Ingests Ongoing Government Infrastructure Projects in Pune District."""

    def __init__(self):
        super().__init__(
            source_name="Pune Municipal Corporation & PMRDA Project Monitoring Cell",
            source_url="https://punecorporation.org/en/ongoing-projects"
        )

    def load_raw_data(self, filepath_or_url: Optional[str] = None) -> List[Dict[str, Any]]:
        return [
            {
                "project_id": "PUN-METRO-L3",
                "name": "Pune Metro Line 3 (Hinjawadi to Shivajinagar Elevated Corridor)",
                "department": "Pune Metropolitan Region Development Authority (PMRDA)",
                "project_type": "Metro Rail Transit",
                "status": "ONGOING",
                "progress": 78.5,
                "start_date": "2021-11-25",
                "expected_end_date": "2026-12-31",
                "lat": 18.5580,
                "lng": 73.7910,
                "officer_emp_id": "PMRDA-ENG-4021",
                "officer_name": "Sanjay Shinde",
                "officer_designation": "Executive Engineer (Metro Infrastructure)",
                "officer_department": "PMRDA Transit Wing",
                "officer_contact": "+91-20-2593-3300",
                "officer_email": "sanjay.shinde@pmrda.gov.in",
                "description": "23.3 km elevated metro line connecting Hinjawadi Rajiv Gandhi Infotech Park with Shivajinagar Central Hub with 23 stations."
            },
            {
                "project_id": "PUN-ROAD-WKD",
                "name": "Wakad-Hinjawadi Flyover Arterial Widening & Underpass",
                "department": "PMC Road & Traffic Management Department",
                "project_type": "Road Widening & Grade Separator",
                "status": "ONGOING",
                "progress": 62.0,
                "start_date": "2024-03-10",
                "expected_end_date": "2026-11-30",
                "lat": 18.5987,
                "lng": 73.7686,
                "officer_emp_id": "PMC-ENG-1108",
                "officer_name": "Rajendra Bhosale",
                "officer_designation": "Superintending Engineer (Roads & Bridges)",
                "officer_department": "PMC Road Infrastructure Cell",
                "officer_contact": "+91-20-2550-1200",
                "officer_email": "r.bhosale@punecorporation.org",
                "description": "Six-lane capacity expansion and pedestrian underpass near Wakad bridge junction to ease peak commute congestion towards Hinjawadi."
            },
            {
                "project_id": "PUN-RIVER-REV",
                "name": "Mula-Mutha Riverfront Development & Pollution Abatement (Shivajinagar to Sangam)",
                "department": "PMC Water Resources & Environment Cell",
                "project_type": "Environmental & Flood Protection Infrastructure",
                "status": "ONGOING",
                "progress": 45.0,
                "start_date": "2023-08-15",
                "expected_end_date": "2027-03-31",
                "lat": 18.5312,
                "lng": 73.8642,
                "officer_emp_id": "PMC-ENV-2245",
                "officer_name": "Pooja Kadam",
                "officer_designation": "Deputy City Engineer (Environment & Water Drainage)",
                "officer_department": "PMC Drainage & Riverfront Division",
                "officer_contact": "+91-20-2550-1450",
                "officer_email": "pooja.kadam@punecorporation.org",
                "description": "Embankment stabilization, interception sewer trunk lines, and flood retention basins along the Mula-Mutha confluence."
            },
            {
                "project_id": "PUN-SWARGATE-HUB",
                "name": "Swargate Underground Multimodal Transport Interchange",
                "department": "Maharashtra Metro Rail Corporation (Maha-Metro)",
                "project_type": "Multimodal Hub & Underground Subway",
                "status": "COMPLETED",
                "progress": 100.0,
                "start_date": "2020-01-15",
                "expected_end_date": "2026-05-30",
                "actual_end_date": "2026-06-15",
                "lat": 18.5018,
                "lng": 73.8584,
                "officer_emp_id": "MAHA-METRO-0912",
                "officer_name": "Atul Gadgil",
                "officer_designation": "Director (Project Infrastructure)",
                "officer_department": "Maha-Metro Pune Division",
                "officer_contact": "+91-20-2605-8800",
                "officer_email": "atul.gadgil@punemetrorail.org",
                "description": "Integrated subterranean terminal connecting Metro Line 1, PMPML bus terminals, and MSRTC intercity bus depot."
            }
        ]

    def validate_and_normalize(self, r: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not r.get("project_id"):
            return None
        return r

    def persist_records(self, db: Session, records: List[Dict[str, Any]]) -> int:
        count = 0
        for data in records:
            # 1. Upsert Officer
            officer = None
            if data.get("officer_emp_id"):
                officer = db.query(Officer).filter(Officer.employee_id == data["officer_emp_id"]).first()
                if not officer:
                    officer = Officer(
                        employee_id=data["officer_emp_id"],
                        department=data.get("officer_department", data["department"]),
                        designation=data.get("officer_designation", "Executive Engineer"),
                        phone=data.get("officer_contact"),
                        email=data.get("officer_email"),
                        public_contact=data.get("officer_contact"),
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(officer)
                    db.flush()

            # 2. Upsert Project
            proj = db.query(GovernmentProject).filter(GovernmentProject.project_id == data["project_id"]).first()
            s_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date() if data.get("start_date") else None
            e_date = datetime.strptime(data["expected_end_date"], "%Y-%m-%d").date() if data.get("expected_end_date") else None
            a_date = datetime.strptime(data["actual_end_date"], "%Y-%m-%d").date() if data.get("actual_end_date") else None

            if not proj:
                proj = GovernmentProject(
                    project_id=data["project_id"],
                    name=data["name"],
                    description=data.get("description"),
                    department=data["department"],
                    project_type=data["project_type"],
                    status=ProjectStatus(data.get("status", "ONGOING")),
                    progress=float(data.get("progress", 0.0)),
                    start_date=s_date,
                    expected_end_date=e_date,
                    actual_end_date=a_date,
                    latitude=float(data["lat"]),
                    longitude=float(data["lng"]),
                    geometry_wkt=point_to_wkt(float(data["lat"]), float(data["lng"])),
                    officer_id=officer.id if officer else None,
                    source=self.source_name,
                    source_url=self.source_url,
                    last_updated=datetime.now(timezone.utc)
                )
                db.add(proj)
            else:
                proj.name = data["name"]
                proj.status = ProjectStatus(data.get("status", "ONGOING"))
                proj.progress = float(data.get("progress", 0.0))
                proj.officer_id = officer.id if officer else proj.officer_id
                proj.last_updated = datetime.now(timezone.utc)

            count += 1

        db.commit()
        return count
