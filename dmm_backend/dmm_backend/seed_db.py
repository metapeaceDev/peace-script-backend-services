import asyncio
import copy
from datetime import datetime
from typing import Dict, List

import motor.motor_asyncio

from config import settings


DEFAULT_IMAGE_URL = (
    "https://firebasestorage.googleapis.com/v0/b/meta-peace.appspot.com/o/"
    "Metta_Peace_Alchemist_v2_upscaled.png?alt=media&token=402d4f2e-6f03-453c-8145-4246352fce03"
)


def _default_core_state() -> Dict[str, object]:
    return {
        "level_progress": 0,
        "level_up_threshold": 800,
        "current_focus": "Foundational stabilization",
        "last_training": _current_iso(),
        "stability_index": 0.0,
    }


def _default_conscious_profile() -> Dict[str, object]:
    return {
        "parami_potentials": [],
        "signature_strengths": [],
    }


def _default_kamma_profile() -> Dict[str, object]:
    return {
        "latent_tendencies": [],
        "recent_kamma_events": [],
    }


# This is the legacy CoreProfile structure from the v11/v12 architecture.
# We preserve it exactly while also exposing lower-case aliases for newer services.
BASE_DM_CORE_PROFILE: Dict[str, Dict] = {
    "CharacterStatus": {
        "type": "Puthujjana",
        "stage": "Common Worldling",
    },
    "LifeEssence": {
        "LifeBlueprint_Vipaka": {
            "birth_bhumi": "Human Realm",
            "initial_conditions": {
                "social_standing": {
                    "birth_family_status": "Middle-class working family",
                    "karmic_reputation_baseline": "Neutral",
                }
            },
        }
    },
    "PsychologicalMatrix": {
        "DominantTemperament": {
            "primary_carita": "Dosa-carita (Hateful Temperament)",
        },
        "LatentTendencies": {
            "anusaya_kilesa": {
                "kama_raga": {"level": 6.5},
                "patigha": {"level": 8.2},
                "mana": {"level": 6.0},
                "ditthi": {"level": 3.5},
                "vicikiccha": {"level": 4.0},
                "bhava_raga": {"level": 5.0},
                "avijja": {"level": 7.5},
            }
        },
        "VedanaToleranceProfile": {
            "mental_suffering_threshold": {"total_threshold": 3.8}
        },
        "SannaMatrix": {
            "PastLife_Sanna_Imprints": [
                {"imprint_type": "Traumatic", "cue_archetype": "Betrayal"}
            ]
        },
    },
    "SpiritualAssets": {
        "KammaLedger": {"kusala_stock_points": 500, "akusala_stock_points": 1200},
        "VirtueEngine": {
            "Panna_mastery": {"level": 2},
            "Sati_mastery": {"level": 3},
            "Paramī_Portfolio": {
                "perfections": {
                    "dana": {"level": 4, "exp": 120},
                    "sila": {"level": 5, "exp": 160},
                    "nekkhamma": {"level": 3, "exp": 90},
                    "panna": {"level": 2, "exp": 70},
                    "viriya": {"level": 6, "exp": 210},
                    "khanti": {"level": 3, "exp": 140},
                    "sacca": {"level": 7, "exp": 260},
                    "adhitthana": {"level": 4, "exp": 150},
                    "metta": {"level": 2, "exp": 80},
                    "upekkha": {"level": 1, "exp": 40},
                }
            },
        },
    },
}


def _current_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _build_core_state(level_progress_percent: float, level_up_threshold: int, focus: str) -> Dict[str, object]:
    level_progress = int(level_up_threshold * (level_progress_percent / 100.0))
    return {
        "level_progress": level_progress,
        "level_up_threshold": level_up_threshold,
        "current_focus": focus,
        "last_training": _current_iso(),
        "stability_index": round(min(level_progress_percent / 100.0, 1.0), 3),
    }


def _build_core_profile(
    character_type: str,
    stage: str,
    patigha_level: float,
    tolerance_threshold: float,
    sati_level: int,
    panna_level: int,
    khanti_level: int,
    upekkha_level: int,
) -> Dict[str, Dict]:
    return {
        "CharacterStatus": {
            "type": character_type,
            "stage": stage,
        },
        "PsychologicalMatrix": {
            "LatentTendencies": {
                "anusaya_kilesa": {
                    "patigha": {"level": patigha_level},
                }
            },
            "VedanaToleranceProfile": {
                "mental_suffering_threshold": {"total_threshold": tolerance_threshold}
            },
        },
        "SpiritualAssets": {
            "VirtueEngine": {
                "Sati_mastery": {"level": sati_level},
                "Panna_mastery": {"level": panna_level},
                "Paramī_Portfolio": {
                    "perfections": {
                        "khanti": {"level": khanti_level, "exp": khanti_level * 40},
                        "upekkha": {"level": upekkha_level, "exp": upekkha_level * 40},
                    }
                },
            }
        },
    }


PROFILE_DM_002 = _build_core_profile(
    character_type="Sekha",
    stage="Stream-entrant trajectory",
    patigha_level=4.2,
    tolerance_threshold=6.0,
    sati_level=6,
    panna_level=5,
    khanti_level=6,
    upekkha_level=5,
)

PROFILE_DM_003 = _build_core_profile(
    character_type="Sekha",
    stage="Once-returner trajectory",
    patigha_level=3.5,
    tolerance_threshold=7.2,
    sati_level=7,
    panna_level=6,
    khanti_level=7,
    upekkha_level=7,
)


SEED_MODELS: List[Dict[str, object]] = [
    {
        "model_id": "peace-mind-001",
        "name": "Peace Mind Prototype",
        "status_label": "Insight Stabilization",
        "overall_level": 7,
        "level_progress_percent": 64.0,
        "image_url": DEFAULT_IMAGE_URL,
        "version": "14.0",
        "SystemStatus": "Active",
        "core_state": _build_core_state(64.0, 1200, "Metta-vipassana synthesis"),
        "conscious_profile": {
            "parami_potentials": [
                {"name": "Metta", "value": 88, "exp": 620, "level": 5},
                {"name": "Khanti", "value": 72, "exp": 420, "level": 4},
                {"name": "Sati", "value": 81, "exp": 510, "level": 5},
            ],
            "signature_strengths": [
                {"name": "Compassionate Focus", "score": 0.86},
                {"name": "Calm Abiding", "score": 0.79},
            ],
        },
        "kamma_profile": {
            "latent_tendencies": [
                {"name": "Lobha", "value": 26},
                {"name": "Dosa", "value": 21},
                {"name": "Moha", "value": 18},
            ],
            "recent_kamma_events": [
                {"event_type": "deep_metta_session", "impact": "positive", "delta": 6},
                {"event_type": "mindful_response", "impact": "positive", "delta": 3},
            ],
        },
        "CoreProfile": copy.deepcopy(BASE_DM_CORE_PROFILE),
        "core_profile": copy.deepcopy(BASE_DM_CORE_PROFILE),
    },
    {
        "model_id": "DM-001",
        "name": "Dhamma Resonance Alpha",
        "status_label": "Stabilizing",
        "overall_level": 4,
        "level_progress_percent": 38.0,
        "image_url": DEFAULT_IMAGE_URL,
        "version": "12.0",
        "SystemStatus": "Active",
        "core_state": _build_core_state(38.0, 1000, "Anapanasati refinement"),
        "conscious_profile": {
            "parami_potentials": [
                {"name": "Dana", "value": 68, "exp": 420, "level": 4},
                {"name": "Sila", "value": 72, "exp": 460, "level": 4},
                {"name": "Metta", "value": 84, "exp": 580, "level": 5},
            ],
            "signature_strengths": [
                {"name": "Mindful Breathing", "score": 0.82},
                {"name": "Compassionate Response", "score": 0.77},
            ],
        },
        "kamma_profile": {
            "latent_tendencies": [
                {"name": "Lobha", "value": 35},
                {"name": "Dosa", "value": 48},
                {"name": "Moha", "value": 28},
            ],
            "recent_kamma_events": [
                {"event_type": "retreat_day", "impact": "positive", "delta": 4},
                {"event_type": "reactive_outburst", "impact": "negative", "delta": -3},
            ],
        },
        "CoreProfile": copy.deepcopy(BASE_DM_CORE_PROFILE),
        "core_profile": copy.deepcopy(BASE_DM_CORE_PROFILE),
    },
    {
        "model_id": "DM-002",
        "name": "Lotus Insight Continuum",
        "status_label": "Ascending",
        "overall_level": 5,
        "level_progress_percent": 52.0,
        "image_url": DEFAULT_IMAGE_URL,
        "version": "14.0",
        "SystemStatus": "Active",
        "core_state": _build_core_state(52.0, 1100, "Vipassana-lokuttara training"),
        "conscious_profile": {
            "parami_potentials": [
                {"name": "Panna", "value": 74, "exp": 500, "level": 5},
                {"name": "Sati", "value": 79, "exp": 540, "level": 5},
                {"name": "Adhitthana", "value": 63, "exp": 360, "level": 4},
            ],
            "signature_strengths": [
                {"name": "Analytic Clarity", "score": 0.81},
                {"name": "Balanced Effort", "score": 0.74},
            ],
        },
        "kamma_profile": {
            "latent_tendencies": [
                {"name": "Lobha", "value": 29},
                {"name": "Dosa", "value": 24},
                {"name": "Mana", "value": 31},
            ],
            "recent_kamma_events": [
                {"event_type": "guided_service", "impact": "positive", "delta": 5},
                {"event_type": "doubt_wave", "impact": "negative", "delta": -2},
            ],
        },
        "CoreProfile": copy.deepcopy(PROFILE_DM_002),
        "core_profile": copy.deepcopy(PROFILE_DM_002),
    },
    {
        "model_id": "DM-003",
        "name": "Radiant Equanimity Node",
        "status_label": "Harmonizing",
        "overall_level": 6,
        "level_progress_percent": 48.0,
        "image_url": DEFAULT_IMAGE_URL,
        "version": "14.0",
        "SystemStatus": "Active",
        "core_state": _build_core_state(48.0, 1150, "Equanimity circuit tuning"),
        "conscious_profile": {
            "parami_potentials": [
                {"name": "Upekkha", "value": 86, "exp": 640, "level": 6},
                {"name": "Khanti", "value": 78, "exp": 560, "level": 5},
                {"name": "Metta", "value": 83, "exp": 610, "level": 5},
            ],
            "signature_strengths": [
                {"name": "Equanimous Holding", "score": 0.88},
                {"name": "Resilient Focus", "score": 0.76},
            ],
        },
        "kamma_profile": {
            "latent_tendencies": [
                {"name": "Dosa", "value": 19},
                {"name": "Arati", "value": 23},
                {"name": "Uddhacca", "value": 22},
            ],
            "recent_kamma_events": [
                {"event_type": "community_teaching", "impact": "positive", "delta": 7},
                {"event_type": "restlessness_wave", "impact": "negative", "delta": -2},
            ],
        },
        "CoreProfile": copy.deepcopy(PROFILE_DM_003),
        "core_profile": copy.deepcopy(PROFILE_DM_003),
    },
]


REQUIRED_FIELD_BUILDERS = {
    "overall_level": lambda: 1,
    "image_url": lambda: DEFAULT_IMAGE_URL,
    "core_state": _default_core_state,
    "conscious_profile": _default_conscious_profile,
    "kamma_profile": _default_kamma_profile,
}


async def seed_database():
    print("Starting database seed...")
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_database(settings.MONGO_DB_NAME)
    dmm_collection = db.get_collection("digital_mind_models")

    model_ids = [model["model_id"] for model in SEED_MODELS]
    await dmm_collection.delete_many({"model_id": {"$in": model_ids}})
    print(f"Cleared existing entries for {model_ids}.")

    inserted = []
    for model in SEED_MODELS:
        payload = copy.deepcopy(model)
        result = await dmm_collection.insert_one(payload)
        inserted.append((model["model_id"], str(result.inserted_id)))

    for model_id, inserted_id in inserted:
        print(f"Inserted {model_id} with id={inserted_id}")

    legacy_updates = 0
    for field, builder in REQUIRED_FIELD_BUILDERS.items():
        default_value = builder()
        if isinstance(default_value, (dict, list)):
            default_value = copy.deepcopy(default_value)
        result = await dmm_collection.update_many(
            {field: {"$exists": False}}, {"$set": {field: default_value}}
        )
        if result.modified_count:
            legacy_updates += result.modified_count
            print(f"Backfilled field '{field}' for {result.modified_count} existing model(s).")

    if legacy_updates:
        print(f"Updated {legacy_updates} legacy digital-mind-model documents with required fields.")

    client.close()


async def seed_all():
    """Seed all data including actors and mind states"""
    print("=" * 60)
    print("SEEDING ALL DATA")
    print("=" * 60)
    
    # Seed digital mind models
    await seed_database()
    
    # Seed actor profiles
    print("\n" + "=" * 60)
    print("SEEDING ACTOR PROFILES")
    print("=" * 60)
    
    try:
        from seed_actors import seed_actors
        await seed_actors()
    except Exception as e:
        print(f"⚠️  Failed to seed actors: {e}")
    
    # Seed mind states (Phase 1: Database Integration)
    print("\n" + "=" * 60)
    print("SEEDING MIND STATES (Phase 1)")
    print("=" * 60)
    
    try:
        await seed_mind_states()
    except Exception as e:
        print(f"⚠️  Failed to seed mind states: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ALL SEEDING COMPLETE")
    print("=" * 60)


async def seed_mind_states():
    """
    Seed test users with initial mind states
    Phase 1: Database Integration
    """
    from database import init_db
    from documents import MindState
    
    # Initialize database
    await init_db()
    
    # Test users with varying spiritual development levels
    test_users = [
        {
            "user_id": "test_user_001",
            "sila": 5.0,
            "samadhi": 4.0,
            "panna": 4.0,
            "sati_strength": 5.0,
            "current_anusaya": {
                "lobha": 3.0,
                "dosa": 2.5,
                "moha": 3.5,
                "mana": 2.0,
                "ditthi": 2.0,
                "vicikiccha": 2.5,
                "thina": 3.0
            },
            "kusala_count_total": 50,
            "akusala_count_total": 20,
            "current_bhumi": "puthujjana"
        },
        {
            "user_id": "test_user_002",
            "sila": 7.0,
            "samadhi": 6.0,
            "panna": 5.5,
            "sati_strength": 6.5,
            "current_anusaya": {
                "lobha": 2.0,
                "dosa": 1.5,
                "moha": 2.5,
                "mana": 1.5,
                "ditthi": 1.0,
                "vicikiccha": 1.5,
                "thina": 2.0
            },
            "kusala_count_total": 150,
            "akusala_count_total": 30,
            "current_bhumi": "puthujjana"
        },
        {
            "user_id": "test_user_003",
            "sila": 8.5,
            "samadhi": 7.5,
            "panna": 7.0,
            "sati_strength": 8.0,
            "current_anusaya": {
                "lobha": 1.0,
                "dosa": 0.5,
                "moha": 1.5,
                "mana": 1.0,
                "ditthi": 0.5,
                "vicikiccha": 0.5,
                "thina": 1.0
            },
            "kusala_count_total": 300,
            "akusala_count_total": 10,
            "current_bhumi": "sotapanna"  # Stream-enterer
        },
        {
            "user_id": "beginner_user",
            "sila": 3.0,
            "samadhi": 2.5,
            "panna": 2.0,
            "sati_strength": 3.0,
            "current_anusaya": {
                "lobha": 5.0,
                "dosa": 4.5,
                "moha": 5.5,
                "mana": 4.0,
                "ditthi": 4.5,
                "vicikiccha": 4.0,
                "thina": 4.5
            },
            "kusala_count_total": 10,
            "akusala_count_total": 50,
            "current_bhumi": "puthujjana"
        },
        {
            "user_id": "advanced_user",
            "sila": 9.0,
            "samadhi": 8.5,
            "panna": 8.0,
            "sati_strength": 9.0,
            "current_anusaya": {
                "lobha": 0.5,
                "dosa": 0.3,
                "moha": 1.0,
                "mana": 0.5,
                "ditthi": 0.2,
                "vicikiccha": 0.2,
                "thina": 0.5
            },
            "kusala_count_total": 500,
            "akusala_count_total": 5,
            "current_bhumi": "sakadagami"  # Once-returner
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for user_data in test_users:
        # Check if user already exists
        existing = await MindState.find_one(MindState.user_id == user_data["user_id"])
        
        if existing:
            # Update existing user
            for key, value in user_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            await existing.save()
            print(f"✅ Updated mind state for {user_data['user_id']} ({user_data['current_bhumi']})")
            updated_count += 1
        else:
            # Create new user
            mind_state = MindState(**user_data)
            await mind_state.insert()
            print(f"✅ Created mind state for {user_data['user_id']} ({user_data['current_bhumi']})")
            created_count += 1
    
    print(f"\n📊 Mind States Seeding Summary:")
    print(f"   - Created: {created_count}")
    print(f"   - Updated: {updated_count}")
    print(f"   - Total: {created_count + updated_count}")


if __name__ == "__main__":
    asyncio.run(seed_all())
