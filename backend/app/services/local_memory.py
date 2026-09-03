import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalMemoryStore:
    """Local file-based vector memory store - no Docker required"""
    
    def __init__(self, storage_dir: str = "./memory_store"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self.vectors_file = self.storage_dir / "vectors.npy"
        self.metadata_file = self.storage_dir / "metadata.json"
        
        # Load or initialize
        self._load()
    
    def _load(self):
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {"documents": [], "next_id": 0}
        
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
        
        if self.vectors_file.exists():
            self.vectors = np.load(self.vectors_file)
        else:
            self.vectors = np.array([]).reshape(0, 384)  # Default embedding dim
    
    def _save(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f)
        if len(self.vectors) > 0:
            np.save(self.vectors_file, self.vectors)
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Simple hash-based embedding for demo - replace with real embeddings"""
        # Use a simple deterministic hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # Expand to 384 dimensions
        vec = np.frombuffer(hash_bytes * 24, dtype=np.uint8)[:384].astype(np.float32)
        return vec / 255.0
    
    def store_persona_memory(
        self,
        persona_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        """Store a memory for a persona"""
        embedding = self._get_embedding(content)
        doc_id = self.index["next_id"]
        self.index["next_id"] += 1
        
        doc_entry = {
            "id": doc_id,
            "persona_id": persona_id,
            "content": content,
            "metadata": {**metadata, "persona_id": persona_id, "timestamp": datetime.now().isoformat()},
            "embedding_index": len(self.vectors)
        }
        self.index["documents"].append(doc_entry)
        
        # Add vector
        if len(self.vectors) == 0:
            self.vectors = embedding.reshape(1, -1)
        else:
            self.vectors = np.vstack([self.vectors, embedding.reshape(1, -1)])
        
        self._save()
    
    def retrieve_memories(
        self,
        persona_id: str,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for a persona"""
        if len(self.vectors) == 0:
            return []
        
        query_embedding = self._get_embedding(query)
        
        # Simple cosine similarity
        similarities = np.dot(self.vectors, query_embedding) / (
            np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(query_embedding) + 1e-8
        )
        
        # Get top results for this persona
        persona_docs = [d for d in self.index["documents"] if d["persona_id"] == persona_id]
        if not persona_docs:
            return []
        
        persona_indices = [d["embedding_index"] for d in persona_docs]
        persona_sims = similarities[persona_indices]
        
        top_indices = np.argsort(persona_sims)[-n_results:][::-1]
        
        results = []
        for idx in top_indices:
            doc = persona_docs[idx]
            results.append({
                "id": str(doc["id"]),
                "content": doc["content"],
                "metadata": doc["metadata"],
                "distance": float(1 - persona_sims[idx])
            })
        
        return results
    
    def store_experiment_log(self, experiment_id: str, data: Dict[str, Any]):
        key = f"exp_{experiment_id}_{datetime.now().timestamp()}"
        self.metadata[key] = {"type": "experiment_log", "experiment_id": experiment_id, **data}
        self._save()
    
    def get_experiment_logs(self, experiment_id: str, limit: int = 100) -> List[Dict]:
        logs = []
        for key, val in self.metadata.items():
            if val.get("type") == "experiment_log" and val.get("experiment_id") == experiment_id:
                logs.append({"id": key, **val})
        return sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]


# Global instance
local_memory = LocalMemoryStore()