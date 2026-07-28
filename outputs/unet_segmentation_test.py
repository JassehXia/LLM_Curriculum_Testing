"""
Unit Tests: Implement U-Net Architecture with Skip Connections
"""

import torch

model = UNet()
dummy_input = torch.randn(1, 3, 64, 64)
output = model(dummy_input)
assert output.shape == torch.Size([1, 64, 64, 64]), 'Output tensor shape is incorrect.'
