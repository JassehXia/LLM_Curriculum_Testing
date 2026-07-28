"""
Implement U-Net Architecture with Skip Connections

Instructions:
In this exercise, you will implement the U-Net architecture, which is commonly used for image segmentation tasks such as skin lesion boundary segmentation. The U-Net architecture consists of an encoder-decoder structure with skip connections that help preserve spatial information during the upsampling process. This is crucial for accurately segmenting fine details in images. Your task is to complete the missing parts in the provided starter code and write unit tests to ensure your implementation works correctly.
"""

from torch import nn
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

        # TODO: Implement skip connections and other layers
        # TODO: Ensure skip connections are used properly

    def forward(self, x):
        # TODO: Complete the forward pass using skip connections
        return x
