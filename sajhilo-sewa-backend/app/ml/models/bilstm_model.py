"""
ml/models/bilstm_model.py
──────────────────────────
Bidirectional LSTM with Temporal Attention for gesture recognition.

Input shape : (N, 30, 63)  — batch × time-steps × features
Output shape: (N, num_classes)

Architecture:
  - Linear input projection + LayerNorm
  - Stacked BiLSTM layers
  - Temporal attention pooling (replaces simple last-step or mean-pool)
  - 3-layer MLP classifier
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class TemporalAttention(nn.Module):
    """
    Soft attention over the time dimension.
    Learns which frames matter most for classification.

    Input : lstm_out  (B, T, hidden_dim)
    Output: context   (B, hidden_dim)   ← weighted sum of frames
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, lstm_out):
        # weights: (B, T, 1)
        weights = F.softmax(self.attn(lstm_out), dim=1)
        # weighted sum over time → (B, hidden_dim)
        return (weights * lstm_out).sum(dim=1)


class BiLSTMModel(nn.Module):
    """
    Bidirectional LSTM classifier.

    Args:
        input_size  : features per time step (default 63)
        hidden_size : LSTM hidden units per direction (default 256)
        num_layers  : number of stacked LSTM layers (default 2)
        num_classes : gesture classes
        dropout     : dropout probability
    """
    def __init__(
        self,
        input_size=63,
        hidden_size=256,
        num_layers=2,
        num_classes=14,
        dropout=0.3,
    ):
        super().__init__()

        # Project raw 63-dim input to a richer 128-dim space
        self.input_proj = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
        )

        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )

        self.attention  = TemporalAttention(hidden_size * 2)   # *2 for bidirectional
        self.dropout    = nn.Dropout(dropout)

        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 256), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(256, 128),            nn.ReLU(), nn.Dropout(dropout * 0.5),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        # x: (N, 30, 63)
        x   = self.input_proj(x)          # (N, 30, 128)
        out, _ = self.lstm(x)             # (N, 30, hidden*2)
        ctx = self.attention(out)         # (N, hidden*2)
        return self.classifier(self.dropout(ctx))