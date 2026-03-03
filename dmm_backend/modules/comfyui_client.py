"""
🔸 ComfyUI API Client - Advanced Image Generation
Integrates with ComfyUI for node-based workflow execution

Features:
- Workflow JSON execution via ComfyUI API
- Queue management and progress tracking
- Image retrieval from ComfyUI output
- WebSocket support for real-time updates (optional)
- Pre-built workflow builders (txt2img, img2img, ControlNet)

Dependencies:
- requests (HTTP client)
- websocket-client (optional, for real-time progress)

Usage:
    >>> client = ComfyUIClient("http://127.0.0.1:8188")
    >>> workflow = WorkflowBuilder.create_txt2img_workflow(
    ...     prompt="beautiful portrait",
    ...     negative_prompt="ugly"
    ... )
    >>> images = client.execute_workflow(workflow)
    >>> print(f"Generated {len(images)} images - comfyui_client.py:23")

Author: Peace Script Development Team
Version: 1.0.0
Created: 2025-11-03
"""

import requests
import time
import uuid
import json
import random
from typing import Dict, Optional, List, Callable
from pathlib import Path

from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# COMFYUI API CLIENT
# =============================================================================

class ComfyUIClient:
    """
    Client for ComfyUI HTTP API
    
    ComfyUI runs on http://127.0.0.1:8188 by default
    
    Endpoints:
    - POST /prompt - Queue workflow for execution
    - GET /history/{prompt_id} - Get execution results
    - GET /view - Download generated images
    - GET /queue - Check queue status
    - GET /system_stats - Server health
    """
    
    def __init__(
        self, 
        base_url: str = "http://127.0.0.1:8188",
        timeout: int = 600,
        poll_interval: float = 1.0
    ):
        """
        Initialize ComfyUI client
        
        Args:
            base_url: ComfyUI server URL
            timeout: Max time to wait for generation (seconds)
            poll_interval: Time between status checks (seconds)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.client_id = str(uuid.uuid4())
        
        logger.info(f"ComfyUI client initialized: {self.base_url}")
    
    def check_health(self) -> bool:
        """
        Check if ComfyUI server is running
        
        Returns:
            True if server is healthy
        """
        try:
            response = requests.get(
                f"{self.base_url}/system_stats",
                timeout=5
            )
            
            if response.status_code == 200:
                stats = response.json()
                logger.debug(f"ComfyUI health check OK: {stats}")
                return True
            
            return False
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"ComfyUI not reachable at {self.base_url}")
            return False
        
        except Exception as e:
            logger.error(f"ComfyUI health check error: {e}")
            return False
    
    def queue_prompt(self, workflow: Dict) -> str:
        """
        Queue a workflow for execution
        
        Args:
            workflow: ComfyUI workflow JSON (nodes graph)
            
        Returns:
            prompt_id: Unique ID for tracking this execution
            
        Raises:
            Exception: If queueing fails
        """
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/prompt",
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                error_msg = f"Failed to queue workflow: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            result = response.json()
            prompt_id = result["prompt_id"]
            
            logger.info(f"Workflow queued successfully: {prompt_id}")
            return prompt_id
        
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to ComfyUI at {self.base_url}")
        
        except Exception as e:
            logger.error(f"Error queueing workflow: {e}", exc_info=True)
            raise
    
    def get_history(self, prompt_id: str) -> Dict:
        """
        Get execution history/results for a prompt
        
        Args:
            prompt_id: Prompt ID from queue_prompt()
            
        Returns:
            History dict with outputs, or empty dict if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {}
        
        except Exception as e:
            logger.warning(f"Error getting history: {e}")
            return {}
    
    def wait_for_completion(
        self, 
        prompt_id: str, 
        timeout: Optional[int] = None,
        callback: Optional[Callable] = None
    ) -> Dict:
        """
        Wait for workflow execution to complete
        
        Args:
            prompt_id: Prompt ID to wait for
            timeout: Override default timeout (seconds)
            callback: Optional function called with progress updates
            
        Returns:
            Complete history dict with outputs
            
        Raises:
            TimeoutError: If execution exceeds timeout
        """
        timeout = timeout or self.timeout
        start_time = time.time()
        
        logger.info(f"Waiting for workflow {prompt_id} (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            
            if prompt_id in history:
                elapsed = time.time() - start_time
                logger.info(f"Workflow {prompt_id} completed in {elapsed:.1f}s")
                return history[prompt_id]
            
            # Optional progress callback
            if callback:
                elapsed = time.time() - start_time
                callback(elapsed, timeout)
            
            time.sleep(self.poll_interval)
        
        raise TimeoutError(
            f"Workflow {prompt_id} timed out after {timeout}s"
        )
    
    def get_image(
        self, 
        filename: str, 
        subfolder: str = "", 
        folder_type: str = "output"
    ) -> bytes:
        """
        Download generated image from ComfyUI
        
        🔥 CRITICAL FIX: Read file DIRECTLY from ComfyUI output folder
        The /view endpoint returns THUMBNAILS (85×128) not full images!
        We must read the actual PNG file from disk to get 512×768 full quality.
        
        Args:
            filename: Image filename from history
            subfolder: Subfolder path (if any)
            folder_type: "output", "input", or "temp"
            
        Returns:
            Image data as bytes (FULL QUALITY, not thumbnail!)
            
        Raises:
            Exception: If download fails
        """
        import os
        
        # 🔥 FIX: Read file directly from ComfyUI output folder
        # ComfyUI default output path
        comfyui_base = os.path.expanduser("~/ComfyUI")
        
        if folder_type == "output":
            folder_path = os.path.join(comfyui_base, "output")
        elif folder_type == "input":
            folder_path = os.path.join(comfyui_base, "input")
        else:
            folder_path = os.path.join(comfyui_base, "temp")
        
        if subfolder:
            folder_path = os.path.join(folder_path, subfolder)
        
        file_path = os.path.join(folder_path, filename)
        
        try:
            # Read file directly from disk (FULL QUALITY!)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    image_bytes = f.read()
                logger.info(f"✅ Read FULL image from disk: {filename} ({len(image_bytes)} bytes)")
                return image_bytes
            else:
                logger.error(f"❌ File not found: {file_path}")
                raise FileNotFoundError(f"Image file not found: {file_path}")
                
        except Exception as e:
            logger.error(f"Error reading image file: {e}")
            # Fallback to API (will get thumbnail - not ideal!)
            logger.warning("⚠️ Falling back to /view API (will get thumbnail!)")
            
            params = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }
            
            response = requests.get(
                f"{self.base_url}/view",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.warning(f"⚠️ Got image via API (thumbnail): {filename}")
                return response.content
            
            raise Exception(
                f"Failed to get image: {response.status_code} - {response.text}"
            )
    
    def execute_workflow(
        self, 
        workflow: Dict, 
        timeout: Optional[int] = None
    ) -> List[bytes]:
        """
        Execute workflow and return generated images
        
        This is the main high-level method for generating images.
        
        Args:
            workflow: ComfyUI workflow JSON
            timeout: Override default timeout
            
        Returns:
            List of image data (bytes) from all SaveImage nodes
            
        Raises:
            Exception: If execution fails
            TimeoutError: If execution times out
        """
        logger.info("Executing ComfyUI workflow...")
        
        # 1. Queue workflow
        prompt_id = self.queue_prompt(workflow)
        
        # 2. Wait for completion
        history = self.wait_for_completion(prompt_id, timeout)
        
        # 3. Extract and download images
        images = []
        
        if "outputs" not in history:
            logger.warning("No outputs in history")
            return images
        
        for _node_id, node_output in history["outputs"].items():
            if "images" not in node_output:
                continue
            
            for img_info in node_output["images"]:
                filename = img_info["filename"]
                subfolder = img_info.get("subfolder", "")
                folder_type = img_info.get("type", "output")
                
                try:
                    image_data = self.get_image(filename, subfolder, folder_type)
                    images.append(image_data)
                    logger.info(f"Retrieved image: {filename}")
                except Exception as e:
                    logger.error(f"Failed to get image {filename}: {e}")
        
        logger.info(f"Workflow completed: {len(images)} images generated")
        return images
    
    def get_queue_status(self) -> Dict:
        """
        Get current queue status
        
        Returns:
            Dict with queue_running, queue_pending counts
        """
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    def clear_queue(self) -> bool:
        """Clear all pending items from queue"""
        try:
            response = requests.post(f"{self.base_url}/queue", json={"clear": True})
            return response.status_code == 200
        except:
            return False


# =============================================================================
# WORKFLOW BUILDER - Pre-configured Workflows
# =============================================================================

class WorkflowBuilder:
    """
    Helper class for building ComfyUI workflows programmatically
    
    ComfyUI workflows are JSON graphs of nodes.
    Each node has:
    - inputs: Dict of parameters and connections to other nodes
    - class_type: Node type (KSampler, CheckpointLoader, etc.)
    
    Node connections format: ["node_id", output_index]
    Example: ["4", 0] means output 0 from node "4"
    """
    
    @staticmethod
    def create_txt2img_workflow(
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,      # ✨ Standard size
        height: int = 768,     # ✨ Standard size
        steps: int = 50,       # ✨ HIGH QUALITY: 50 steps สำหรับภาพคมชัดสุด
        cfg: float = 8.0,      # ✨ เพิ่ม guidance สูงขึ้นเพื่อความชัดและรายละเอียด
        seed: Optional[int] = None,
        sampler_name: str = "dpmpp_2m_sde",    # ✨ FIX: เปลี่ยนจาก dpmpp_2m → dpmpp_2m_sde (คุณภาพสูงกว่า)
        scheduler: str = "karras",
        model_name: str = "realisticVisionV60B1_v51HyperVAE.safetensors",
        lora_name: Optional[str] = None,
        lora_strength: float = 1.0
    ) -> Dict:
        """
        Create basic txt2img workflow
        
        This is the most common workflow for generating images from text.
        
        Args:
            prompt: Positive prompt (what you want)
            negative_prompt: Negative prompt (what to avoid)
            width: Image width (multiple of 64)
            height: Image height (multiple of 64)
            steps: Sampling steps (20-50 typical)
            cfg: CFG scale (guidance strength, 7.0 typical)
            seed: Random seed (None = random)
            sampler_name: Sampler algorithm
            scheduler: Noise scheduler
            model_name: Checkpoint filename in models/checkpoints/
            lora_name: LoRA model filename (without extension) - optional
            lora_strength: LoRA strength/weight (0.0-2.0) - default 1.0
            
        Returns:
            ComfyUI workflow JSON ready to execute
        """
        
        # Generate random seed if not provided
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        
        # Determine model/clip source based on whether LoRA is used
        model_source = ["10", 0] if lora_name else ["4", 0]  # LoRA or Checkpoint
        clip_source = ["10", 1] if lora_name else ["4", 1]   # LoRA or Checkpoint
        
        workflow = {
            # Node 3: KSampler (The main sampling/generation node)
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler_name,
                    "scheduler": scheduler,
                    "denoise": 1.0,
                    "model": model_source,       # From LoRA or Checkpoint
                    "positive": ["6", 0],        # From positive CLIP encode
                    "negative": ["7", 0],        # From negative CLIP encode
                    "latent_image": ["5", 0]     # From EmptyLatentImage
                },
                "class_type": "KSampler"
            },
            
            # Node 4: Load Checkpoint (SD model)
            "4": {
                "inputs": {
                    "ckpt_name": model_name
                },
                "class_type": "CheckpointLoaderSimple"
            },
            
            # Node 5: Empty Latent Image (initial noise)
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            
            # Node 6: CLIP Text Encode (Positive prompt)
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": clip_source  # CLIP from LoRA or checkpoint
                },
                "class_type": "CLIPTextEncode"
            },
            
            # Node 7: CLIP Text Encode (Negative prompt)
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": clip_source  # CLIP from LoRA or checkpoint
                },
                "class_type": "CLIPTextEncode"
            },
            
            # Node 8: VAE Decode (latent to image)
            "8": {
                "inputs": {
                    "samples": ["3", 0],  # From KSampler
                    "vae": ["4", 2]       # VAE from checkpoint
                },
                "class_type": "VAEDecode"
            },
            
            # Node 9: Save Image (output)
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI_PeaceScript",
                    "images": ["8", 0]  # From VAE decode
                },
                "class_type": "SaveImage"
            }
        }
        
        # Add LoRA loader node if LoRA is specified
        if lora_name:
            # Need to add .safetensors extension if not present
            lora_filename = lora_name if '.' in lora_name else f"{lora_name}.safetensors"
            
            workflow["10"] = {
                "inputs": {
                    "lora_name": lora_filename,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["4", 0],  # Base model from checkpoint
                    "clip": ["4", 1]    # Base CLIP from checkpoint
                },
                "class_type": "LoraLoader"
            }
        
        return workflow
    
    @staticmethod
    def create_batch_txt2img_workflow(
        prompt: str,
        negative_prompt: str = "",
        width: int = 768,      # ✨ FIX: เพิ่มจาก 512 → 768
        height: int = 1024,    # ✨ FIX: เพิ่มจาก 768 → 1024
        steps: int = 40,       # ✨ FIX: เพิ่มจาก 30 → 40
        cfg: float = 7.0,
        seeds: Optional[List[int]] = None,
        model_name: str = "realisticVisionV60B1_v51HyperVAE.safetensors"
    ) -> List[Dict]:
        """
        Create multiple workflows with different seeds
        
        Use this for generating variations.
        
        Args:
            seeds: List of seeds to use (generates one workflow per seed)
            
        Returns:
            List of workflows
        """
        if seeds is None:
            seeds = [random.randint(0, 2**32 - 1) for _ in range(4)]
        
        workflows = []
        for seed in seeds:
            workflow = WorkflowBuilder.create_txt2img_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                cfg=cfg,
                seed=seed,
                model_name=model_name
            )
            workflows.append(workflow)
        
        return workflows
    
    @staticmethod
    def add_lora_to_workflow(
        workflow: Dict,
        lora_name: str,
        strength_model: float = 1.0,
        strength_clip: float = 1.0
    ) -> Dict:
        """
        Add LORA loader to existing workflow
        
        LORAs are fine-tuned adjustments applied on top of base model.
        
        Args:
            workflow: Existing workflow to modify
            lora_name: LORA filename (e.g., "add_detail.safetensors")
            strength_model: LORA strength for model (0.0-1.0)
            strength_clip: LORA strength for CLIP (0.0-1.0)
            
        Returns:
            Modified workflow with LORA
        """
        
        # Add LORA Loader node
        workflow["10"] = {
            "inputs": {
                "lora_name": lora_name,
                "strength_model": strength_model,
                "strength_clip": strength_clip,
                "model": ["4", 0],  # Model from checkpoint
                "clip": ["4", 1]    # CLIP from checkpoint
            },
            "class_type": "LoraLoader"
        }
        
        # Update KSampler to use LORA model
        workflow["3"]["inputs"]["model"] = ["10", 0]
        
        # Update CLIP encoders to use LORA CLIP
        workflow["6"]["inputs"]["clip"] = ["10", 1]
        workflow["7"]["inputs"]["clip"] = ["10", 1]
        
        return workflow


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_with_comfyui(
    prompt: str,
    negative_prompt: str = "",
    width: int = 512,      # ✨ HIGH QUALITY: ขนาดมาตรฐาน 512×768
    height: int = 768,     # ✨ HIGH QUALITY: สัดส่วน 2:3 สำหรับโปรไฟล์
    steps: int = 50,       # ✨ HIGH QUALITY: 50 steps สำหรับภาพคมชัดสุด
    cfg: float = 8.0,      # ✨ HIGH QUALITY: เพิ่ม guidance สูงสุดเพื่อความชัดและรายละเอียด
    seed: Optional[int] = None,
    comfyui_url: str = "http://127.0.0.1:8188",
    model_name: str = "realisticVisionV60B1_v51HyperVAE.safetensors",
    lora_name: Optional[str] = None,
    lora_strength: float = 1.0,
    timeout: Optional[int] = None
) -> Optional[bytes]:
    """
    Convenience function for quick image generation
    
    Example:
        >>> image_data = generate_with_comfyui(
        ...     prompt="beautiful portrait of a woman",
        ...     negative_prompt="ugly, deformed"
        ... )
        >>> if image_data:
        ...     with open("output.png", "wb") as f:
        ...         f.write(image_data)
    
    Returns:
        Image data (bytes) or None if failed
    """
    try:
        # Create client
        client_timeout = timeout or 600
        client = ComfyUIClient(comfyui_url, timeout=client_timeout)
        
        # Check if ComfyUI is running
        if not client.check_health():
            logger.error("ComfyUI is not running")
            return None
        
        # Build workflow
        workflow = WorkflowBuilder.create_txt2img_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg,
            seed=seed,
            model_name=model_name,
            lora_name=lora_name,
            lora_strength=lora_strength
        )
        
        # ✨ LOG WORKFLOW DETAILS
        logger.info(f"🔍 Workflow created with KSampler settings:")
        ksampler = workflow.get("3", {}).get("inputs", {})
        logger.info(f"   seed: {ksampler.get('seed', 'N/A')}")
        logger.info(f"   steps: {ksampler.get('steps', 'N/A')}")
        logger.info(f"   cfg: {ksampler.get('cfg', 'N/A')}")
        logger.info(f"   sampler_name: {ksampler.get('sampler_name', 'N/A')}")
        logger.info(f"   scheduler: {ksampler.get('scheduler', 'N/A')}")
        
        latent = workflow.get("5", {}).get("inputs", {})
        logger.info(f"🔍 Latent image size:")
        logger.info(f"   width: {latent.get('width', 'N/A')}")
        logger.info(f"   height: {latent.get('height', 'N/A')}")
        
        # Execute
        images = client.execute_workflow(workflow, timeout=timeout)
        
        if images:
            return images[0]  # Return first image
        
        return None
    
    except TimeoutError as e:
        logger.error(f"ComfyUI generation timed out after {client_timeout}s: {e}")
        raise
    except Exception as e:
        logger.error(f"ComfyUI generation failed: {e}", exc_info=True)
        return None


def batch_generate_with_comfyui(
    prompt: str,
    negative_prompt: str = "",
    num_variations: int = 4,
    width: int = 512,      # ✨ HIGH QUALITY: ขนาดมาตรฐาน 512×768
    height: int = 768,     # ✨ HIGH QUALITY: สัดส่วน 2:3 สำหรับโปรไฟล์
    steps: int = 50,       # ✨ HIGH QUALITY: 50 steps สำหรับภาพคมชัดสุด
    cfg: float = 8.0,      # ✨ HIGH QUALITY: เพิ่ม guidance สูงสุดเพื่อความชัดและรายละเอียด
    comfyui_url: str = "http://127.0.0.1:8188",
    model_name: str = "realisticVisionV60B1_v51HyperVAE.safetensors",
    lora_name: Optional[str] = None,
    lora_strength: float = 1.0,
    timeout: Optional[int] = None
) -> List[bytes]:
    """
    Generate multiple variations with different seeds
    
    Example:
        >>> images = batch_generate_with_comfyui(
        ...     prompt="character portrait",
        ...     num_variations=4
        ... )
        >>> for i, img_data in enumerate(images):
        ...     with open(f"output_{i}.png", "wb") as f:
        ...         f.write(img_data)
    
    Returns:
        List of image data (bytes)
    """
    client_timeout = timeout or 600
    client = ComfyUIClient(comfyui_url, timeout=client_timeout)
    
    if not client.check_health():
        logger.error("ComfyUI is not running")
        return []
    
    # Generate random seeds
    seeds = [random.randint(0, 2**32 - 1) for _ in range(num_variations)]
    
    all_images = []
    
    for i, seed in enumerate(seeds):
        logger.info(f"Generating variation {i+1}/{num_variations} (seed: {seed})")
        
        try:
            workflow = WorkflowBuilder.create_txt2img_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                cfg=cfg,
                seed=seed,
                model_name=model_name,
                lora_name=lora_name,
                lora_strength=lora_strength
            )
            
            images = client.execute_workflow(workflow, timeout=timeout)
            if images:
                all_images.extend(images)
        
        except TimeoutError as e:
            logger.error(f"Variation {i+1} timed out after {client_timeout}s")
            raise
        except Exception as e:
            logger.error(f"Failed to generate variation {i+1}: {e}")
    
    return all_images


# =============================================================================
# TESTING / DEMO
# =============================================================================

if __name__ == "__main__":
    """
    Quick test of ComfyUI client
    
    Run:
        python -m modules.comfyui_client
    """
    
    print("🎨 ComfyUI Client Test - comfyui_client.py:745")
    print("= - comfyui_client.py:746" * 50)
    
    # Check if ComfyUI is running
    client = ComfyUIClient()
    
    print(f"\n1. Health Check: {client.base_url} - comfyui_client.py:751")
    is_healthy = client.check_health()
    print(f"Status: {'✅ Running' if is_healthy else '❌ Not Running'} - comfyui_client.py:753")
    
    if not is_healthy:
        print("\n⚠️  ComfyUI is not running! - comfyui_client.py:756")
        print("Start it with: cd ~/ComfyUI && python main.py listen 0.0.0.0 port 8188 - comfyui_client.py:757")
        exit(1)
    
    # Get queue status
    print("\n2. Queue Status: - comfyui_client.py:761")
    queue = client.get_queue_status()
    print(f"{json.dumps(queue, indent=2)} - comfyui_client.py:763")
    
    # Generate test image
    print("\n3. Generating Test Image... - comfyui_client.py:766")
    print("Prompt: 'beautiful portrait of a woman, photorealistic' - comfyui_client.py:767")
    
    test_prompt = "beautiful portrait of a woman, photorealistic, highly detailed"
    test_negative = "ugly, deformed, blurry, bad anatomy"
    
    try:
        image_data = generate_with_comfyui(
            prompt=test_prompt,
            negative_prompt=test_negative,
            width=512,
            height=768,
            steps=20,  # Fast test
            cfg=7.0
        )
        
        if image_data:
            output_path = Path("comfyui_test_output.png")
            output_path.write_bytes(image_data)
            print(f"✅ Success! Saved to: {output_path} - comfyui_client.py:785")
            print(f"Size: {len(image_data) / 1024:.1f} KB - comfyui_client.py:786")
        else:
            print("❌ Failed to generate image - comfyui_client.py:788")
    
    except Exception as e:
        print(f"❌ Error: {e} - comfyui_client.py:791")
    
    print("\n - comfyui_client.py:793" + "=" * 50)
    print("Test complete! - comfyui_client.py:794")
