"""
DICOM Processing API
Handle DICOM files and series
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
import logging

from database.models import User
from .auth import get_current_user
from dicom_processing.dicom_handler import DICOMHandler

logger = logging.getLogger(__name__)
router = APIRouter()


class DICOMMetadata(BaseModel):
    study_instance_uid: str
    series_instance_uid: str
    sop_instance_uid: str
    patient_id: str
    patient_name: str
    study_date: str
    modality: str
    body_part: str
    manufacturer: Optional[str] = None
    series_description: Optional[str] = None


class DICOMSeriesResponse(BaseModel):
    series_id: str
    study_id: str
    num_instances: int
    metadata: DICOMMetadata
    thumbnail_url: Optional[str]


@router.post("/upload")
async def upload_dicom(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload DICOM files

    Supports single or multiple files (complete series)
    """
    try:
        dicom_handler = DICOMHandler()
        results = []

        for file in files:
            content = await file.read()
            result = await dicom_handler.process_dicom(content)
            results.append({
                "filename": file.filename,
                "metadata": result["metadata"],
                "image_id": result["image_id"]
            })

        return {
            "status": "success",
            "uploaded": len(results),
            "files": results
        }

    except Exception as e:
        logger.error(f"DICOM upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/{image_id}")
async def get_dicom_metadata(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get DICOM metadata for an image
    """
    dicom_handler = DICOMHandler()

    try:
        metadata = await dicom_handler.get_metadata(image_id)
        return metadata

    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")


@router.get("/series/{series_id}")
async def get_series(
    series_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all images in a DICOM series
    """
    dicom_handler = DICOMHandler()

    try:
        series = await dicom_handler.get_series(series_id)
        return series

    except Exception as e:
        raise HTTPException(status_code=404, detail="Series not found")


@router.get("/study/{study_id}")
async def get_study(
    study_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all series in a DICOM study
    """
    dicom_handler = DICOMHandler()

    try:
        study = await dicom_handler.get_study(study_id)
        return study

    except Exception as e:
        raise HTTPException(status_code=404, detail="Study not found")


@router.post("/anonymize/{image_id}")
async def anonymize_dicom(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Anonymize DICOM file

    Removes patient identifying information
    """
    dicom_handler = DICOMHandler()

    try:
        result = await dicom_handler.anonymize(image_id)
        return {
            "status": "success",
            "anonymized_id": result["anonymized_id"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{image_id}")
async def export_dicom(
    image_id: str,
    format: str = "dicom",  # dicom, png, jpg
    current_user: User = Depends(get_current_user)
):
    """
    Export DICOM in various formats
    """
    dicom_handler = DICOMHandler()

    try:
        file_data = await dicom_handler.export(image_id, format)
        return {
            "download_url": file_data["url"],
            "format": format
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
