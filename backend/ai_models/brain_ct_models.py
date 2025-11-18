"""
Brain CT Deep Learning Models
Models for hemorrhage detection and brain pathology classification
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class BrainCTModel(nn.Module):
    """
    3D CNN for brain CT analysis
    Detects intracranial hemorrhages and other pathologies
    """

    def __init__(self, num_classes: int = 5, in_channels: int = 1):
        super().__init__()

        # 3D Convolutional blocks
        self.conv1 = self._conv_block(in_channels, 32)
        self.conv2 = self._conv_block(32, 64)
        self.conv3 = self._conv_block(64, 128)
        self.conv4 = self._conv_block(128, 256)

        self.pool = nn.MaxPool3d(2)
        self.dropout = nn.Dropout3d(0.3)

        # Global average pooling
        self.gap = nn.AdaptiveAvgPool3d(1)

        # Classifier
        self.fc = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

        logger.info(f"Initialized BrainCTModel with {num_classes} classes")

    def _conv_block(self, in_channels: int, out_channels: int) -> nn.Module:
        """Create a 3D convolutional block"""
        return nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass

        Args:
            x: Input tensor [B, 1, D, H, W]

        Returns:
            Predictions [B, num_classes]
        """
        x = self.pool(self.conv1(x))
        x = self.dropout(x)

        x = self.pool(self.conv2(x))
        x = self.dropout(x)

        x = self.pool(self.conv3(x))
        x = self.dropout(x)

        x = self.pool(self.conv4(x))

        # Global pooling
        x = self.gap(x)
        x = x.view(x.size(0), -1)

        # Classification
        x = self.fc(x)

        return x


class HemorrhageDetector(nn.Module):
    """
    Specialized model for intracranial hemorrhage detection
    Multi-task learning for hemorrhage type classification
    """

    def __init__(self):
        super().__init__()

        # Shared feature extractor
        self.features = nn.Sequential(
            self._conv_block_3d(1, 32),
            nn.MaxPool3d(2),
            self._conv_block_3d(32, 64),
            nn.MaxPool3d(2),
            self._conv_block_3d(64, 128),
            nn.MaxPool3d(2),
            self._conv_block_3d(128, 256),
            nn.MaxPool3d(2)
        )

        # Global pooling
        self.gap = nn.AdaptiveAvgPool3d(1)

        # Task 1: Hemorrhage presence (binary)
        self.hemorrhage_classifier = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1)  # Binary: hemorrhage yes/no
        )

        # Task 2: Hemorrhage type classification
        self.type_classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 5)  # 5 hemorrhage types
        )

        # Task 3: Urgency classification
        self.urgency_classifier = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 3)  # Low, medium, high urgency
        )

        logger.info("Initialized HemorrhageDetector")

    def _conv_block_3d(self, in_ch: int, out_ch: int) -> nn.Module:
        """3D convolutional block"""
        return nn.Sequential(
            nn.Conv3d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm3d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm3d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass with multi-task outputs

        Returns:
            (hemorrhage_presence, hemorrhage_type, urgency)
        """
        # Extract features
        features = self.features(x)
        features = self.gap(features)
        features = features.view(features.size(0), -1)

        # Multi-task predictions
        hemorrhage_present = self.hemorrhage_classifier(features)
        hemorrhage_type = self.type_classifier(features)
        urgency = self.urgency_classifier(features)

        return hemorrhage_present, hemorrhage_type, urgency


class StrokeDetector(nn.Module):
    """
    Acute stroke detection model
    Detects ischemic and hemorrhagic stroke
    """

    def __init__(self):
        super().__init__()

        # 3D ResNet-like architecture
        self.conv1 = nn.Conv3d(1, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm3d(64)
        self.pool1 = nn.MaxPool3d(3, stride=2, padding=1)

        # Residual blocks
        self.layer1 = self._make_layer(64, 64, 2)
        self.layer2 = self._make_layer(64, 128, 2, stride=2)
        self.layer3 = self._make_layer(128, 256, 2, stride=2)

        self.gap = nn.AdaptiveAvgPool3d(1)

        # Classifier
        self.fc = nn.Linear(256, 3)  # Normal, Ischemic, Hemorrhagic

        logger.info("Initialized StrokeDetector")

    def _make_layer(
        self,
        in_channels: int,
        out_channels: int,
        blocks: int,
        stride: int = 1
    ) -> nn.Module:
        """Create residual layer"""
        layers = []
        layers.append(ResidualBlock3D(in_channels, out_channels, stride))
        for _ in range(1, blocks):
            layers.append(ResidualBlock3D(out_channels, out_channels))
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)

        x = self.gap(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x


class ResidualBlock3D(nn.Module):
    """3D Residual Block"""

    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()

        self.conv1 = nn.Conv3d(
            in_channels, out_channels, 3, stride=stride, padding=1
        )
        self.bn1 = nn.BatchNorm3d(out_channels)

        self.conv2 = nn.Conv3d(out_channels, out_channels, 3, padding=1)
        self.bn2 = nn.BatchNorm3d(out_channels)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv3d(in_channels, out_channels, 1, stride=stride),
                nn.BatchNorm3d(out_channels)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out


# Hemorrhage type labels
HEMORRHAGE_LABELS = [
    'Epidural',
    'Intraparenchymal',
    'Intraventricular',
    'Subarachnoid',
    'Subdural'
]
