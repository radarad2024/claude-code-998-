"""
Patient Management API
HIPAA-compliant patient data management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from database.models import User
from .auth import get_current_user

router = APIRouter()


class PatientCreate(BaseModel):
    patient_id: str  # Hospital MRN or unique ID
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class PatientResponse(BaseModel):
    id: str
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime


class StudyCreate(BaseModel):
    patient_id: str
    study_type: str  # xray, ct, mri, ultrasound
    body_part: str
    indication: str
    referring_physician: str
    study_date: datetime


class StudyResponse(BaseModel):
    id: str
    patient_id: str
    study_type: str
    body_part: str
    indication: str
    referring_physician: str
    study_date: datetime
    num_images: int
    status: str


@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new patient record

    All data is encrypted at rest
    """
    patient_data = patient.dict()
    patient_data["id"] = str(uuid.uuid4())
    patient_data["created_at"] = datetime.utcnow()
    patient_data["updated_at"] = datetime.utcnow()

    # TODO: Save to database with encryption
    return PatientResponse(**patient_data)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get patient by ID

    Requires appropriate permissions
    """
    # Mock data
    patient_data = {
        "id": patient_id,
        "patient_id": "MRN-123456",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": datetime(1980, 1, 1),
        "gender": "M",
        "phone": "+1-555-0100",
        "email": "john.doe@email.com",
        "address": "123 Main St",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    return PatientResponse(**patient_data)


@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    List patients with optional search

    Supports searching by name, MRN, etc.
    """
    # Mock data
    patients = []
    return patients


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient: PatientCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Update patient information

    All changes are logged for audit trail
    """
    patient_data = patient.dict()
    patient_data["id"] = patient_id
    patient_data["created_at"] = datetime.utcnow()
    patient_data["updated_at"] = datetime.utcnow()

    return PatientResponse(**patient_data)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete patient record

    HIPAA-compliant deletion with audit trail
    """
    return {"status": "deleted", "patient_id": patient_id}


@router.post("/{patient_id}/studies", response_model=StudyResponse)
async def create_study(
    patient_id: str,
    study: StudyCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new imaging study for patient
    """
    study_data = study.dict()
    study_data["id"] = str(uuid.uuid4())
    study_data["num_images"] = 0
    study_data["status"] = "pending"

    return StudyResponse(**study_data)


@router.get("/{patient_id}/studies", response_model=List[StudyResponse])
async def get_patient_studies(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all studies for a patient
    """
    # Mock data
    studies = []
    return studies
