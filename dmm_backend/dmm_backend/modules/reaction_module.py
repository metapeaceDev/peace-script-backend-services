import random
import statistics
from core.logging_config import get_logger
from core import constants as const

logger = get_logger(__name__)

# This module contains the core logic for the Reaction Engine.

def calculate_reaction_outcome(dmm_profile: dict, stimulus: dict, environment: dict) -> dict:
    """Calculates the reaction based on the character's profile and the stimulus."""
    logger.info(f"Calculating reaction outcome for model_id: {dmm_profile.get('model_id')}")
    core_profile = dmm_profile.get("CoreProfile", {})
    
    # 1. Analyze Stimulus
    base_kilesa_trigger = stimulus.get('intensity', 0) * (1 + (environment.get('ambient_stress_level', 0) * const.AMBIENT_STRESS_MULTIPLIER))
    logger.debug(f"Base kilesa trigger: {base_kilesa_trigger}")

    # 2. Vedanā Tolerance Check
    tolerance_profile = core_profile.get("PsychologicalMatrix", {}).get("VedanaToleranceProfile", {})
    threshold = tolerance_profile.get("mental_suffering_threshold", {}).get("total_threshold", 10)
    if base_kilesa_trigger < threshold:
        logger.debug("Stimulus intensity is below Vedanā tolerance threshold.")
        pass

    # 3. Calculate Kilesa Force
    anusaya = core_profile.get("PsychologicalMatrix", {}).get("LatentTendencies", {}).get("anusaya_kilesa", {})
    # Simplified: assumes negative stimulus triggers patigha (anger)
    anusaya_level = anusaya.get("patigha", {}).get("level", 5)
    initial_kilesa_force = (anusaya_level * const.ANUSAYA_LEVEL_WEIGHT) + (base_kilesa_trigger * const.STIMULUS_INTENSITY_WEIGHT)
    final_kilesa_force = initial_kilesa_force
    logger.debug(f"Initial kilesa force: {initial_kilesa_force}")

    # 4. Sati Intervention
    virtue_engine = core_profile.get("SpiritualAssets", {}).get("VirtueEngine", {})
    sati_level = virtue_engine.get("Sati_mastery", {}).get("level", 0)
    sati_chance = sati_level / const.SATI_CHANCE_DIVISOR
    sati_intervened = random.random() < sati_chance
    logger.debug(f"Sati intervention check: level={sati_level}, chance={sati_chance}, intervened={sati_intervened}")

    # 5. Paññā Override
    panna_intervened = False
    if sati_intervened:
        panna_level = virtue_engine.get("Panna_mastery", {}).get("level", 0)
        panna_chance = panna_level / const.PANNA_CHANCE_DIVISOR
        if random.random() < panna_chance:
            panna_intervened = True
            final_kilesa_force *= const.PANNA_KILESA_REDUCTION_FACTOR
            logger.info("Paññā override successful!")
    logger.debug(f"Paññā intervention check: intervened={panna_intervened}, final_kilesa_force={final_kilesa_force}")

    # 6. Calculate Pāramī Force
    parami_perfections = virtue_engine.get("Paramī_Portfolio", {}).get("perfections", {})
    khanti_level = parami_perfections.get("khanti", {}).get("level", 0)
    upekkha_level = parami_perfections.get("upekkha", {}).get("level", 0)
    parami_force = (khanti_level * const.PARAMI_KHANTI_WEIGHT) + (upekkha_level * const.PARAMI_UPEKKHA_WEIGHT)
    logger.debug(f"Pāramī force calculated: {parami_force} (Khanti: {khanti_level}, Upekkhā: {upekkha_level})")

    # 7. Final Resolution
    final_score = parami_force - final_kilesa_force
    is_wholesome = final_score > 0
    resulting_citta = "มหากุศลจิต" if is_wholesome else "โทสมูลจิต"
    logger.info(f"Final resolution: score={final_score}, is_wholesome={is_wholesome}, resulting_citta='{resulting_citta}'")

    return {
        "resulting_citta": resulting_citta,
        "is_wholesome": is_wholesome,
        "conflict_analysis": {
            "initial_kilesa_force": round(initial_kilesa_force, 2),
            "final_kilesa_force": round(final_kilesa_force, 2),
            "parami_force": round(parami_force, 2),
            "sati_intervened": sati_intervened,
            "panna_intervened": panna_intervened,
        },
    }

def apply_consequences(dmm_profile: dict, reaction_outcome: dict, stimulus: dict) -> dict:
    """
    Calculates the changes to the profile after a reaction and formats them
    for MongoDB's $inc operator.
    """
    logger.info(f"Applying consequences for model_id: {dmm_profile.get('model_id')}")
    
    update_operations = {"$inc": {}}
    
    if reaction_outcome["is_wholesome"]:
        # Increase experience for Khanti (patience)
        update_operations["$inc"]["CoreProfile.SpiritualAssets.VirtueEngine.Paramī_Portfolio.perfections.khanti.exp"] = const.WHOLESOME_REACTION_EXP_GAIN
        logger.debug(f"Applying wholesome consequence: +{const.WHOLESOME_REACTION_EXP_GAIN} exp to Khanti")
    else:
        # Increase the level of Patigha (aversion)
        update_operations["$inc"]["CoreProfile.PsychologicalMatrix.LatentTendencies.anusaya_kilesa.patigha.level"] = const.UNWHOLESOME_REACTION_LEVEL_INCREASE
        logger.debug(f"Applying unwholesome consequence: +{const.UNWHOLESOME_REACTION_LEVEL_INCREASE} to Patigha level")
    
    kamma_id = f"k-{random.randint(10000, 99999)}"
    logger.info(f"Generated new kamma_id: {kamma_id}")
    
    return {
        "new_kamma_id": kamma_id,
        "update_operations": update_operations
    }
