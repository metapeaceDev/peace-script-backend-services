# 🎬 Video Generation API - Quality Settings Guide

## Overview

The Video Generation API supports two approaches for controlling output quality:

1. **Quality Presets** - Pre-configured settings optimized for different use cases
2. **Custom Parameters** - Manual control for advanced users

---

## Quality Presets

### Available Presets

| Preset | Resolution | Steps | Images | Est. Time | Use Case |
|--------|-----------|-------|--------|-----------|----------|
| `preview` | 256x144 | 3 | 1 | ~3s | Ultra-fast testing & iterations |
| `low` | 512x288 | 10 | 2 | ~10s | Draft reviews & storyboards |
| `medium` | 1024x576 | 20 | 3 | ~30s | General content & social media |
| `high` | 1920x1080 | 40 | 4 | ~60s | Professional videos |
| `ultra` | 1920x1080 | 80 | 5 | ~120s | Final renders & archival |

### Using Presets

```bash
# Simple request with preset
curl -X POST http://127.0.0.1:8000/api/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my_project",
    "prompt": "sunset over mountains, cinematic",
    "quality": "preview"
  }'
```

---

## Custom Parameters

Override any preset parameter for fine-grained control:

### Available Overrides

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `custom_width` | int | 256-3840 | preset | Video width in pixels |
| `custom_height` | int | 144-2160 | preset | Video height in pixels |
| `custom_steps` | int | 1-150 | preset | ComfyUI generation steps |
| `custom_fps` | int | 12-60 | preset | Frames per second |
| `custom_num_images` | int | 1-10 | preset | Number of images to generate |

### Example: Custom Quality

```bash
# Use "low" preset but override resolution to 720p
curl -X POST http://127.0.0.1:8000/api/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my_project",
    "prompt": "futuristic city, cyberpunk style",
    "quality": "low",
    "custom_width": 1280,
    "custom_height": 720,
    "custom_steps": 15
  }'
```

### Example: Maximum Customization

```bash
# Full custom control
curl -X POST http://127.0.0.1:8000/api/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my_project",
    "prompt": "ancient temple, mystical atmosphere",
    "quality": "medium",
    "custom_width": 1920,
    "custom_height": 1080,
    "custom_steps": 50,
    "custom_fps": 30,
    "custom_num_images": 5
  }'
```

---

## Quality Presets Info Endpoint

Get detailed information about all available presets:

```bash
GET /api/video/quality-presets
```

**Response:**
```json
{
  "presets": {
    "preview": {
      "name": "Preview",
      "description": "Ultra-fast preview for testing (256p, 3 steps)",
      "resolution": "256x144",
      "estimated_time": "~3s",
      "file_size": "0.5 MB/s",
      "recommended_for": "Quick tests and iterations"
    },
    "low": {
      "name": "Low Quality",
      "description": "Fast generation for drafts (480p, 10 steps)",
      "resolution": "512x288",
      "estimated_time": "~10s",
      "file_size": "1 MB/s",
      "recommended_for": "Draft reviews and storyboards"
    }
    // ... more presets
  },
  "default": "preview",
  "recommended": {
    "testing": "preview",
    "draft": "low",
    "production": "medium",
    "final": "high",
    "archive": "ultra"
  }
}
```

---

## Complete Request Schema

```typescript
{
  // Required
  "project_id": string,
  
  // Basic settings
  "prompt": string,                    // AI generation prompt
  "quality": "preview" | "low" | "medium" | "high" | "ultra",
  "mode": "image_to_video" | "animate_diff",
  
  // Optional custom overrides
  "custom_width": number,              // 256-3840
  "custom_height": number,             // 144-2160
  "custom_steps": number,              // 1-150 (ComfyUI steps)
  "custom_fps": number,                // 12-60
  "custom_num_images": number,         // 1-10
  
  // Motion parameters (optional)
  "motion_parameters": {
    "zoom": number,                    // 0.5-3.0
    "pan_x": number,                   // -1.0 to 1.0
    "pan_y": number,                   // -1.0 to 1.0
    "speed": number                    // 0.1-5.0
  },
  
  // Additional options
  "shot_id": string,
  "format": "mp4" | "webm" | "mov",
  "duration": number,                  // 1.0-30.0 seconds
  "style_preset": string
}
```

---

## Performance Tips

### 1. Choose the Right Preset

- **Testing & Iteration**: Use `preview` (3s generation)
- **Client Review**: Use `low` or `medium` (10-30s)
- **Final Delivery**: Use `high` or `ultra` (60-120s)

### 2. Custom Optimization

- **Reduce steps** for faster generation (quality tradeoff)
- **Lower resolution** for draft versions
- **Fewer images** for simpler videos
- **Lower FPS** (12-24) for social media

### 3. Quality vs Speed Matrix

```
Fast ←────────────────────→ Quality
preview → low → medium → high → ultra
  3s      10s     30s      60s    120s
```

---

## Examples

### Quick Test
```json
{
  "project_id": "test",
  "prompt": "test scene",
  "quality": "preview"
}
```
**Result**: 256x144, 3 steps, ~3 seconds

### Social Media
```json
{
  "project_id": "instagram_post",
  "prompt": "product showcase, professional lighting",
  "quality": "medium"
}
```
**Result**: 1024x576, 20 steps, ~30 seconds

### Custom High-Res Draft
```json
{
  "project_id": "client_review",
  "prompt": "architectural visualization",
  "quality": "low",
  "custom_width": 1920,
  "custom_height": 1080
}
```
**Result**: 1920x1080 but only 10 steps (faster than "high")

### Maximum Quality
```json
{
  "project_id": "final_render",
  "prompt": "cinematic landscape, golden hour",
  "quality": "ultra",
  "motion_parameters": {
    "zoom": 1.2,
    "pan_x": 0.1,
    "speed": 0.8
  }
}
```
**Result**: 1920x1080, 80 steps, 5 images, smooth motion

---

## Error Handling

### Invalid Custom Values

If custom parameters are out of range, you'll get a validation error:

```json
{
  "detail": [
    {
      "loc": ["body", "custom_width"],
      "msg": "ensure this value is greater than or equal to 256",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### Invalid Quality Preset

Falls back to `preview` automatically with a warning in logs.

---

## Monitoring Generation

After submitting a request, poll the job status:

```bash
GET /api/video/jobs/{job_id}
```

**Response includes:**
- `progress`: 0-100
- `status`: queued, generating, complete, failed
- `estimated_completion`: Based on quality preset
- `error_message`: If failed
