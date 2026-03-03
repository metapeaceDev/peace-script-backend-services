"""
Video Generation Router

Handles:
- Video generation from Motion Editor settings
- Job status polling
- Video retrieval
- Generation queue management

Endpoints:
- POST /api/video/generate         - Start video generation
- GET  /api/video/jobs/{job_id}    - Get job status
- GET  /api/video/{video_id}       - Get video details
- DELETE /api/video/jobs/{job_id}  - Cancel job
- GET  /api/video/list             - List user videos
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os

from documents_video import (
    VideoGenerationJob, GeneratedVideo, 
    VideoStatus, VideoFormat, VideoQuality,
    MotionParameters, CameraSettings, LightingSettings, AISettings,
    VideoMetadata
)

router = APIRouter(prefix="/api/video", tags=["Video Generation"])


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateVideoRequest(BaseModel):
    """Request to generate video"""
    project_id: str
    shot_id: Optional[str] = None
    
    # ✨ NEW: Character Integration
    actor_id: Optional[str] = Field(default=None, description="Actor ID for character-based video generation")
    use_character_appearance: bool = Field(default=True, description="Use character appearance in prompt (if actor_id provided)")
    use_character_personality: bool = Field(default=False, description="Use character personality in prompt")
    use_character_mood: bool = Field(default=False, description="Use character emotional state in prompt")
    character_emotion: Optional[str] = Field(default=None, description="Character emotion (e.g., 'happy', 'sad', 'angry')")
    
    # Generation settings
    motion_parameters: Optional[MotionParameters] = None
    camera_settings: Optional[CameraSettings] = None
    lighting_settings: Optional[LightingSettings] = None
    ai_settings: Optional[AISettings] = None
    
    # Output settings
    quality: VideoQuality = VideoQuality.PREVIEW  # Default to fastest for testing
    format: VideoFormat = VideoFormat.MP4
    duration: float = Field(default=3.0, ge=1.0, le=30.0, description="Video duration in seconds")
    
    # Additional data
    prompt: Optional[str] = None
    style_preset: Optional[str] = None
    keyframes: Optional[List[Dict[str, Any]]] = None
    
    # Video mode
    mode: str = Field(default="image_to_video", description="Generation mode: image_to_video or animate_diff")
    
    # Custom quality overrides (optional - override preset values)
    custom_width: Optional[int] = Field(default=None, ge=256, le=3840, description="Override width (leave None to use preset)")
    custom_height: Optional[int] = Field(default=None, ge=144, le=2160, description="Override height (leave None to use preset)")
    custom_steps: Optional[int] = Field(default=None, ge=1, le=150, description="Override ComfyUI steps (leave None to use preset)")
    custom_fps: Optional[int] = Field(default=None, ge=12, le=60, description="Override FPS (leave None to use preset)")
    custom_num_images: Optional[int] = Field(default=None, ge=1, le=10, description="Override number of images (leave None to use preset)")


class GenerateVideoResponse(BaseModel):
    """Video generation job created"""
    job_id: str
    status: VideoStatus
    message: str
    estimated_time: Optional[int] = None  # seconds


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: VideoStatus
    progress: float
    status_message: Optional[str] = None
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class VideoResponse(BaseModel):
    """Video details response"""
    video_id: str
    job_id: str
    project_id: str
    shot_id: Optional[str] = None
    file_url: str
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    format: VideoFormat
    quality: VideoQuality
    metadata: Optional[VideoMetadata] = None
    tags: List[str] = []
    description: Optional[str] = None
    created_at: datetime
    views: int = 0
    downloads: int = 0


class VideoListResponse(BaseModel):
    """List of videos"""
    videos: List[VideoResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Background Tasks
# ============================================================================

async def process_video_generation(job_id: str):
    """
    Background task to generate video using ComfyUI + FFmpeg
    
    Supports 2 modes:
    1. image_to_video: ComfyUI images → FFmpeg video (fast, high control)
    2. animate_diff: AnimateDiff direct video (smooth motion)
    """
    import asyncio
    import traceback
    from modules.video_renderer import HybridVideoGenerator, VideoMode
    
    job = None
    try:
        print(f"\n{'='*60} - video_generation.py:139")
        print(f"🎬 VIDEO GENERATION JOB STARTED: {job_id} - video_generation.py:140")
        print(f"{'='*60}\n - video_generation.py:141")
        
        # Find job
        job = await VideoGenerationJob.find_one(VideoGenerationJob.job_id == job_id)
        if not job:
            print(f"❌ Job {job_id} not found in database - video_generation.py:146")
            return
        
        # Update to generating
        job.status = VideoStatus.GENERATING
        job.started_at = datetime.utcnow()
        job.progress = 5.0
        job.status_message = "Initializing video generator..."
        await job.save()
        print(f"✅ Job status updated to GENERATING - video_generation.py:154")
        
        # Initialize video generator
        print(f"🔧 Initializing HybridVideoGenerator... - video_generation.py:157")
        generator = HybridVideoGenerator(
            comfyui_url="http://127.0.0.1:8188",
            output_dir="/tmp/video_output"
        )
        print(f"✅ Generator initialized - video_generation.py:162")
        
        # Determine mode from AI settings
        ai_settings = job.ai_settings or {}
        mode = ai_settings.get("model") if isinstance(ai_settings, dict) else None
        
        # Map model to mode
        if mode == "animatediff":
            video_mode = VideoMode.ANIMATE_DIFF
        else:
            video_mode = VideoMode.IMAGE_TO_VIDEO  # Default
        
        # Extract settings from job
        user_prompt = job.input_settings.get("prompt", "cinematic scene") if job.input_settings else "cinematic scene"
        quality = job.input_settings.get("quality", "preview") if job.input_settings else "preview"
        
        # ✨ NEW: Character Integration - Build enhanced prompt if actor_id provided
        actor_id = job.input_settings.get("actor_id") if job.input_settings else None
        final_prompt = user_prompt  # Default to user prompt
        
        if actor_id:
            try:
                from modules.character_prompt_builder import CharacterPromptBuilder, CharacterPromptOptions
                from documents_actors import ActorProfile
                
                print(f"🎭 Character Integration: Building enhanced prompt for actor {actor_id}...")
                
                # Find actor
                actor = await ActorProfile.find_one({"actor_id": actor_id})
                if actor:
                    # Build character prompt
                    options = CharacterPromptOptions(
                        use_appearance=job.input_settings.get("use_character_appearance", True),
                        use_personality=job.input_settings.get("use_character_personality", False),
                        use_mood=job.input_settings.get("use_character_mood", False),
                        emotion=job.input_settings.get("character_emotion"),
                        style="realistic",
                        include_clothing=True,
                        include_expression=True
                    )
                    
                    builder = CharacterPromptBuilder()
                    result = await builder.build_prompt(
                        actor=actor,
                        user_prompt=user_prompt,
                        options=options
                    )
                    
                    final_prompt = result.positive_prompt
                    print(f"✅ Enhanced prompt built ({len(final_prompt)} chars)")
                    print(f"   Character: {result.character_name}")
                    print(f"   Preview: {final_prompt[:100]}...")
                else:
                    print(f"⚠️  Actor {actor_id} not found, using original prompt")
                    
            except Exception as e:
                print(f"⚠️  Failed to build character prompt: {e}")
                print(f"   Falling back to original prompt")
                import traceback
                traceback.print_exc()
        
        # Use final_prompt (either enhanced or original)
        prompt = final_prompt
        
        # Get custom overrides
        custom_width = job.input_settings.get("custom_width") if job.input_settings else None
        custom_height = job.input_settings.get("custom_height") if job.input_settings else None
        custom_steps = job.input_settings.get("custom_steps") if job.input_settings else None
        custom_fps = job.input_settings.get("custom_fps") if job.input_settings else None
        custom_num_images = job.input_settings.get("custom_num_images") if job.input_settings else None
        
        # Get quality preset info
        from modules.video_quality_presets import get_preset, estimate_generation_time
        try:
            preset = get_preset(quality)
            
            # Apply custom overrides or use preset defaults
            final_width = custom_width or preset.width
            final_height = custom_height or preset.height
            final_steps = custom_steps or preset.steps
            final_fps = custom_fps or preset.fps
            final_num_images = custom_num_images or preset.num_images
            
            estimated_time = estimate_generation_time(quality, preset.duration_per_image * final_num_images)
            
            print(f"📝 Settings: - video_generation.py:199")
            print(f"Prompt: {(prompt or 'default')[:50]}... - video_generation.py:200")
            print(f"Mode: {video_mode} - video_generation.py:201")
            print(f"Quality Preset: {quality} ({preset.name}) - video_generation.py:202")
            print(f"Resolution: {final_width}x{final_height} - video_generation.py:203" + (" [CUSTOM]" if custom_width or custom_height else ""))
            print(f"Steps: {final_steps} - video_generation.py:204" + (" [CUSTOM]" if custom_steps else ""))
            print(f"FPS: {final_fps} - video_generation.py:205" + (" [CUSTOM]" if custom_fps else ""))
            print(f"Images: {final_num_images} - video_generation.py:206" + (" [CUSTOM]" if custom_num_images else ""))
            print(f"Estimated time: ~{estimated_time}s - video_generation.py:207")
        except ValueError as e:
            print(f"⚠️  Invalid quality '{quality}', falling back to 'preview' - video_generation.py:209")
            quality = "preview"
            preset = get_preset(quality)
            final_width = custom_width or preset.width
            final_height = custom_height or preset.height
            final_steps = custom_steps or preset.steps
            final_fps = custom_fps or preset.fps
            final_num_images = custom_num_images or preset.num_images
            estimated_time = estimate_generation_time(quality, preset.duration_per_image * final_num_images)
        
        # Prepare motion parameters
        motion_params = None
        if job.motion_parameters:
            motion_params = {
                "zoom": job.motion_parameters.zoom,
                "pan_x": job.motion_parameters.pan_x,
                "pan_y": job.motion_parameters.pan_y,
                "speed": job.motion_parameters.speed
            }
            print(f"Motion: zoom={motion_params['zoom']}, pan=({motion_params['pan_x']}, {motion_params['pan_y']}) - video_generation.py:228")
        
        # Progress updates
        job.progress = 10.0
        job.status_message = f"Starting generation: {final_num_images} images at {final_width}x{final_height}"
        job.total_steps = final_num_images
        job.current_step = 0
        await job.save()
        
        # Define progress callback for real-time updates
        async def progress_callback(current_step: int, total_steps: int, message: str = ""):
            """Update job progress during video generation"""
            # Map steps to progress: 10% (start) → 80% (images done) → 90% (video assembled)
            progress_range = 70.0  # 10% to 80%
            progress = 10.0 + (progress_range * current_step / total_steps)
            job.progress = min(progress, 80.0)
            job.status_message = message or f"Generating image {current_step}/{total_steps}"
            job.current_step = current_step
            job.total_steps = total_steps
            await job.save()
            print(f"📊 Progress: {job.progress:.0f}%  [{current_step}/{total_steps}] {message} - video_generation.py:242")
        
        # Generate video with quality preset settings or custom overrides
        print(f"\n🎨 Starting video generation... - video_generation.py:245")
        print(f"Using: {final_width}x{final_height}, {final_steps} steps, {final_num_images} images - video_generation.py:246")
        
        # Calculate timeout
        timeout_seconds = max(600.0, estimated_time * 3)  # Increased to 10 mins min, or 3x estimate
        
        result = await asyncio.wait_for(
            generator.generate_video(
                mode=video_mode,
                prompt=prompt,
                negative_prompt="ugly, blurry, low quality, distorted",
                motion_params=motion_params,
                quality=quality,
                # Use final values (preset or custom overrides)
                num_images=final_num_images,
                duration_per_image=preset.duration_per_image,
                width=final_width,
                height=final_height,
                steps=final_steps,
                cfg=preset.cfg_scale,
                # Pass progress callback
                progress_callback=progress_callback
            ),
            timeout=timeout_seconds
        )
        print(f"✅ Video generation completed! - video_generation.py:270")
        
        job.progress = 90.0
        job.status_message = "Assembling video from images..."
        await job.save()
        print(f"📊 Progress: 90%  Creating database record... - video_generation.py:274")
        
        # Create video document
        video_id = f"vid_{uuid.uuid4().hex[:12]}"
        
        print(f"💾 Saving video metadata: - video_generation.py:279")
        print(f"Video ID: {video_id} - video_generation.py:280")
        print(f"File: {result.get('video_path', 'N/A')} - video_generation.py:281")
        print(f"Metadata: {result.get('metadata', {})} - video_generation.py:282")
        
        # Convert absolute path to API-accessible URL
        video_filename = os.path.basename(result["video_path"])
        api_video_url = f"/videos/{video_filename}"
        
        video = GeneratedVideo(
            video_id=video_id,
            job_id=job_id,
            project_id=job.project_id,
            shot_id=job.shot_id,
            file_url=api_video_url,
            thumbnail_url=None,  # TODO: Generate thumbnail
            format=VideoFormat.MP4,
            quality=VideoQuality.MEDIUM,
            metadata=VideoMetadata(
                width=result["metadata"].get("width", 512),
                height=result["metadata"].get("height", 512),
                fps=result["metadata"].get("fps", 24),
                duration=result["metadata"].get("duration", 2.0),
                codec=result["metadata"].get("codec", "h264"),
                file_size=result["metadata"].get("file_size", 0)
            ),
            generation_settings=job.input_settings,
            tags=[video_mode, "comfyui", "ai-generated"]
        )
        await video.insert()
        print(f"✅ Video document created in database - video_generation.py:309")
        
        # Update job
        job.status = VideoStatus.COMPLETE
        job.progress = 100.0
        job.output_video_id = video_id
        job.completed_at = datetime.utcnow()
        await job.save()
        
        print(f"\n{'='*60} - video_generation.py:318")
        print(f"✅ VIDEO GENERATION COMPLETE: {video_id} - video_generation.py:319")
        print(f"Mode: {video_mode} - video_generation.py:320")
        duration_seconds = (job.completed_at - job.started_at).total_seconds()
        print(f"Duration: {duration_seconds:.1f}s - video_generation.py:322")
        print(f"{'='*60}\n - video_generation.py:323")
        
    except asyncio.TimeoutError:
        error_msg = f"Video generation timeout (exceeded {timeout_seconds:.0f} seconds)"
        print(f"\n{'='*60} - video_generation.py:327")
        print(f"⏱️  TIMEOUT: {job_id} - video_generation.py:328")
        print(f"{'='*60}\n - video_generation.py:329")
        
        if job:
            job.status = VideoStatus.FAILED
            job.error_message = error_msg
            job.completed_at = datetime.utcnow()
            await job.save()
    
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n{'='*60} - video_generation.py:339")
        print(f"❌ VIDEO GENERATION FAILED: {job_id} - video_generation.py:340")
        print(f"Error: {error_msg} - video_generation.py:341")
        print(f"{'='*60} - video_generation.py:342")
        print(f"\nFull traceback: - video_generation.py:343")
        traceback.print_exc()
        print(f"{'='*60}\n - video_generation.py:345")
        
        if job:
            job.status = VideoStatus.FAILED
            job.error_message = error_msg[:500]  # จำกัดความยาว
            job.completed_at = datetime.utcnow()
            await job.save()
            print(f"💾 Job marked as FAILED in database - video_generation.py:352")


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/generate", response_model=GenerateVideoResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: GenerateVideoRequest,
    background_tasks: BackgroundTasks
):
    """
    Start video generation job.
    
    This creates a job and returns immediately.
    Use GET /api/video/jobs/{job_id} to poll status.
    
    Returns:
        job_id and estimated completion time
    """
    try:
        # Create job
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        # Prepare input settings
        input_settings = {
            "quality": request.quality,
            "format": request.format,
            "duration": request.duration,
            "prompt": request.prompt,
            "style_preset": request.style_preset,
            "keyframes": request.keyframes,
            "mode": request.mode,
            # Custom quality overrides
            "custom_width": request.custom_width,
            "custom_height": request.custom_height,
            "custom_steps": request.custom_steps,
            "custom_fps": request.custom_fps,
            "custom_num_images": request.custom_num_images
        }
        
        job = VideoGenerationJob(
            job_id=job_id,
            project_id=request.project_id,
            shot_id=request.shot_id,
            status=VideoStatus.QUEUED,
            input_settings=input_settings,
            motion_parameters=request.motion_parameters,
            camera_settings=request.camera_settings,
            lighting_settings=request.lighting_settings,
            ai_settings=request.ai_settings
        )
        
        await job.insert()
        
        # Queue background task
        print(f"🔥 DEBUG: Queueing background task for job_id: {job_id} - video_generation.py:409")
        background_tasks.add_task(process_video_generation, job_id)
        print(f"✅ DEBUG: Background task queued successfully - video_generation.py:411")
        
        return GenerateVideoResponse(
            job_id=job_id,
            status=VideoStatus.QUEUED,
            message="Video generation started",
            estimated_time=10  # 10 seconds for demo
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start video generation: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get video generation job status.
    
    Poll this endpoint to check generation progress.
    When status is COMPLETE, video_id and video_url will be available.
    """
    try:
        job = await VideoGenerationJob.find_one(VideoGenerationJob.job_id == job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        # Get video if complete
        video_url = None
        thumbnail_url = None
        if job.status == VideoStatus.COMPLETE and job.output_video_id:
            video = await GeneratedVideo.find_one(GeneratedVideo.video_id == job.output_video_id)
            if video:
                video_url = video.file_url
                thumbnail_url = video.thumbnail_url
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            status_message=job.status_message,
            current_step=job.current_step,
            total_steps=job.total_steps,
            video_id=job.output_video_id,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            error_message=job.error_message,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            estimated_completion=job.estimated_completion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/quality-presets")
async def get_quality_presets():
    """
    Get available quality presets for video generation.
    
    Returns information about all quality levels:
    - preview: Ultra-fast testing
    - low: Quick drafts
    - medium: Balanced quality/speed
    - high: High quality production
    - ultra: Maximum quality
    """
    from modules.video_quality_presets import get_preset_summary
    
    try:
        presets = get_preset_summary()
        
        return {
            "presets": presets,
            "default": "preview",
            "recommended": {
                "testing": "preview",
                "draft": "low",
                "production": "medium",
                "final": "high",
                "archive": "ultra"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quality presets: {str(e)}"
        )


@router.get("/videos", response_model=VideoListResponse)
async def list_videos(
    project_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    List generated videos.
    
    Filter by project_id if provided.
    Supports pagination.
    """
    print("🎬 [VIDEO] list_videos called! project_id= - video_generation.py:524", project_id, "page=", page)
    try:
        # Build filter
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        
        # Count total
        if filters:
            total = await GeneratedVideo.find(GeneratedVideo.project_id == project_id).count()
            videos = await GeneratedVideo.find(GeneratedVideo.project_id == project_id).skip((page - 1) * page_size).limit(page_size).to_list()
        else:
            total = await GeneratedVideo.find_all().count()
            videos = await GeneratedVideo.find_all().skip((page - 1) * page_size).limit(page_size).to_list()
        
        video_responses = [
            VideoResponse(
                video_id=v.video_id,
                job_id=v.job_id,
                project_id=v.project_id,
                shot_id=v.shot_id,
                file_url=v.file_url,
                thumbnail_url=v.thumbnail_url,
                preview_url=v.preview_url,
                format=v.format,
                quality=v.quality,
                metadata=v.metadata,
                tags=v.tags,
                description=v.description,
                created_at=v.created_at,
                views=v.views,
                downloads=v.downloads
            )
            for v in videos
        ]
        
        return VideoListResponse(
            videos=video_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list videos: {str(e)}"
        )


@router.get("/list", response_model=VideoListResponse)
async def list_videos_alias(
    project_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Alias for /videos to support frontend"""
    return await list_videos(project_id, page, page_size)


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get video details by ID"""
    try:
        video = await GeneratedVideo.find_one(GeneratedVideo.video_id == video_id)
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        # Increment view count
        video.views += 1
        await video.save()
        
        return VideoResponse(
            video_id=video.video_id,
            job_id=video.job_id,
            project_id=video.project_id,
            shot_id=video.shot_id,
            file_url=video.file_url,
            thumbnail_url=video.thumbnail_url,
            preview_url=video.preview_url,
            format=video.format,
            quality=video.quality,
            metadata=video.metadata,
            tags=video.tags,
            description=video.description,
            created_at=video.created_at,
            views=video.views,
            downloads=video.downloads
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get video: {str(e)}"
        )


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(job_id: str):
    """Cancel video generation job"""
    try:
        job = await VideoGenerationJob.find_one(VideoGenerationJob.job_id == job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        if job.status in [VideoStatus.COMPLETE, VideoStatus.FAILED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel job with status {job.status}"
            )
        
        job.status = VideoStatus.CANCELLED
        job.error_message = "Cancelled by user"
        await job.save()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {str(e)}"
        )


