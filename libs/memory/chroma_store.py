import chromadb
import asyncio
from chromadb.config import Settings
from typing import List, Dict, Any

class ChromaStore:
    """
    Asynchronous wrapper for ChromaDB semantic memory.
    Prevents blocking the event loop during heavy vector queries.
    """
    def __init__(self, path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="policies")

    async def add_policy(self, tenant_id: str, policy_id: str, content: str, metadata: Dict[str, Any]):
        loop = asyncio.get_event_loop()
        metadata["tenant_id"] = tenant_id
        metadata["policy_id"] = policy_id
        
        await loop.run_in_executor(
            None,
            self.collection.add,
            [content],
            None,
            [metadata],
            [f"{tenant_id}_{policy_id}"]
        )

    async def query_policies(self, tenant_id: str, query_text: str, n_results: int = 3, **kwargs):
        """Executes vector query in a thread pool to avoid blocking"""
        loop = asyncio.get_event_loop()
        
        where_filter = {"tenant_id": tenant_id}
        if "namespace" in kwargs:
             where_filter["namespace"] = kwargs["namespace"]
             
        results = await loop.run_in_executor(
            None,
            lambda: self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )
        )
        return results

    async def get_playbook(self, tenant_id: str, signal_type: str):
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.collection.query(
                query_texts=[f"Playbook for {signal_type}"],
                n_results=1,
                where={"tenant_id": tenant_id, "type": "playbook"}
            )
        )
        return results
