import os
import json
from typing import Dict, List
import redis.asyncio as redis
import numpy as np

class MetricsManager:
    """
    Persistent metrics storage using Redis (async).
    Tracks expert utilization and load balancing scores.
    """
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", 6379))
        self.redis = redis.Redis(host=self.host, port=self.port, decode_responses=True)
        self.experts = ["fia_expert", "sea_expert", "risk_expert", "escalate"]

    async def log_routing(self, selected_experts: List[str]):
        """Records routing decisions and increments expert usage counts"""
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.incr("metrics:total_signals")
            for expert in selected_experts:
                await pipe.hincrby("metrics:expert_load", expert, 1)
            await pipe.execute()

    async def get_load_balance_score(self) -> float:
        """Calculates standard deviation of load across all experts"""
        loads = await self.redis.hgetall("metrics:expert_load")
        counts = [int(loads.get(expert, 0)) for expert in self.experts]
        if not counts:
            return 0.0
        return float(np.std(counts))

    async def get_utilization_rates(self) -> Dict[str, float]:
        """Returns the percentage of total signals handled by each expert"""
        total = int(await self.redis.get("metrics:total_signals") or 1)
        loads = await self.redis.hgetall("metrics:expert_load")
        
        return {
            expert: int(loads.get(expert, 0)) / total 
            for expert in self.experts
        }

    async def close(self):
        await self.redis.close()
