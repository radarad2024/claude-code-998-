"""
Segmentation Models for Medical Imaging
U-Net, Attention U-Net, and variants for precise anatomical segmentation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""

    def __init__(self, in_channels: int, out_channels: int, mid_channels: int = None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels

        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling then double conv"""

    def __init__(self, in_channels: int, out_channels: int, bilinear: bool = True):
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # input is CHW
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class UNetSegmentation(nn.Module):
    """
    Standard U-Net architecture for medical image segmentation

    Segments organs, tumors, and anatomical structures
    """

    def __init__(self, n_channels: int = 1, n_classes: int = 2, bilinear: bool = True):
        super().__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear

        self.inc = DoubleConv(n_channels, 64)
        self.down1 = Down(64, 128)
        self.down2 = Down(128, 256)
        self.down3 = Down(256, 512)
        factor = 2 if bilinear else 1
        self.down4 = Down(512, 1024 // factor)

        self.up1 = Up(1024, 512 // factor, bilinear)
        self.up2 = Up(512, 256 // factor, bilinear)
        self.up3 = Up(256, 128 // factor, bilinear)
        self.up4 = Up(128, 64, bilinear)
        self.outc = OutConv(64, n_classes)

        logger.info(f"Initialized UNetSegmentation with {n_channels} input channels and {n_classes} classes")

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


class AttentionBlock(nn.Module):
    """
    Attention mechanism for U-Net
    Helps the model focus on relevant features
    """

    def __init__(self, F_g: int, F_l: int, F_int: int):
        super().__init__()

        self.W_g = nn.Sequential(
            nn.Conv2d(F_g, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )

        self.W_x = nn.Sequential(
            nn.Conv2d(F_l, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )

        self.psi = nn.Sequential(
            nn.Conv2d(F_int, 1, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(1),
            nn.Sigmoid()
        )

        self.relu = nn.ReLU(inplace=True)

    def forward(self, g, x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = self.relu(g1 + x1)
        psi = self.psi(psi)
        return x * psi


class AttentionUp(nn.Module):
    """Upscaling with attention mechanism"""

    def __init__(self, in_channels: int, out_channels: int, bilinear: bool = True):
        super().__init__()

        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

        self.attention = AttentionBlock(F_g=in_channels // 2, F_l=in_channels // 2, F_int=out_channels // 2)

    def forward(self, x1, x2):
        x1 = self.up(x1)

        # Attention
        x2 = self.attention(g=x1, x=x2)

        # Pad if necessary
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])

        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class AttentionUNet(nn.Module):
    """
    U-Net with attention mechanisms

    Better performance on complex segmentation tasks
    Particularly good for tumor and lesion segmentation
    """

    def __init__(self, n_channels: int = 1, n_classes: int = 2, bilinear: bool = True):
        super().__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear

        self.inc = DoubleConv(n_channels, 64)
        self.down1 = Down(64, 128)
        self.down2 = Down(128, 256)
        self.down3 = Down(256, 512)
        factor = 2 if bilinear else 1
        self.down4 = Down(512, 1024 // factor)

        self.up1 = AttentionUp(1024, 512 // factor, bilinear)
        self.up2 = AttentionUp(512, 256 // factor, bilinear)
        self.up3 = AttentionUp(256, 128 // factor, bilinear)
        self.up4 = AttentionUp(128, 64, bilinear)
        self.outc = OutConv(64, n_classes)

        logger.info(f"Initialized AttentionUNet with {n_channels} input channels and {n_classes} classes")

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


class ResUNet(nn.Module):
    """
    Residual U-Net for improved gradient flow

    Combines residual connections with U-Net architecture
    Better for very deep networks
    """

    def __init__(self, n_channels: int = 1, n_classes: int = 2):
        super().__init__()

        # Encoder
        self.enc1 = self._residual_block(n_channels, 64)
        self.enc2 = self._residual_block(64, 128)
        self.enc3 = self._residual_block(128, 256)
        self.enc4 = self._residual_block(256, 512)

        # Bridge
        self.bridge = self._residual_block(512, 1024)

        # Decoder
        self.dec4 = self._decoder_block(1024, 512)
        self.dec3 = self._decoder_block(512, 256)
        self.dec2 = self._decoder_block(256, 128)
        self.dec1 = self._decoder_block(128, 64)

        # Output
        self.out = nn.Conv2d(64, n_classes, kernel_size=1)

        logger.info(f"Initialized ResUNet with {n_channels} input channels and {n_classes} classes")

    def _residual_block(self, in_channels: int, out_channels: int):
        """Residual block"""
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def _decoder_block(self, in_channels: int, out_channels: int):
        """Decoder block with upsampling"""
        return nn.Sequential(
            nn.ConvTranspose2d(in_channels, out_channels, 2, stride=2),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            self._residual_block(out_channels, out_channels)
        )

    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(F.max_pool2d(enc1, 2))
        enc3 = self.enc3(F.max_pool2d(enc2, 2))
        enc4 = self.enc4(F.max_pool2d(enc3, 2))

        # Bridge
        bridge = self.bridge(F.max_pool2d(enc4, 2))

        # Decoder with skip connections
        dec4 = self.dec4(bridge) + enc4
        dec3 = self.dec3(dec4) + enc3
        dec2 = self.dec2(dec3) + enc2
        dec1 = self.dec1(dec2) + enc1

        return self.out(dec1)


class UNet3D(nn.Module):
    """
    3D U-Net for volumetric segmentation

    Used for CT and MRI volume segmentation
    """

    def __init__(self, in_channels: int = 1, n_classes: int = 2, base_n_filter: int = 8):
        super().__init__()

        self.in_channels = in_channels
        self.n_classes = n_classes

        # Encoder
        self.enc1 = self._conv3d_block(in_channels, base_n_filter)
        self.enc2 = self._conv3d_block(base_n_filter, base_n_filter * 2)
        self.enc3 = self._conv3d_block(base_n_filter * 2, base_n_filter * 4)
        self.enc4 = self._conv3d_block(base_n_filter * 4, base_n_filter * 8)

        # Bridge
        self.bridge = self._conv3d_block(base_n_filter * 8, base_n_filter * 16)

        # Decoder
        self.dec4 = self._upconv3d_block(base_n_filter * 16, base_n_filter * 8)
        self.dec3 = self._upconv3d_block(base_n_filter * 8, base_n_filter * 4)
        self.dec2 = self._upconv3d_block(base_n_filter * 4, base_n_filter * 2)
        self.dec1 = self._upconv3d_block(base_n_filter * 2, base_n_filter)

        # Output
        self.out = nn.Conv3d(base_n_filter, n_classes, kernel_size=1)

        logger.info(f"Initialized UNet3D with {in_channels} input channels and {n_classes} classes")

    def _conv3d_block(self, in_channels: int, out_channels: int):
        """3D convolutional block"""
        return nn.Sequential(
            nn.Conv3d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )

    def _upconv3d_block(self, in_channels: int, out_channels: int):
        """3D upsampling block"""
        return nn.Sequential(
            nn.ConvTranspose3d(in_channels, out_channels, 2, stride=2),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(F.max_pool3d(enc1, 2))
        enc3 = self.enc3(F.max_pool3d(enc2, 2))
        enc4 = self.enc4(F.max_pool3d(enc3, 2))

        # Bridge
        bridge = self.bridge(F.max_pool3d(enc4, 2))

        # Decoder with skip connections
        dec4 = self.dec4(bridge)
        dec4 = torch.cat([dec4, enc4], dim=1)

        dec3 = self.dec3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)

        dec2 = self.dec2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)

        dec1 = self.dec1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)

        return self.out(dec1)


# Segmentation task labels
SEGMENTATION_TASKS = {
    'lung': 'Lung parenchyma segmentation',
    'liver': 'Liver segmentation',
    'kidney': 'Kidney segmentation',
    'tumor': 'Tumor/lesion segmentation',
    'brain': 'Brain tissue segmentation',
    'cardiac': 'Cardiac chamber segmentation',
}
