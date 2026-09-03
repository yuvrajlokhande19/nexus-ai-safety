from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Ollama (Local)
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma4:latest"
    
    # Gemini API
    gemini_api_keys: List[str] = Field(default_factory=list)
    gemini_model: str = "gemini-3.6-flash"
    gemini_temperature: float = 0.8
    gemini_max_tokens: int = 8192
    
    # ChromaDB (Memory)
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "persona_memories"
    
    # GitHub
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    
    # Experiment
    max_personas: int = 15
    default_rounds: int = 20
    websocket_heartbeat: int = 30
    
    # Paths
    experiments_dir: str = "./experiments"
    exports_dir: str = "./exports"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


settings = Settings()