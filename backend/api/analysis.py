"""
AI Analysis API Endpoints
Handles medical image analysis using deep learning models
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
from datetime import datetime
import uuid

from services.model_service import ModelService
from services.analysis_service import AnalysisService
from dicom_processing.dicom_handler import DICOMHandler
from database.models import Analysis, User
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalysisRequest(BaseModel):
    """Analysis request model"""
    image_id: str
    model_type: str = "ensemble"
    modality: str  # xray, ct, mri
    body_part: str  # chest, brain, bone, etc.
    priority: str = "normal"  # low, normal, high, urgent


class AnalysisResponse(BaseModel):
    """Analysis response model"""
    analysis_id: str
    status: str
    findings: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    heatmap_url: Optional[str]
    report_draft: Optional[str]
    processing_time: float
    model_version: str
    timestamp: datetime


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request"""
    image_ids: List[str]
    model_type: str = "ensemble"
    modality: str
    body_part: str


@router.post("/upload", response_model=Dict[str, Any])
async def upload_and_analyze(
    file: UploadFile = File(...),
    modality: str = "xray",
    body_part: str = "chest",
    model_type: str = "ensemble",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """
    Upload medical image and run AI analysis

    Supports DICOM, PNG, JPG formats
    Returns immediate analysis results with AI findings
    """
    try:
        logger.info(f"Received upload from user {current_user.id}: {file.filename}")

        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Read file content
        content = await file.read()

        # Initialize services
        analysis_service = AnalysisService()
        dicom_handler = DICOMHandler()

        # Process image
        if file.filename.lower().endswith('.dcm'):
            # Handle DICOM
            image_data = await dicom_handler.process_dicom(content)
        else:
            # Handle standard images
            import io
            from PIL import Image
            import numpy as np

            image = Image.open(io.BytesIO(content))
            image_data = {
                'pixels': np.array(image),
                'metadata': {
                    'modality': modality,
                    'body_part': body_part,
                    'filename': file.filename
                }
            }

        # Run AI analysis
        analysis_result = await analysis_service.analyze_image(
            image_data=image_data,
            modality=modality,
            body_part=body_part,
            model_type=model_type,
            user_id=current_user.id
        )

        logger.info(f"Analysis completed: {analysis_result['analysis_id']}")

        return {
            "status": "success",
            "analysis_id": analysis_result['analysis_id'],
            "findings": analysis_result['findings'],
            "confidence_scores": analysis_result['confidence_scores'],
            "heatmap_url": analysis_result.get('heatmap_url'),
            "report_draft": analysis_result.get('report_draft'),
            "processing_time": analysis_result['processing_time'],
            "model_info": analysis_result['model_info']
        }

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_existing_image(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze an already uploaded image

    Useful for re-running analysis with different models
    """
    try:
        analysis_service = AnalysisService()

        result = await analysis_service.analyze_by_id(
            image_id=request.image_id,
            modality=request.modality,
            body_part=request.body_part,
            model_type=request.model_type,
            user_id=current_user.id
        )

        return AnalysisResponse(**result)

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=Dict[str, Any])
async def batch_analysis(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Run batch analysis on multiple images

    Processes images asynchronously and returns batch ID for tracking
    """
    try:
        batch_id = str(uuid.uuid4())
        analysis_service = AnalysisService()

        # Queue batch processing
        background_tasks.add_task(
            analysis_service.process_batch,
            batch_id=batch_id,
            image_ids=request.image_ids,
            modality=request.modality,
            body_part=request.body_part,
            model_type=request.model_type,
            user_id=current_user.id
        )

        return {
            "status": "processing",
            "batch_id": batch_id,
            "total_images": len(request.image_ids),
            "message": "Batch analysis started"
        }

    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_results(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve analysis results by ID
    """
    try:
        analysis_service = AnalysisService()
        result = await analysis_service.get_analysis(analysis_id, current_user.id)

        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return AnalysisResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's analysis history
    """
    try:
        analysis_service = AnalysisService()
        results = await analysis_service.get_user_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        return [AnalysisResponse(**r) for r in results]

    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_analyses(
    analysis_ids: List[str],
    current_user: User = Depends(get_current_user)
):
    """
    Compare multiple analyses side-by-side

    Useful for tracking disease progression or comparing different timepoints
    """
    try:
        analysis_service = AnalysisService()
        comparison = await analysis_service.compare_analyses(
            analysis_ids=analysis_ids,
            user_id=current_user.id
        )

        return comparison

    except Exception as e:
        logger.error(f"Comparison error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an analysis
    """
    try:
        analysis_service = AnalysisService()
        await analysis_service.delete_analysis(analysis_id, current_user.id)

        return {"status": "deleted", "analysis_id": analysis_id}

    except Exception as e:
        logger.error(f"Delete error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
