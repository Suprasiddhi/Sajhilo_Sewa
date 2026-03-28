"""
ml/models/stgcn_model.py
─────────────────────────
Spatial-Temporal Graph Convolutional Network (ST-GCN) for gesture recognition.

Input shape : (N, 3, 30, 21)  — batch × coords × time × joints
Output shape: (N, num_classes)

Architecture:
  - Graph convolution (spatial) over hand skeleton adjacency matrix
  - Temporal convolution (9×1) on joint features
  - 6 ST-GCN blocks with channel doubling and stride-2 downsampling
  - Global average pooling → MLP classifier
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from app.ml.config import HAND_CONNECTIONS, NUM_JOINTS


def build_adjacency_matrix(num_joints: int = NUM_JOINTS) -> np.ndarray:
    """
    Build a normalised adjacency matrix for the MediaPipe hand skeleton.

    D^{-1/2} A D^{-1/2}  (symmetric normalisation with self-loops)

    Returns: (21, 21) float32 numpy array
    """
    A = np.zeros((num_joints, num_joints), dtype=np.float32)
    for i, j in HAND_CONNECTIONS:
        A[i, j] = 1
        A[j, i] = 1
    A += np.eye(num_joints, dtype=np.float32)            # self-loops
    D = np.diag(A.sum(axis=1) ** -0.5)
    return (D @ A @ D).astype(np.float32)


class GraphConv(nn.Module):
    """
    Single graph convolution layer.
    Aggregates neighbour features using the fixed adjacency matrix A,
    then applies a 1×1 conv.
    """
    def __init__(self, in_channels: int, out_channels: int, A: np.ndarray):
        super().__init__()
        self.register_buffer("A", torch.FloatTensor(A))
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        self.bn   = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        # x: (N, C, T, V)
        out = torch.einsum("nctv,vw->nctw", x, self.A)
        return F.relu(self.bn(self.conv(out)))


class STGCNBlock(nn.Module):
    """
    One ST-GCN block = GraphConv (spatial) + Conv2d over time (temporal).

    Args:
        stride   : temporal stride; 2 = halve the time dimension
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        A: np.ndarray,
        stride: int = 1,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.gcn = GraphConv(in_channels, out_channels, A)
        self.tcn = nn.Sequential(
            nn.Conv2d(
                out_channels, out_channels,
                kernel_size=(9, 1), padding=(4, 0), stride=(stride, 1),
            ),
            nn.BatchNorm2d(out_channels),
            nn.Dropout(dropout),
        )
        self.residual = (
            nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=(stride, 1)),
                nn.BatchNorm2d(out_channels),
            )
            if in_channels != out_channels or stride != 1
            else nn.Identity()
        )
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.relu(self.tcn(self.gcn(x)) + self.residual(x))


class STGCNModel(nn.Module):
    """
    Full ST-GCN classifier.

    Args:
        in_channels : coordinate dimensions (default 3 — x, y, z)
        num_classes : gesture classes
        A           : adjacency matrix; built automatically if None
        dropout     : dropout probability
    """
    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 14,
        A: np.ndarray = None,
        dropout: float = 0.2,
    ):
        super().__init__()
        if A is None:
            A = build_adjacency_matrix()

        self.data_bn = nn.BatchNorm1d(in_channels * NUM_JOINTS)

        # (in_ch, out_ch, stride) — stride=2 halves time resolution
        block_cfg = [
            (in_channels, 64,  1),
            (64,          64,  1),
            (64,          128, 2),
            (128,         128, 1),
            (128,         256, 2),
            (256,         256, 1),
        ]
        self.blocks = nn.ModuleList(
            [STGCNBlock(i, o, A, s, dropout) for i, o, s in block_cfg]
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        # x: (N, 3, 30, 21)
        N, C, T, V = x.shape
        # BatchNorm over flattened joints×coords per frame
        x = self.data_bn(
            x.permute(0, 3, 1, 2).contiguous().view(N, V * C, T)
        )
        x = x.view(N, V, C, T).permute(0, 2, 3, 1).contiguous()  # (N,C,T,V)
        for block in self.blocks:
            x = block(x)
        return self.classifier(x)