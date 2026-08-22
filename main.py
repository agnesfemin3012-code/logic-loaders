import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.core.logging import logger
from app.core.exceptions import SmartInfraException
from app.api import api_router
from app.ingestion.opencity import OpenCityRoadsAdapter, OpenCitySewageAdapter, OpenCityFireStationsAdapter
from app.ingestion.water_leaks import WaterLeaksAdapter
from app.ingestion.government_projects import GovernmentProjectsAdapter
from app.ingestion.sensors import SensorRegistryAdapter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan startup and shutdown routines.
    Initializes database tables, runs baseline dataset ingestion if empty.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    init_db()

    # Seed initial datasets if database is fresh
    db = SessionLocal()
    try:
        from app.models.asset import InfrastructureAsset
        asset_count = db.query(InfrastructureAsset).count()
        if asset_count == 0:
            logger.info("Initializing baseline Pune infrastructure datasets and PMC projects...")
            OpenCityRoadsAdapter().run(db)
            OpenCitySewageAdapter().run(db)
            OpenCityFireStationsAdapter().run(db)
            WaterLeaksAdapter().run(db)
            GovernmentProjectsAdapter().run(db)
            SensorRegistryAdapter().run(db)
            logger.info("Baseline municipal datasets loaded successfully.")
    except Exception as e:
        logger.warning(f"Initial baseline dataset load note: {e}")
    finally:
        db.close()

    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Driven Predictive Infrastructure Maintenance and Smart-City Intelligence Platform for Pune City.",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging & performance header middleware
@app.middleware("http")
async def add_process_time_and_log(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    
    # Do not log spam health checks in debug
    if request.url.path not in ("/health", "/"):
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({process_time:.1f}ms)")
    return response


# Global Exception Handlers
@app.exception_handler(SmartInfraException)
async def smartinfra_exception_handler(request: Request, exc: SmartInfraException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg')}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": {"validation_errors": errors}
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing the request."
            }
        }
    )


# Health check
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint confirming system uptime and status."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "city": "Pune",
        "timezone": settings.TIMEZONE
    }


@app.get("/", tags=["Health"])
def root_redirect():
    """Root metadata endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} Backend API",
        "docs_url": "/docs",
        "health_url": "/health",
        "city": "Pune, Maharashtra, India"
    }


# Mount API V1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
