"""
Analytics API
Data analytics and statistics endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel

from database.models import User
from .auth import get_current_user
from services.analytics_service import AnalyticsService
from services.nlp_analysis_service import ReportAnalyzer, ReportComparison

router = APIRouter()


class DateRangeRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@router.get("/dashboard")
async def get_dashboard_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard statistics

    Includes AI performance, workload, pathology distribution, and trends
    """
    analytics_service = AnalyticsService()

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    stats = await analytics_service.generate_dashboard_stats(
        user_id=current_user.id,
        start_date=start,
        end_date=end
    )

    return stats


@router.get("/performance")
async def get_ai_performance(
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed AI model performance metrics

    Returns accuracy, AUC, sensitivity, specificity for all models
    """
    analytics_service = AnalyticsService()
    performance = await analytics_service.get_ai_performance_metrics()

    return performance


@router.get("/workload")
async def get_workload_stats(
    user_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get workload distribution statistics

    Can filter by specific user or get system-wide stats
    """
    analytics_service = AnalyticsService()
    workload = await analytics_service.get_workload_distribution(user_id)

    return workload


@router.get("/pathologies")
async def get_pathology_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get pathology distribution statistics

    Shows frequency and severity of detected pathologies
    """
    analytics_service = AnalyticsService()
    pathologies = await analytics_service.get_pathology_distribution()

    return pathologies


@router.get("/modalities")
async def get_modality_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get imaging modality usage statistics
    """
    analytics_service = AnalyticsService()
    modalities = await analytics_service.get_modality_usage()

    return modalities


@router.get("/turnaround-time")
async def get_turnaround_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get turnaround time statistics

    Includes AI analysis time and report generation time
    """
    analytics_service = AnalyticsService()
    tat = await analytics_service.get_turnaround_time_stats()

    return tat


@router.get("/trends")
async def get_temporal_trends(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get temporal trends in operations

    Shows volume trends, accuracy trends, and patterns over time
    """
    analytics_service = AnalyticsService()

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    trends = await analytics_service.get_temporal_trends(start, end)

    return trends


@router.get("/quality")
async def get_quality_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    Get quality assurance metrics

    Includes AI agreement rate, false positive/negative rates, etc.
    """
    analytics_service = AnalyticsService()
    quality = await analytics_service.generate_quality_metrics()

    return quality


@router.post("/cohort-analysis")
async def analyze_cohort(
    cohort_definition: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze specific patient cohort

    Requires cohort definition criteria
    """
    analytics_service = AnalyticsService()
    analysis = await analytics_service.generate_cohort_analysis(cohort_definition)

    return analysis


@router.get("/export/{report_type}")
async def export_analytics_report(
    report_type: str,
    format: str = "pdf",
    current_user: User = Depends(get_current_user)
):
    """
    Export analytics report

    Supports PDF, Excel, and CSV formats
    """
    analytics_service = AnalyticsService()

    try:
        report = await analytics_service.export_analytics_report(
            report_type=report_type,
            format=format
        )
        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# NLP Report Analysis Endpoints

@router.post("/analyze-report")
async def analyze_report_text(
    report_text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze radiology report using NLP

    Extracts findings, severity, measurements, and recommendations
    """
    analyzer = ReportAnalyzer()

    try:
        analysis = await analyzer.analyze_report(report_text)
        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-reports")
async def compare_reports(
    report_ids: list,
    current_user: User = Depends(get_current_user)
):
    """
    Compare multiple reports for longitudinal analysis

    Tracks changes and trends across multiple timepoints
    """
    # Mock - retrieve reports from database
    reports = []
    analysis_results = []

    comparison = await ReportComparison.compare_reports(
        reports=reports,
        analysis_results=analysis_results
    )

    return comparison
