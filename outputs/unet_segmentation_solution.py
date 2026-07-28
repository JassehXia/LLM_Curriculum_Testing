"""
Solution: Implement U-Net Architecture with Skip Connections
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()

        # Encoder
        self.encoder1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Decoder
        self.decoder1 = nn.Sequential(
            nn.ConvTranspose2d(64, 64, kernel_size=2, stride=2),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )

        # Skip connection
        self.skip_connection1 = nn.Sequential(
            nn.Conv2d(128, 64, kernel_size=1),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        # Encoder path
        x1 = self.encoder1(x)
        x = self.pool(x1)

        # Decoder path with skip connections
        x = self.decoder1(x)
        x = torch.cat([x, x1], dim=1)
        x = self.skip_connection1(x)

        return x
