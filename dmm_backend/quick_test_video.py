#!/usr/bin/env python3
"""
Quick Video Generation Test - Minimal settings for fast testing
"""
import asyncio
import sys
from pathlib import Path
from modules.video_renderer import HybridVideoGenerator, VideoMode

async def quick_test():
    """Ultra-fast test with minimal settings"""
    print("🎬 Quick Video Test (1 image, 5 steps, 1 second)")
    print("=" * 60)
    
    try:
        # Initialize
        print("1. Initializing...")
        gen = HybridVideoGenerator(
            comfyui_url="http://127.0.0.1:8188",
            output_dir="/tmp/quick_video_test"
        )
        
        # Generate with minimal settings
        print("2. Generating (should take ~10-15 seconds)...")
        result = await gen.generate_video(
            mode=VideoMode.IMAGE_TO_VIDEO,
            prompt="sunset",
            negative_prompt="ugly",
            num_images=1,           # ✅ Only 1 image
            duration_per_image=1.0, # ✅ 1 second only
            width=512,
            height=512,
            steps=5,                # ✅ Only 5 steps (very fast)
            quality="low"
        )
        
        # Check result
        print("\n3. Result:")
        video_path = result.get('video_path')
        metadata = result.get('metadata', {})
        
        print(f"   Path: {video_path}")
        print(f"   Metadata: {metadata}")
        
        if video_path and Path(video_path).exists():
            size = Path(video_path).stat().st_size
            print(f"\n✅ SUCCESS! Video created: {size:,} bytes")
            print(f"   Location: {video_path}")
            return True
        else:
            print(f"\n❌ FAILED! File not found")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
