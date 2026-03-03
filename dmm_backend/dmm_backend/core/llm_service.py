"""
Local LLM Service using Ollama (Free & Open Source)

This service provides AI text generation capabilities without API costs.
All models run locally on your machine using Ollama.

Installation:
    brew install ollama
    ollama serve
    ollama pull llama3.2:3b

Usage:
    from core.llm_service import get_ollama_service
    
    service = get_ollama_service()
    text = service.generate("เขียนชื่อภาพยนตร์ 5 ชื่อ")
    print(text)

Author: Peace Script Team
Date: 26 January 2025
"""

import requests
from typing import Optional, Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class OllamaService:
    """Service for interacting with local Ollama LLM models
    
    Ollama runs AI models locally on your machine, providing:
    - 100% free text generation
    - No API costs
    - Privacy (data stays local)
    - No rate limits
    - Offline capability
    
    Attributes:
        base_url: Ollama API endpoint (default: http://localhost:11434)
        default_model: Default model to use (llama3.2:3b)
    
    Example:
        ```python
        service = OllamaService()
        
        # Check if available
        if service.check_available():
            # Generate text
            text = service.generate("สวัสดีครับ")
            print(text)
        ```
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama service
        
        Args:
            base_url: Ollama API endpoint URL
        """
        self.base_url = base_url
        self.default_model = "llama3.2:3b"  # Best for Thai
        logger.info(f"OllamaService initialized with base_url={base_url}")
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text using Ollama
        
        Args:
            prompt: User prompt/question
            model: Model name (default: llama3.2:3b)
            temperature: Randomness 0.0-1.0 (higher = more creative)
            max_tokens: Maximum response length
            system_prompt: System instructions for the model
            
        Returns:
            Generated text string (empty if failed)
            
        Example:
            ```python
            text = service.generate(
                prompt="เขียนชื่อภาพยนตร์ 3 ชื่อ",
                temperature=0.8,
                max_tokens=200
            )
            ```
        """
        model = model or self.default_model
        
        # Build full prompt with system instructions
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        
        try:
            logger.info(f"Generating text with model={model}, prompt_length={len(prompt)}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            logger.info(f"Generated {len(generated_text)} characters")
            return generated_text
            
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running? Run: ollama serve")
            return ""
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout (60s)")
            return ""
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""
    
    def generate_scene_description(self, scene_title: str, context: str = "") -> str:
        """Generate scene description for Peace Script
        
        Creates a 2-3 sentence scene description in Thai,
        focusing on mood and atmosphere.
        
        Args:
            scene_title: Scene title/name
            context: Additional context (location, time, mood)
            
        Returns:
            Scene description in Thai (2-3 sentences)
            
        Example:
            ```python
            desc = service.generate_scene_description(
                scene_title="ฉากเปิดเรื่อง - จดหมายลึกลับ",
                context="ตอนกลางคืน บรรยากาศหม่นมัว"
            )
            # Output: "ในคืนที่มืดมน รินรดานั่งคนเดียวในห้องสมุดเก่า..."
            ```
        """
        system_prompt = """คุณคือนักเขียนบทภาพยนตร์มืออาชีพ 
เขียนคำบรรยายฉากภาพยนตร์แบบละเอียด สั้นกระชับ 2-3 ประโยค
ใช้ภาษาไทยที่สละสลวย เน้นความรู้สึกและบรรยากาศ
ไม่ต้องใส่หัวข้อ เขียนเฉพาะเนื้อหา"""
        
        prompt = f"เขียนคำบรรยายฉาก: {scene_title}"
        if context:
            prompt += f"\n\nบริบท: {context}"
        
        logger.info(f"Generating scene description for: {scene_title}")
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=200
        )
    
    def generate_character_background(
        self,
        name: str,
        role: str,
        personality: str
    ) -> str:
        """Generate character background story
        
        Creates a 3-4 sentence background story focusing on:
        - Past events
        - Motivations
        - Internal conflicts
        
        Args:
            name: Character name
            role: Character role (protagonist/antagonist/support)
            personality: Personality traits
            
        Returns:
            Character background story (3-4 sentences)
            
        Example:
            ```python
            bg = service.generate_character_background(
                name="รินรดา สมพงษ์",
                role="protagonist",
                personality="เข้มแข็ง แต่มีบาดแผลในใจ"
            )
            ```
        """
        system_prompt = """คุณคือนักเขียนตัวละคร 
เขียนประวัติตัวละครแบบกระชับ 3-4 ประโยค
เน้นที่อดีต แรงจูงใจ และความขัดแย้งภายใน
ใช้ภาษาไทยที่ลึกซึ้ง สร้างความรู้สึกเอาใจใส่"""
        
        prompt = f"""ชื่อ: {name}
บทบาท: {role}
บุคลิก: {personality}

เขียนประวัติตัวละคร:"""
        
        logger.info(f"Generating character background for: {name}")
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=300
        )
    
    def generate_image_prompt(
        self,
        shot_description: str,
        style: str = "cinematic"
    ) -> str:
        """Generate image prompt for Stable Diffusion
        
        Converts Thai shot description to English prompt suitable
        for image generation with quality keywords.
        
        Args:
            shot_description: Thai description of the shot
            style: Visual style (cinematic/anime/realistic/artistic)
            
        Returns:
            English image prompt with quality keywords
            
        Example:
            ```python
            prompt = service.generate_image_prompt(
                shot_description="แมนชันเก่าในตอนกลางคืน มืดมน น่ากลัว",
                style="cinematic"
            )
            # Output: "Old mansion at night, dark and eerie atmosphere,
            #          cinematic lighting, 4K, highly detailed..."
            ```
        """
        system_prompt = """คุณคือผู้เชี่ยวชาญ image prompt สำหรับ Stable Diffusion
แปลคำบรรยายภาษาไทยเป็น English prompt ที่มีคุณภาพ
เน้น: camera angle, lighting, mood, composition, quality keywords
ห้ามใส่คนหรือตัวละคร (no people)
เขียนเป็นประโยคเดียว คั่นด้วย comma"""
        
        prompt = f"""คำบรรยาย: {shot_description}
สไตล์: {style}

เขียน Stable Diffusion prompt (English, no people):"""
        
        logger.info(f"Generating image prompt for: {shot_description[:50]}...")
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model="codellama:7b",  # Better at English
            temperature=0.5,
            max_tokens=150
        )
    
    def generate_dialogue(
        self,
        character_name: str,
        situation: str,
        emotion: str,
        style: str = "natural"
    ) -> str:
        """Generate character dialogue
        
        Args:
            character_name: Character name
            situation: Current situation/context
            emotion: Character's emotional state
            style: Dialogue style (natural/formal/poetic)
            
        Returns:
            Generated dialogue (1-2 sentences)
            
        Example:
            ```python
            dialogue = service.generate_dialogue(
                character_name="รินรดา",
                situation="เห็นจดหมายลึกลับ",
                emotion="สงสัย กังวล"
            )
            ```
        """
        system_prompt = """คุณคือนักเขียนบทภาพยนตร์
เขียนบทสนทนาที่เป็นธรรมชาติ สั้นกระชับ 1-2 ประโยค
เหมาะกับตัวละครและสถานการณ์
เขียนเฉพาะคำพูด ไม่ต้องใส่ชื่อตัวละคร"""
        
        prompt = f"""ตัวละคร: {character_name}
สถานการณ์: {situation}
อารมณ์: {emotion}
สไตล์: {style}

เขียนบทสนทนา:"""
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=150
        )
    
    def check_available(self) -> bool:
        """Check if Ollama service is running
        
        Returns:
            True if Ollama is available, False otherwise
            
        Example:
            ```python
            if not service.check_available():
                print("Please run: ollama serve")
            ```
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            available = response.status_code == 200
            logger.info(f"Ollama available: {available}")
            return available
        except:
            logger.warning("Ollama not available (connection failed)")
            return False
    
    def list_models(self) -> List[str]:
        """List installed Ollama models
        
        Returns:
            List of model names
            
        Example:
            ```python
            models = service.list_models()
            print(f"Available models: {models}")
            # Output: ['llama3.2:3b', 'mistral:7b', 'codellama:7b']
            ```
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            logger.info(f"Found {len(models)} installed models")
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model: str) -> bool:
        """Download a model from Ollama library
        
        Args:
            model: Model name (e.g., "llama3.2:3b")
            
        Returns:
            True if successful
            
        Note:
            This is a synchronous operation and may take several minutes.
            Consider running this via CLI instead: `ollama pull model_name`
        """
        try:
            logger.info(f"Pulling model: {model}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                timeout=300  # 5 minutes
            )
            response.raise_for_status()
            logger.info(f"Model {model} pulled successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model}: {e}")
            return False


# ============================================================================
# Singleton Instance
# ============================================================================

_ollama_service: Optional[OllamaService] = None

def get_ollama_service() -> OllamaService:
    """Get or create OllamaService singleton instance
    
    Returns:
        OllamaService instance
        
    Example:
        ```python
        from core.llm_service import get_ollama_service
        
        service = get_ollama_service()
        text = service.generate("สวัสดีครับ")
        ```
    """
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
        logger.info("OllamaService singleton created")
    return _ollama_service


# ============================================================================
# Utility Functions
# ============================================================================

def is_ollama_available() -> bool:
    """Quick check if Ollama is available"""
    service = get_ollama_service()
    return service.check_available()


def get_available_models() -> List[str]:
    """Get list of available models"""
    service = get_ollama_service()
    return service.list_models()
