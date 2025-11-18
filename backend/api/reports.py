"""
Radiology Reports API
AI-assisted report generation with templates
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import uuid

from database.models import User
from .auth import get_current_user
from services.report_service import ReportService

router = APIRouter()


class ReportCreate(BaseModel):
    analysis_id: str
    patient_id: str
    study_id: str
    template_id: Optional[str] = None
    custom_findings: Optional[str] = None


class ReportResponse(BaseModel):
    id: str
    analysis_id: str
    patient_id: str
    study_id: str
    findings: str
    impression: str
    recommendations: str
    report_text: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime


class ReportTemplate(BaseModel):
    id: str
    name: str
    modality: str
    body_part: str
    template_text: str


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-assisted radiology report

    Uses analysis results to create structured report
    """
    try:
        report_service = ReportService()

        # Generate report using AI
        report = await report_service.generate_report(
            analysis_id=request.analysis_id,
            patient_id=request.patient_id,
            study_id=request.study_id,
            template_id=request.template_id,
            custom_findings=request.custom_findings,
            user_id=current_user.id
        )

        return ReportResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get report by ID
    """
    report_service = ReportService()
    report = await report_service.get_report(report_id, current_user.id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse(**report)


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    findings: Optional[str] = None,
    impression: Optional[str] = None,
    recommendations: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Update report content

    Maintains version history
    """
    report_service = ReportService()
    report = await report_service.update_report(
        report_id=report_id,
        findings=findings,
        impression=impression,
        recommendations=recommendations,
        user_id=current_user.id
    )

    return ReportResponse(**report)


@router.post("/{report_id}/finalize")
async def finalize_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Finalize and sign report

    Once finalized, report cannot be edited (new version required)
    """
    report_service = ReportService()
    report = await report_service.finalize_report(
        report_id=report_id,
        user_id=current_user.id
    )

    return {"status": "finalized", "report_id": report_id}


@router.get("/templates/", response_model=List[ReportTemplate])
async def get_templates(
    modality: Optional[str] = None,
    body_part: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get available report templates
    """
    # Mock templates
    templates = [
        {
            "id": "chest-xray-template",
            "name": "Chest X-Ray Standard",
            "modality": "xray",
            "body_part": "chest",
            "template_text": "FINDINGS:\n\nIMPRESSION:\n\nRECOMMENDATIONS:"
        },
        {
            "id": "brain-ct-template",
            "name": "Brain CT Standard",
            "modality": "ct",
            "body_part": "brain",
            "template_text": "TECHNIQUE:\nNon-contrast CT of the brain\n\nFINDINGS:\n\nIMPRESSION:"
        }
    ]

    if modality:
        templates = [t for t in templates if t["modality"] == modality]
    if body_part:
        templates = [t for t in templates if t["body_part"] == body_part]

    return [ReportTemplate(**t) for t in templates]


@router.post("/templates/", response_model=ReportTemplate)
async def create_template(
    template: ReportTemplate,
    current_user: User = Depends(get_current_user)
):
    """
    Create custom report template

    Only admins and senior radiologists can create templates
    """
    if current_user.role not in ["admin", "senior_radiologist"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # TODO: Save template to database
    return template


@router.get("/export/{report_id}")
async def export_report(
    report_id: str,
    format: str = "pdf",  # pdf, docx, txt
    current_user: User = Depends(get_current_user)
):
    """
    Export report in various formats

    Supports PDF, DOCX, and plain text
    """
    report_service = ReportService()

    try:
        file_data = await report_service.export_report(
            report_id=report_id,
            format=format,
            user_id=current_user.id
        )

        return {
            "status": "success",
            "download_url": file_data["url"],
            "format": format
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
