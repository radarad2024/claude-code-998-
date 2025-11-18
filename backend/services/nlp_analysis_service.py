"""
NLP-based Report Analysis Service
Natural Language Processing for radiology report analysis
"""

import re
from typing import Dict, List, Optional, Set
import logging
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)


class ReportAnalyzer:
    """
    NLP-based analyzer for radiology reports
    Extracts key findings, entities, and patterns
    """

    def __init__(self):
        self.pathology_keywords = self._load_pathology_keywords()
        self.anatomy_keywords = self._load_anatomy_keywords()
        self.severity_modifiers = self._load_severity_modifiers()
        logger.info("Report Analyzer initialized")

    def _load_pathology_keywords(self) -> Dict[str, List[str]]:
        """Load medical pathology keywords"""
        return {
            'pneumonia': ['pneumonia', 'consolidation', 'infiltrate', 'infection'],
            'fracture': ['fracture', 'broken', 'crack', 'displaced'],
            'mass': ['mass', 'tumor', 'neoplasm', 'lesion', 'nodule'],
            'hemorrhage': ['hemorrhage', 'bleeding', 'hematoma', 'blood'],
            'effusion': ['effusion', 'fluid collection', 'pleural fluid'],
            'edema': ['edema', 'swelling', 'fluid'],
            'atelectasis': ['atelectasis', 'collapse', 'collapsed lung'],
            'pneumothorax': ['pneumothorax', 'air in pleural space'],
            'cardiomegaly': ['cardiomegaly', 'enlarged heart', 'cardiac enlargement'],
            'normal': ['normal', 'unremarkable', 'no acute', 'clear', 'negative']
        }

    def _load_anatomy_keywords(self) -> Dict[str, List[str]]:
        """Load anatomical location keywords"""
        return {
            'lung': ['lung', 'pulmonary', 'bronch'],
            'heart': ['heart', 'cardiac', 'cardio'],
            'brain': ['brain', 'cerebral', 'intracranial'],
            'bone': ['bone', 'osseous', 'skeletal'],
            'liver': ['liver', 'hepatic'],
            'kidney': ['kidney', 'renal'],
            'chest': ['chest', 'thoracic', 'thorax']
        }

    def _load_severity_modifiers(self) -> Dict[str, int]:
        """Load severity modifiers with weights"""
        return {
            'severe': 3,
            'significant': 3,
            'marked': 3,
            'extensive': 3,
            'moderate': 2,
            'mild': 1,
            'minimal': 1,
            'trace': 1,
            'possible': 1,
            'probable': 2,
            'definite': 3
        }

    async def analyze_report(self, report_text: str) -> Dict:
        """
        Comprehensive analysis of a radiology report

        Args:
            report_text: Full report text

        Returns:
            Analysis results including entities, findings, and statistics
        """
        try:
            # Normalize text
            text = report_text.lower()

            # Extract findings
            findings = self._extract_findings(text)

            # Extract anatomical locations
            anatomies = self._extract_anatomies(text)

            # Assess severity
            severity = self._assess_severity(text, findings)

            # Extract measurements
            measurements = self._extract_measurements(text)

            # Determine urgency
            urgency = self._determine_urgency(findings, severity)

            # Extract recommendations
            recommendations = self._extract_recommendations(report_text)

            # Generate summary
            summary = self._generate_summary(findings, anatomies, severity)

            return {
                'findings': findings,
                'anatomies': anatomies,
                'severity': severity,
                'measurements': measurements,
                'urgency': urgency,
                'recommendations': recommendations,
                'summary': summary,
                'analyzed_at': 'utcnow'
            }

        except Exception as e:
            logger.error(f"Report analysis error: {str(e)}", exc_info=True)
            raise

    def _extract_findings(self, text: str) -> List[Dict]:
        """Extract pathological findings from text"""
        findings = []

        for pathology, keywords in self.pathology_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    # Find context around keyword
                    context = self._get_context(text, keyword)

                    # Check for negation
                    is_negated = self._check_negation(context, keyword)

                    if not is_negated:
                        findings.append({
                            'pathology': pathology,
                            'keyword': keyword,
                            'context': context,
                            'confidence': 0.8 if keyword == pathology else 0.6
                        })
                        break  # Only count once per pathology

        return findings

    def _extract_anatomies(self, text: str) -> List[str]:
        """Extract mentioned anatomical structures"""
        anatomies = set()

        for anatomy, keywords in self.anatomy_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    anatomies.add(anatomy)
                    break

        return list(anatomies)

    def _assess_severity(self, text: str, findings: List[Dict]) -> str:
        """Assess overall severity of findings"""
        if not findings:
            return 'normal'

        # Check for severity modifiers
        severity_score = 0
        for modifier, weight in self.severity_modifiers.items():
            if modifier in text:
                severity_score += weight

        # Check for urgent findings
        urgent_terms = ['acute', 'emergency', 'urgent', 'critical', 'emergent']
        for term in urgent_terms:
            if term in text:
                severity_score += 4

        # Determine severity level
        if severity_score >= 8:
            return 'critical'
        elif severity_score >= 5:
            return 'severe'
        elif severity_score >= 3:
            return 'moderate'
        elif severity_score > 0:
            return 'mild'
        else:
            return 'normal'

    def _extract_measurements(self, text: str) -> List[Dict]:
        """Extract numerical measurements from report"""
        measurements = []

        # Pattern for measurements (e.g., "5.2 cm", "3 mm", "12x15 mm")
        patterns = [
            r'(\d+\.?\d*)\s*(mm|cm|m)\b',
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*(mm|cm|m)\b',
            r'(\d+\.?\d*)%'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.group(0), window=50)
                measurements.append({
                    'value': match.group(0),
                    'context': context
                })

        return measurements

    def _determine_urgency(self, findings: List[Dict], severity: str) -> str:
        """Determine urgency level of report"""
        # Check for critical findings
        critical_pathologies = ['hemorrhage', 'pneumothorax', 'fracture']
        has_critical = any(
            f['pathology'] in critical_pathologies
            for f in findings
        )

        if severity == 'critical' or has_critical:
            return 'urgent'
        elif severity == 'severe':
            return 'high'
        elif severity == 'moderate':
            return 'medium'
        else:
            return 'routine'

    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from report"""
        recommendations = []

        # Common recommendation patterns
        rec_patterns = [
            r'recommend[s]?\s+([^.]+)',
            r'suggest[s]?\s+([^.]+)',
            r'follow[- ]up\s+([^.]+)',
            r'correlation\s+([^.]+)'
        ]

        for pattern in rec_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                rec_text = match.group(0).strip()
                if len(rec_text) > 10:  # Filter out very short matches
                    recommendations.append(rec_text)

        return list(set(recommendations))[:5]  # Limit to 5 unique recommendations

    def _get_context(self, text: str, keyword: str, window: int = 100) -> str:
        """Get surrounding context for a keyword"""
        idx = text.find(keyword)
        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)

        return text[start:end].strip()

    def _check_negation(self, context: str, keyword: str) -> bool:
        """Check if a finding is negated"""
        negation_terms = [
            'no ', 'not ', 'without ', 'denies ', 'negative for ',
            'rule out ', 'absence of ', 'free of '
        ]

        # Check if negation appears before keyword in context
        keyword_idx = context.find(keyword)
        if keyword_idx == -1:
            return False

        context_before = context[:keyword_idx].lower()

        for neg_term in negation_terms:
            if neg_term in context_before[-50:]:  # Check last 50 chars before keyword
                return True

        return False

    def _generate_summary(
        self,
        findings: List[Dict],
        anatomies: List[str],
        severity: str
    ) -> str:
        """Generate concise summary of analysis"""
        if not findings or severity == 'normal':
            return "No significant abnormalities detected in report."

        pathologies = [f['pathology'] for f in findings]
        unique_pathologies = list(set(pathologies))

        summary = f"Report indicates {severity} findings. "

        if unique_pathologies:
            summary += f"Pathologies: {', '.join(unique_pathologies)}. "

        if anatomies:
            summary += f"Anatomical areas: {', '.join(anatomies)}."

        return summary


class ReportComparison:
    """Compare multiple reports for longitudinal analysis"""

    @staticmethod
    async def compare_reports(
        reports: List[Dict],
        analysis_results: List[Dict]
    ) -> Dict:
        """
        Compare multiple reports to track changes over time

        Args:
            reports: List of report dictionaries
            analysis_results: List of analysis results for each report

        Returns:
            Comparison results with trends and changes
        """
        if len(reports) < 2:
            return {'error': 'Need at least 2 reports for comparison'}

        # Track findings over time
        findings_timeline = []
        severity_trend = []

        for i, analysis in enumerate(analysis_results):
            findings_timeline.append({
                'report_index': i,
                'findings': [f['pathology'] for f in analysis.get('findings', [])],
                'severity': analysis.get('severity', 'normal')
            })
            severity_trend.append(analysis.get('severity', 'normal'))

        # Detect new findings
        all_findings = set()
        new_findings_by_report = []

        for entry in findings_timeline:
            current_findings = set(entry['findings'])
            new = current_findings - all_findings
            new_findings_by_report.append(list(new))
            all_findings.update(current_findings)

        # Assess trend
        severity_scores = {
            'normal': 0,
            'mild': 1,
            'moderate': 2,
            'severe': 3,
            'critical': 4
        }

        trend_values = [severity_scores.get(s, 0) for s in severity_trend]
        if len(trend_values) >= 2:
            if trend_values[-1] > trend_values[0]:
                trend = 'worsening'
            elif trend_values[-1] < trend_values[0]:
                trend = 'improving'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'num_reports': len(reports),
            'findings_timeline': findings_timeline,
            'severity_trend': severity_trend,
            'new_findings_by_report': new_findings_by_report,
            'overall_trend': trend,
            'all_pathologies': list(all_findings)
        }
