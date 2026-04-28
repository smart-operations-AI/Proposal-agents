import httpx
import os
import json
from typing import Dict, Any, List

class LocalInferenceEngine:
    """
    Interface for local LLM inference (e.g., Ollama, vLLM, or local FastAPI).
    Prevents dependency on external APIs like OpenAI/Gemini.
    """
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")

    async def chat(self, system_prompt: str, user_content: str) -> str:
        """Simulates or calls a local model"""
        # In a real environment, this would hit Ollama or a local vLLM instance
        # For this demonstration, we simulate the response to maintain local-first logic
        
        # Simulation logic for experts
        if "Financial" in system_prompt:
            return json.dumps({
                "action": "PROPOSE_DISCOUNT",
                "params": {"discount": 0.15, "roi_target": 2.5},
                "rationale": "High priority signal with positive churn trend."
            })
        elif "Sales" in system_prompt:
            return json.dumps({
                "action": "WHATSAPP_OUTREACH",
                "params": {"template": "retention_v1", "urgency": "high"},
                "rationale": "Urgent signal requiring immediate multi-channel contact."
            })
        
        return "Local model response placeholder"

    async def get_embeddings(self, text: str) -> List[float]:
        """Simulates local embeddings generation"""
        # Placeholder for local embedding model (e.g. sentence-transformers)
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()
        return [int(h[i:i+2], 16) / 255.0 for i in range(0, len(h), 2)]
