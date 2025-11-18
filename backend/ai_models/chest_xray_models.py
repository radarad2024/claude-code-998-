"""
Chest X-Ray Deep Learning Models
State-of-the-art models for thoracic pathology detection
"""

import torch
import torch.nn as nn
import timm
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ChestXRayEnsemble(nn.Module):
    """
    Ensemble of multiple architectures for robust chest X-ray analysis
    Combines EfficientNet, DenseNet, and ResNet
    """

    def __init__(
        self,
        num_classes: int = 14,
        pretrained: bool = True,
        ensemble_weights: List[float] = None
    ):
        super().__init__()

        self.num_classes = num_classes

        # Model 1: EfficientNet-B7
        self.efficientnet = timm.create_model(
            'efficientnet_b7',
            pretrained=pretrained,
            num_classes=num_classes
        )

        # Model 2: DenseNet-201
        self.densenet = timm.create_model(
            'densenet201',
            pretrained=pretrained,
            num_classes=num_classes
        )

        # Model 3: ResNet-152
        self.resnet = timm.create_model(
            'resnet152',
            pretrained=pretrained,
            num_classes=num_classes
        )

        # Ensemble weights
        self.ensemble_weights = ensemble_weights or [0.4, 0.35, 0.25]

        logger.info(f"Initialized ChestXRayEnsemble with {num_classes} classes")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through ensemble

        Args:
            x: Input tensor [B, C, H, W]

        Returns:
            Ensemble predictions [B, num_classes]
        """
        # Get predictions from each model
        pred_eff = torch.sigmoid(self.efficientnet(x))
        pred_dense = torch.sigmoid(self.densenet(x))
        pred_res = torch.sigmoid(self.resnet(x))

        # Weighted ensemble
        ensemble_pred = (
            self.ensemble_weights[0] * pred_eff +
            self.ensemble_weights[1] * pred_dense +
            self.ensemble_weights[2] * pred_res
        )

        return ensemble_pred

    def get_individual_predictions(
        self,
        x: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """Get predictions from individual models"""
        return {
            'efficientnet': torch.sigmoid(self.efficientnet(x)),
            'densenet': torch.sigmoid(self.densenet(x)),
            'resnet': torch.sigmoid(self.resnet(x))
        }


class ChestXRayDenseNet(nn.Module):
    """
    DenseNet-201 based chest X-ray classifier
    With attention mechanism for explainability
    """

    def __init__(self, num_classes: int = 14, pretrained: bool = True):
        super().__init__()

        # DenseNet backbone
        self.backbone = timm.create_model(
            'densenet201',
            pretrained=pretrained,
            features_only=True
        )

        # Get number of features
        with torch.no_grad():
            dummy_input = torch.randn(1, 3, 512, 512)
            features = self.backbone(dummy_input)
            num_features = features[-1].shape[1]

        # Global average pooling
        self.gap = nn.AdaptiveAvgPool2d(1)

        # Attention module
        self.attention = nn.Sequential(
            nn.Conv2d(num_features, num_features // 4, 1),
            nn.ReLU(),
            nn.Conv2d(num_features // 4, 1, 1),
            nn.Sigmoid()
        )

        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, num_classes)
        )

        logger.info(f"Initialized ChestXRayDenseNet with {num_classes} classes")

    def forward(
        self,
        x: torch.Tensor,
        return_attention: bool = False
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass with optional attention map

        Args:
            x: Input tensor
            return_attention: Whether to return attention map

        Returns:
            Predictions and optionally attention map
        """
        # Extract features
        features = self.backbone(x)[-1]

        # Apply attention
        attention_map = self.attention(features)
        attended_features = features * attention_map

        # Global pooling
        pooled = self.gap(attended_features)
        pooled = pooled.view(pooled.size(0), -1)

        # Classification
        output = self.classifier(pooled)

        if return_attention:
            return output, attention_map
        else:
            return output


class COVID19Detector(nn.Module):
    """
    Specialized model for COVID-19 detection in chest X-rays
    """

    def __init__(self, pretrained: bool = True):
        super().__init__()

        # Vision Transformer backbone
        self.backbone = timm.create_model(
            'vit_base_patch16_224',
            pretrained=pretrained,
            num_classes=0  # Remove classifier
        )

        num_features = self.backbone.num_features

        # COVID-specific classifier
        self.classifier = nn.Sequential(
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 3)  # Normal, Pneumonia, COVID-19
        )

        logger.info("Initialized COVID19Detector")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        features = self.backbone(x)
        output = self.classifier(features)
        return output


class PneumoniaDetector(nn.Module):
    """
    High-sensitivity pneumonia detection model
    """

    def __init__(self, pretrained: bool = True):
        super().__init__()

        # EfficientNet-B5 backbone
        self.model = timm.create_model(
            'efficientnet_b5',
            pretrained=pretrained,
            num_classes=1  # Binary classification
        )

        logger.info("Initialized PneumoniaDetector")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return torch.sigmoid(self.model(x))


# Pathology labels for chest X-ray models
CHEST_XRAY_LABELS = [
    'Atelectasis',
    'Cardiomegaly',
    'Consolidation',
    'Edema',
    'Effusion',
    'Emphysema',
    'Fibrosis',
    'Hernia',
    'Infiltration',
    'Mass',
    'Nodule',
    'Pleural_Thickening',
    'Pneumonia',
    'Pneumothorax'
]
