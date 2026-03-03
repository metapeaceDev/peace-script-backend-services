import statistics
from datetime import datetime, timezone
from beanie.operators import Inc, Set
# Prefer package-qualified imports; fallback to local modules when executed without package
try:
    from dmm_backend.documents import DigitalMindModel, KammaLogEntry  # type: ignore
except Exception:
    from documents import DigitalMindModel, KammaLogEntry  # type: ignore

try:
    from dmm_backend.modules.reaction_module import calculate_reaction_outcome, apply_consequences  # type: ignore
except Exception:
    from modules.reaction_module import calculate_reaction_outcome, apply_consequences  # type: ignore

try:
    from dmm_backend.schemas import ReactionRequest, KammaLogEntrySchema  # type: ignore
except Exception:
    from schemas import ReactionRequest, KammaLogEntrySchema  # type: ignore

try:
    from dmm_backend.core.logging_config import get_logger  # type: ignore
except Exception:
    from core.logging_config import get_logger  # type: ignore

logger = get_logger(__name__)

async def process_reaction_simulation(request: ReactionRequest) -> KammaLogEntrySchema:
    """
    Handles the core logic for simulating a character's reaction using Beanie.
    """
    # Model id may be missing if request validation failed upstream; guard early
    model_id = getattr(request, 'model_id', None)
    logger.info(f"Processing reaction for model_id: {model_id}")
    dmm_profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not dmm_profile:
        logger.warning(f"DMM profile not found for model_id: {model_id} in service layer.")
        return None

    # Convert Beanie doc to dict for processing by existing modules
    dmm_profile_dict = dmm_profile.dict()

    logger.debug(f"Calculating reaction outcome for model_id: {model_id}")
    # Safe dict converters for varying request object shapes
    def _to_dict(obj):
        if obj is None:
            return {}
        for attr in ("model_dump", "dict"):
            fn = getattr(obj, attr, None)
            if callable(fn):
                try:
                    return fn()
                except Exception:
                    pass
        if isinstance(obj, dict):
            return obj
        try:
            return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_") and not callable(getattr(obj, k))}
        except Exception:
            return {}

    # In schemas, field is `environment` with alias environment_modifiers
    env = {}
    if getattr(request, "environment", None) is not None:
        env = _to_dict(request.environment)
    elif getattr(request, "environment_modifiers", None) is not None:
        env = _to_dict(request.environment_modifiers)

    stimulus_dict = _to_dict(getattr(request, "stimulus", None))

    reaction_outcome = calculate_reaction_outcome(
        dmm_profile_dict,
        stimulus_dict,
        env,
    )
    
    logger.debug(f"Applying consequences for model_id: {model_id}")
    consequences = apply_consequences(
        dmm_profile_dict,
        reaction_outcome,
        stimulus_dict,
    )

    # The 'consequences' dictionary contains the MongoDB update operations ($inc, $set)
    update_ops = consequences.get("update_operations")
    if update_ops:
        update_query = []
        if "$inc" in update_ops:
            update_query.append(Inc(update_ops["$inc"]))
        if "$set" in update_ops:
            update_query.append(Set(update_ops["$set"]))
        
        if update_query:
            logger.info(f"Applying profile updates for model_id: {model_id}")
            await dmm_profile.update(*update_query)
        else:
            logger.info(f"No profile updates to apply for model_id: {model_id}")
    else:
        logger.info(f"No update operations generated for model_id: {model_id}")


    # We need to remove the raw update operations before creating the log and sending the response
    clean_consequences = consequences.copy()
    if "update_operations" in clean_consequences:
        del clean_consequences["update_operations"]

    # Create and save the Kamma Log using Beanie
    kamma_log_entry = None
    try:
        kamma_log_entry = KammaLogEntry(
            model_id=model_id,
            context={
                "stimulus": stimulus_dict,
                "outcome": reaction_outcome,
                "consequences": clean_consequences,
            },
            event_type="reaction",
            description="Reaction simulation",
            impact_level=clean_consequences.get("impact_level", 0),
        )
        await kamma_log_entry.insert()
        logger.info(f"Successfully created kamma log for model_id: {model_id}")
    except Exception as e:
        logger.error(f"Failed to create kamma log for model_id: {model_id}. Error: {e}")
        # Decide if this should be a critical failure or just a warning
        # For now, we'll log the error and continue

    logger.info(f"Reaction simulation completed for model_id: {model_id}")
    # Return schema-like dict (ensure required fields are present even if insert failed)
    safe_timestamp = (
        kamma_log_entry.timestamp.isoformat()
        if (kamma_log_entry and getattr(kamma_log_entry, "timestamp", None))
        else datetime.now(timezone.utc).isoformat()
    )
    return {
        "_id": str(getattr(kamma_log_entry, "id", "")) if kamma_log_entry else "",
        "model_id": getattr(kamma_log_entry, "model_id", model_id) if kamma_log_entry else model_id,
        "timestamp": safe_timestamp,
        "event_type": getattr(kamma_log_entry, "event_type", "reaction") if kamma_log_entry else "reaction",
        "description": getattr(kamma_log_entry, "description", "Reaction simulation") if kamma_log_entry else "Reaction simulation",
        "impact_level": getattr(kamma_log_entry, "impact_level", clean_consequences.get("impact_level", 0)),
        "context": getattr(kamma_log_entry, "context", {"stimulus": stimulus_dict, "outcome": reaction_outcome, "consequences": clean_consequences}),
    }

def transform_dmm_to_editor_profile(dmm: dict) -> dict:
    """Transforms the raw DMM data structure into a format suitable for the frontend editor."""
    logger.info(f"Transforming DMM data to editor profile for model_id: {dmm.get('model_id')}")

    # Start with a shallow copy so we can enrich while preserving original attributes the UI expects
    profile = dict(dmm or {})

    # Normalize identifier fields for frontend consumption
    raw_id = profile.get("_id") or profile.get("id")
    if raw_id is not None:
        try:
            profile["_id"] = str(raw_id)
        except Exception:
            profile["_id"] = raw_id
    else:
        profile.setdefault("_id", profile.get("model_id"))
    
    # Ensure model_id is always present (required by DMMProfileSchema)
    if "model_id" not in profile or profile["model_id"] is None:
        profile["model_id"] = profile.get("_id", "unknown")
    
    # Avoid leaking duplicate id fields in the payload
    if "id" in profile:
        profile.pop("id")

    # Extract data from the nested structure with safe fallbacks
    core_state = profile.get("core_state") or {}
    conscious_profile = profile.get("conscious_profile") or {}
    kamma_profile = profile.get("kamma_profile") or {}

    # Provide sensible defaults for frequently accessed attributes
    profile.setdefault("name", "Unknown")
    profile.setdefault("status_label", "Unknown")
    profile.setdefault("overall_level", 0)
    profile.setdefault("image_url", "https://firebasestorage.googleapis.com/v0/b/meta-peace.appspot.com/o/Metta_Peace_Alchemist_v2_upscaled.png?alt=media&token=402d4f2e-6f03-453c-8145-4246352fce03")

    # --- Character Card ---
    level_progress = core_state.get("level_progress", 0)
    level_up_threshold = core_state.get("level_up_threshold", 1000)
    level_progress_percent = (level_progress / level_up_threshold) * 100 if level_up_threshold > 0 else 0

    character_card = {
        "image_url": profile.get("image_url"),
        "name": profile.get("name"),
        "status_label": profile.get("status_label"),
        "overall_level": profile.get("overall_level", 0),
        "level_progress_percent": level_progress_percent
    }

    # --- Core Stats ---
    latent_tendencies_data = kamma_profile.get("latent_tendencies", [])
    tendency_labels = [item.get("name") for item in latent_tendencies_data]
    tendency_values = [item.get("value") for item in latent_tendencies_data]

    parami_potentials_data = conscious_profile.get("parami_potentials", [])

    summary_metrics = {}
    if parami_potentials_data:
        for item in parami_potentials_data:
            metric_id = (item.get("name") or "").lower()
            if not metric_id:
                continue
            summary_metrics[metric_id] = {
                "label": item.get("name"),
                "value": item.get("value", 0),
                "max_value": 100
            }
    else:
        summary_metrics = {
            "mindfulness": {"label": "Mindfulness", "value": 75, "max_value": 100},
            "wisdom": {"label": "Wisdom", "value": 62, "max_value": 100},
            "compassion": {"label": "Compassion", "value": 89, "max_value": 100}
        }

    core_stats = {
        "latent_tendencies": {
            "labels": tendency_labels,
            "values": tendency_values
        },
        "summary_metrics": summary_metrics
    }

    # --- Training Module ---
    start_training_options = [
        {"id": "meditation", "label": "Meditation Session"},
        {"id": "study", "label": "Study Dhamma"},
        {"id": "dana", "label": "Practice Dana"}
    ]

    training_module = {
        "start_training_options": start_training_options,
        "training_log": []  # This will be populated by a separate API call now
    }

    # Persist enriched data for frontend consumers
    profile["level_progress_percent"] = level_progress_percent
    profile["character_card"] = character_card
    profile["core_stats"] = core_stats
    profile["training_module"] = training_module
    profile["editor_profile_for"] = profile.get("model_id")

    logger.debug(f"Transformation complete for model_id: {profile.get('model_id')}")
    return profile

