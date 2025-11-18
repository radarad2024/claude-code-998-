"""
Report Generation Service
AI-powered radiology report generation
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating radiology reports"""

    def __init__(self):
        self.reports = {}  # In-memory storage (replace with database)
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load report templates"""
        return {
            'chest_xray': """
CHEST X-RAY

CLINICAL INDICATION: {indication}

TECHNIQUE: {technique}

FINDINGS:
{findings}

IMPRESSION:
{impression}

RECOMMENDATIONS:
{recommendations}

Electronically signed by {radiologist}
Date: {date}
""",
            'brain_ct': """
CT BRAIN WITHOUT CONTRAST

CLINICAL INDICATION: {indication}

TECHNIQUE: {technique}

FINDINGS:
{findings}

IMPRESSION:
{impression}

RECOMMENDATIONS:
{recommendations}

Electronically signed by {radiologist}
Date: {date}
""",
            'generic': """
RADIOLOGY REPORT

EXAMINATION: {modality} {body_part}

CLINICAL INDICATION: {indication}

FINDINGS:
{findings}

IMPRESSION:
{impression}

RECOMMENDATIONS:
{recommendations}

Electronically signed by {radiologist}
Date: {date}
"""
        }

    async def generate_preliminary_report(
        self,
        findings: List[Dict],
        modality: str,
        body_part: str
    ) -> str:
        """
        Generate preliminary report text from AI findings

        This is a draft that should be reviewed and edited by radiologist
        """
        try:
            findings_text = self._format_findings(findings)
            impression_text = self._generate_impression(findings)
            recommendations_text = self._generate_recommendations(findings)

            report = f"""PRELIMINARY AI-ASSISTED REPORT (REQUIRES RADIOLOGIST REVIEW)

FINDINGS:
{findings_text}

PRELIMINARY IMPRESSION:
{impression_text}

SUGGESTED RECOMMENDATIONS:
{recommendations_text}

NOTE: This is an AI-generated preliminary report and must be reviewed,
edited, and signed by a qualified radiologist before finalization.
"""
            return report

        except Exception as e:
            logger.error(f"Error generating preliminary report: {str(e)}")
            return "Error generating report. Please review AI findings manually."

    def _format_findings(self, findings: List[Dict]) -> str:
        """Format findings into readable text"""
        if not findings:
            return "- No significant abnormalities detected by AI analysis."

        formatted = []
        for i, finding in enumerate(findings, 1):
            pathology = finding.get('pathology', 'Unknown')
            confidence = finding.get('confidence', 0.0)
            severity = finding.get('severity', '')
            location = finding.get('location', '')

            text = f"- {pathology}"

            if location:
                text += f" in {location}"

            if severity and severity != 'normal':
                text += f" ({severity})"

            text += f" [AI confidence: {confidence:.2%}]"

            formatted.append(text)

        return "\n".join(formatted)

    def _generate_impression(self, findings: List[Dict]) -> str:
        """Generate impression from findings"""
        significant_findings = [
            f for f in findings
            if f.get('confidence', 0) > 0.5 and f.get('severity') != 'normal'
        ]

        if not significant_findings:
            return "No acute abnormalities identified by AI analysis."

        # Group by severity
        high_confidence = [f for f in significant_findings if f.get('confidence', 0) > 0.8]

        impression_parts = []

        if high_confidence:
            pathologies = [f['pathology'] for f in high_confidence]
            impression_parts.append(
                f"AI analysis suggests: {', '.join(pathologies)}."
            )

        impression_parts.append(
            "Correlation with clinical presentation and prior studies is recommended."
        )

        return " ".join(impression_parts)

    def _generate_recommendations(self, findings: List[Dict]) -> str:
        """Generate recommendations based on findings"""
        significant_findings = [
            f for f in findings
            if f.get('confidence', 0) > 0.5 and f.get('severity') != 'normal'
        ]

        if not significant_findings:
            return "- Routine follow-up as clinically indicated."

        recommendations = []

        # Check for urgent findings
        urgent_findings = [
            f for f in significant_findings
            if any(term in f.get('pathology', '').lower()
                   for term in ['hemorrhage', 'pneumothorax', 'fracture'])
        ]

        if urgent_findings:
            recommendations.append(
                "- Urgent clinical correlation recommended given AI findings"
            )

        # General recommendations
        recommendations.append("- Clinical correlation recommended")
        recommendations.append("- Consider follow-up imaging if clinically warranted")

        return "\n".join(recommendations)

    async def generate_report(
        self,
        analysis_id: str,
        patient_id: str,
        study_id: str,
        template_id: Optional[str] = None,
        custom_findings: Optional[str] = None,
        user_id: str = None
    ) -> Dict:
        """
        Generate complete radiology report

        Args:
            analysis_id: ID of the AI analysis
            patient_id: Patient ID
            study_id: Study ID
            template_id: Template to use
            custom_findings: Custom findings text from radiologist
            user_id: Radiologist generating report

        Returns:
            Complete report data
        """
        report_id = str(uuid.uuid4())

        # Mock analysis data (in production, retrieve from database)
        analysis_data = {
            'findings': [
                {'pathology': 'Clear lung fields', 'confidence': 0.92},
                {'pathology': 'Normal cardiac silhouette', 'confidence': 0.88}
            ],
            'modality': 'xray',
            'body_part': 'chest'
        }

        # Generate findings text
        findings_text = custom_findings or self._format_findings(
            analysis_data['findings']
        )

        # Generate impression
        impression_text = self._generate_impression(analysis_data['findings'])

        # Generate recommendations
        recommendations_text = self._generate_recommendations(
            analysis_data['findings']
        )

        # Select template
        template_key = template_id or f"{analysis_data['body_part']}_{analysis_data['modality']}"
        template = self.templates.get(template_key, self.templates['generic'])

        # Format complete report
        report_text = template.format(
            indication="AI-assisted screening",
            technique="Standard imaging protocol",
            findings=findings_text,
            impression=impression_text,
            recommendations=recommendations_text,
            radiologist=user_id or "Dr. [NAME]",
            date=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            modality=analysis_data['modality'].upper(),
            body_part=analysis_data['body_part'].upper()
        )

        report = {
            'id': report_id,
            'analysis_id': analysis_id,
            'patient_id': patient_id,
            'study_id': study_id,
            'findings': findings_text,
            'impression': impression_text,
            'recommendations': recommendations_text,
            'report_text': report_text,
            'status': 'draft',
            'created_by': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Store report
        self.reports[report_id] = report

        logger.info(f"Generated report {report_id} for analysis {analysis_id}")

        return report

    async def get_report(self, report_id: str, user_id: str) -> Optional[Dict]:
        """Retrieve report by ID"""
        return self.reports.get(report_id)

    async def update_report(
        self,
        report_id: str,
        findings: Optional[str] = None,
        impression: Optional[str] = None,
        recommendations: Optional[str] = None,
        user_id: str = None
    ) -> Dict:
        """Update report content"""
        report = self.reports.get(report_id)

        if not report:
            raise ValueError("Report not found")

        if findings:
            report['findings'] = findings
        if impression:
            report['impression'] = impression
        if recommendations:
            report['recommendations'] = recommendations

        report['updated_at'] = datetime.utcnow()

        # Regenerate report text
        # (Implementation omitted for brevity)

        logger.info(f"Updated report {report_id}")

        return report

    async def finalize_report(self, report_id: str, user_id: str) -> Dict:
        """Finalize and sign report"""
        report = self.reports.get(report_id)

        if not report:
            raise ValueError("Report not found")

        report['status'] = 'finalized'
        report['finalized_by'] = user_id
        report['finalized_at'] = datetime.utcnow()

        logger.info(f"Finalized report {report_id} by {user_id}")

        return report

    async def export_report(
        self,
        report_id: str,
        format: str,
        user_id: str
    ) -> Dict:
        """
        Export report in various formats

        Args:
            report_id: Report ID
            format: Export format (pdf, docx, txt)
            user_id: User requesting export

        Returns:
            File data with download URL
        """
        report = self.reports.get(report_id)

        if not report:
            raise ValueError("Report not found")

        # Mock export (in production, generate actual files)
        file_url = f"/api/v1/reports/download/{report_id}.{format}"

        return {
            'url': file_url,
            'format': format,
            'report_id': report_id
        }
