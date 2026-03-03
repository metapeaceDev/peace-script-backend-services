"""
🎬 Video Renderer Module - Hybrid Video Generation System

Supports 2 modes:
1. Image-to-Video: ComfyUI images → FFmpeg video (Ken Burns effect)
2. AnimateDiff: Direct video generation with ComfyUI AnimateDiff/SVD nodes

Features:
- ComfyUI integration for AI image/video generation
- FFmpeg video assembly with motion effects
- Ken Burns effect (zoom, pan, tilt)
- AnimateDiff workflow support
- Stable Video Diffusion (SVD) support
- Progress tracking
- Multiple output formats (MP4, WebM)

Author: Peace Script Team
Date: 20 November 2025
Version: 1.0.0
"""

import os
import asyncio
import subprocess
import json
import uuid
from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path
from datetime import datetime

from modules.comfyui_client import ComfyUIClient, WorkflowBuilder
from modules.video_quality_presets import get_preset, QualityPreset
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# VIDEO GENERATION MODES
# =============================================================================

class VideoMode:
    """Video generation modes"""
    IMAGE_TO_VIDEO = "image_to_video"  # ComfyUI images → FFmpeg video
    ANIMATE_DIFF = "animate_diff"      # AnimateDiff direct video
    SVD = "svd"                        # Stable Video Diffusion


# =============================================================================
# FFMPEG VIDEO ASSEMBLER
# =============================================================================

class FFmpegVideoAssembler:
    """
    Assemble video from images using FFmpeg with motion effects
    
    Supports:
    - Ken Burns effect (zoom, pan)
    - Crossfade transitions
    - Audio overlay
    - Multiple codecs (H.264, VP9)
    """
    
    def __init__(self, output_dir: str = "/tmp/video_output"):
        """
        Initialize FFmpeg assembler
        
        Args:
            output_dir: Directory for output videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check FFmpeg installation
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✅ FFmpeg found")
            else:
                logger.warning("⚠️ FFmpeg not found - video generation will fail")
        except Exception as e:
            logger.warning(f"⚠️ FFmpeg check failed: {e}")
    
    async def create_video_from_images(
        self,
        image_paths: List[str],
        output_path: str,
        fps: int = 24,
        duration_per_image: float = 3.0,
        motion_params: Optional[Dict] = None,
        codec: str = "h264",
        quality: str = "high",
        width: int = 1920,
        height: int = 1080
    ) -> Dict:
        """
        Create video from list of images with motion effects
        
        Args:
            image_paths: List of image file paths
            output_path: Output video file path
            fps: Frames per second
            duration_per_image: Duration for each image (seconds)
            motion_params: Motion effect parameters (zoom, pan, tilt)
            codec: Video codec (h264, vp9)
            quality: Quality preset (low, medium, high)
            width: Output video width
            height: Output video height
            
        Returns:
            Dict with video metadata
        """
        logger.info(f"🎬 Creating video from {len(image_paths)} images ({width}x{height})")
        
        # Default motion parameters
        if motion_params is None:
            motion_params = {
                "zoom": 1.0,
                "pan_x": 0.0,
                "pan_y": 0.0,
                "speed": 1.0
            }
        
        # Build FFmpeg command
        cmd = await self._build_ffmpeg_command(
            image_paths=image_paths,
            output_path=output_path,
            fps=fps,
            duration_per_image=duration_per_image,
            motion_params=motion_params,
            codec=codec,
            quality=quality,
            width=width,
            height=height
        )
        
        # Execute FFmpeg
        try:
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8')
                logger.error(f"❌ FFmpeg failed: {error_msg}")
                raise Exception(f"FFmpeg error: {error_msg}")
            
            # Get video metadata
            metadata = await self._get_video_metadata(output_path)
            
            logger.info(f"✅ Video created: {output_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            raise
    
    async def _build_ffmpeg_command(
        self,
        image_paths: List[str],
        output_path: str,
        fps: int,
        duration_per_image: float,
        motion_params: Dict,
        codec: str,
        quality: str,
        width: int,
        height: int
    ) -> List[str]:
        """Build FFmpeg command with motion effects"""
        
        # Create concat file for images
        concat_file = self.output_dir / f"concat_{uuid.uuid4().hex[:8]}.txt"
        with open(concat_file, 'w') as f:
            for img_path in image_paths:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration_per_image}\n")
            # Add last image again (FFmpeg concat requirement)
            if image_paths:
                f.write(f"file '{image_paths[-1]}'\n")
        
        # Quality presets
        quality_settings = {
            "preview": {"crf": "35", "preset": "ultrafast"},
            "low": {"crf": "28", "preset": "superfast"},
            "medium": {"crf": "23", "preset": "medium"},
            "high": {"crf": "18", "preset": "slow"},
            "ultra": {"crf": "16", "preset": "veryslow"}
        }
        settings = quality_settings.get(quality, quality_settings["medium"])
        
        # Build Ken Burns effect filter
        zoom = motion_params.get("zoom", 1.0)
        pan_x = motion_params.get("pan_x", 0.0)
        pan_y = motion_params.get("pan_y", 0.0)
        
        # Zoompan filter for Ken Burns effect
        # Use dynamic width/height instead of hardcoded 1920x1080
        filter_complex = f"zoompan=z='min(zoom+0.0015,{zoom})':d={int(duration_per_image * fps)}:x='iw/2-(iw/zoom/2)+{pan_x}':y='ih/2-(ih/zoom/2)+{pan_y}':s={width}x{height}:fps={fps}"
        
        cmd = [
            "ffmpeg",
            "-nostdin",  # Prevent hanging in background
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-vf", filter_complex,
            "-c:v", "libx264" if codec == "h264" else "libvpx-vp9",
            "-crf", settings["crf"],
            "-preset", settings["preset"],
            "-pix_fmt", "yuv420p",
            "-y",  # Overwrite output
            output_path
        ]
        
        return cmd
    
    async def _get_video_metadata(self, video_path: str) -> Dict:
        """Get video file metadata using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            data = json.loads(stdout.decode('utf-8'))
            
            # Extract relevant metadata
            video_stream = next(
                (s for s in data.get("streams", []) if s["codec_type"] == "video"),
                {}
            )
            format_info = data.get("format", {})
            
            return {
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "duration": float(format_info.get("duration", 0)),
                "fps": eval(video_stream.get("r_frame_rate", "24/1")),
                "codec": video_stream.get("codec_name", "unknown"),
                "bitrate": int(format_info.get("bit_rate", 0)) // 1000,  # kbps
                "file_size": int(format_info.get("size", 0))
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get video metadata: {e}")
            return {}


# =============================================================================
# COMFYUI ANIMATEDIFF WORKFLOW
# =============================================================================

class AnimateDiffWorkflow:
    """
    AnimateDiff workflow builder for ComfyUI
    
    AnimateDiff generates smooth video animations directly from text prompts.
    Requires AnimateDiff nodes installed in ComfyUI.
    """
    
    @staticmethod
    def create_animatediff_workflow(
        prompt: str,
        negative_prompt: str = "ugly, blurry, low quality",
        width: int = 512,
        height: int = 512,
        frames: int = 16,
        fps: int = 8,
        seed: Optional[int] = None,
        model_name: str = "realisticVisionV60B1_v51HyperVAE.safetensors",
        motion_module: str = "mm_sd_v15_v2.ckpt"
    ) -> Dict:
        """
        Create AnimateDiff workflow for video generation using AnimateDiff-Evolved
        
        Args:
            prompt: Text description of video
            negative_prompt: What to avoid
            width: Video width
            height: Video height
            frames: Number of frames (16-24 typical)
            fps: Frames per second
            seed: Random seed
            model_name: SD checkpoint
            motion_module: AnimateDiff motion module
            
        Returns:
            ComfyUI workflow JSON
        """
        if seed is None:
            seed = int(datetime.now().timestamp() * 1000) % (2**32)
        
        workflow = {
            # Load Checkpoint
            "1": {
                "inputs": {
                    "ckpt_name": model_name
                },
                "class_type": "CheckpointLoaderSimple"
            },
            
            # Load AnimateDiff Model (ADE_AnimateDiffLoaderGen1)
            "2": {
                "inputs": {
                    "model_name": motion_module,
                    "beta_schedule": "sqrt_linear (AnimateDiff)",
                    "model": ["1", 0]
                },
                "class_type": "ADE_AnimateDiffLoaderGen1"
            },
            
            # Positive Prompt
            "3": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            
            # Negative Prompt
            "4": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            
            # Empty Latent
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": frames
                },
                "class_type": "EmptyLatentImage"
            },
            
            # KSampler with AnimateDiff (BALANCED: ความเร็ว + คุณภาพ)
            "6": {
                "inputs": {
                    "seed": seed,
                    "steps": 12,         # 12 steps = balance (8 = เร็วแต่คุณภาพต่ำ, 20 = ช้า)
                    "cfg": 7.0,          # CFG scale (ควบคุมความใกล้เคียง prompt)
                    "sampler_name": "euler_a",  # euler_a ให้ motion สมูทกว่า euler
                    "scheduler": "karras",      # karras scheduler = คุณภาพดีกว่า normal
                    "denoise": 1.0,
                    "model": ["2", 0],  # AnimateDiff model from ADE loader
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            
            # VAE Decode
            "7": {
                "inputs": {
                    "samples": ["6", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            
            # Save Video
            "8": {
                "inputs": {
                    "filename_prefix": "animatediff_",
                    "frame_rate": fps,
                    "loop_count": 0,
                    "images": ["7", 0],
                    "format": "video/h264-mp4",
                    "pingpong": False,
                    "save_output": True
                },
                "class_type": "VHS_VideoCombine"
            }
        }
        
        return workflow


# =============================================================================
# HYBRID VIDEO GENERATOR
# =============================================================================

class HybridVideoGenerator:
    """
    Hybrid video generator supporting multiple modes:
    1. Image-to-Video (ComfyUI + FFmpeg)
    2. AnimateDiff (Direct video generation)
    3. SVD (Stable Video Diffusion)
    """
    
    def __init__(
        self,
        comfyui_url: str = "http://127.0.0.1:8188",
        output_dir: str = "/tmp/video_output"
    ):
        """
        Initialize hybrid video generator
        
        Args:
            comfyui_url: ComfyUI server URL
            output_dir: Output directory for videos
        """
        self.comfyui = ComfyUIClient(base_url=comfyui_url)
        self.ffmpeg = FFmpegVideoAssembler(output_dir=output_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🎬 Hybrid Video Generator initialized")
    
    async def generate_video(
        self,
        mode: str,
        prompt: str,
        negative_prompt: str = "ugly, blurry, low quality",
        motion_params: Optional[Dict] = None,
        quality: str = "medium",
        progress_callback: Optional[Callable] = None,
        **kwargs
    ) -> Dict:
        """
        Generate video using specified mode
        
        Args:
            mode: Generation mode (image_to_video, animate_diff, svd)
            prompt: Text description
            negative_prompt: What to avoid
            motion_params: Motion effect parameters
            quality: Quality preset
            **kwargs: Mode-specific parameters
            
        Returns:
            Dict with video_path, metadata, mode
        """
        logger.info(f"🎬 Generating video - Mode: {mode}")
        
        if mode == VideoMode.IMAGE_TO_VIDEO:
            return await self._generate_image_to_video(
                prompt, negative_prompt, motion_params, quality, progress_callback, **kwargs
            )
        elif mode == VideoMode.ANIMATE_DIFF:
            return await self._generate_animatediff(
                prompt, negative_prompt, quality, **kwargs
            )
        elif mode == VideoMode.SVD:
            return await self._generate_svd(
                prompt, negative_prompt, quality, **kwargs
            )
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    async def _generate_image_to_video(
        self,
        prompt: str,
        negative_prompt: str,
        motion_params: Optional[Dict],
        quality: str,
        progress_callback: Optional[Callable] = None,
        num_images: Optional[int] = None,
        duration_per_image: Optional[float] = None,
        **kwargs
    ) -> Dict:
        """
        Mode 1: Generate images with ComfyUI → Assemble video with FFmpeg
        
        Fast, high control, great for slideshows with Ken Burns effect
        """
        logger.info(f"🎨 Mode: Image-to-Video (Quality: {quality})")
        
        # Get quality preset
        from modules.video_quality_presets import get_preset
        preset = get_preset(quality)
        
        # Use preset values or override with kwargs
        num_images = num_images or kwargs.get("num_images", preset.num_images)
        duration_per_image = duration_per_image or kwargs.get("duration_per_image", preset.duration_per_image)
        width = kwargs.get("width", preset.width)
        height = kwargs.get("height", preset.height)
        steps = kwargs.get("steps", preset.steps)
        cfg = kwargs.get("cfg", preset.cfg_scale)
        
        logger.info(f"📊 Settings: {width}x{height}, {steps} steps, {num_images} images")
        logger.info(f"⏱️  Estimated time: ~{preset.estimated_time}s")
        
        # Step 1: Generate images with ComfyUI
        logger.info(f"Step 1/3: Generating {num_images} images with ComfyUI...")
        
        image_paths = []
        for i in range(num_images):
            # Update progress
            if progress_callback:
                await progress_callback(
                    current_step=i,
                    total_steps=num_images,
                    message=f"Generating image {i+1}/{num_images}"
                )
            
            workflow = WorkflowBuilder.create_txt2img_workflow(
                prompt=f"{prompt}, cinematic shot {i+1}" if num_images > 1 else prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                cfg=cfg
            )
            
            # Execute workflow and get image bytes
            image_bytes_list = await asyncio.to_thread(
                self.comfyui.execute_workflow,
                workflow
            )
            
            # Save bytes to temp files
            if image_bytes_list:
                for j, image_bytes in enumerate(image_bytes_list):
                    temp_image_path = str(self.output_dir / f"temp_img_{uuid.uuid4().hex[:8]}_{i}_{j}.png")
                    with open(temp_image_path, 'wb') as f:
                        f.write(image_bytes)
                    image_paths.append(temp_image_path)
                    logger.info(f"  ✓ Image {i+1}/{num_images} saved: {temp_image_path}")
        
        if not image_paths:
            raise Exception("No images generated")
        
        # Step 2: Create video with FFmpeg
        logger.info("Step 2/3: Assembling video with FFmpeg...")
        
        video_id = uuid.uuid4().hex[:12]
        output_path = str(self.output_dir / f"video_{video_id}.mp4")
        
        metadata = await self.ffmpeg.create_video_from_images(
            image_paths=image_paths,
            output_path=output_path,
            duration_per_image=duration_per_image,
            motion_params=motion_params,
            quality=quality,
            width=width,
            height=height
        )
        
        logger.info("✅ Image-to-Video complete")
        
        return {
            "video_path": output_path,
            "metadata": metadata,
            "mode": VideoMode.IMAGE_TO_VIDEO,
            "num_images": len(image_paths)
        }
    
    async def _generate_animatediff(
        self,
        prompt: str,
        negative_prompt: str,
        quality: str,
        frames: int = 16,  # 16 frames = มาตรฐาน AnimateDiff (balance ระหว่างความสมูทกับความเร็ว)
        fps: int = 8,      # 8 fps เพียงพอสำหรับ AI video (ไม่ใช่ภาพยนตร์จริง)
        **kwargs
    ) -> Dict:
        """
        Mode 2: Direct video generation with AnimateDiff
        
        Smooth motion, better for character animations
        
        Auto-fallback to IMAGE_TO_VIDEO if AnimateDiff not available
        """
        logger.info("🎞️ Mode: AnimateDiff (Direct Video)")
        
        try:
            # Create AnimateDiff workflow
            width = kwargs.get("width", 512)
            height = kwargs.get("height", 512)
            
            logger.info(f"📊 AnimateDiff Settings: {width}x{height}, {frames} frames @ {fps} fps")
            
            # เพิ่ม motion keywords ให้ prompt เพื่อ motion ที่สมจริงขึ้น
            enhanced_prompt = f"{prompt}, dynamic motion, cinematic movement, smooth animation, natural flow"
            enhanced_negative = f"{negative_prompt}, static, frozen, still image, no motion, blurry"
            
            workflow = AnimateDiffWorkflow.create_animatediff_workflow(
                prompt=enhanced_prompt,
                negative_prompt=enhanced_negative,
                width=width,
                height=height,
                frames=frames,
                fps=fps
            )
            
            logger.info(f"🔧 Workflow created: {json.dumps(workflow, indent=2)}")
            
            # Execute workflow (VHS_VideoCombine saves directly to ComfyUI output folder)
            logger.info("⚡ Executing AnimateDiff workflow in ComfyUI...")
            
            # Get list of existing videos before generation
            comfyui_output = Path.home() / "ComfyUI" / "output"
            existing_videos = set(comfyui_output.glob("animatediff_*.mp4"))
            
            await asyncio.to_thread(
                self.comfyui.execute_workflow,
                workflow
            )
            
            # Find newly created video
            new_videos = set(comfyui_output.glob("animatediff_*.mp4")) - existing_videos
            
            if not new_videos:
                raise Exception("AnimateDiff generation failed: no video output found")
            
            # Get the newest video
            source_video = max(new_videos, key=lambda p: p.stat().st_mtime)
            logger.info(f"📦 Found generated video: {source_video}")
            
            # Copy to our output directory
            video_id = uuid.uuid4().hex[:12]
            output_path = str(self.output_dir / f"animatediff_{video_id}.mp4")
            
            import shutil
            shutil.copy2(source_video, output_path)
                
            logger.info(f"✅ AnimateDiff video saved: {output_path}")
            
            metadata = await self.ffmpeg._get_video_metadata(output_path)
            
            logger.info("✅ AnimateDiff complete")
            
            return {
                "video_path": output_path,
                "metadata": metadata,
                "mode": VideoMode.ANIMATE_DIFF,
                "frames": frames,
                "fps": fps
            }
            
        except Exception as e:
            logger.warning(f"⚠️ AnimateDiff failed: {str(e)}")
            logger.info("🔄 Falling back to IMAGE_TO_VIDEO mode...")
            
            # Fallback to IMAGE_TO_VIDEO mode
            return await self._generate_image_to_video(
                prompt=prompt,
                negative_prompt=negative_prompt,
                quality=quality,
                **kwargs
            )
    
    async def _generate_svd(
        self,
        prompt: str,
        negative_prompt: str,
        quality: str,
        **kwargs
    ) -> Dict:
        """
        Mode 3: Stable Video Diffusion
        
        Experimental, requires SVD nodes in ComfyUI
        """
        logger.info("🚀 Mode: Stable Video Diffusion (SVD)")
        
        # TODO: Implement SVD workflow when available
        raise NotImplementedError("SVD mode coming soon")
