"""
AI Models Management API
Information about available AI models and their performance
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from database.models import User
from .auth import get_current_user
from services.model_service import ModelService

router = APIRouter()


class ModelInfo(BaseModel):
    model_id: str
    name: str
    version: str
    modality: str
    body_part: str
    pathologies: List[str]
    performance: Dict[str, float]
    description: str
    status: str


class ModelPerformance(BaseModel):
    model_id: str
    auc: float
    sensitivity: float
    specificity: float
    accuracy: float
    f1_score: float


@router.get("/available", response_model=List[ModelInfo])
async def get_available_models(
    modality: Optional[str] = None,
    body_part: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available AI models

    Filter by modality and body part
    """
    models = [
        {
            "model_id": "chest-xray-ensemble-v2",
            "name": "Chest X-Ray Ensemble",
            "version": "2.0",
            "modality": "xray",
            "body_part": "chest",
            "pathologies": [
                "Pneumonia",
                "COVID-19",
                "Lung Cancer",
                "Pneumothorax",
                "Pleural Effusion",
                "Cardiomegaly",
                "Atelectasis",
                "Emphysema"
            ],
            "performance": {
                "auc": 0.96,
                "sensitivity": 0.94,
                "specificity": 0.92
            },
            "description": "State-of-the-art ensemble model for chest X-ray analysis",
            "status": "active"
        },
        {
            "model_id": "brain-ct-hemorrhage-v1",
            "name": "Brain CT Hemorrhage Detector",
            "version": "1.5",
            "modality": "ct",
            "body_part": "brain",
            "pathologies": [
                "Intracranial Hemorrhage",
                "Subdural Hematoma",
                "Epidural Hematoma",
                "Subarachnoid Hemorrhage",
                "Intraventricular Hemorrhage"
            ],
            "performance": {
                "auc": 0.95,
                "sensitivity": 0.93,
                "specificity": 0.94
            },
            "description": "Deep learning model for detecting brain hemorrhages on CT",
            "status": "active"
        },
        {
            "model_id": "bone-fracture-detector-v1",
            "name": "Bone Fracture Detector",
            "version": "1.0",
            "modality": "xray",
            "body_part": "bone",
            "pathologies": [
                "Fracture",
                "Comminuted Fracture",
                "Greenstick Fracture",
                "Stress Fracture"
            ],
            "performance": {
                "auc": 0.93,
                "sensitivity": 0.90,
                "specificity": 0.93
            },
            "description": "AI model for detecting bone fractures in various anatomical regions",
            "status": "active"
        }
    ]

    if modality:
        models = [m for m in models if m["modality"] == modality]
    if body_part:
        models = [m for m in models if m["body_part"] == body_part]

    return [ModelInfo(**m) for m in models]


@router.get("/{model_id}", response_model=ModelInfo)
async def get_model_info(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific model
    """
    # Mock data - replace with actual model lookup
    model_data = {
        "model_id": model_id,
        "name": "Chest X-Ray Ensemble",
        "version": "2.0",
        "modality": "xray",
        "body_part": "chest",
        "pathologies": ["Pneumonia", "COVID-19"],
        "performance": {"auc": 0.96, "sensitivity": 0.94, "specificity": 0.92},
        "description": "Advanced ensemble model",
        "status": "active"
    }

    return ModelInfo(**model_data)


@router.get("/{model_id}/performance", response_model=ModelPerformance)
async def get_model_performance(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed performance metrics for a model
    """
    performance = {
        "model_id": model_id,
        "auc": 0.96,
        "sensitivity": 0.94,
        "specificity": 0.92,
        "accuracy": 0.93,
        "f1_score": 0.93
    }

    return ModelPerformance(**performance)


@router.post("/{model_id}/reload")
async def reload_model(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Reload a model from disk

    Admin only - useful for model updates
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    model_service = ModelService()
    await model_service.reload_model(model_id)

    return {"status": "reloaded", "model_id": model_id}
