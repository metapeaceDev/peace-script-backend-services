"""
⚙️ Rupa Calculation Engine - เครื่องมือคำนวณรูป ๒๘

Purpose: Calculate 28 Material Forms from CoreProfile data
Based on: Abhidhamma principles (ปรมัตถโชติกะ)

Features:
1. Calculate Mahabhuta (4 Great Elements) from age, health, vitality
2. Calculate Pasada (5 Sense Organs) from sensory capabilities
3. Generate Kalapa (Material Groups) by Samutthana (4 origins)
4. Simulate Rupa lifecycle (uppada-thiti-bhanga) - 17 moments

Author: Peace Mind System
Date: 17 October 2568
Version: 1.0
"""

from typing import List, Dict, Optional
from datetime import datetime
import random

from documents import DigitalMindModel
from rupa_models import (
    RupaProfile, MahabhutaRupa, PasadaRupa, GocaraRupa,
    BhavaRupa, HadayaRupa, JivitaRupa, AharaRupa,
    ParicchedaRupa, VinnattiRupa, VikaraRupa, LakkhanaRupa,
    RupaKalapa, RupaSamutthana, YoniType, RupaKhana,
    PathaviCharacteristics, ApoCharacteristics,
    TejoCharacteristics, VayoCharacteristics,
    create_suddhatthaka_kalapa
)


# =============================================================================
# RUPA CALCULATION ENGINE
# =============================================================================

class RupaCalculationEngine:
    """
    Calculation engine for 28 Material Forms (รูป ๒๘)
    Based on Abhidhamma principles
    """
    
    @staticmethod
    def infer_yoni_from_profile(profile: DigitalMindModel) -> YoniType:
        """
        Infer birth type (โยนิ ๔) from profile characteristics
        
        Default: JALABUJA (human womb birth)
        
        4 Birth Types:
        - OPAPATIKA (โอปปาติกะ): Spontaneous birth (devas, brahmas, hell beings)
        - SAMSEDAJA (สังเสทชะ): Moisture birth (insects, worms)
        - ANDAJA (อัณฑชะ): Egg birth (birds, reptiles, fish)
        - JALABUJA (ชลาพุชะ): Womb birth (mammals, humans)
        """
        # Logic based on spiritual attainment and character traits
        try:
            core_profile = profile.get_core_profile()
            
            # Check for noble being status (devas/brahmas tend to have OPAPATIKA)
            if core_profile.is_noble():
                spiritual_score = core_profile.get_overall_spiritual_score()
                # Very high spiritual score suggests deva/brahma realm
                if spiritual_score >= 90.0:
                    return YoniType.OPAPATIKA
            
            # Check species indicator if available (custom metadata)
            if hasattr(profile, 'species') and profile.species:
                species_lower = str(profile.species).lower()
                if 'deva' in species_lower or 'brahma' in species_lower or 'hell' in species_lower:
                    return YoniType.OPAPATIKA
                elif 'insect' in species_lower or 'worm' in species_lower:
                    return YoniType.SAMSEDAJA
                elif 'bird' in species_lower or 'reptile' in species_lower or 'fish' in species_lower:
                    return YoniType.ANDAJA
            
            # Check birth circumstances from vipaka
            if hasattr(profile, 'life_essence') and profile.life_essence:
                vipaka = getattr(profile.life_essence, 'life_blueprint_vipaka', None)
                if vipaka and hasattr(vipaka, 'initial_conditions'):
                    birth_context = getattr(vipaka.initial_conditions, 'birth_context', None)
                    if birth_context:
                        bc_lower = str(birth_context).lower()
                        if 'spontaneous' in bc_lower or 'sudden' in bc_lower:
                            return YoniType.OPAPATIKA
                        elif 'moisture' in bc_lower or 'swamp' in bc_lower:
                            return YoniType.SAMSEDAJA
                        elif 'egg' in bc_lower or 'hatched' in bc_lower:
                            return YoniType.ANDAJA
        
        except (AttributeError, KeyError):
            pass  # Fallback to default
        
        # Default: human womb birth (most common in human realm)
        return YoniType.JALABUJA
    
    @staticmethod
    def calculate_mahabhuta_from_core_profile(profile: DigitalMindModel) -> MahabhutaRupa:
        """
        Calculate 4 Great Elements (มหาภูตรูป ๔) from CoreProfile
        
        Logic based on:
        - Pathavi (Earth): Physical strength, stability, body mass
        - Apo (Water): Hydration, health, fluidity
        - Tejo (Fire): Metabolism, energy, body temperature
        - Vayo (Wind): Activity level, vitality, movement
        
        Returns:
            MahabhutaRupa with all 4 elements balanced
        """
        try:
            age = profile.life_essence.age_in_years
            health = profile.life_essence.life_blueprint_vipaka.initial_conditions.health_baseline
            jiv = profile.life_essence.jivitindriya_mechanics.current_jivitindriya
        except AttributeError as e:
            # Fallback to defaults if fields missing
            age = 30
            health = 80.0
            jiv = 75.0
        
        # Pathavi (ปถวีธาตุ): Solidity/hardness decreases with age
        # Young = more solid/firm, Old = softer/weaker
        hardness = max(10, 100 - (age * 0.5) - (100 - health) * 0.3)
        softness = 100 - hardness
        
        # Apo (อาโปธาตุ): Cohesion based on health/hydration
        # Good health = good cohesion, Poor health = more fluid/dispersed
        cohesion = health * 0.8
        fluidity = 100 - cohesion
        
        # Tejo (เตโชธาตุ): Body temperature based on life force
        # High vitality = warmer, Low vitality = cooler
        # Normal human: 36.5-38°C
        heat = 36.5 + (jiv / 100) * 1.5  # 36.5-38°C range
        cold = 0 if heat > 36 else 36 - heat
        
        # Vayo (วาโยธาตุ): Tension/movement based on vitality
        # High vitality = more tension/movement, Low = loose/still
        tension = jiv * 0.7
        looseness = 100 - tension
        
        return MahabhutaRupa(
            pathavi=PathaviCharacteristics(
                hardness_level=hardness,
                softness_level=softness,
                support_function=True
            ),
            apo=ApoCharacteristics(
                cohesion_level=cohesion,
                fluidity_level=fluidity,
                binding_function=True
            ),
            tejo=TejoCharacteristics(
                heat_level=heat,
                cold_level=cold,
                maturing_function=True
            ),
            vayo=VayoCharacteristics(
                tension_level=tension,
                looseness_level=looseness,
                distension_function=True,
                movement_function=True,
                vayo_types=["uddhangama", "adhogama"]  # Basic types
            ),
            balanced=True,
            dominant_element=RupaCalculationEngine._determine_dominant_element(
                hardness, cohesion, heat, tension
            )
        )
    
    @staticmethod
    def _determine_dominant_element(
        pathavi_strength: float,
        apo_strength: float,
        tejo_strength: float,
        vayo_strength: float
    ) -> str:
        """Determine which mahabhuta is most prominent"""
        from rupa_models import MahabhutaType
        
        strengths = {
            "pathavi": pathavi_strength,
            "apo": apo_strength,
            "tejo": tejo_strength / 0.38,  # Normalize temperature to 0-100
            "vayo": vayo_strength
        }
        
        dominant = max(strengths, key=strengths.get)
        return MahabhutaType[dominant.upper()]
    
    @staticmethod
    def calculate_pasada_from_abilities(profile: DigitalMindModel) -> PasadaRupa:
        """
        Calculate 5 Sense Organs (ปสาทรูป ๕) sensitivity
        
        Factors:
        - Age (sensory decline with age)
        - Health baseline (physical condition of organs)
        - Sati level (mindfulness sharpens senses)
        - Path stage (advanced practitioners have sharper awareness)
        
        Returns:
            PasadaRupa with sensitivity levels for all 5 senses
        """
        try:
            age = profile.life_essence.age_in_years
            health = profile.life_essence.life_blueprint_vipaka.initial_conditions.health_baseline
            
            # Try to get sati level from spiritual assets
            sati_level = 1
            if hasattr(profile, 'spiritual_assets'):
                virtue_engine = getattr(profile.spiritual_assets, 'virtue_engine', None)
                if virtue_engine:
                    sati_mastery = getattr(virtue_engine, 'sati_mastery', None)
                    if sati_mastery:
                        sati_level = getattr(sati_mastery, 'level', 1)
        except AttributeError:
            age = 30
            health = 80.0
            sati_level = 1
        
        # Age factor: 20-60 peak, then decline
        age_factor = 1.0
        if age < 20:
            age_factor = age / 20  # Developing
        elif age > 60:
            age_factor = max(0.3, 1.0 - (age - 60) * 0.02)  # Declining
        
        base_sensitivity = health * age_factor
        
        # Sati boost: Mindfulness sharpens all senses
        sati_boost = 1.0 + (sati_level / 10) * 0.3  # Up to +30%
        
        # Calculate individual sense organ sensitivity
        return PasadaRupa(
            cakkhu_pasada=min(100, base_sensitivity * sati_boost),  # Eye
            sota_pasada=min(100, base_sensitivity * sati_boost),    # Ear
            ghana_pasada=min(100, base_sensitivity * sati_boost * 0.9),  # Nose (declines faster)
            jivha_pasada=min(100, base_sensitivity * sati_boost * 0.95), # Tongue
            kaya_pasada=min(100, base_sensitivity * sati_boost),    # Body
            locations={
                "cakkhu": "Pupil of eye (black part)",
                "sota": "Inner ear cavity",
                "ghana": "Nasal mucous membrane",
                "jivha": "Taste buds on tongue",
                "kaya": "Throughout entire body surface"
            }
        )
    
    @staticmethod
    def calculate_gocara_neutral() -> GocaraRupa:
        """
        Calculate 7 Sense Objects (วิสยรูป/โคจรรูป ๗)
        
        Returns neutral/default values as these are external objects
        """
        return GocaraRupa(
            rupa_arammana=50.0,      # Visible form
            sadda_arammana=50.0,     # Sound
            gandha_arammana=50.0,    # Odor
            rasa_arammana=50.0,      # Taste
            photthabbayatana=50.0,   # Tangible object (3 mahabhuta)
            apo_gocara=50.0,         # Water element (implicit)
            akasa_gocara=50.0        # Space element
        )
    
    @staticmethod
    def determine_bhava_rupa(profile: DigitalMindModel) -> BhavaRupa:
        """
        Determine sex (ภาวรูป ๒) from profile or random
        
        Returns:
            BhavaRupa with either itthindriya or purisindriya
        """
        # Check profile for sex/gender indicator
        sex = None
        
        try:
            # Try to get from core_profile metadata or custom fields
            if hasattr(profile, 'gender'):
                gender = str(profile.gender).lower()
                if 'female' in gender or 'woman' in gender or 'itthi' in gender:
                    sex = "itthi"
                elif 'male' in gender or 'man' in gender or 'purisa' in gender:
                    sex = "purisa"
            
            # Try from core_profile if available
            if not sex and hasattr(profile, 'core_profile') and profile.core_profile:
                if isinstance(profile.core_profile, dict):
                    gender_val = profile.core_profile.get('gender') or profile.core_profile.get('sex')
                    if gender_val:
                        gender_str = str(gender_val).lower()
                        if 'female' in gender_str or 'woman' in gender_str:
                            sex = "itthi"
                        elif 'male' in gender_str or 'man' in gender_str:
                            sex = "purisa"
            
            # Try from name field as heuristic (if name suggests gender)
            if not sex and hasattr(profile, 'name') and profile.name:
                name = str(profile.name).lower()
                # Common Thai female names/patterns
                if any(x in name for x in ['นาง', 'น.ส.', 'miss', 'ms', 'mrs']):
                    sex = "itthi"
                # Common Thai male names/patterns  
                elif any(x in name for x in ['นาย', 'mr', 'พระ']):
                    sex = "purisa"
        
        except (AttributeError, KeyError, TypeError):
            pass  # Fallback to random
        
        # If still no sex indicator, use random selection
        if not sex:
            sex = random.choice(["itthi", "purisa"])
        
        if sex == "itthi":
            return BhavaRupa(itthindriya=100.0, purisindriya=None)
        else:
            return BhavaRupa(itthindriya=None, purisindriya=100.0)
    
    @staticmethod
    def generate_kamma_born_kalapas(
        yoni: YoniType,
        health: float,
        model_id: str
    ) -> List[RupaKalapa]:
        """
        Generate Kamma-born kalapas (กัมมชรูป) at patisandhi-kshana (rebirth-linking)
        
        According to Abhidhamma:
        - All beings start with kamma-born rupa at rebirth
        - Minimum: Suddhatthaka (8 rupa: 4 mahabhuta + 4 lakkhana)
        - Add: Jivita, Pasada (5), Hadaya, Bhava depending on yoni
        
        Args:
            yoni: Birth type (JALABUJA, ANDAJA, etc.)
            health: Health baseline (determines rupa quality)
            model_id: Reference to DigitalMindModel
        
        Returns:
            List of RupaKalapa at birth
        """
        kalapas = []
        
        # 1. Minimum: Suddhatthaka (8 rupa)
        base_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.KAMMA)
        kalapas.append(base_kalapa)
        
        # 2. Add Jivita kalapa (9 rupa: 8 + jivitindriya)
        jivita_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.KAMMA)
        jivita_kalapa.jivita = JivitaRupa(rupa_jivitindriya=health)
        kalapas.append(jivita_kalapa)
        
        # 3. Add 5 Pasada kalapas (for beings with 5 senses)
        if yoni in [YoniType.JALABUJA, YoniType.ANDAJA]:  # Womb/egg birth
            for sense in ["cakkhu", "sota", "ghana", "jivha", "kaya"]:
                pasada_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.KAMMA)
                pasada_kalapa.pasada = PasadaRupa(**{f"{sense}_pasada": health * 0.9})
                kalapas.append(pasada_kalapa)
        
        # 4. Add Hadaya kalapa (heart-base for 5-khandha beings)
        if yoni != YoniType.OPAPATIKA:  # Not deva/brahma (they have no physical heart)
            hadaya_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.KAMMA)
            hadaya_kalapa.hadaya = HadayaRupa(heart_base_location="Physical heart")
            kalapas.append(hadaya_kalapa)
        
        # 5. Add Bhava kalapa (sex) if applicable
        if yoni in [YoniType.JALABUJA, YoniType.ANDAJA]:
            sex = random.choice(["itthi", "purisa"])
            bhava_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.KAMMA)
            bhava_kalapa.bhava = BhavaRupa(**{f"{sex}ndriya": 100.0})
            kalapas.append(bhava_kalapa)
        
        return kalapas
    
    @staticmethod
    def generate_citta_born_rupa(
        citta_strength: float,
        intention_type: str = "neutral"
    ) -> List[RupaKalapa]:
        """
        Generate Citta-born rupa (จิตตชรูป)
        
        According to Abhidhamma:
        - Citta produces rupa continuously during life
        - Strongest in: kaya-vinnatti (bodily intimation), vaci-vinnatti (speech)
        - Generated by: Mental intention → Physical movement
        
        Args:
            citta_strength: Strength of consciousness (0-100)
            intention_type: Type of intention (neutral, wholesome, unwholesome)
        
        Returns:
            List of citta-born RupaKalapa
        """
        kalapas = []
        
        # Basic citta-born kalapa
        citta_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.CITTA)
        
        # Add vinnatti (intimation) if intention strong enough
        if citta_strength > 30:
            citta_kalapa.vinnatti = VinnattiRupa(
                kaya_vinnatti=citta_strength * 0.8,  # Bodily movement
                vaci_vinnatti=citta_strength * 0.9   # Speech intention
            )
        
        kalapas.append(citta_kalapa)
        return kalapas
    
    @staticmethod
    def generate_utu_born_rupa(
        temperature: float,
        season: str = "normal"
    ) -> List[RupaKalapa]:
        """
        Generate Utu-born rupa (อุตุชรูป)
        
        Utu (temperature-born):
        - Generated by: Heat/cold, seasonal changes
        - Affects: Tejo-dhatu (fire element) primarily
        - Continuous production throughout life
        
        Args:
            temperature: Environmental temperature (°C)
            season: Season type (hot, cold, rainy, normal)
        
        Returns:
            List of utu-born RupaKalapa
        """
        kalapas = []
        
        # Utu-born kalapa with adjusted tejo
        utu_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.UTU)
        
        # Adjust fire element based on temperature
        if temperature > 30:  # Hot
            utu_kalapa.mahabhuta.tejo.heat_level = min(38, 36.5 + (temperature - 30) * 0.1)
            utu_kalapa.mahabhuta.tejo.cold_level = 0
        elif temperature < 20:  # Cold
            utu_kalapa.mahabhuta.tejo.heat_level = max(35, 36.5 - (20 - temperature) * 0.1)
            utu_kalapa.mahabhuta.tejo.cold_level = 20 - temperature
        
        kalapas.append(utu_kalapa)
        return kalapas
    
    @staticmethod
    def generate_ahara_born_rupa(
        nutriment_quality: float,
        meal_size: float = 50.0
    ) -> List[RupaKalapa]:
        """
        Generate Ahara-born rupa (อาหารชรูป)
        
        Ahara (nutriment-born):
        - Generated by: Food intake
        - Maintains: Body strength, health
        - Lifespan: Up to 7 days after eating
        
        Args:
            nutriment_quality: Quality of food (0-100)
            meal_size: Portion size (0-100)
        
        Returns:
            List of ahara-born RupaKalapa
        """
        kalapas = []
        
        # Number of kalapas proportional to meal size
        num_kalapas = max(1, int(meal_size / 20))
        
        for _ in range(num_kalapas):
            ahara_kalapa = create_suddhatthaka_kalapa(RupaSamutthana.AHARA)
            ahara_kalapa.ahara = AharaRupa(
                oja_nutriment=nutriment_quality,
                last_meal_impact=meal_size
            )
            kalapas.append(ahara_kalapa)
        
        return kalapas
    
    @staticmethod
    def simulate_rupa_lifecycle(
        kalapa: RupaKalapa,
        current_moment: int = 0
    ) -> RupaKalapa:
        """
        Simulate Rupa lifecycle (รูปขณะ ๓)
        
        3 Moments:
        - Uppada (อุปปาทขณะ): Arising (moment 0)
        - Thiti (ฐิติขณะ): Standing/Continuity (moments 1-16)
        - Bhanga (ภังคขณะ): Dissolution (moment 17)
        
        Lifespan: 17 citta-kshanas (mind-moments) for kamma-born
        
        Args:
            kalapa: RupaKalapa to simulate
            current_moment: Current moment (0-17)
        
        Returns:
            Updated RupaKalapa with new moment state
        """
        if current_moment == 0:
            kalapa.moment = RupaKhana.UPPADA
            kalapa.lakkhana.upacaya = 100.0  # Production at peak
            kalapa.lakkhana.santati = 0.0
            kalapa.lakkhana.jarata = 0.0
        
        elif 1 <= current_moment < kalapa.lifetime_kshanas:
            kalapa.moment = RupaKhana.THITI
            kalapa.lakkhana.upacaya = 0.0
            kalapa.lakkhana.santati = 100.0  # Continuity
            kalapa.lakkhana.jarata = (current_moment / kalapa.lifetime_kshanas) * 100
        
        elif current_moment >= kalapa.lifetime_kshanas:
            kalapa.moment = RupaKhana.BHANGA
            kalapa.lakkhana.upacaya = 0.0
            kalapa.lakkhana.santati = 0.0
            kalapa.lakkhana.jarata = 100.0  # Full decay
        
        # Aniccata (impermanence) always 100%
        kalapa.lakkhana.aniccata = 100.0
        
        return kalapa
    
    @staticmethod
    async def create_complete_rupa_profile(
        model: DigitalMindModel
    ) -> RupaProfile:
        """
        Create complete RupaProfile (28 Material Forms) from CoreProfile
        
        This is the main function that generates all 28 rupa from scratch
        
        Args:
            model: DigitalMindModel to extract data from
        
        Returns:
            Complete RupaProfile with all 28 Material Forms
        """
        # Get CoreProfile from model
        profile = model.get_core_profile()
        
        # 1. Determine birth type
        yoni = RupaCalculationEngine.infer_yoni_from_profile(profile)
        
        # 2. Calculate 4 Great Elements
        mahabhuta = RupaCalculationEngine.calculate_mahabhuta_from_core_profile(profile)
        
        # 3. Calculate 5 Sense Organs
        pasada = RupaCalculationEngine.calculate_pasada_from_abilities(profile)
        
        # 4. Calculate 7 Sense Objects (neutral)
        gocara = RupaCalculationEngine.calculate_gocara_neutral()
        
        # 5. Determine sex
        bhava = RupaCalculationEngine.determine_bhava_rupa(profile)
        
        # 6. Heart-base (for humans)
        hadaya = HadayaRupa(heart_base_location="Physical heart")
        
        # 7. Life faculty (from jivitindriya)
        jiv = profile.life_essence.jivitindriya_mechanics.current_jivitindriya
        jivita = JivitaRupa(rupa_jivitindriya=jiv)
        
        # 8. Nutriment (from health)
        health = profile.life_essence.life_blueprint_vipaka.initial_conditions.health_baseline
        ahara = AharaRupa(
            kabalinkara_ahara=health,  # Oja level
            nutriment_level=health
        )
        
        # 9. Space
        pariccheda = ParicchedaRupa(space_delimitation=50.0)
        
        # 10. Intimation (neutral - descriptive strings)
        vinnatti = VinnattiRupa(
            kaya_vinnatti="Normal bodily movements",
            vaci_vinnatti="Normal speech patterns"
        )
        
        # 11. Mutability (based on health)
        health_factor = health / 100
        vikara = VikaraRupa(
            lahuta=health_factor * 80,
            muduta=health_factor * 80,
            kammañata=health_factor * 80  # Note: ñ not nn
        )
        
        # 12. Characteristics (age-based)
        age = profile.life_essence.age_in_years
        age_factor = age / 150
        lakkhana = LakkhanaRupa(
            upacaya=max(0, 100 - age_factor * 100),
            santati=50.0,
            jarata=age_factor * 100,
            aniccata=100.0
        )
        
        # 13. Generate kamma-born kalapas at birth
        kalapas = RupaCalculationEngine.generate_kamma_born_kalapas(
            yoni=yoni,
            health=health,
            model_id=model.model_id
        )
        
        # 14. Count by samutthana
        total_kalapas = len(kalapas)
        
        # 15. Create RupaProfile
        return RupaProfile(
            model_id=model.model_id,
            yoni=yoni,
            patisandhi_kalapas=kalapas,
            mahabhuta_state=mahabhuta,
            pasada_state=pasada,
            gocara_state=gocara,
            bhava_state=bhava,
            hadaya_state=hadaya,
            jivita_state=jivita,
            ahara_state=ahara,
            pariccheda_state=pariccheda,
            vinnatti_state=vinnatti,
            vikara_state=vikara,
            lakkhana_state=lakkhana,
            active_kalapas=kalapas,
            total_kalapa_count=total_kalapas,
            kamma_rupa_count=total_kalapas,
            citta_rupa_count=0,
            utu_rupa_count=0,
            ahara_rupa_count=0,
            age_in_moments=age * 365 * 24 * 60 * 60 * 1000,
            last_updated=datetime.utcnow()
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def calculate_and_save_rupa(model_id: str) -> RupaProfile:
    """
    Calculate complete 28-rupa and save to database
    
    Args:
        model_id: DigitalMindModel ID
    
    Returns:
        Saved RupaProfile
    """
    # Get model (use find_one because model_id is string, not ObjectId)
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise ValueError(f"Model not found: {model_id}")
    
    # Calculate
    rupa = await RupaCalculationEngine.create_complete_rupa_profile(model)
    
    # Check if already exists
    existing = await RupaProfile.find_one(RupaProfile.model_id == model_id)
    if existing:
        # Update existing
        existing.mahabhuta_state = rupa.mahabhuta_state
        existing.pasada_state = rupa.pasada_state
        existing.jivita_state = rupa.jivita_state
        existing.last_updated = datetime.utcnow()
        await existing.save()
        return existing
    else:
        # Create new
        await rupa.insert()
        return rupa


async def recalculate_rupa_from_changes(
    model_id: str,
    changed_fields: Dict[str, any]
) -> RupaProfile:
    """
    Recalculate only affected rupa after specific changes
    
    Args:
        model_id: DigitalMindModel ID
        changed_fields: Dict of changed fields (e.g., {"age": 31, "health": 85})
    
    Returns:
        Updated RupaProfile
    """
    rupa = await RupaProfile.find_one(RupaProfile.model_id == model_id)
    if not rupa:
        # Create new if doesn't exist
        return await calculate_and_save_rupa(model_id)
    
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise ValueError(f"Model not found: {model_id}")
    
    # Get CoreProfile from model
    profile = model.get_core_profile()
    
    # Recalculate affected parts
    if "age" in changed_fields or "health" in changed_fields:
        rupa.mahabhuta_state = RupaCalculationEngine.calculate_mahabhuta_from_core_profile(profile)
        rupa.pasada_state = RupaCalculationEngine.calculate_pasada_from_abilities(profile)
    
    if "jivitindriya" in changed_fields:
        rupa.jivita_state.rupa_jivitindriya = changed_fields["jivitindriya"]
    
    rupa.last_updated = datetime.utcnow()
    await rupa.save()
    return rupa
