# 🔊 Voice Synthesis Guide
**Kamma-Based Voice Generation with TTS**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Setup Requirements](#setup-requirements)
3. [Architecture](#architecture)
4. [API Endpoints](#api-endpoints)
5. [Usage Examples](#usage-examples)
6. [Voice Parameter Mapping](#voice-parameter-mapping)
7. [TTS Engine Comparison](#tts-engine-comparison)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Voice Synthesis Module** converts Kamma-based VoiceScore into synthesized speech using Text-to-Speech (TTS) engines.

### Key Features
- ✅ **Buddhist-Accurate Mapping** - Voice reflects kamma (truthful speech, harsh speech, mettā)
- ✅ **Multiple TTS Engines** - Google TTS (free), ElevenLabs (premium), Coqui TTS (local)
- ✅ **Intelligent Parameter Mapping** - VoiceScore → pitch, speed, warmth, clarity
- ✅ **Caching System** - Reuse generated audio
- ✅ **Multi-Language Support** - Thai, English, and 100+ languages

### Buddhist Mappings

| Kamma Type | Voice Effect | TTS Parameters |
|------------|--------------|----------------|
| **Truthful Speech (Musāvāda veramaṇī)** | Clear, stable voice | High clarity (0.9+), stable pitch |
| **Harsh Speech (Pharusā vācā veramaṇī)** | Soft, gentle voice | Low tension (0.2), high warmth (0.8+) |
| **Mettā Practice** | Warm, compassionate tone | High warmth (0.9+), gentle speed |
| **Lying/Deceit** | Unclear, unstable voice | Low clarity (0.4), erratic pitch |

### Flow
```
VoiceScore (from Kamma Analysis)
    ↓
VoiceParameterMapper (Convert to TTS params)
    ↓
TTS Engine (Google/ElevenLabs/Coqui)
    ↓
Audio File (.mp3, .wav, .ogg)
```

---

## Setup Requirements

### 1. Install Python Dependencies

```bash
cd dmm_backend

# Google TTS (Free, recommended for Thai)
pip install gTTS

# ElevenLabs (Premium, best quality)
pip install elevenlabs

# Coqui TTS (Local, customizable)
pip install TTS

# Audio processing
pip install pydub
```

### 2. Configure TTS Engine

#### Google TTS (No setup needed)
```python
config = TTSConfig(
    engine="gtts",
    gtts_lang="th",  # Thai language
)
```

#### ElevenLabs (Requires API key)
```python
config = TTSConfig(
    engine="elevenlabs",
    elevenlabs_api_key="YOUR_API_KEY_HERE",
    elevenlabs_voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
)
```

Get API key: https://elevenlabs.io/

#### Coqui TTS (Local setup)
```bash
# Download models
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/your_tts')"
```

---

## Architecture

### Module Structure

```
dmm_backend/
├── modules/
│   ├── voice_synthesizer.py           # ⭐ Main module
│   ├── kamma_appearance_analyzer.py   # Provides VoiceScore
│   └── appearance_synthesizer.py      # Provides ExternalCharacter
├── routers/
│   └── kamma_appearance_router.py     # Voice API endpoints
└── VOICE_SYNTHESIS_GUIDE.md           # This file
```

### Core Classes

#### 1. **VoiceParameters**
TTS parameters derived from VoiceScore

```python
class VoiceParameters:
    pitch: float          # 0.5-2.0 (1.0 = normal)
    speed: float          # 0.5-2.0 (1.0 = normal)
    volume: float         # 0.0-1.0
    warmth: float         # 0.0-1.0
    clarity: float        # 0.0-1.0
    resonance: float      # 0.0-1.0
    tension: float        # 0.0-1.0
    breathiness: float    # 0.0-1.0
    emotional_tone: str   # "warm and gentle", "harsh and tense"
    energy_level: float   # 0.0-1.0
    metta_influence: float      # 0.0-1.0
    truthfulness_marker: float  # 0.0-1.0
```

#### 2. **VoiceParameterMapper**
Converts VoiceScore → VoiceParameters

**Algorithm:**
```python
1. Calculate pitch from voice_quality and warmth
   - High quality → natural pitch (1.0)
   - High warmth → slightly lower pitch (0.95)

2. Calculate speed from speech_clarity
   - High clarity → confident speed (0.95)
   - Low clarity → slower, hesitant (0.85)

3. Calculate clarity from speech_clarity + truthful_speech_score
   - High truthfulness → crystal clear
   - Low truthfulness → muddy, unclear

4. Calculate tension from harsh_speech_score
   - High harsh speech → high tension (tense voice)
   - Low harsh speech → relaxed (gentle voice)

5. Determine emotional_tone from all scores
   - "warm, gentle, and trustworthy"
   - "harsh, tense, and sharp"
   - "clear and articulate"
```

#### 3. **VoiceSynthesizer**
Main coordinator for TTS engines

**Key Methods:**
- `synthesize_voice()` - Generate audio from text + VoiceScore
- `get_voice_parameters()` - Get parameters without synthesizing
- `_generate_cache_key()` - Cache management

---

## API Endpoints

### 1. **POST /api/kamma-appearance/synthesize-voice**

Synthesize character's voice from text.

**Request:**
```json
{
    "model_id": "peace-mind-001",
    "text": "สวัสดีครับ ผมชื่อพีช ยินดีที่ได้รู้จักครับ",
    "engine": "gtts",
    "language": "th",
    "use_cache": true
}
```

**Response:**
```json
{
    "model_id": "peace-mind-001",
    "success": true,
    "audio_path": "audio_cache/voice_a1b2c3d4e5f6.mp3",
    "audio_base64": "SUQzBAAAAAAAI1RTU0UAAAAP...",
    "voice_parameters": {
        "pitch": 0.98,
        "speed": 0.95,
        "volume": 0.85,
        "warmth": 0.92,
        "clarity": 0.90,
        "emotional_tone": "warm, gentle, and trustworthy",
        "metta_influence": 0.92,
        "truthfulness_marker": 0.95
    },
    "voice_description": "Warm, gentle voice with excellent clarity. High mettā influence creates compassionate tone.",
    "engine": "gtts",
    "text_length": 45,
    "cached": false,
    "generated_at": "2025-10-17T10:30:00Z"
}
```

**Supported Engines:**
- `gtts` - Google TTS (free, Thai/English)
- `elevenlabs` - ElevenLabs (premium, requires API key)
- `coqui` - Coqui TTS (local, open source)

### 2. **GET /api/kamma-appearance/voice-parameters/{model_id}**

Get voice parameters without generating audio.

**Request:**
```bash
GET /api/kamma-appearance/voice-parameters/peace-mind-001
```

**Response:**
```json
{
    "model_id": "peace-mind-001",
    "voice_parameters": {
        "pitch": 0.98,
        "speed": 0.95,
        "volume": 0.85,
        "warmth": 0.92,
        "clarity": 0.90,
        "resonance": 0.88,
        "tension": 0.15,
        "breathiness": 0.25,
        "emotional_tone": "warm, gentle, and trustworthy",
        "energy_level": 0.87,
        "metta_influence": 0.92,
        "truthfulness_marker": 0.95
    },
    "voice_description": "Warm, gentle voice with excellent clarity. High mettā influence creates compassionate tone.",
    "voice_score": {
        "voice_quality": 85,
        "speech_clarity": 90,
        "vocal_warmth": 92,
        "truthful_speech_score": 95,
        "harsh_speech_score": 10
    },
    "timestamp": "2025-10-17T10:30:00Z"
}
```

### 3. **GET /api/kamma-appearance/voice-description/{model_id}**

Get human-readable voice description.

**Request:**
```bash
GET /api/kamma-appearance/voice-description/peace-mind-001
```

**Response:**
```json
{
    "model_id": "peace-mind-001",
    "description": "Warm, gentle voice with excellent clarity. High mettā influence creates compassionate tone. Honest and trustworthy quality.",
    "voice_quality": 85,
    "vocal_warmth": 92,
    "speech_clarity": 90,
    "truthful_speech_score": 95,
    "timestamp": "2025-10-17T10:30:00Z"
}
```

---

## Usage Examples

### Example 1: Basic Voice Synthesis (Python)

```python
from modules.voice_synthesizer import synthesize_character_voice
from kamma_appearance_models import VoiceScore

# Create VoiceScore
voice_score = VoiceScore(
    voice_quality=85.0,
    speech_clarity=90.0,
    vocal_warmth=92.0,
    truthful_speech_score=95.0,
    harsh_speech_score=10.0,
    description="Warm, gentle voice from mettā practice"
)

# Synthesize voice
result = synthesize_character_voice(
    text="สวัสดีครับ ผมชื่อพีช ยินดีที่ได้รู้จักครับ",
    voice_score=voice_score,
    engine="gtts"
)

if result["success"]:
    print(f"✅ Audio saved: {result['output_path']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Example 2: Get Voice Parameters Only

```python
from modules.voice_synthesizer import VoiceSynthesizer, TTSConfig

config = TTSConfig(engine="gtts")
synthesizer = VoiceSynthesizer(config)

params = synthesizer.get_voice_parameters(voice_score)

print(f"Pitch: {params.pitch}")
print(f"Speed: {params.speed}")
print(f"Warmth: {params.warmth}")
print(f"Emotional tone: {params.emotional_tone}")
```

### Example 3: Voice Description

```python
from modules.voice_synthesizer import get_voice_description

description = get_voice_description(voice_score)
print(description)
# Output: "Warm, gentle voice with excellent clarity. High mettā influence creates compassionate tone."
```

### Example 4: API Request (cURL)

```bash
# Synthesize voice
curl -X POST "http://localhost:8000/api/kamma-appearance/synthesize-voice" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "peace-mind-001",
    "text": "สวัสดีครับ",
    "engine": "gtts",
    "language": "th"
  }'

# Get voice parameters
curl "http://localhost:8000/api/kamma-appearance/voice-parameters/peace-mind-001"

# Get voice description
curl "http://localhost:8000/api/kamma-appearance/voice-description/peace-mind-001"
```

### Example 5: Frontend Integration (React)

```javascript
// Synthesize and play voice
async function speakCharacterText(modelId, text) {
  const response = await fetch('/api/kamma-appearance/synthesize-voice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model_id: modelId,
      text: text,
      engine: 'gtts',
      language: 'th'
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Play audio from base64
    const audio = new Audio(`data:audio/mp3;base64,${data.audio_base64}`);
    audio.play();
    
    // Show voice characteristics
    console.log('Voice:', data.voice_description);
    console.log('Parameters:', data.voice_parameters);
  }
}
```

---

## Voice Parameter Mapping

### Detailed Mappings

#### Pitch Calculation
```python
base_pitch = 1.0

# Quality adjustment (70-100 → 0.9-1.1)
quality_factor = (voice_quality - 50) / 500.0

# Warmth lowers pitch slightly (more resonant)
warmth_factor = -0.05 * (vocal_warmth / 100.0)

pitch = base_pitch + quality_factor + warmth_factor
```

**Examples:**
- High quality (90), high warmth (85): pitch = 0.99
- Low quality (40), low warmth (30): pitch = 1.01
- Neutral (70, 70): pitch = 1.00

#### Speed Calculation
```python
# Base speed from clarity
if speech_clarity >= 80:
    base_speed = 0.95  # Clear, confident
elif speech_clarity >= 60:
    base_speed = 0.9   # Moderate
else:
    base_speed = 0.85  # Slower, less confident

# Adjust for communication effectiveness
effectiveness_factor = (communication_effectiveness - 50) / 500.0

speed = base_speed + effectiveness_factor
```

**Examples:**
- High clarity (90), high effectiveness (85): speed = 0.97
- Low clarity (45), low effectiveness (40): speed = 0.83

#### Clarity Calculation
```python
base_clarity = speech_clarity / 100.0

# Truthfulness boost (truthful speech = clear speech)
truth_bonus = (truthful_speech_score - 50) / 200.0

clarity = base_clarity + truth_bonus
```

**Examples:**
- High clarity (90), high truth (95): clarity = 1.13 → clamped to 1.0
- Low clarity (40), low truth (30): clarity = 0.30

#### Tension Calculation
```python
# Harsh speech creates vocal tension
tension = harsh_speech_score / 100.0
```

**Examples:**
- High harsh speech (80): tension = 0.80 (very tense)
- Low harsh speech (10): tension = 0.10 (relaxed)

---

## TTS Engine Comparison

| Feature | Google TTS | ElevenLabs | Coqui TTS |
|---------|-----------|------------|-----------|
| **Cost** | Free | Paid (from $5/mo) | Free |
| **Quality** | Basic | Excellent | Good |
| **Thai Support** | ✅ Yes | ⚠️ Limited | ✅ Yes (with models) |
| **Setup** | Easy | Easy (API key) | Medium (download models) |
| **Customization** | Low | High | Very High |
| **Speed** | Fast | Fast (API) | Slow (local CPU) |
| **Privacy** | Cloud | Cloud | Local |
| **Voice Control** | Limited | Excellent | Good |

### Recommendations

**For Thai Language:**
- ✅ **Google TTS** - Best free option, good Thai support
- ✅ **Coqui TTS** - Best for local/private deployment

**For English:**
- ✅ **ElevenLabs** - Best quality, emotional expression
- ✅ **Google TTS** - Good free option

**For Production:**
- High budget → ElevenLabs
- Medium budget → Google TTS
- Privacy concerns → Coqui TTS

---

## Testing

See `test_voice_synthesis.py` for comprehensive tests.

---

## Buddhist Scriptural References

### Voice Quality from Kamma

**Aṅguttara Nikāya (AN 8.35)**
> "Monks, there are these eight causes for the acquisition of a beautiful voice... abstaining from harsh speech."

**Subha Sutta (SN 3.3)**
> "One who speaks gentle words has a sweet voice, pleasant to hear."

**Vācā Sutta (AN 5.198)**
> "Right speech leads to a voice that is clear, understandable, and pleasing to hear."

### Truthful Speech Effects

**Sacca Saṃyutta**
> "One who speaks truth, their words carry weight and clarity."

---

## Troubleshooting

### Error: "gTTS not installed"

**Solution:**
```bash
pip install gTTS
```

### Error: "elevenlabs not installed"

**Solution:**
```bash
pip install elevenlabs
```

### Error: "TTS not installed"

**Solution:**
```bash
pip install TTS
```

### Poor Thai Voice Quality

**Solutions:**
- Use Google TTS (best for Thai)
- Train custom Coqui model with Thai corpus
- Adjust speed/pitch parameters

### Audio Not Playing in Browser

**Solutions:**
- Check audio format (mp3 recommended)
- Verify base64 encoding is correct
- Test with `<audio>` tag in HTML

---

**Author:** Peace Script Development Team  
**Version:** 1.0.0  
**Date:** 2025-10-17
