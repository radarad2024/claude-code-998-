"""
AI Radiologist Assistant - Main API Entry Point
A state-of-the-art medical imaging AI system for radiologists
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from api import (
    analysis_router,
    patients_router,
    reports_router,
    dicom_router,
    models_router,
    auth_router,
)
from api.analytics import router as analytics_router
from database.db_setup import init_db, close_db
from services.model_service import ModelService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('radiologist_assistant.log')
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting AI Radiologist Assistant...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Load AI models
    model_service = ModelService()
    await model_service.load_models()
    app.state.model_service = model_service
    logger.info("✅ AI models loaded")

    yield

    # Cleanup
    logger.info("🛑 Shutting down...")
    await close_db()
    logger.info("✅ Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title="AI Radiologist Assistant",
    description="Advanced AI-powered radiology analysis system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Radiologist Assistant",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Radiologist Assistant API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["AI Analysis"])
app.include_router(patients_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(dicom_router, prefix="/api/v1/dicom", tags=["DICOM"])
app.include_router(models_router, prefix="/api/v1/models", tags=["AI Models"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
