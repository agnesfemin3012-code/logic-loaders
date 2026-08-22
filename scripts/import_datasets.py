import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db
from app.ingestion.opencity import OpenCityRoadsAdapter, OpenCitySewageAdapter, OpenCityFireStationsAdapter
from app.ingestion.water_leaks import WaterLeaksAdapter
from app.ingestion.government_projects import GovernmentProjectsAdapter
from app.ingestion.sensors import SensorRegistryAdapter
from app.core.logging import logger


def import_all_datasets():
    """Execute all dataset ingestion adapters."""
    init_db()
    db = SessionLocal()
    try:
        adapters = [
            OpenCityRoadsAdapter(),
            OpenCitySewageAdapter(),
            OpenCityFireStationsAdapter(),
            WaterLeaksAdapter(),
            GovernmentProjectsAdapter(),
            SensorRegistryAdapter(),
        ]

        for adapter in adapters:
            res = adapter.run(db)
            print(f"[{res['source']}] Ingested {res['persisted_count']} records in {res['duration_seconds']:.2f}s (Errors: {res['error_count']})")

        print("All municipal datasets imported successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    import_all_datasets()
