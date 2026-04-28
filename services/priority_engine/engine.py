from typing import List
from libs.contracts.models import InternalSignal, SignalType

class PriorityEngine:
    @staticmethod
    def rank_signals(signals: List[InternalSignal]) -> List[InternalSignal]:
        """
        Rank signals based on impact, urgency and business rules.
        """
        # 1. Rule-based Conflict Resolution
        # PAYMENT_RISK always takes precedence
        payment_risks = [s for s in signals if s.signal_type == SignalType.PAYMENT_RISK]
        if payment_risks:
            # If payment risk exists, we might want to suppress other expansion signals
            return sorted(payment_risks, key=lambda x: x.priority_score, reverse=True)

        # 2. ROI / Impact Sorting
        return sorted(signals, key=lambda x: (x.priority_score, x.estimated_revenue_impact), reverse=True)

    @staticmethod
    def calculate_roi(signal: InternalSignal, execution_cost: float) -> float:
        """Calculate ROI based on provided execution cost."""
        if execution_cost == 0: return 0
        return (signal.estimated_revenue_impact - execution_cost) / execution_cost
