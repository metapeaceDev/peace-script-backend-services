# 🎨 AI Image Generation Guide
**Kamma-Based Character Visualization with Stable Diffusion**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Setup Requirements](#setup-requirements)
3. [Architecture](#architecture)
4. [API Endpoints](#api-endpoints)
5. [Usage Examples](#usage-examples)
6. [Prompt Generation](#prompt-generation)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The **AI Image Generation Module** converts Kamma-based character appearances into photorealistic images using Stable Diffusion.

### Key Features
- ✅ **Automatic Prompt Generation** - Converts `ExternalCharacter` → SD prompt
- ✅ **Buddhist Accuracy** - Reflects kamma influence in visuals
- ✅ **Multiple Styles** - Realistic, anime, portrait, cinematic
- ✅ **Stable Diffusion Integration** - Uses AUTOMATIC1111 WebUI API
- ✅ **Caching System** - Reuse generated images
- ✅ **Base64 Response** - Easy frontend integration

### Flow
```
DigitalMindModel (Kamma Ledger)
    ↓
KammaAppearanceAnalyzer (Analyze kamma)
    ↓
AppearanceSynthesizer (Generate ExternalCharacter)
    ↓
AppearancePromptGenerator (Convert to SD prompt)
    ↓
StableDiffusionClient (Generate image)
    ↓
Base64 Image + Metadata
```

---

## Setup Requirements

### 1. Install Stable Diffusion WebUI

```bash
# Clone AUTOMATIC1111 repo
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# Run setup
./webui.sh --api --listen

# Or on macOS
./webui.sh --api --no-half --skip-torch-cuda-test
```

### 2. Install Python Dependencies

```bash
# In dmm_backend directory
pip install requests Pillow
```

### 3. Download SD Model (Optional)

Recommended models:
- **Realistic Vision V5.1** - Best for photorealistic portraits
- **Deliberate V2** - Balanced realism
- **DreamShaper** - Artistic style

Place `.safetensors` files in:
```
stable-diffusion-webui/models/Stable-diffusion/
```

### 4. Verify API Running

```bash
curl http://localhost:7860/sdapi/v1/sd-models
```

Should return list of models.

---

## Architecture

### Module Structure

```
dmm_backend/
├── modules/
│   ├── ai_image_generator.py          # ⭐ Main module
│   ├── kamma_appearance_analyzer.py   # Kamma analysis
│   └── appearance_synthesizer.py      # Appearance generation
├── routers/
│   └── kamma_appearance_router.py     # API endpoints
└── AI_IMAGE_GENERATION_GUIDE.md       # This file
```

### Core Classes

#### 1. **AppearancePromptGenerator**
Converts `ExternalCharacter` → Stable Diffusion prompt

**Key Methods:**
- `generate_prompt()` - Main entry point
- `_generate_physical_prompt()` - Body/fitness
- `_generate_facial_prompt()` - Face/skin/eyes/hair
- `_generate_expression_prompt()` - Demeanor/posture
- `_generate_kamma_traits()` - Buddhist influence

**Example Output:**
```python
{
    "positive": "(masterpiece:1.2), (best quality:1.2), (ultra-detailed:1.2), (photorealistic:1.4), professional photography, studio lighting, 8k uhd, dslr, Thai person, Southeast Asian features, 28 year old male, athletic, fit, toned, oval face, radiant skin, healthy glow, luminous, brown eyes, short black hair, warm expression, friendly demeanor, confident posture, shoulders back, charismatic presence, captivating, casual clothing, everyday wear, wearing blue, white, centered composition, upper body portrait, peaceful aura, inner light, compassionate eyes, gentle smile",
    
    "negative": "ugly, deformed, noisy, blurry, distorted, out of focus, bad anatomy, extra limbs, poorly drawn face, poorly drawn hands, missing fingers, extra fingers, mutated hands, bad proportions, gross proportions, duplicate, watermark, signature, text, logo, lowres, low quality, worst quality"
}
```

#### 2. **StableDiffusionClient**
Communicates with SD WebUI API

**Key Methods:**
- `generate_image()` - Generate image from ExternalCharacter
- `generate_prompt_only()` - Get prompt without generation

**Configuration:**
```python
class SDConfig:
    api_url: str = "http://localhost:7860"
    model: str = "realisticVisionV51_v51VAE"
    sampler: str = "DPM++ 2M Karras"
    steps: int = 30
    cfg_scale: float = 7.0
    width: int = 512
    height: int = 768  # Portrait ratio
    seed: int = -1     # Random
```

---

## API Endpoints

### 1. **POST /api/kamma-appearance/generate-image**

Generate AI image from character's appearance.

**Request:**
```json
{
    "model_id": "peace-mind-001",
    "style": "realistic",
    "sd_api_url": "http://localhost:7860",
    "save_to_db": true
}
```

**Response:**
```json
{
    "model_id": "peace-mind-001",
    "success": true,
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "prompts": {
        "positive": "(masterpiece:1.2)...",
        "negative": "ugly, deformed..."
    },
    "seed": 1234567890,
    "width": 512,
    "height": 768,
    "model": "realisticVisionV51_v51VAE",
    "saved_to": null,
    "generated_at": "2025-06-15T10:30:00Z"
}
```

**Error Response:**
```json
{
    "model_id": "peace-mind-001",
    "success": false,
    "prompts": {...},
    "error": "Cannot connect to Stable Diffusion API. Is it running?",
    "generated_at": "2025-06-15T10:30:00Z"
}
```

### 2. **GET /api/kamma-appearance/prompt/{model_id}**

Get SD prompt without generating image (for testing).

**Request:**
```bash
GET /api/kamma-appearance/prompt/peace-mind-001?style=realistic
```

**Response:**
```json
{
    "model_id": "peace-mind-001",
    "style": "realistic",
    "prompts": {
        "positive": "(masterpiece:1.2)...",
        "negative": "ugly, deformed..."
    },
    "prompt_length": 450,
    "timestamp": "2025-06-15T10:30:00Z"
}
```

---

## Usage Examples

### Example 1: Basic Image Generation

```python
from modules.ai_image_generator import generate_character_image
from modules.appearance_synthesizer import synthesize_from_model

# 1. Generate ExternalCharacter from model
profile = {...}  # KammaAppearanceProfile
external = synthesize_from_model(profile)

# 2. Generate image
result = generate_character_image(
    external=external,
    output_path="output/peace-mind-001.png",
    sd_api_url="http://localhost:7860",
    style="realistic"
)

# 3. Check result
if result.get("success"):
    print(f"✅ Image saved to: {result['saved_to']}")
    print(f"🎲 Seed: {result['seed']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Example 2: Get Prompt Only

```python
from modules.ai_image_generator import get_prompt_for_character

prompts = get_prompt_for_character(
    external=external,
    kamma_profile=profile,
    style="realistic"
)

print("Positive Prompt:")
print(prompts["positive"])

print("\nNegative Prompt:")
print(prompts["negative"])
```

### Example 3: Custom SD Configuration

```python
from modules.ai_image_generator import StableDiffusionClient, SDConfig

# Custom config
config = SDConfig(
    api_url="http://192.168.1.100:7860",
    model="deliberate_v2",
    steps=50,
    cfg_scale=8.5,
    width=768,
    height=1024,
    seed=42  # Fixed seed for reproducibility
)

client = StableDiffusionClient(config)
result = client.generate_image(external, kamma_profile=profile)
```

### Example 4: API Request (cURL)

```bash
# Generate image
curl -X POST "http://localhost:8000/api/kamma-appearance/generate-image" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "peace-mind-001",
    "style": "realistic",
    "sd_api_url": "http://localhost:7860"
  }'

# Get prompt only
curl "http://localhost:8000/api/kamma-appearance/prompt/peace-mind-001?style=realistic"
```

### Example 5: Frontend Integration (React)

```javascript
// Generate and display image
async function generateCharacterImage(modelId) {
  const response = await fetch('/api/kamma-appearance/generate-image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model_id: modelId,
      style: 'realistic',
      sd_api_url: 'http://localhost:7860'
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Display image
    const imgElement = document.getElementById('character-image');
    imgElement.src = `data:image/png;base64,${data.image_base64}`;
    
    console.log('Prompt used:', data.prompts.positive);
    console.log('Seed:', data.seed);
  } else {
    console.error('Error:', data.error);
  }
}
```

---

## Prompt Generation

### Prompt Structure

The generated prompt follows this structure:

```
[Quality Prefix] + [Style] + [Cultural Context] + [Physical] + [Facial] + [Expression] + [Clothing] + [Kamma Traits] + [Camera/Composition]
```

### Kamma → Visual Mapping

| Kamma Category | Visual Effect | Prompt Addition |
|----------------|---------------|-----------------|
| **High Mettā (>80)** | Warm, compassionate appearance | "compassionate eyes, gentle smile, warm expression" |
| **High Kusala (>70)** | Peaceful aura, inner glow | "peaceful aura, inner light, serene expression" |
| **Meditation Practice** | Calm, centered presence | "mindful presence, centered composure, calm demeanor" |
| **Protection Kamma** | Vibrant, healthy appearance | "vibrant, energetic presence, healthy glow" |
| **Truthful Speech** | Clear, honest features | "clear eyes, honest expression, open face" |
| **Harmful Actions** | Tense, harsh features | "tense expression, harsh features, stern look" |

### Style Variations

#### Realistic
```
(masterpiece:1.2), (best quality:1.2), (ultra-detailed:1.2), (photorealistic:1.4), professional photography, studio lighting, 8k uhd, dslr
```

#### Anime
```
anime style, highly detailed, cel shading, vibrant colors, studio quality
```

#### Portrait
```
portrait photography, bokeh background, 85mm lens, shallow depth of field, professional lighting
```

#### Cinematic
```
cinematic lighting, dramatic, film grain, anamorphic lens, movie still
```

---

## Testing

### Test Case 1: Monk with High Mettā

```python
# Character: Peaceful monk
profile = KammaAppearanceProfile(
    model_id="monk-001",
    health_score=HealthScore(
        body_strength=85,
        skin_quality=90,
        overall_health=88,
        description="Excellent health from protection practice"
    ),
    voice_score=VoiceScore(
        voice_quality=92,
        speech_clarity=95,
        description="Clear, gentle voice from truthful speech"
    ),
    demeanor_score=DemeanorScore(
        peacefulness=95,
        loving_kindness_score=98,
        expression_openness=90,
        description="Radiant with mettā practice"
    ),
    kusala_percentage=95.0,
    akusala_percentage=5.0
)

result = generate_character_image(
    external=synthesize_from_model(profile),
    style="portrait"
)

# Expected: Peaceful, radiant, compassionate face
```

### Test Case 2: Warrior with Mixed Kamma

```python
# Character: Conflicted warrior
profile = KammaAppearanceProfile(
    model_id="warrior-001",
    health_score=HealthScore(
        body_strength=95,
        vitality=85,
        overall_health=75,
        description="Strong body but conflicted mind"
    ),
    demeanor_score=DemeanorScore(
        confidence_level=85,
        peacefulness=40,
        tension_level=70,
        description="Confident but tense"
    ),
    kusala_percentage=50.0,
    akusala_percentage=50.0
)

result = generate_character_image(
    external=synthesize_from_model(profile),
    style="cinematic"
)

# Expected: Strong, intense, somewhat tense appearance
```

### Test Case 3: Young Student

```python
# Character: Bright student
profile = KammaAppearanceProfile(
    model_id="student-001",
    health_score=HealthScore(
        energy_level=90,
        overall_health=82
    ),
    voice_score=VoiceScore(
        voice_quality=85,
        speech_clarity=88
    ),
    demeanor_score=DemeanorScore(
        intellectual_appearance=92,
        expression_openness=85,
        charisma_modifier=5
    ),
    kusala_percentage=75.0
)

result = generate_character_image(
    external=synthesize_from_model(profile),
    style="realistic"
)

# Expected: Youthful, bright, intellectual appearance
```

---

## Troubleshooting

### Error: "Cannot connect to Stable Diffusion API"

**Cause:** SD WebUI not running

**Solution:**
```bash
cd stable-diffusion-webui
./webui.sh --api --listen
```

Check if API is responding:
```bash
curl http://localhost:7860/sdapi/v1/sd-models
```

### Error: "Import requests could not be resolved"

**Cause:** Missing Python package

**Solution:**
```bash
pip install requests Pillow
```

### Error: "No images in SD response"

**Cause:** SD generation failed (invalid prompt, OOM, etc.)

**Solution:**
- Check SD WebUI console for errors
- Reduce image resolution (width/height)
- Reduce steps (e.g., 20 instead of 30)
- Simplify prompt (remove some modifiers)

### Poor Image Quality

**Solutions:**
- Use better SD model (Realistic Vision V5.1)
- Increase steps (40-50)
- Adjust CFG scale (7-9 range)
- Add more detail to prompt
- Use higher resolution (768x1024)

### Images Don't Match Kamma

**Solutions:**
- Check `KammaAppearanceProfile` scores
- Verify prompt generation in `/prompt/{model_id}` endpoint
- Adjust kamma-to-visual mappings in `AppearancePromptGenerator`
- Use fixed seed for reproducibility

### Slow Generation

**Solutions:**
- Reduce steps (20-25 for fast preview)
- Use smaller resolution (512x512)
- Use faster sampler (Euler a, DPM++ SDE)
- Use GPU-optimized SD setup

---

## Advanced Features

### Batch Generation

```python
model_ids = ["monk-001", "warrior-001", "student-001"]

for model_id in model_ids:
    external = await get_external_character(model_id)
    result = generate_character_image(
        external,
        output_path=f"output/{model_id}.png"
    )
    print(f"Generated: {model_id}")
```

### Prompt Customization

```python
# Override default prompt generator
class CustomPromptGenerator(AppearancePromptGenerator):
    QUALITY_PREFIX = "(8k resolution), (extremely detailed), (award winning)"
    
    def _generate_kamma_traits(self, profile):
        # Custom kamma visualization
        if profile.kusala_percentage >= 90:
            return "divine presence, enlightened aura, radiant light"
        return super()._generate_kamma_traits(profile)

# Use custom generator
client.prompt_generator = CustomPromptGenerator()
```

### Image Post-Processing

```python
from PIL import Image, ImageEnhance

result = generate_character_image(external)
image = result["image"]

# Enhance
enhancer = ImageEnhance.Brightness(image)
image = enhancer.enhance(1.2)

image.save("enhanced.png")
```

---

## Buddhist Scriptural References

### Visual Kamma Effects

**Aṅguttara Nikāya (AN 8.35)**
> "Monks, there are these eight causes for the acquisition of wisdom... avoiding violence leads to beauty and radiance."

**Kamma Vibhāga Sutta**
> "Through abstaining from killing, one has a beautiful complexion and a clear complexion."

### Mettā Influence

**Metta Sutta**
> "One who develops loving-kindness becomes beautiful, sleeps peacefully, and is dear to human and non-human beings."

---

## Next Steps

1. ✅ **Completed:** Basic image generation
2. 🔄 **Phase 2.3:** Voice synthesis integration
3. 🔄 **Phase 2.4:** 3D avatar animation
4. 🔄 **Phase 2.5:** Temporal tracking (kamma changes over time)

---

**Author:** Peace Script Development Team  
**Version:** 1.0.0  
**Date:** 2025-06-15
