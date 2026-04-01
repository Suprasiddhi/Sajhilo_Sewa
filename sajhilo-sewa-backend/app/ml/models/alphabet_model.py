import torch
import torch.nn as nn

class AlphabetModel(nn.Module):
    """
    A simple Multi-Layer Perceptron for static alphabet recognition.
    Input: 63 features (21 landmarks * 3 coordinates)
    Output: N classes (A-Z, space, del, nothing)
    """
    def __init__(self, input_size=63, num_classes=29):
        super(AlphabetModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(64, 32),
            nn.ReLU(),
            
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        # x shape: (batch, 63)
        return self.network(x)
