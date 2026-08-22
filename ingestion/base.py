from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.logging import logger


class BaseIngestionAdapter(ABC):
    """
    Standard Base Ingestion Adapter interface for OpenCity, PMC, and municipal datasets.
    Ensures data normalization, coordinate validation, provenance tracking, and idempotent upserts.
    """

    def __init__(self, source_name: str, source_url: Optional[str] = None):
        self.source_name = source_name
        self.source_url = source_url

    @abstractmethod
    def load_raw_data(self, filepath_or_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Read data from file, remote URL, or built-in verified registry."""
        pass

    @abstractmethod
    def validate_and_normalize(self, raw_record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize column names, coordinates, and types into canonical internal schemas."""
        pass

    @abstractmethod
    def persist_records(self, db: Session, normalized_records: List[Dict[str, Any]]) -> int:
        """Upsert records idempotently into the database."""
        pass

    def run(self, db: Session, filepath_or_url: Optional[str] = None) -> Dict[str, Any]:
        """Execute complete ingestion pipeline with logging and telemetry."""
        logger.info(f"Starting ingestion for source: {self.source_name}")
        start_time = datetime.now(timezone.utc)
        raw = self.load_raw_data(filepath_or_url)
        normalized = []
        errors = 0

        for r in raw:
            try:
                norm = self.validate_and_normalize(r)
                if norm:
                    normalized.append(norm)
            except Exception as e:
                errors += 1
                logger.warning(f"Normalization error in {self.source_name}: {e}")

        inserted_count = self.persist_records(db, normalized)
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info(f"Completed ingestion for {self.source_name}. Processed: {len(raw)}, Persisted: {inserted_count}, Errors: {errors}, Duration: {duration:.2f}s")
        return {
            "source": self.source_name,
            "raw_count": len(raw),
            "persisted_count": inserted_count,
            "error_count": errors,
            "duration_seconds": duration,
        }
