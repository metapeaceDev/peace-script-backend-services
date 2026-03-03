"""
🎬 FFmpeg Video Builder - Images to Video Conversion

Features:
- Convert image sequences to video
- Apply motion effects (Ken Burns: zoom, pan)
- Add transitions between shots
- Audio overlay support
- Multiple output formats (MP4, WebM)

Dependencies:
- FFmpeg (must be installed: brew install ffmpeg)
- Pillow (for image processing)

Author: Peace Script Development Team
Version: 1.0.0
Created: 2025-01-20
"""

import subprocess
import os
import tempfile
import shutil
from typing import List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MotionEffect:
    """
    Motion effect parameters (Ken Burns style)
    
    Ken Burns effect: slow zoom/pan to create cinematic feel
    """
    zoom_start: float = 1.0    # Start zoom (1.0 = no zoom)
    zoom_end: float = 1.1      # End zoom (1.1 = 10% zoom in)
    pan_x: float = 0.0         # Horizontal pan (-1 to 1)
    pan_y: float = 0.0         # Vertical pan (-1 to 1)
    duration: float = 3.0      # Effect duration in seconds


@dataclass
class VideoConfig:
    """Video output configuration"""
    width: int = 1920
    height: int = 1080
    fps: int = 24
    codec: str = "libx264"     # H.264 for MP4
    quality: str = "medium"    # preset: ultrafast, fast, medium, slow, veryslow
    format: str = "mp4"        # mp4, webm, mov


# =============================================================================
# FFMPEG VIDEO BUILDER
# =============================================================================

class FFmpegVideoBuilder:
    """
    Build videos from images using FFmpeg
    
    Workflow:
    1. Generate images using ComfyUI
    2. Apply motion effects (zoom/pan)
    3. Add transitions
    4. Combine into video
    5. Add audio (optional)
    """
    
    def __init__(self, ffmpeg_path: str = "/opt/homebrew/bin/ffmpeg"):
        """
        Initialize FFmpeg video builder
        
        Args:
            ffmpeg_path: Path to ffmpeg binary (default: /opt/homebrew/bin/ffmpeg)
        """
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                logger.info(f"✅ FFmpeg found: {version}")
                return True
            
            logger.error("❌ FFmpeg not working")
            return False
            
        except FileNotFoundError:
            logger.error("❌ FFmpeg not installed!")
            logger.error("Install with: brew install ffmpeg")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking FFmpeg: {e}")
            return False
    
    def create_ken_burns_video(
        self,
        image_path: str,
        output_path: str,
        motion: MotionEffect,
        config: VideoConfig = VideoConfig()
    ) -> bool:
        """
        Create video from single image with Ken Burns effect
        
        Ken Burns effect: slow zoom and pan to create motion
        
        Args:
            image_path: Input image file
            output_path: Output video file
            motion: Motion effect parameters
            config: Video configuration
            
        Returns:
            True if successful
            
        Example:
            >>> motion = MotionEffect(zoom_start=1.0, zoom_end=1.2, duration=5.0)
            >>> builder.create_ken_burns_video("input.png", "output.mp4", motion)
        """
        try:
            # Calculate zoom filter
            # zoompan filter: zoom in from 1.0x to zoom_end over duration
            total_frames = int(motion.duration * config.fps)
            
            # zoompan parameters:
            # z='min(zoom+0.0015,1.5)' = gradual zoom
            # d=1 = duration per frame
            # x='iw/2-(iw/zoom/2)' = center horizontally
            # y='ih/2-(ih/zoom/2)' = center vertically
            zoom_rate = (motion.zoom_end - motion.zoom_start) / total_frames
            
            filter_complex = (
                f"zoompan="
                f"z='min(zoom+{zoom_rate},{motion.zoom_end})':"
                f"d={total_frames}:"
                f"x='iw/2-(iw/zoom/2)+{motion.pan_x * 100}':"
                f"y='ih/2-(ih/zoom/2)+{motion.pan_y * 100}':"
                f"s={config.width}x{config.height},"
                f"fps={config.fps}"
            )
            
            # FFmpeg command
            cmd = [
                self.ffmpeg_path,
                "-loop", "1",                    # Loop input image
                "-i", image_path,                # Input image
                "-vf", filter_complex,           # Apply video filter
                "-c:v", config.codec,            # Video codec
                "-preset", config.quality,       # Encoding preset
                "-pix_fmt", "yuv420p",          # Pixel format (compatibility)
                "-t", str(motion.duration),      # Duration
                "-y",                            # Overwrite output
                output_path
            ]
            
            logger.info(f"🎬 Creating Ken Burns video: {output_path}")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ Video created: {output_path} ({file_size:.2f} MB)")
                return True
            else:
                logger.error(f"❌ FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating Ken Burns video: {e}")
            return False
    
    def create_slideshow(
        self,
        image_paths: List[str],
        output_path: str,
        duration_per_image: float = 3.0,
        transition_duration: float = 0.5,
        config: VideoConfig = VideoConfig()
    ) -> bool:
        """
        Create slideshow video from multiple images
        
        Args:
            image_paths: List of image file paths
            output_path: Output video file
            duration_per_image: How long each image displays (seconds)
            transition_duration: Fade transition duration (seconds)
            config: Video configuration
            
        Returns:
            True if successful
        """
        try:
            if not image_paths:
                logger.error("❌ No images provided")
                return False
            
            logger.info(f"🎬 Creating slideshow: {len(image_paths)} images")
            
            # Create temp directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy and prepare images
                prepared_images = []
                for i, img_path in enumerate(image_paths):
                    # Resize to target resolution
                    prepared_path = os.path.join(temp_dir, f"img_{i:04d}.png")
                    self._prepare_image(img_path, prepared_path, config.width, config.height)
                    prepared_images.append(prepared_path)
                
                # Build complex filter for transitions
                filter_parts = []
                inputs = ""
                
                for i, img_path in enumerate(prepared_images):
                    inputs += f"-loop 1 -t {duration_per_image} -i {img_path} "
                    
                    # Scale input
                    filter_parts.append(
                        f"[{i}:v]scale={config.width}:{config.height}:"
                        f"force_original_aspect_ratio=decrease,"
                        f"pad={config.width}:{config.height}:(ow-iw)/2:(oh-ih)/2,"
                        f"setsar=1,fps={config.fps}[v{i}]"
                    )
                
                # Add crossfade transitions
                if len(prepared_images) > 1:
                    # First video
                    current = "v0"
                    
                    for i in range(1, len(prepared_images)):
                        offset = duration_per_image - transition_duration
                        next_label = f"v{i}_{i-1}" if i < len(prepared_images) - 1 else "out"
                        
                        filter_parts.append(
                            f"[{current}][v{i}]xfade=transition=fade:"
                            f"duration={transition_duration}:"
                            f"offset={offset * i}[{next_label}]"
                        )
                        current = next_label
                
                filter_complex = ";".join(filter_parts)
                
                # Build FFmpeg command
                cmd = f"{self.ffmpeg_path} {inputs} -filter_complex \"{filter_complex}\" "
                cmd += f"-c:v {config.codec} -preset {config.quality} -pix_fmt yuv420p "
                cmd += f"-y {output_path}"
                
                logger.debug(f"Command: {cmd}")
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    logger.info(f"✅ Slideshow created: {output_path} ({file_size:.2f} MB)")
                    return True
                else:
                    logger.error(f"❌ FFmpeg error: {result.stderr}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating slideshow: {e}")
            return False
    
    def _prepare_image(
        self,
        input_path: str,
        output_path: str,
        width: int,
        height: int
    ):
        """Resize and prepare image for video"""
        try:
            from PIL import Image
            
            img = Image.open(input_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize maintaining aspect ratio
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Create canvas and center image
            canvas = Image.new('RGB', (width, height), (0, 0, 0))
            offset = ((width - img.width) // 2, (height - img.height) // 2)
            canvas.paste(img, offset)
            
            canvas.save(output_path, 'PNG')
            
        except Exception as e:
            logger.error(f"❌ Error preparing image {input_path}: {e}")
            # Fallback: copy original
            shutil.copy(input_path, output_path)
    
    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> bool:
        """
        Add audio track to video
        
        Args:
            video_path: Input video file
            audio_path: Audio file (MP3, WAV, etc.)
            output_path: Output video with audio
            
        Returns:
            True if successful
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",           # Copy video stream
                "-c:a", "aac",            # Encode audio to AAC
                "-shortest",              # Match shortest stream
                "-y",
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Audio added: {output_path}")
                return True
            else:
                logger.error(f"❌ FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding audio: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata using ffprobe
        
        Returns:
            Dict with width, height, duration, fps, codec, etc.
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                video_stream = next(
                    (s for s in data.get('streams', []) if s['codec_type'] == 'video'),
                    None
                )
                
                if video_stream:
                    return {
                        'width': video_stream.get('width'),
                        'height': video_stream.get('height'),
                        'duration': float(data.get('format', {}).get('duration', 0)),
                        'fps': eval(video_stream.get('r_frame_rate', '24/1')),
                        'codec': video_stream.get('codec_name'),
                        'bitrate': int(data.get('format', {}).get('bit_rate', 0)),
                        'size': int(data.get('format', {}).get('size', 0))
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting video info: {e}")
            return {}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_video_from_images(
    image_paths: List[str],
    output_path: str,
    motion_effects: Optional[List[MotionEffect]] = None,
    config: VideoConfig = VideoConfig()
) -> Tuple[bool, Optional[dict]]:
    """
    High-level function to create video from images
    
    Args:
        image_paths: List of image files
        output_path: Output video path
        motion_effects: Optional motion effects per image
        config: Video configuration
        
    Returns:
        (success, video_info)
    """
    builder = FFmpegVideoBuilder()
    
    if len(image_paths) == 1:
        # Single image with Ken Burns effect
        motion = motion_effects[0] if motion_effects else MotionEffect()
        success = builder.create_ken_burns_video(
            image_paths[0],
            output_path,
            motion,
            config
        )
    else:
        # Multiple images slideshow
        success = builder.create_slideshow(
            image_paths,
            output_path,
            duration_per_image=3.0,
            transition_duration=0.5,
            config=config
        )
    
    if success:
        info = builder.get_video_info(output_path)
        return True, info
    
    return False, None


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    """
    Test FFmpeg video builder
    
    Run:
        python -m modules.ffmpeg_video_builder
    """
    
    print("🎬 FFmpeg Video Builder Test")
    print("=" * 50)
    
    builder = FFmpegVideoBuilder()
    
    # Test 1: Check FFmpeg
    print("\n1. FFmpeg Status:")
    print(f"   {'✅ Ready' if builder._check_ffmpeg() else '❌ Not Available'}")
    
    # Test 2: Create test video (if test image exists)
    test_image = "/tmp/test_image.png"
    test_output = "/tmp/test_video.mp4"
    
    if os.path.exists(test_image):
        print(f"\n2. Creating test video from: {test_image}")
        
        motion = MotionEffect(
            zoom_start=1.0,
            zoom_end=1.2,
            pan_x=0.1,
            pan_y=0.0,
            duration=5.0
        )
        
        success = builder.create_ken_burns_video(
            test_image,
            test_output,
            motion
        )
        
        if success:
            info = builder.get_video_info(test_output)
            print(f"\n   ✅ Video Info:")
            print(f"      Resolution: {info.get('width')}x{info.get('height')}")
            print(f"      Duration: {info.get('duration'):.1f}s")
            print(f"      FPS: {info.get('fps')}")
            print(f"      Size: {info.get('size') / (1024*1024):.2f} MB")
    else:
        print(f"\n2. Skipping test (no test image at {test_image})")
    
    print("\n" + "=" * 50)
    print("Test complete!")
