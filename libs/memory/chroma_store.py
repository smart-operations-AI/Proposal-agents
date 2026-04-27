import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

class ChromaStore:
    def __init__(self, path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="policies")

    def add_policy(self, tenant_id: str, policy_id: str, content: str, metadata: Dict[str, Any]):
        metadata["tenant_id"] = tenant_id
        metadata["policy_id"] = policy_id
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[f"{tenant_id}_{policy_id}"]
        )

    def query_policies(self, tenant_id: str, query_text: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"tenant_id": tenant_id}
        )
        return results

    def get_playbook(self, tenant_id: str, signal_type: str):
        results = self.collection.query(
            query_texts=[f"Playbook for {signal_type}"],
            n_results=1,
            where={"tenant_id": tenant_id, "type": "playbook"}
        )
        return results
