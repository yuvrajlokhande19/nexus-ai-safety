import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..config import settings
from .local_memory import local_memory

logger = logging.getLogger(__name__)


class MemoryStore:
    """Local file-based vector memory store - no external dependencies"""
    
    def __init__(self):
        self.client = local_memory
        logger.info("Local memory store initialized (no Docker required)")
    
    def store_persona_memory(
        self,
        persona_id: str,
        content: str,
        metadata: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ):
        """Store a memory for a persona"""
        self.client.store_persona_memory(persona_id, content, metadata)
    
    def retrieve_memories(
        self,
        persona_id: str,
        query: str,
        n_results: int = 5,
        embedding: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for a persona"""
        return self.client.retrieve_memories(persona_id, query, n_results)
    
    def store_experiment_log(self, experiment_id: str, data: Dict[str, Any]):
        """Store experiment log entry"""
        self.client.store_experiment_log(experiment_id, data)
    
    def get_experiment_logs(self, experiment_id: str, limit: int = 100) -> List[Dict]:
        """Retrieve experiment logs"""
        return self.client.get_experiment_logs(experiment_id, limit)


memory_store = MemoryStore()