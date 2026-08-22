from datetime import datetime, timezone
import zoneinfo
from app.core.config import settings

PUNE_TZ = zoneinfo.ZoneInfo(settings.TIMEZONE)


def utc_now() -> datetime:
    """Return current datetime in UTC."""
    return datetime.now(timezone.utc)


def format_iso_utc(dt: datetime) -> str:
    """Format datetime as ISO 8601 UTC string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def to_pune_time(dt: datetime) -> datetime:
    """Convert UTC datetime to Pune Asia/Kolkata local time."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(PUNE_TZ)
