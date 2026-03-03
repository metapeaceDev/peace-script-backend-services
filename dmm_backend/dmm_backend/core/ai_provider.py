"""
AI Provider Service - Multi-Provider Support

Supports multiple AI providers for character generation:
1. OpenAI GPT-4 (Paid, Best Quality)
2. Ollama Qwen2.5 (Free, Best Thai Support)
3. Ollama Llama 3.2 (Free, Lightweight)

Usage:
    provider = AIProviderService()
    result = await provider.generate_character(
        actor_name="อนุชา",
        character_bio="ชายไทย อายุ 30 ปี",
        provider="qwen2.5"  # or "gpt-4" or "llama3.2"
    )

Author: Peace Script Team
Date: 11 November 2568
"""

import os
import json
import httpx
from typing import Dict, Any, Optional, List
from openai import OpenAI
from core.logging_config import get_logger

logger = get_logger(__name__)


class AIProviderService:
    """
    Multi-Provider AI Service for Character Generation
    
    Supports:
    - OpenAI GPT-4 Turbo (gpt-4)
    - Ollama Qwen2.5:7b (qwen2.5) - Best Thai support
    - Ollama Llama 3.2:3b (llama3.2) - Lightweight
    """
    
    PROVIDERS = {
        "qwen2.5": {
            "name": "Qwen2.5:7b (Ollama)",
            "model": "qwen2.5:7b",
            "cost": "🆓 Free",
            "speed": "⚡⚡ Medium (5-10s)",
            "quality": "⭐⭐⭐⭐ Very Good",
            "thai_support": "⭐⭐⭐⭐⭐ Excellent",
            "type": "ollama"
        },
        "gpt-4": {
            "name": "OpenAI GPT-4 Turbo",
            "model": "gpt-4-turbo-preview",
            "cost": "💰 Paid (~$0.01/generation)",
            "speed": "⚡ Fast (3-5s)",
            "quality": "⭐⭐⭐⭐⭐ Excellent",
            "thai_support": "⭐⭐⭐⭐⭐ Excellent",
            "type": "openai"
        },
        "llama3.2": {
            "name": "Llama 3.2:3b (Ollama)",
            "model": "llama3.2:3b",
            "cost": "🆓 Free",
            "speed": "⚡⚡⚡ Slower (10-20s)",
            "quality": "⭐⭐⭐ Good",
            "thai_support": "⭐⭐ Limited",
            "type": "ollama"
        }
    }
    
    def __init__(self):
        """Initialize AI Provider Service"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        
        # Initialize OpenAI client if API key available
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            logger.info("✅ OpenAI client initialized")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not set - OpenAI provider disabled")
    
    async def check_provider_availability(self, provider: str) -> Dict[str, Any]:
        """
        Check if a provider is available and working
        
        Args:
            provider: Provider ID (gpt-4, qwen2.5, llama3.2)
            
        Returns:
            {
                "available": true/false,
                "provider": "qwen2.5",
                "name": "Qwen2.5:7b (Ollama)",
                "error": "..." (if not available)
            }
        """
        if provider not in self.PROVIDERS:
            return {
                "available": False,
                "provider": provider,
                "error": f"Unknown provider: {provider}"
            }
        
        provider_info = self.PROVIDERS[provider]
        
        # Check OpenAI
        if provider_info["type"] == "openai":
            if not self.openai_client:
                return {
                    "available": False,
                    "provider": provider,
                    "name": provider_info["name"],
                    "error": "OPENAI_API_KEY not configured"
                }
            return {
                "available": True,
                "provider": provider,
                "name": provider_info["name"],
                **provider_info
            }
        
        # Check Ollama
        if provider_info["type"] == "ollama":
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # Check if Ollama is running
                    response = await client.get(f"{self.ollama_base_url}/api/tags")
                    if response.status_code == 200:
                        models = response.json().get("models", [])
                        model_names = [m["name"] for m in models]
                        
                        # Check if specific model is downloaded
                        if provider_info["model"] in model_names:
                            return {
                                "available": True,
                                "provider": provider,
                                "name": provider_info["name"],
                                **provider_info
                            }
                        else:
                            return {
                                "available": False,
                                "provider": provider,
                                "name": provider_info["name"],
                                "error": f"Model '{provider_info['model']}' not downloaded. Run: ollama pull {provider_info['model']}"
                            }
                    else:
                        return {
                            "available": False,
                            "provider": provider,
                            "name": provider_info["name"],
                            "error": f"Ollama API error: {response.status_code}"
                        }
            except httpx.ConnectError:
                return {
                    "available": False,
                    "provider": provider,
                    "name": provider_info["name"],
                    "error": "Ollama not running. Start with: ollama serve"
                }
            except Exception as e:
                return {
                    "available": False,
                    "provider": provider,
                    "name": provider_info["name"],
                    "error": str(e)
                }
        
        return {
            "available": False,
            "provider": provider,
            "error": "Unknown provider type"
        }
    
    async def list_available_providers(self) -> List[Dict[str, Any]]:
        """
        List all available providers with their status
        
        Returns:
            [
                {
                    "provider": "qwen2.5",
                    "name": "Qwen2.5:7b (Ollama)",
                    "available": true,
                    "cost": "🆓 Free",
                    "speed": "⚡⚡ Medium",
                    ...
                },
                ...
            ]
        """
        results = []
        for provider_id in self.PROVIDERS.keys():
            status = await self.check_provider_availability(provider_id)
            results.append(status)
        
        logger.info(f"📊 Available providers: {[p['provider'] for p in results if p['available']]}")
        return results
    
    async def generate_character(
        self,
        actor_name: str,
        character_bio: Optional[str] = None,
        internal_character: Optional[Dict[str, Any]] = None,
        existing_external: Optional[Dict[str, Any]] = None,
        provider: str = "qwen2.5",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate character profile using specified AI provider
        
        Args:
            actor_name: Character's name
            character_bio: Character biography (optional)
            internal_character: Internal character data (optional)
            existing_external: Existing external character data (optional)
            provider: AI provider to use (gpt-4, qwen2.5, llama3.2)
            temperature: Creativity level (0.0-1.0)
            max_tokens: Max response length
            
        Returns:
            {
                "provider": "qwen2.5",
                "model": "qwen2.5:7b",
                "generated_data": { ... character fields ... },
                "generation_time": 5.2,
                "success": true
            }
        """
        import time
        start_time = time.time()
        
        # Check provider availability
        provider_status = await self.check_provider_availability(provider)
        if not provider_status["available"]:
            raise ValueError(f"Provider '{provider}' not available: {provider_status.get('error')}")
        
        provider_info = self.PROVIDERS[provider]
        
        # Build prompt
        prompt = self._build_character_prompt(
            actor_name=actor_name,
            character_bio=character_bio,
            internal_character=internal_character,
            existing_external=existing_external
        )
        
        logger.info(f"🤖 Generating character with provider: {provider_info['name']}")
        
        # Generate with appropriate provider
        if provider_info["type"] == "openai":
            generated_data = await self._generate_with_openai(
                prompt=prompt,
                model=provider_info["model"],
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider_info["type"] == "ollama":
            generated_data = await self._generate_with_ollama(
                prompt=prompt,
                model=provider_info["model"],
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_info['type']}")
        
        generation_time = time.time() - start_time
        
        return {
            "provider": provider,
            "provider_name": provider_info["name"],
            "model": provider_info["model"],
            "generated_data": generated_data,
            "generation_time": round(generation_time, 2),
            "success": True
        }
    
    def _build_character_prompt(
        self,
        actor_name: str,
        character_bio: Optional[str] = None,
        internal_character: Optional[Dict[str, Any]] = None,
        existing_external: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build comprehensive character generation prompt"""
        
        prompt = f"""คุณคือผู้เชี่ยวชาญด้านการสร้างตัวละคร 3D และการออกแบบบุคลิกภาพ

สร้างข้อมูลภายนอก (External Character) สำหรับตัวละครชื่อ "{actor_name}"

"""
        
        if character_bio:
            prompt += f"""ประวัติตัวละคร:
{character_bio}

"""
        
        if internal_character:
            prompt += f"""บุคลิกภาพภายใน:
- ค่านิยมหลัก: {internal_character.get('core_values', [])}
- แรงจูงใจ: {internal_character.get('motivations', [])}
- ความกลัว: {internal_character.get('fears', [])}

"""
        
        prompt += """กรุณาสร้างข้อมูลในรูปแบบ JSON โดย return เฉพาะ object เดียว ที่มี key-value pairs ต่อไปนี้:

{
  "age": 30,
  "gender": "male",
  "ethnicity": "Thai",
  "height": 175.0,
  "weight": 70.0,
  "body_type": "athletic",
  "fitness_level": 7.5,
  "face_shape": "oval",
  "eye_color": "dark brown",
  "eye_expression": "warm",
  "hair_color": "black",
  "hair_style": "short",
  "skin_tone": "medium",
  "smile_type": "confident",
  "fashion_style": "casual",
  "color_palette": ["blue", "white", "grey"],
  "accessories": ["watch", "sunglasses"],
  "posture": "upright",
  "gait": "confident",
  "voice_tone": "medium",
  "voice_characteristics": ["clear", "warm"],
  "speech_pattern": "thoughtful",
  "accent": "Central Thai",
  "first_impression": "friendly and approachable",
  "charisma_level": 7.0,
  "approachability": 8.0
}

**IMPORTANT:** 
- Return ONLY the JSON object, no markdown, no explanations
- Do NOT group fields under headers like "ข้อมูลพื้นฐาน", "ใบหน้า", etc.
- All fields should be at the TOP LEVEL of the JSON object
- Use the EXACT field names shown above (in English)
- Fill ALL fields with appropriate values based on the character description
- Numeric fields (fitness_level, charisma_level, approachability) must be numbers 0-10
"""
        
        return prompt
    
    async def _generate_with_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Generate using OpenAI GPT-4"""
        
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert character designer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI returned empty content")
            
            data = json.loads(content)
            
            logger.info(f"✅ OpenAI generated {len(data)} fields")
            return data
            
        except Exception as e:
            logger.error(f"❌ OpenAI generation failed: {e}")
            raise
    
    async def _generate_with_ollama(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Generate using Ollama local LLM"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise ValueError(f"Ollama API error: {response.status_code} - {response.text}")
                
                result = response.json()
                content = result.get("response", "{}")
                
                # Parse JSON response
                data = json.loads(content)
                
                logger.info(f"✅ Ollama ({model}) generated {len(data)} fields")
                return data
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ollama returned invalid JSON: {e}")
            raise ValueError(f"Ollama response was not valid JSON: {content[:200]}")
        except Exception as e:
            logger.error(f"❌ Ollama generation failed: {e}")
            raise


# Global instance
_ai_provider_service = None

def get_ai_provider_service() -> AIProviderService:
    """Get or create global AIProviderService instance"""
    global _ai_provider_service
    if _ai_provider_service is None:
        _ai_provider_service = AIProviderService()
    return _ai_provider_service
