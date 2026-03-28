"""
ml/models/tcn_model.py
───────────────────────
Temporal Convolutional Network (TCN) for gesture recognition.

Input shape : (N, 63, 30)  — batch × features × time-steps
Output shape: (N, num_classes)

Architecture:
  - 4 causal residual blocks with exponentially growing dilation
  - Adaptive average pooling → MLP classifier
"""
import torch.nn as nn


class CausalConv1d(nn.Module):
    """
    1-D convolution that never looks into the future.
    Achieved by left-padding by (kernel_size-1)*dilation and then
    trimming the right tail of the output.
    """
    def __init__(self, in_channels, out_channels, kernel_size, dilation):
        super().__init__()
        self.padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(
            in_channels, out_channels, kernel_size,
            dilation=dilation, padding=self.padding
        )

    def forward(self, x):
        x = self.conv(x)
        # Remove future-leaking right padding
        return x[:, :, :-self.padding] if self.padding != 0 else x


class TCNResidualBlock(nn.Module):
    """
    Two stacked causal convolutions with BatchNorm, Dropout,
    and a skip connection that projects channels when needed.
    """
    def __init__(self, in_channels, out_channels, kernel_size, dilation, dropout=0.2):
        super().__init__()
        self.conv1    = CausalConv1d(in_channels,  out_channels, kernel_size, dilation)
        self.bn1      = nn.BatchNorm1d(out_channels)
        self.conv2    = CausalConv1d(out_channels, out_channels, kernel_size, dilation)
        self.bn2      = nn.BatchNorm1d(out_channels)
        self.drop     = nn.Dropout(dropout)
        self.residual = (
            nn.Conv1d(in_channels, out_channels, 1)
            if in_channels != out_channels else nn.Identity()
        )
        self.relu = nn.ReLU()

    def forward(self, x):
        res = self.residual(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.drop(out)
        out = self.relu(self.bn2(self.conv2(out)))
        out = self.drop(out)
        return self.relu(out + res)


class TCNModel(nn.Module):
    """
    Full TCN classifier.

    Args:
        input_size  : number of input features per time step (default 63)
        num_classes : number of gesture classes
        num_channels: list of out-channel sizes for each residual block
        kernel_size : convolution kernel width
        dropout     : dropout probability
    """
    def __init__(
        self,
        input_size=63,
        num_classes=14,
        num_channels=None,
        kernel_size=3,
        dropout=0.2,
    ):
        super().__init__()
        if num_channels is None:
            num_channels = [64, 128, 128, 256]

        layers = []
        in_ch = input_size
        for i, out_ch in enumerate(num_channels):
            layers.append(
                TCNResidualBlock(in_ch, out_ch, kernel_size, dilation=2**i, dropout=dropout)
            )
            in_ch = out_ch

        self.network = nn.Sequential(*layers)
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(num_channels[-1], 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        # x: (N, 63, 30)
        return self.classifier(self.network(x))