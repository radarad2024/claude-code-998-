"""
DICOM Processing Handler
Handles DICOM file parsing, processing, and manipulation
"""

import pydicom
from pydicom.dataset import Dataset
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
import uuid
from datetime import datetime
import io

logger = logging.getLogger(__name__)


class DICOMHandler:
    """Handler for DICOM medical imaging files"""

    def __init__(self):
        self.storage = {}  # In-memory storage (replace with proper storage)
        logger.info("DICOM Handler initialized")

    async def process_dicom(self, dicom_bytes: bytes) -> Dict:
        """
        Process DICOM file from bytes

        Args:
            dicom_bytes: DICOM file as bytes

        Returns:
            Dictionary with image data and metadata
        """
        try:
            # Parse DICOM
            dcm = pydicom.dcmread(io.BytesIO(dicom_bytes))

            # Extract metadata
            metadata = self._extract_metadata(dcm)

            # Convert to pixel array
            pixels = self._get_pixel_array(dcm)

            # Generate unique ID
            image_id = str(uuid.uuid4())

            # Store DICOM data
            self.storage[image_id] = {
                'dcm': dcm,
                'pixels': pixels,
                'metadata': metadata,
                'created_at': datetime.utcnow()
            }

            logger.info(f"Processed DICOM: {metadata.get('Modality')} {metadata.get('BodyPartExamined')}")

            return {
                'image_id': image_id,
                'pixels': pixels,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error processing DICOM: {str(e)}", exc_info=True)
            raise ValueError(f"Invalid DICOM file: {str(e)}")

    def _extract_metadata(self, dcm: Dataset) -> Dict:
        """Extract relevant metadata from DICOM"""
        metadata = {}

        # Study/Series/Instance UIDs
        metadata['StudyInstanceUID'] = str(dcm.get('StudyInstanceUID', ''))
        metadata['SeriesInstanceUID'] = str(dcm.get('SeriesInstanceUID', ''))
        metadata['SOPInstanceUID'] = str(dcm.get('SOPInstanceUID', ''))

        # Patient information
        metadata['PatientID'] = str(dcm.get('PatientID', ''))
        metadata['PatientName'] = str(dcm.get('PatientName', ''))
        metadata['PatientBirthDate'] = str(dcm.get('PatientBirthDate', ''))
        metadata['PatientSex'] = str(dcm.get('PatientSex', ''))

        # Study information
        metadata['StudyDate'] = str(dcm.get('StudyDate', ''))
        metadata['StudyTime'] = str(dcm.get('StudyTime', ''))
        metadata['StudyDescription'] = str(dcm.get('StudyDescription', ''))
        metadata['AccessionNumber'] = str(dcm.get('AccessionNumber', ''))

        # Series information
        metadata['Modality'] = str(dcm.get('Modality', ''))
        metadata['SeriesDescription'] = str(dcm.get('SeriesDescription', ''))
        metadata['SeriesNumber'] = str(dcm.get('SeriesNumber', ''))
        metadata['BodyPartExamined'] = str(dcm.get('BodyPartExamined', ''))

        # Image information
        metadata['InstanceNumber'] = str(dcm.get('InstanceNumber', ''))
        metadata['ImageType'] = str(dcm.get('ImageType', ''))

        # Equipment information
        metadata['Manufacturer'] = str(dcm.get('Manufacturer', ''))
        metadata['ManufacturerModelName'] = str(dcm.get('ManufacturerModelName', ''))
        metadata['StationName'] = str(dcm.get('StationName', ''))

        # Image parameters
        metadata['Rows'] = int(dcm.get('Rows', 0))
        metadata['Columns'] = int(dcm.get('Columns', 0))
        metadata['PixelSpacing'] = str(dcm.get('PixelSpacing', ''))
        metadata['SliceThickness'] = str(dcm.get('SliceThickness', ''))

        # Window/Level
        metadata['WindowCenter'] = str(dcm.get('WindowCenter', ''))
        metadata['WindowWidth'] = str(dcm.get('WindowWidth', ''))

        return metadata

    def _get_pixel_array(self, dcm: Dataset) -> np.ndarray:
        """
        Convert DICOM to pixel array with proper windowing

        Args:
            dcm: DICOM dataset

        Returns:
            Normalized pixel array
        """
        try:
            # Get pixel data
            pixels = dcm.pixel_array.astype(float)

            # Apply modality LUT (rescale slope/intercept)
            if hasattr(dcm, 'RescaleSlope') and hasattr(dcm, 'RescaleIntercept'):
                pixels = pixels * float(dcm.RescaleSlope) + float(dcm.RescaleIntercept)

            # Apply windowing if available
            if hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'):
                window_center = float(dcm.WindowCenter) if isinstance(dcm.WindowCenter, (int, float, str)) else float(dcm.WindowCenter[0])
                window_width = float(dcm.WindowWidth) if isinstance(dcm.WindowWidth, (int, float, str)) else float(dcm.WindowWidth[0])

                # Apply window
                img_min = window_center - window_width // 2
                img_max = window_center + window_width // 2
                pixels = np.clip(pixels, img_min, img_max)

            # Normalize to 0-255
            pixels = self._normalize_pixels(pixels)

            return pixels

        except Exception as e:
            logger.error(f"Error converting pixel array: {str(e)}")
            # Return raw pixel array if processing fails
            return dcm.pixel_array.astype(float)

    def _normalize_pixels(self, pixels: np.ndarray) -> np.ndarray:
        """Normalize pixel values to 0-255 range"""
        pixels = pixels.astype(float)
        pixels_min = pixels.min()
        pixels_max = pixels.max()

        if pixels_max > pixels_min:
            pixels = ((pixels - pixels_min) / (pixels_max - pixels_min)) * 255.0

        return pixels.astype(np.uint8)

    async def get_metadata(self, image_id: str) -> Dict:
        """Get metadata for a stored DICOM image"""
        if image_id not in self.storage:
            raise ValueError("Image not found")

        return self.storage[image_id]['metadata']

    async def get_series(self, series_id: str) -> Dict:
        """
        Get all images in a DICOM series

        Args:
            series_id: Series Instance UID

        Returns:
            Dictionary with series information and images
        """
        series_images = []

        for image_id, data in self.storage.items():
            if data['metadata'].get('SeriesInstanceUID') == series_id:
                series_images.append({
                    'image_id': image_id,
                    'instance_number': data['metadata'].get('InstanceNumber'),
                    'metadata': data['metadata']
                })

        # Sort by instance number
        series_images.sort(key=lambda x: int(x.get('instance_number', 0)))

        return {
            'series_id': series_id,
            'num_images': len(series_images),
            'images': series_images
        }

    async def get_study(self, study_id: str) -> Dict:
        """
        Get all series in a DICOM study

        Args:
            study_id: Study Instance UID

        Returns:
            Dictionary with study information and series
        """
        study_series = {}

        for image_id, data in self.storage.items():
            if data['metadata'].get('StudyInstanceUID') == study_id:
                series_uid = data['metadata'].get('SeriesInstanceUID')

                if series_uid not in study_series:
                    study_series[series_uid] = {
                        'series_id': series_uid,
                        'description': data['metadata'].get('SeriesDescription'),
                        'modality': data['metadata'].get('Modality'),
                        'images': []
                    }

                study_series[series_uid]['images'].append({
                    'image_id': image_id,
                    'instance_number': data['metadata'].get('InstanceNumber')
                })

        return {
            'study_id': study_id,
            'num_series': len(study_series),
            'series': list(study_series.values())
        }

    async def anonymize(self, image_id: str) -> Dict:
        """
        Anonymize DICOM file

        Removes patient identifying information while preserving
        medically relevant metadata

        Args:
            image_id: Image to anonymize

        Returns:
            New anonymized image ID
        """
        if image_id not in self.storage:
            raise ValueError("Image not found")

        # Get original DICOM
        original_dcm = self.storage[image_id]['dcm'].copy()

        # Tags to anonymize
        anonymize_tags = [
            'PatientName',
            'PatientID',
            'PatientBirthDate',
            'PatientAddress',
            'InstitutionName',
            'InstitutionAddress',
            'ReferringPhysicianName',
            'PerformingPhysicianName',
            'OperatorsName',
            'AccessionNumber'
        ]

        # Remove/replace tags
        for tag in anonymize_tags:
            if tag in original_dcm:
                if tag in ['PatientName', 'PatientID']:
                    original_dcm.data_element(tag).value = 'ANONYMIZED'
                else:
                    del original_dcm[tag]

        # Generate new UIDs
        original_dcm.PatientID = 'ANON-' + str(uuid.uuid4())[:8]

        # Create new storage entry
        anonymized_id = str(uuid.uuid4())
        pixels = self._get_pixel_array(original_dcm)
        metadata = self._extract_metadata(original_dcm)

        self.storage[anonymized_id] = {
            'dcm': original_dcm,
            'pixels': pixels,
            'metadata': metadata,
            'created_at': datetime.utcnow(),
            'anonymized': True
        }

        logger.info(f"Anonymized image {image_id} -> {anonymized_id}")

        return {
            'anonymized_id': anonymized_id,
            'original_id': image_id
        }

    async def export(self, image_id: str, format: str) -> Dict:
        """
        Export DICOM in various formats

        Args:
            image_id: Image to export
            format: Export format (dicom, png, jpg)

        Returns:
            File information with download URL
        """
        if image_id not in self.storage:
            raise ValueError("Image not found")

        data = self.storage[image_id]

        # Mock export - in production, generate actual files
        file_url = f"/api/v1/dicom/download/{image_id}.{format}"

        return {
            'url': file_url,
            'format': format,
            'image_id': image_id
        }

    def get_3d_volume(self, series_id: str) -> Optional[np.ndarray]:
        """
        Construct 3D volume from DICOM series

        Args:
            series_id: Series Instance UID

        Returns:
            3D numpy array
        """
        # Get all images in series
        series_images = []

        for image_id, data in self.storage.items():
            if data['metadata'].get('SeriesInstanceUID') == series_id:
                series_images.append({
                    'instance_number': int(data['metadata'].get('InstanceNumber', 0)),
                    'pixels': data['pixels']
                })

        if not series_images:
            return None

        # Sort by instance number
        series_images.sort(key=lambda x: x['instance_number'])

        # Stack into 3D volume
        volume = np.stack([img['pixels'] for img in series_images], axis=0)

        logger.info(f"Created 3D volume: shape={volume.shape}")

        return volume
