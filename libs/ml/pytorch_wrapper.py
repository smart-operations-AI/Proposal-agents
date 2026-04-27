import torch
import torch.nn as nn
from typing import Any, Dict

class RevenueModelWrapper:
    def __init__(self, model_path: str, model_class: Any):
        self.model = model_class()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def predict(self, features: torch.Tensor) -> float:
        with torch.no_grad():
            output = self.model(features)
            # Assuming single score output
            return output.item()

# Example simple model class
class ChurnModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.net(x)
