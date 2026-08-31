import asyncio
import random
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import ollama
import google.generativeai as genai
from ..config import settings
from ..models import PersonaProfile

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    model_used: str
    tokens_used: int = 0
    latency_ms: int = 0


class LLMRouter:
    """Routes requests to local (Ollama) or remote (Gemini) models based on persona assignment"""
    
    def __init__(self):
        self.gemini_keys = settings.gemini_api_keys.copy()
        self.current_key_index = 0
        self.key_usage = {key: 0 for key in self.gemini_keys}
        self._init_gemini()
        self._init_ollama()
    
    def _init_gemini(self):
        if self.gemini_keys:
            genai.configure(api_key=self.gemini_keys[0])
            self.gemini_model = genai.GenerativeModel(settings.gemini_model)
        else:
            self.gemini_model = None
            logger.warning("No Gemini API keys configured")
    
    def _init_ollama(self):
        try:
            self.ollama_client = ollama.AsyncClient(host=settings.ollama_host)
            # Test connection
            asyncio.create_task(self._test_ollama())
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            self.ollama_client = None
    
    async def _test_ollama(self):
        try:
            models = await self.ollama_client.list()
            logger.info(f"Ollama models available: {[m['name'] for m in models.get('models', [])]}")
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self.ollama_client = None
    
    def _get_next_gemini_key(self) -> Optional[str]:
        """Round-robin with usage balancing"""
        if not self.gemini_keys:
            return None
        # Find least used key
        min_usage = min(self.key_usage.values())
        candidates = [k for k, v in self.key_usage.items() if v == min_usage]
        key = random.choice(candidates)
        self.key_usage[key] += 1
        return key
    
    async def generate(
        self,
        prompt: str,
        persona: PersonaProfile,
        temperature: float = 0.8,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate response using assigned model"""
        import time
        start = time.time()
        
        if persona.assigned_model == "local":
            return await self._generate_local(prompt, persona, temperature, max_tokens, system_prompt, start)
        else:
            return await self._generate_gemini(prompt, persona, temperature, max_tokens, system_prompt, start)
    
    async def _generate_local(
        self,
        prompt: str,
        persona: PersonaProfile,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str],
        start_time: float
    ) -> LLMResponse:
        if not self.ollama_client:
            # Fallback to Gemini if Ollama unavailable
            logger.warning("Ollama unavailable, falling back to Gemini")
            return await self._generate_gemini(prompt, persona, temperature, max_tokens, system_prompt, start_time)
        
        try:
            model = persona.llm_config.get("model", settings.ollama_model)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.ollama_client.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                }
            )
            
            content = response.get("message", {}).get("content", "")
            latency = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                content=content.strip(),
                model_used=f"ollama:{model}",
                tokens_used=response.get("eval_count", 0),
                latency_ms=latency
            )
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            # Fallback to Gemini
            return await self._generate_gemini(prompt, persona, temperature, max_tokens, system_prompt, start_time)
    
    async def _generate_gemini(
        self,
        prompt: str,
        persona: PersonaProfile,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str],
        start_time: float
    ) -> LLMResponse:
        if not self.gemini_model:
            raise RuntimeError("No Gemini API keys available")
        
        try:
            # Rotate key if needed
            key = self._get_next_gemini_key()
            if key and key != settings.gemini_api_keys[0]:
                genai.configure(api_key=key)
                self.gemini_model = genai.GenerativeModel(settings.gemini_model)
            
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.9,
                top_k=40,
            )
            
            response = await self.gemini_model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            
            content = response.text if response.text else ""
            latency = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                content=content.strip(),
                model_used=f"gemini:{settings.gemini_model}",
                tokens_used=0,  # Gemini doesn't return token count easily
                latency_ms=latency
            )
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            # Try next key
            if len(self.gemini_keys) > 1:
                self.current_key_index = (self.current_key_index + 1) % len(self.gemini_keys)
                genai.configure(api_key=self.gemini_keys[self.current_key_index])
                self.gemini_model = genai.GenerativeModel(settings.gemini_model)
                return await self._generate_gemini(prompt, persona, temperature, max_tokens, system_prompt, start_time)
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        persona: PersonaProfile,
        schema: Dict[str, Any],
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """Generate structured JSON output (Gemini only for now)"""
        if persona.assigned_model == "local":
            # For local, use prompt engineering to get JSON
            prompt += "\n\nOUTPUT ONLY VALID JSON. NO OTHER TEXT."
        
        response = await self.generate(prompt, persona, temperature, max_tokens)
        
        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Failed to parse structured output: {response.content}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "local_available": self.ollama_client is not None,
            "local_model": settings.ollama_model,
            "gemini_keys_count": len(self.gemini_keys),
            "gemini_model": settings.gemini_model,
            "key_usage": self.key_usage
        }


# Singleton instance
llm_router = LLMRouter()