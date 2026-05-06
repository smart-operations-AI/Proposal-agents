import httpx
import os
import json
import asyncio
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer

class LocalInferenceEngine:
    """
    Real local LLM inference engine using Ollama for chat and 
    SentenceTransformers for embeddings.
    """
    def __init__(self, model_name: str = "llama3:8b", embedding_model: str = "all-MiniLM-L6-v2"):
        self.ollama_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/chat")
        self.model_name = model_name
        self.embedding_model_name = embedding_model
        # Load embedding model once
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

    async def chat(self, system_prompt: str, user_content: str) -> str:
        """Calls Ollama Chat API for local inference"""
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "stream": False,
            "format": "json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.ollama_url, json=payload, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                # Return content from message object
                return result.get("message", {}).get("content", "{}")
            except Exception as e:
                return json.dumps({"error": str(e), "action": "ERROR", "params": {}})

    async def get_embeddings(self, text: str) -> List[float]:
        """Generates real semantic embeddings using SentenceTransformers without blocking"""
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, 
            self.embedding_model.encode, 
            text
        )
        return embeddings.tolist()
