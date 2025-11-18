"""
Analysis Service
Orchestrates medical image analysis workflow
"""

import uuid
import time
from typing import Dict, List, Optional
import logging
import numpy as np
from datetime import datetime

from .model_service import ModelService
from .report_service import ReportService

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for managing image analysis workflow"""

    def __init__(self):
        self.model_service = ModelService()
        self.report_service = ReportService()
        # In-memory storage (replace with database)
        self.analyses = {}

    async def analyze_image(
        self,
        image_data: Dict,
        modality: str,
        body_part: str,
        model_type: str = "ensemble",
        user_id: str = None
    ) -> Dict:
        """
        Analyze medical image using AI models

        Args:
            image_data: Dictionary containing image pixels and metadata
            modality: Image modality (xray, ct, mri)
            body_part: Body part being examined
            model_type: Type of model to use
            user_id: User performing the analysis

        Returns:
            Analysis results with findings and confidence scores
        """
        analysis_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            logger.info(f"Starting analysis {analysis_id} for {modality} {body_part}")

            # Extract image pixels
            pixels = image_data['pixels']
            metadata = image_data.get('metadata', {})

            # Run AI prediction
            predictions = await self.model_service.predict(
                image=pixels,
                modality=modality,
                body_part=body_part,
                model_type=model_type
            )

            # Generate heatmap for visualization
            heatmap = await self.model_service.generate_heatmap(
                image=pixels,
                model_key=f"{modality}_{body_part}"
            )

            # Generate preliminary report draft
            report_draft = await self.report_service.generate_preliminary_report(
                findings=predictions['findings'],
                modality=modality,
                body_part=body_part
            )

            processing_time = time.time() - start_time

            # Build analysis result
            result = {
                'analysis_id': analysis_id,
                'status': 'completed',
                'findings': predictions['findings'],
                'confidence_scores': predictions['confidence_scores'],
                'all_scores': predictions['all_scores'],
                'heatmap_url': f"/api/v1/analysis/heatmap/{analysis_id}",
                'report_draft': report_draft,
                'processing_time': processing_time,
                'model_info': {
                    'model_type': model_type,
                    'version': '2.0',
                    'modality': modality,
                    'body_part': body_part
                },
                'metadata': {
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'image_metadata': metadata
                }
            }

            # Store analysis (in production, save to database)
            self.analyses[analysis_id] = {
                **result,
                'image_data': pixels,
                'heatmap': heatmap
            }

            logger.info(f"Analysis {analysis_id} completed in {processing_time:.2f}s")
            logger.info(f"Found {len(predictions['findings'])} findings")

            return result

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            raise

    async def analyze_by_id(
        self,
        image_id: str,
        modality: str,
        body_part: str,
        model_type: str = "ensemble",
        user_id: str = None
    ) -> Dict:
        """Re-analyze an existing image"""
        # Mock - retrieve image from storage
        image_data = {
            'pixels': np.random.rand(512, 512),
            'metadata': {'image_id': image_id}
        }

        return await self.analyze_image(
            image_data=image_data,
            modality=modality,
            body_part=body_part,
            model_type=model_type,
            user_id=user_id
        )

    async def get_analysis(self, analysis_id: str, user_id: str) -> Optional[Dict]:
        """Retrieve analysis results"""
        analysis = self.analyses.get(analysis_id)
        if not analysis:
            return None

        # Remove binary data before returning
        result = {k: v for k, v in analysis.items() if k not in ['image_data', 'heatmap']}
        return result

    async def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get user's analysis history"""
        # Filter analyses by user
        user_analyses = [
            {k: v for k, v in analysis.items() if k not in ['image_data', 'heatmap']}
            for analysis in self.analyses.values()
            if analysis.get('metadata', {}).get('user_id') == user_id
        ]

        # Sort by timestamp
        user_analyses.sort(
            key=lambda x: x.get('metadata', {}).get('timestamp', ''),
            reverse=True
        )

        return user_analyses[offset:offset + limit]

    async def compare_analyses(
        self,
        analysis_ids: List[str],
        user_id: str
    ) -> Dict:
        """
        Compare multiple analyses

        Useful for tracking disease progression
        """
        analyses = []
        for analysis_id in analysis_ids:
            analysis = await self.get_analysis(analysis_id, user_id)
            if analysis:
                analyses.append(analysis)

        if not analyses:
            return {'error': 'No analyses found'}

        # Extract key metrics for comparison
        comparison = {
            'analysis_count': len(analyses),
            'analyses': analyses,
            'progression': self._analyze_progression(analyses),
            'summary': self._generate_comparison_summary(analyses)
        }

        return comparison

    def _analyze_progression(self, analyses: List[Dict]) -> Dict:
        """Analyze disease progression across multiple timepoints"""
        # Sort by timestamp
        sorted_analyses = sorted(
            analyses,
            key=lambda x: x.get('metadata', {}).get('timestamp', '')
        )

        progression = {
            'trend': 'stable',
            'changes': []
        }

        # Compare findings across timepoints
        for i in range(1, len(sorted_analyses)):
            prev_findings = set(
                f['pathology'] for f in sorted_analyses[i - 1]['findings']
            )
            curr_findings = set(
                f['pathology'] for f in sorted_analyses[i]['findings']
            )

            new_findings = curr_findings - prev_findings
            resolved_findings = prev_findings - curr_findings

            if new_findings:
                progression['changes'].append({
                    'type': 'new_findings',
                    'findings': list(new_findings),
                    'timepoint': i
                })

            if resolved_findings:
                progression['changes'].append({
                    'type': 'resolved',
                    'findings': list(resolved_findings),
                    'timepoint': i
                })

        if progression['changes']:
            progression['trend'] = 'changing'

        return progression

    def _generate_comparison_summary(self, analyses: List[Dict]) -> str:
        """Generate text summary of comparison"""
        summary_parts = [
            f"Compared {len(analyses)} analyses.",
        ]

        all_findings = set()
        for analysis in analyses:
            all_findings.update(f['pathology'] for f in analysis['findings'])

        if all_findings:
            summary_parts.append(
                f"Pathologies observed: {', '.join(list(all_findings)[:5])}"
            )

        return " ".join(summary_parts)

    async def process_batch(
        self,
        batch_id: str,
        image_ids: List[str],
        modality: str,
        body_part: str,
        model_type: str,
        user_id: str
    ):
        """Process batch of images asynchronously"""
        logger.info(f"Starting batch analysis {batch_id} with {len(image_ids)} images")

        results = []
        for image_id in image_ids:
            try:
                result = await self.analyze_by_id(
                    image_id=image_id,
                    modality=modality,
                    body_part=body_part,
                    model_type=model_type,
                    user_id=user_id
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {image_id}: {str(e)}")
                results.append({'image_id': image_id, 'error': str(e)})

        logger.info(f"Batch analysis {batch_id} completed: {len(results)} results")
        return results

    async def delete_analysis(self, analysis_id: str, user_id: str):
        """Delete an analysis"""
        if analysis_id in self.analyses:
            analysis = self.analyses[analysis_id]
            if analysis.get('metadata', {}).get('user_id') == user_id:
                del self.analyses[analysis_id]
                logger.info(f"Deleted analysis {analysis_id}")
            else:
                raise PermissionError("Not authorized to delete this analysis")
        else:
            raise ValueError("Analysis not found")
