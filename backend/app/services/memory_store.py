import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config import settings
from ..models import PersonaState, Message, ResourceShare

logger = logging.getLogger(__name__)


class MemoryStore:
    """Vector memory store for cross-session persona memory"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._init_client()
    
    def _init_client(self):
        try:
            self.client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB connected: {self.collection.count()} documents")
        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}. Using in-memory fallback.")
            self.client = None
            self.collection = None
            self._memory_fallback = {}
    
    def store_persona_memory(
        self,
        persona_id: str,
        content: str,
        metadata: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ):
        """Store a memory for a persona"""
        doc_id = f"{persona_id}_{datetime.now().timestamp()}"
        
        if self.collection:
            try:
                self.collection.add(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[{**metadata, "persona_id": persona_id, "timestamp": datetime.now().isoformat()}],
                    embeddings=[embedding] if embedding else None
                )
            except Exception as e:
                logger.error(f"Failed to store memory: {e}")
        else:
            if persona_id not in self._memory_fallback:
                self._memory_fallback[persona_id] = []
            self._memory_fallback[persona_id].append({
                "id": doc_id,
                "content": content,
                "metadata": {**metadata, "persona_id": persona_id, "timestamp": datetime.now().isoformat()}
            })
    
    def retrieve_memories(
        self,
        persona_id: str,
        query: str,
        n_results: int = 5,
        embedding: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for a persona"""
        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query] if not embedding else None,
                    query_embeddings=[embedding] if embedding else None,
                    n_results=n_results,
                    where={"persona_id": persona_id}
                )
                memories = []
                for i in range(len(results['ids'][0])):
                    memories.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else 0
                    })
                return memories
            except Exception as e:
                logger.error(f"Failed to retrieve memories: {e}")
                return []
        else:
            # Fallback: simple text matching
            memories = self._memory_fallback.get(persona_id, [])
            # Simple relevance scoring
            scored = []
            query_lower = query.lower()
            for m in memories:
                score = sum(1 for word in query_lower.split() if word in m['content'].lower())
                scored.append((score, m))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [m for _, m in scored[:n_results]]
    
    def store_experiment_log(self, experiment_id: str, data: Dict[str, Any]):
        """Store experiment log entry"""
        if self.collection:
            try:
                self.collection.add(
                    ids=[f"exp_{experiment_id}_{datetime.now().timestamp()}"],
                    documents=[str(data)],
                    metadatas=[{
                        "type": "experiment_log",
                        "experiment_id": experiment_id,
                        "timestamp": datetime.now().isoformat()
                    }]
                )
            except Exception as e:
                logger.error(f"Failed to store experiment log: {e}")
    
    def get_experiment_logs(self, experiment_id: str, limit: int = 100) -> List[Dict]:
        """Retrieve experiment logs"""
        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[""],
                    n_results=limit,
                    where={"experiment_id": experiment_id, "type": "experiment_log"}
                )
                return [
                    {"id": results['ids'][0][i], "content": results['documents'][0][i], "metadata": results['metadatas'][0][i]}
                    for i in range(len(results['ids'][0]))
                ]
            except Exception as e:
                logger.error(f"Failed to retrieve experiment logs: {e}")
                return []
        return []


memory_store = MemoryStore()