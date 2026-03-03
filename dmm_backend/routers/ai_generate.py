"""
AI Generation Router - Local LLM (Free & Open Source)

This router provides endpoints for AI text generation using local Ollama models.
All operations are 100% free with no API costs.

Prerequisites:
    1. Install Ollama: brew install ollama
    2. Start Ollama: ollama serve
    3. Download models: ollama pull llama3.2:3b

Endpoints:
    - GET  /api/ai/health - Check if Ollama is running
    - POST /api/ai/generate - General text generation
    - POST /api/ai/generate/scene - Generate scene description
    - POST /api/ai/generate/character - Generate character background
    - POST /api/ai/generate/image-prompt - Generate image prompt
    - POST /api/ai/generate/dialogue - Generate character dialogue

Author: Peace Script Team
Date: 26 January 2025
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from core.llm_service import get_ollama_service
from core.logging_config import get_logger

router = APIRouter(prefix="/api/ai", tags=["AI Generation (Free - Ollama)"])
logger = get_logger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateTextRequest(BaseModel):
    """Request for general text generation"""
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Text prompt for the AI model",
        example="เขียนชื่อภาพยนตร์ไทย 5 ชื่อ"
    )
    model: Optional[str] = Field(
        None,
        description="Model name (e.g., llama3.2:3b, mistral:7b)",
        example="llama3.2:3b"
    )
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Creativity level (0.0=deterministic, 1.0=creative)"
    )
    max_tokens: int = Field(
        500,
        ge=50,
        le=2000,
        description="Maximum response length in tokens"
    )
    system_prompt: Optional[str] = Field(
        None,
        description="System instructions for the model",
        example="คุณคือนักเขียนบทภาพยนตร์มืออาชีพ"
    )


class GenerateTextResponse(BaseModel):
    """Response with generated text"""
    text: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Model used for generation")
    prompt_length: int = Field(..., description="Length of input prompt")
    response_length: int = Field(..., description="Length of generated response")


class GenerateSceneRequest(BaseModel):
    """Request for scene description generation"""
    scene_title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Scene title or name",
        example="ฉากเปิดเรื่อง - จดหมายลึกลับ"
    )
    context: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional context (location, time, mood)",
        example="ตอนกลางคืน บรรยากาศหม่นมัว"
    )


class GenerateCharacterRequest(BaseModel):
    """Request for character background generation"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Character name",
        example="รินรดา สมพงษ์"
    )
    role: str = Field(
        ...,
        description="Character role",
        example="protagonist"
    )
    personality: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Personality traits",
        example="เข้มแข็ง แต่มีบาดแผลในใจ"
    )


class GenerateImagePromptRequest(BaseModel):
    """Request for image prompt generation (for Stable Diffusion)"""
    shot_description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Thai description of the shot",
        example="แมนชันเก่าในตอนกลางคืน มืดมน น่ากลัว"
    )
    style: str = Field(
        "cinematic",
        max_length=50,
        description="Visual style",
        example="cinematic"
    )


class GenerateDialogueRequest(BaseModel):
    """Request for character dialogue generation"""
    character_name: str = Field(
        ...,
        description="Character name",
        example="รินรดา"
    )
    situation: str = Field(
        ...,
        description="Current situation/context",
        example="เห็นจดหมายลึกลับบนโต๊ะ"
    )
    emotion: str = Field(
        ...,
        description="Character's emotional state",
        example="สงสัย กังวล"
    )
    style: str = Field(
        "natural",
        description="Dialogue style (natural/formal/poetic)",
        example="natural"
    )


class HealthResponse(BaseModel):
    """AI service health status"""
    available: bool = Field(..., description="Whether Ollama is running")
    models: List[str] = Field(..., description="List of installed models")
    default_model: str = Field(..., description="Default model name")
    message: str = Field(..., description="Status message")


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check AI Service Health",
    description="Check if Ollama service is running and list available models"
)
async def check_ai_health():
    """
    Check if Ollama service is available
    
    Returns:
        - available: True if Ollama is running
        - models: List of installed models
        - default_model: Default model name
        - message: Status message
        
    Example Response:
        ```json
        {
          "available": true,
          "models": ["llama3.2:3b", "codellama:7b"],
          "default_model": "llama3.2:3b",
          "message": "Ollama is running with 2 models"
        }
        ```
    """
    service = get_ollama_service()
    available = service.check_available()
    models = service.list_models() if available else []
    
    if available:
        message = f"Ollama is running with {len(models)} model(s)"
    else:
        message = "Ollama is not running. Run: ollama serve"
    
    return HealthResponse(
        available=available,
        models=models,
        default_model=service.default_model,
        message=message
    )


@router.post(
    "/generate",
    response_model=GenerateTextResponse,
    summary="Generate Text (Free)",
    description="Generate text using local Ollama LLM. 100% free, no API costs."
)
async def generate_text(request: GenerateTextRequest):
    """
    Generate text using local LLM (Free)
    
    This endpoint uses Ollama to generate text locally on your machine.
    No API costs, completely free, unlimited usage.
    
    Request Body:
        ```json
        {
          "prompt": "เขียนชื่อภาพยนตร์ไทย 5 ชื่อ",
          "model": "llama3.2:3b",
          "temperature": 0.8,
          "max_tokens": 300
        }
        ```
    
    Response:
        ```json
        {
          "text": "1. เงาแค้น\\n2. ลมหายใจสุดท้าย\\n3. ...",
          "model": "llama3.2:3b",
          "prompt_length": 35,
          "response_length": 120
        }
        ```
    
    Raises:
        503: Ollama service not available
        500: Text generation failed
    """
    service = get_ollama_service()
    
    # Check if Ollama is running
    if not service.check_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Ollama service not available",
                "message": "Please start Ollama service",
                "command": "ollama serve"
            }
        )
    
    # Generate text
    text = service.generate(
        prompt=request.prompt,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        system_prompt=request.system_prompt
    )
    
    # Check if generation failed
    if not text:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Text generation failed. Check Ollama logs."
        )
    
    return GenerateTextResponse(
        text=text,
        model=request.model or service.default_model,
        prompt_length=len(request.prompt),
        response_length=len(text)
    )


@router.post(
    "/generate/scene",
    response_model=GenerateTextResponse,
    summary="Generate Scene Description (Free)",
    description="Generate scene description for Peace Script. Optimized for Thai language."
)
async def generate_scene_description(request: GenerateSceneRequest):
    """
    Generate scene description for Peace Script (Free)
    
    Creates a 2-3 sentence scene description in Thai,
    focusing on mood, atmosphere, and visual details.
    
    Request Body:
        ```json
        {
          "scene_title": "ฉากเปิดเรื่อง - จดหมายลึกลับ",
          "context": "ตอนกลางคืน บรรยากาศหม่นมัว"
        }
        ```
    
    Response:
        ```json
        {
          "text": "ในคืนที่มืดมน รินรดานั่งคนเดียวในห้องสมุดเก่า...",
          "model": "llama3.2:3b",
          "prompt_length": 45,
          "response_length": 180
        }
        ```
    """
    service = get_ollama_service()
    
    if not service.check_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service not available. Run: ollama serve"
        )
    
    text = service.generate_scene_description(
        scene_title=request.scene_title,
        context=request.context or ""
    )
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scene generation failed"
        )
    
    return GenerateTextResponse(
        text=text,
        model=service.default_model,
        prompt_length=len(request.scene_title),
        response_length=len(text)
    )


@router.post(
    "/generate/character",
    response_model=GenerateTextResponse,
    summary="Generate Character Background (Free)",
    description="Generate character background story. Creates 3-4 sentences."
)
async def generate_character_background(request: GenerateCharacterRequest):
    """
    Generate character background story (Free)
    
    Creates a 3-4 sentence background story focusing on:
    - Past events that shaped the character
    - Current motivations and goals
    - Internal conflicts or trauma
    
    Request Body:
        ```json
        {
          "name": "รินรดา สมพงษ์",
          "role": "protagonist",
          "personality": "เข้มแข็ง แต่มีบาดแผลในใจ"
        }
        ```
    
    Response:
        ```json
        {
          "text": "รินรดาเติบโตมาในครอบครัวที่มีอิทธิพล...",
          "model": "llama3.2:3b",
          "prompt_length": 50,
          "response_length": 250
        }
        ```
    """
    service = get_ollama_service()
    
    if not service.check_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service not available"
        )
    
    text = service.generate_character_background(
        name=request.name,
        role=request.role,
        personality=request.personality
    )
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Character generation failed"
        )
    
    return GenerateTextResponse(
        text=text,
        model=service.default_model,
        prompt_length=len(request.name + request.personality),
        response_length=len(text)
    )


@router.post(
    "/generate/image-prompt",
    response_model=GenerateTextResponse,
    summary="Generate Image Prompt (Free)",
    description="Convert Thai description to English Stable Diffusion prompt"
)
async def generate_image_prompt(request: GenerateImagePromptRequest):
    """
    Generate image prompt for Stable Diffusion (Free)
    
    Converts Thai shot description to high-quality English prompt
    suitable for image generation with Stable Diffusion.
    
    Includes quality keywords like:
    - Camera angles
    - Lighting details
    - Mood and atmosphere
    - Quality tags (4K, highly detailed, etc.)
    
    Request Body:
        ```json
        {
          "shot_description": "แมนชันเก่าในตอนกลางคืน มืดมน น่ากลัว",
          "style": "cinematic"
        }
        ```
    
    Response:
        ```json
        {
          "text": "Old mansion at night, dark and eerie atmosphere, cinematic lighting, moonlight through broken windows, gothic architecture, 4K, highly detailed, dramatic shadows",
          "model": "codellama:7b",
          "prompt_length": 50,
          "response_length": 140
        }
        ```
    """
    service = get_ollama_service()
    
    if not service.check_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service not available"
        )
    
    text = service.generate_image_prompt(
        shot_description=request.shot_description,
        style=request.style
    )
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image prompt generation failed"
        )
    
    return GenerateTextResponse(
        text=text,
        model="codellama:7b",
        prompt_length=len(request.shot_description),
        response_length=len(text)
    )


@router.post(
    "/generate/dialogue",
    response_model=GenerateTextResponse,
    summary="Generate Character Dialogue (Free)",
    description="Generate natural character dialogue based on situation and emotion"
)
async def generate_dialogue(request: GenerateDialogueRequest):
    """
    Generate character dialogue (Free)
    
    Creates 1-2 sentences of natural dialogue appropriate for:
    - The character's personality
    - Current situation
    - Emotional state
    
    Request Body:
        ```json
        {
          "character_name": "รินรดา",
          "situation": "เห็นจดหมายลึกลับบนโต๊ะ",
          "emotion": "สงสัย กังวล",
          "style": "natural"
        }
        ```
    
    Response:
        ```json
        {
          "text": "นี่มัน... จดหมายจากใคร? ทำไมถึงมาถึงที่นี่ได้?",
          "model": "llama3.2:3b",
          "prompt_length": 60,
          "response_length": 45
        }
        ```
    """
    service = get_ollama_service()
    
    if not service.check_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service not available"
        )
    
    text = service.generate_dialogue(
        character_name=request.character_name,
        situation=request.situation,
        emotion=request.emotion,
        style=request.style
    )
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dialogue generation failed"
        )
    
    return GenerateTextResponse(
        text=text,
        model=service.default_model,
        prompt_length=len(request.situation),
        response_length=len(text)
    )
