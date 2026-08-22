import os
import sys
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_smartinfra.db"
os.environ["SECRET_KEY"] = "test_super_secret_jwt_key_smartinfra"
os.environ["GEMINI_API_KEY"] = ""
os.environ["GOOGLE_MAPS_API_KEY"] = ""

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole
from app.ingestion.opencity import OpenCityRoadsAdapter, OpenCitySewageAdapter, OpenCityFireStationsAdapter
from app.ingestion.water_leaks import WaterLeaksAdapter
from app.ingestion.government_projects import GovernmentProjectsAdapter
from app.ingestion.sensors import SensorRegistryAdapter

TEST_DATABASE_URL = "sqlite:///./test_smartinfra.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables and seed standard municipal test data."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

    # Seed Users
    users = [
        User(name="Admin User", email="admin@test.gov.in", password_hash=hash_password("admin123"), role=UserRole.ADMIN, is_active=True),
        User(name="Officer User", email="officer@test.gov.in", password_hash=hash_password("officer123"), role=UserRole.OFFICER, is_active=True),
        User(name="Engineer User", email="engineer@test.gov.in", password_hash=hash_password("engineer123"), role=UserRole.ENGINEER, is_active=True),
        User(name="Field Tech", email="tech@test.gov.in", password_hash=hash_password("tech123"), role=UserRole.FIELD_TECHNICIAN, is_active=True),
        User(name="Citizen User", email="citizen@test.com", password_hash=hash_password("citizen123"), role=UserRole.CITIZEN, is_active=True),
    ]
    for u in users:
        db.add(u)
    db.commit()

    # Run Ingestion Adapters
    OpenCityRoadsAdapter().run(db)
    OpenCitySewageAdapter().run(db)
    OpenCityFireStationsAdapter().run(db)
    WaterLeaksAdapter().run(db)
    GovernmentProjectsAdapter().run(db)
    SensorRegistryAdapter().run(db)

    db.close()
    yield
    # Teardown
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_smartinfra.db"):
        try:
            os.remove("test_smartinfra.db")
        except Exception:
            pass


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provides test database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Test client overriding get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token() -> str:
    return create_access_token({"sub": "1", "email": "admin@test.gov.in", "role": "ADMIN"})


@pytest.fixture
def officer_token() -> str:
    return create_access_token({"sub": "2", "email": "officer@test.gov.in", "role": "OFFICER"})


@pytest.fixture
def citizen_token() -> str:
    return create_access_token({"sub": "5", "email": "citizen@test.com", "role": "CITIZEN"})
