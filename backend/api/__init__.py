"""API Router Modules"""

from .analysis import router as analysis_router
from .patients import router as patients_router
from .reports import router as reports_router
from .dicom import router as dicom_router
from .models import router as models_router
from .auth import router as auth_router

__all__ = [
    "analysis_router",
    "patients_router",
    "reports_router",
    "dicom_router",
    "models_router",
    "auth_router",
]
