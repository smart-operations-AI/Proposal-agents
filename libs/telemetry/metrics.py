import json
import os
from typing import Dict, List
import numpy as np

class MetricsManager:
    def __init__(self, metrics_file: str = "expert_metrics.json"):
        self.metrics_file = metrics_file
        self.experts = ["fia_expert", "sea_expert", "risk_expert", "escalate"]
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.metrics_file):
            initial_data = {expert: 0 for expert in self.experts}
            initial_data["total_signals"] = 0
            with open(self.metrics_file, "w") as f:
                json.dump(initial_data, f)

    def log_routing(self, selected_experts: List[str]):
        with open(self.metrics_file, "r") as f:
            data = json.load(f)
        
        data["total_signals"] += 1
        for expert in selected_experts:
            if expert in data:
                data[expert] += 1
        
        with open(self.metrics_file, "w") as f:
            json.dump(data, f)

    def get_load_balance_score(self) -> float:
        """Standard deviation of load among experts"""
        with open(self.metrics_file, "r") as f:
            data = json.load(f)
        
        counts = [data[expert] for expert in self.experts]
        return float(np.std(counts))

    def get_utilization_rates(self) -> Dict[str, float]:
        with open(self.metrics_file, "r") as f:
            data = json.load(f)
        
        total = data.get("total_signals", 1)
        if total == 0: total = 1
        return {expert: data[expert] / total for expert in self.experts}
