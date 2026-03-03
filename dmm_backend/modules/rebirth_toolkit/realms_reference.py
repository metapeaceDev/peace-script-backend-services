"""
31 Realms of Existence (ภพภูมิ 31)
==================================

Based on Buddhist Cosmology from Pali Canon:
- Vibhanga (Abhidhamma)
- Anguttara Nikaya
- Majjhima Nikaya

Reference: https://en.wikipedia.org/wiki/Buddhist_cosmology
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RealmCategory(str, Enum):
    """4 Main Categories of 31 Realms"""
    APAYA_BHUMI = "apaya_bhumi"  # อบายภูมิ (Suffering Realms 1-4)
    KAMA_SUGATI = "kama_sugati"  # กามสุคติภูมิ (Happy Sensual Realms 5-11)
    RUPA_BRAHMA = "rupa_brahma"  # รูปพรหมภูมิ (Fine-Material Realms 12-27)
    ARUPA_BRAHMA = "arupa_brahma"  # อรูปพรหมภูมิ (Formless Realms 28-31)


class Realm(BaseModel):
    """
    Single Realm/Bhumi Definition
    """
    # Identity
    id: int = Field(..., ge=1, le=31, description="Realm ID (1-31)")
    name_en: str = Field(..., description="English name")
    name_th: str = Field(..., description="Thai name")
    name_pali: str = Field(..., description="Pali canonical name")
    
    # Category
    category: RealmCategory = Field(..., description="Realm category")
    category_name_th: str = Field(..., description="Category name in Thai")
    
    # Kamma Requirements
    min_kamma_score: float = Field(..., description="Minimum kamma score for rebirth")
    max_kamma_score: float = Field(..., description="Maximum kamma score for rebirth")
    
    # Life Characteristics
    lifespan_years: int = Field(..., description="Average lifespan in human years")
    suffering_level: int = Field(..., ge=0, le=100, description="Suffering intensity (0-100)")
    happiness_level: int = Field(..., ge=0, le=100, description="Happiness intensity (0-100)")
    
    # Educational Content
    description_th: str = Field(..., description="Description in Thai")
    description_en: str = Field(..., description="Description in English")
    buddhist_reference: str = Field(..., description="Pali Canon reference")
    
    # Special Features
    special_abilities: List[str] = Field(default_factory=list, description="Special abilities in this realm")
    obstacles_to_enlightenment: List[str] = Field(default_factory=list, description="Obstacles to Nibbana")


# ========================================
# 31 REALMS COMPLETE DEFINITION
# ========================================

THIRTY_ONE_REALMS: List[Realm] = [
    
    # ========================================
    # อบายภูมิ (APAYA BHUMI) - Suffering Realms (1-4)
    # ========================================
    
    Realm(
        id=1,
        name_en="Avici Hell",
        name_th="นรกอเวจี",
        name_pali="Avīci Niraya",
        category=RealmCategory.APAYA_BHUMI,
        category_name_th="อบายภูมิ (นรก)",
        min_kamma_score=-100,
        max_kamma_score=-90,
        lifespan_years=100_000_000,  # 1 antara-kappa
        suffering_level=100,
        happiness_level=0,
        description_th="นรกชั้นต่ำสุด ทุกข์ที่สุด สำหรับผู้กระทำอนันตริยกรรม 5 (ฆ่าพ่อแม่ พระอรหันต์ ทำพระโลหิตตก ทำลายสงฆ์)",
        description_en="Lowest hell realm with maximum suffering for those who committed the 5 Anantarika Kamma (patricide, matricide, killing an Arahant, drawing blood from Buddha, causing schism in Sangha)",
        buddhist_reference="Majjhima Nikāya 129, 130; Anguttara Nikāya 5.129",
        special_abilities=[],
        obstacles_to_enlightenment=["extreme_suffering", "no_dhamma_access", "constant_torture"]
    ),
    
    Realm(
        id=2,
        name_en="Great Hells (Maha Naraka)",
        name_th="มหานรก (นรกชั้นอื่นๆ)",
        name_pali="Mahā Niraya",
        category=RealmCategory.APAYA_BHUMI,
        category_name_th="อบายภูมิ (นรก)",
        min_kamma_score=-90,
        max_kamma_score=-70,
        lifespan_years=50_000_000,
        suffering_level=95,
        happiness_level=0,
        description_th="นรกชั้นรองลงมา ทุกข์มาก สำหรับผู้กระทำอกุศลกรรมหนัก (ฆ่าคน ทรมาน ข่มขืน)",
        description_en="Major hell realms for severe unwholesome kamma (murder, torture, rape, extreme cruelty)",
        buddhist_reference="Majjhima Nikāya 129, 130",
        special_abilities=[],
        obstacles_to_enlightenment=["extreme_suffering", "no_dhamma_teachers", "burning_pain"]
    ),
    
    Realm(
        id=3,
        name_en="Peta Realm (Hungry Ghosts)",
        name_th="เปรตภูมิ",
        name_pali="Peta Loka",
        category=RealmCategory.APAYA_BHUMI,
        category_name_th="อบายภูมิ (เปรต)",
        min_kamma_score=-70,
        max_kamma_score=-40,
        lifespan_years=500,
        suffering_level=85,
        happiness_level=5,
        description_th="เปรตภูมิ หิวกระหายตลอดเวลา สำหรับผู้โลภมาก ตระหนี่ ไม่ให้ทาน",
        description_en="Hungry ghost realm with constant hunger and thirst for those with extreme greed, stinginess, and no generosity",
        buddhist_reference="Petavatthu; Dhammapada 303-305",
        special_abilities=[],
        obstacles_to_enlightenment=["constant_hunger", "obsession_with_food", "extreme_greed"]
    ),
    
    Realm(
        id=4,
        name_en="Animal Realm",
        name_th="ดิรัจฉานภูมิ",
        name_pali="Tiracchāna Yoni",
        category=RealmCategory.APAYA_BHUMI,
        category_name_th="อบายภูมิ (สัตว์)",
        min_kamma_score=-40,
        max_kamma_score=-10,
        lifespan_years=20,
        suffering_level=70,
        happiness_level=10,
        description_th="สัตว์เดรัจฉาน มีความทุกข์สูง ถูกควบคุมโดยกิเลส ไม่มีปัญญา สำหรับผู้โง่เขลา ดื้อรั้น ไม่ฟังธรรม",
        description_en="Animal realm with high suffering, controlled by defilements, lacking wisdom. For the ignorant, stubborn, and those who refuse Dhamma",
        buddhist_reference="Aṅguttara Nikāya 8.35; Dhammapada 338",
        special_abilities=["physical_strength"],
        obstacles_to_enlightenment=["no_speech", "no_reasoning", "ruled_by_instinct"]
    ),
    
    # ========================================
    # กามสุคติภูมิ (KAMA SUGATI) - Happy Sensual Realms (5-11)
    # ========================================
    
    Realm(
        id=5,
        name_en="Asura Realm (Titans/Demons)",
        name_th="อสุรกายภูมิ",
        name_pali="Asura Kāya",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ",
        min_kamma_score=-10,
        max_kamma_score=10,
        lifespan_years=100,
        suffering_level=60,
        happiness_level=40,
        description_th="อสูรกาย มีอำนาจมาก แต่ชอบอิจฉาริษยา ทะเลาะวิวาท สำหรับผู้โกรธง่าย หยิ่งผยอง",
        description_en="Titan/Demon realm with power but plagued by jealousy and conflict. For the angry, prideful, and competitive",
        buddhist_reference="Saṃyutta Nikāya 11.22; Jātaka 31, 513",
        special_abilities=["great_power", "magical_abilities"],
        obstacles_to_enlightenment=["jealousy", "pride", "constant_warfare"]
    ),
    
    Realm(
        id=6,
        name_en="Human Realm",
        name_th="มนุษย์",
        name_pali="Manussa Loka",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ",
        min_kamma_score=10,
        max_kamma_score=50,
        lifespan_years=80,
        suffering_level=50,
        happiness_level=50,
        description_th="มนุษย์โลก สมดุลระหว่างสุขและทุกข์ ดีที่สุดสำหรับการบรรลุธรรม เพราะมีความทุกข์พอที่จะกระตุ้นให้แสวงหาธรรม และมีปัญญาพอที่จะเข้าใจธรรม",
        description_en="Human realm with balance of suffering and happiness. Best realm for enlightenment because there's enough suffering to motivate Dhamma practice and enough wisdom to understand it",
        buddhist_reference="Aṅguttara Nikāya 5.192; Saṃyutta Nikāya 56.48",
        special_abilities=["moral_reasoning", "dhamma_understanding", "can_practice_path"],
        obstacles_to_enlightenment=[]  # Best realm for practice!
    ),
    
    Realm(
        id=7,
        name_en="Catumaharajika Deva",
        name_th="จาตุมหาราชิกา",
        name_pali="Cātummahārājika",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ (เทวดาชั้นที่ 1)",
        min_kamma_score=50,
        max_kamma_score=60,
        lifespan_years=9_000_000,  # 500 celestial years = 9M human years
        suffering_level=10,
        happiness_level=90,
        description_th="เทวดาชั้นที่ 1 ชั้นจาตุมหาราชิกา ที่อยู่ของจาตุมหาราชเทพ (ผู้พิทักษ์ทิศ 4) มีความสุขมาก อายุยืนนาน",
        description_en="First deva realm, dwelling of the Four Great Kings (guardians of 4 directions). Great happiness and long life",
        buddhist_reference="Aṅguttara Nikāya 7.49; Dīgha Nikāya 20",
        special_abilities=["divine_sight", "divine_hearing", "flight", "shape_shifting"],
        obstacles_to_enlightenment=["too_much_pleasure", "long_life_distraction"]
    ),
    
    Realm(
        id=8,
        name_en="Tavatimsa Deva",
        name_th="ดาวดึงส์",
        name_pali="Tāvatiṃsa",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ (เทวดาชั้นที่ 2)",
        min_kamma_score=60,
        max_kamma_score=70,
        lifespan_years=36_000_000,  # 1000 celestial years
        suffering_level=5,
        happiness_level=95,
        description_th="เทวดาชั้นที่ 2 ชั้นดาวดึงส์ เป็นที่ประทับของพระอินทร์ มี 33 เทวดาชั้นผู้ใหญ่ มีความสุขมาก พระพุทธองค์เคยแสดงอภิธรรมที่นี่",
        description_en="Second deva realm, dwelling of Indra and 33 great devas. Buddha taught Abhidhamma here. Great happiness",
        buddhist_reference="Dīgha Nikāya 21; Saṃyutta Nikāya 11; Kathāvatthu",
        special_abilities=["divine_powers", "create_objects", "instant_travel"],
        obstacles_to_enlightenment=["overwhelming_pleasure", "distraction_from_practice"]
    ),
    
    Realm(
        id=9,
        name_en="Yama Deva",
        name_th="ยามา",
        name_pali="Yāmā",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ (เทวดาชั้นที่ 3)",
        min_kamma_score=70,
        max_kamma_score=75,
        lifespan_years=144_000_000,  # 2000 celestial years
        suffering_level=3,
        happiness_level=97,
        description_th="เทวดาชั้นที่ 3 ชั้นยามา ไม่มีความทุกข์เกือบทั้งหมด มีแต่ความสุข",
        description_en="Third deva realm with almost no suffering, only happiness",
        buddhist_reference="Aṅguttara Nikāya 7.49",
        special_abilities=["wish_fulfillment", "divine_pleasures"],
        obstacles_to_enlightenment=["extreme_comfort", "no_dukkha_to_motivate"]
    ),
    
    Realm(
        id=10,
        name_en="Tusita Deva",
        name_th="ดุสิต",
        name_pali="Tusitā",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ (เทวดาชั้นที่ 4)",
        min_kamma_score=75,
        max_kamma_score=80,
        lifespan_years=576_000_000,  # 4000 celestial years
        suffering_level=2,
        happiness_level=98,
        description_th="เทวดาชั้นที่ 4 ชั้นดุสิต เป็นที่อยู่ของพระโพธิสัตว์ก่อนจุติลงมาบังเกิดเป็นพระพุทธเจ้า มีความสุขสูงมาก",
        description_en="Fourth deva realm, dwelling place of Bodhisattvas before their final birth. Very high happiness",
        buddhist_reference="Aṅguttara Nikāya 7.49; Jātaka Nidāna",
        special_abilities=["bodhisatta_presence", "dhamma_teachings"],
        obstacles_to_enlightenment=["contentment", "postponing_practice"]
    ),
    
    Realm(
        id=11,
        name_en="Nimmanarati Deva",
        name_th="นิมมานรดี",
        name_pali="Nimmānaratī",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ (เทวดาชั้นที่ 5)",
        min_kamma_score=80,
        max_kamma_score=85,
        lifespan_years=2_304_000_000,  # 8000 celestial years
        suffering_level=1,
        happiness_level=99,
        description_th="เทวดาชั้นที่ 5 ชั้นนิมมานรดี สามารถสร้างสิ่งต่างๆ ขึ้นมาเพื่อความสุขได้ด้วยจิต มีความสุขเกือบสูงสุด",
        description_en="Fifth deva realm with ability to create objects of pleasure with mind. Almost maximum happiness",
        buddhist_reference="Aṅguttara Nikāya 7.49",
        special_abilities=["creation_by_mind", "instant_manifestation"],
        obstacles_to_enlightenment=["addiction_to_creation", "sensual_pleasure"]
    ),
    
    Realm(
        id=12,
        name_en="Paranimmitavasavatti Deva",
        name_th="ปรนิมมิตวสวัตดี",
        name_pali="Paranimmita-vasavattī",
        category=RealmCategory.KAMA_SUGATI,
        category_name_th="กามสุคติภูมิ (เทวดาชั้นที่ 6)",
        min_kamma_score=85,
        max_kamma_score=90,
        lifespan_years=9_216_000_000,  # 16000 celestial years
        suffering_level=1,
        happiness_level=99,
        description_th="เทวดาชั้นที่ 6 ชั้นสูงสุดของกามาวจรภูมิ เป็นที่อยู่ของพญามาร สามารถควบคุมสิ่งที่ผู้อื่นสร้างได้ มีความสุขสูงสุดในกามภพ",
        description_en="Sixth and highest sensual deva realm, dwelling of Mara. Can control objects created by others. Highest happiness in sensual existence",
        buddhist_reference="Aṅguttara Nikāya 7.49; Saṃyutta Nikāya 4.24",
        special_abilities=["control_others_creations", "mara_powers"],
        obstacles_to_enlightenment=["mara_influence", "peak_sensual_pleasure"]
    ),
    
    # ========================================
    # รูปพรหมภูมิ (RUPA BRAHMA) - Fine-Material Realms (13-28)
    # ========================================
    
    # First Jhana Realms (3 realms)
    Realm(
        id=13,
        name_en="Brahma Parisajja",
        name_th="พรหมปริสัชชา",
        name_pali="Brahma-pārisajjā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 1 ชั้นที่ 1)",
        min_kamma_score=90,
        max_kamma_score=92,
        lifespan_years=1_000_000_000_000,  # 1/3 kappa
        suffering_level=0,
        happiness_level=80,
        description_th="พรหมชั้นต่ำสุดของปฐมฌาน สำหรับผู้บรรลุฌานที่ 1 อ่อน มีความสุขเบื้องต้นจากการปลีกกาม",
        description_en="Lowest first jhana brahma realm for those who attained weak first jhana. Initial happiness from renunciation of sensual pleasures",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["freedom_from_sensual_desire"],
        obstacles_to_enlightenment=["attached_to_jhana_bliss"]
    ),
    
    Realm(
        id=14,
        name_en="Brahma Purohita",
        name_th="พรหมปุโรหิต",
        name_pali="Brahma-purohitā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 1 ชั้นที่ 2)",
        min_kamma_score=92,
        max_kamma_score=94,
        lifespan_years=2_000_000_000_000,  # 1/2 kappa
        suffering_level=0,
        happiness_level=85,
        description_th="พรหมชั้นกลางของปฐมฌาน สำหรับผู้บรรลุฌานที่ 1 ปานกลาง เป็นที่ปรึกษาของมหาพรหม",
        description_en="Middle first jhana realm for medium first jhana attainment. Ministers of Maha Brahma",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["brahma_wisdom"],
        obstacles_to_enlightenment=["pride_in_attainment"]
    ),
    
    Realm(
        id=15,
        name_en="Maha Brahma",
        name_th="มหาพรหม",
        name_pali="Mahā-brahmā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 1 ชั้นที่ 3)",
        min_kamma_score=94,
        max_kamma_score=96,
        lifespan_years=4_000_000_000_000,  # 1 kappa
        suffering_level=0,
        happiness_level=90,
        description_th="มหาพรหม ชั้นสูงสุดของปฐมฌาน สำหรับผู้บรรลุฌานที่ 1 เข้ม เคยเข้าใจผิดว่าเป็นผู้สร้างโลก",
        description_en="Great Brahma, highest first jhana realm for strong first jhana. Sometimes mistaken as creator god",
        buddhist_reference="Dīgha Nikāya 1 (Brahmajāla Sutta); Dīgha Nikāya 11",
        special_abilities=["appearing_as_creator", "vast_power"],
        obstacles_to_enlightenment=["wrong_view_of_creator", "extreme_pride"]
    ),
    
    # Second Jhana Realms (3 realms)
    Realm(
        id=16,
        name_en="Parittabha",
        name_th="ปริตตาภา",
        name_pali="Parittābhā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 2 ชั้นที่ 1)",
        min_kamma_score=96,
        max_kamma_score=97,
        lifespan_years=8_000_000_000_000,  # 2 kappa
        suffering_level=0,
        happiness_level=92,
        description_th="พรหมแห่งแสงสว่างเล็กน้อย สำหรับผู้บรรลุทุติยฌาน อ่อน มีความสุขจากสมาธิ",
        description_en="Brahma of limited radiance for weak second jhana. Happiness from concentration",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["limited_light_emanation"],
        obstacles_to_enlightenment=["attachment_to_light"]
    ),
    
    Realm(
        id=17,
        name_en="Appamanabha",
        name_th="อัปปมาณาภา",
        name_pali="Appamāṇābhā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 2 ชั้นที่ 2)",
        min_kamma_score=97,
        max_kamma_score=98,
        lifespan_years=16_000_000_000_000,  # 4 kappa
        suffering_level=0,
        happiness_level=94,
        description_th="พรหมแห่งแสงสว่างไพศาล สำหรับผู้บรรลุทุติยฌาน ปานกลาง มีรัศมีกว้างใหญ่",
        description_en="Brahma of infinite radiance for medium second jhana. Vast radiance",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["infinite_light"],
        obstacles_to_enlightenment=["dazzled_by_radiance"]
    ),
    
    Realm(
        id=18,
        name_en="Abhassara",
        name_th="อาภัสสรา",
        name_pali="Ābhassarā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 2 ชั้นที่ 3)",
        min_kamma_score=98,
        max_kamma_score=100,
        lifespan_years=32_000_000_000_000,  # 8 kappa
        suffering_level=0,
        happiness_level=96,
        description_th="พรหมแห่งแสงสว่างรุ่งเรือง สำหรับผู้บรรลุทุติยฌาน เข้ม เปล่งรัศมีสว่างไสวตลอดเวลา เมื่อโลกแตกพรหมเหล่านี้รอด",
        description_en="Streaming radiance brahma for strong second jhana. Constantly emanating brilliant light. Survive world destruction by fire",
        buddhist_reference="Dīgha Nikāya 27 (Aggañña Sutta)",
        special_abilities=["survive_fire_destruction", "streaming_light"],
        obstacles_to_enlightenment=["complacency"]
    ),
    
    # Third Jhana Realms (3 realms)
    Realm(
        id=19,
        name_en="Parittasubha",
        name_th="ปริตตสุภา",
        name_pali="Parittasubhā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 3 ชั้นที่ 1)",
        min_kamma_score=100,
        max_kamma_score=102,
        lifespan_years=64_000_000_000_000,  # 16 kappa
        suffering_level=0,
        happiness_level=97,
        description_th="พรหมแห่งความสุขเล็กน้อย สำหรับผู้บรรลุตติยฌาน อ่อน มีสุข (ไม่ใช่ปีติ) จากฌาน",
        description_en="Limited glory brahma for weak third jhana. Sukha (not piti) from jhana",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["sublime_happiness"],
        obstacles_to_enlightenment=["attached_to_sukha"]
    ),
    
    Realm(
        id=20,
        name_en="Appamanasubha",
        name_th="อัปปมาณสุภา",
        name_pali="Appamāṇasubhā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 3 ชั้นที่ 2)",
        min_kamma_score=102,
        max_kamma_score=104,
        lifespan_years=128_000_000_000_000,  # 32 kappa
        suffering_level=0,
        happiness_level=98,
        description_th="พรหมแห่งความสุขไพศาล สำหรับผู้บรรลุตติยฌาน ปานกลาง มีความสุขมากมาย",
        description_en="Infinite glory brahma for medium third jhana. Infinite happiness",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["boundless_joy"],
        obstacles_to_enlightenment=["unwilling_to_leave_bliss"]
    ),
    
    Realm(
        id=21,
        name_en="Subhakinha",
        name_th="สุภกิณหา",
        name_pali="Subhakiṇhā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 3 ชั้นที่ 3)",
        min_kamma_score=104,
        max_kamma_score=106,
        lifespan_years=256_000_000_000_000,  # 64 kappa
        suffering_level=0,
        happiness_level=99,
        description_th="พรหมแห่งความสุขรุ่งเรือง สำหรับผู้บรรลุตติยฌาน เข้ม มีความสุขสูงสุดในรูปพรหม เมื่อโลกแตกด้วยน้ำพรหมเหล่านี้รอด",
        description_en="Refulgent glory brahma for strong third jhana. Maximum happiness in fine-material realm. Survive world destruction by water",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["survive_water_destruction", "peak_brahma_bliss"],
        obstacles_to_enlightenment=["extreme_attachment_to_bliss"]
    ),
    
    # Fourth Jhana Realms (9 realms total: 7 normal + 5 Pure Abodes)
    Realm(
        id=22,
        name_en="Vehapphala",
        name_th="เวหัปผละ",
        name_pali="Vehapphalā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (ฌาน 4 ชั้นที่ 1)",
        min_kamma_score=106,
        max_kamma_score=108,
        lifespan_years=512_000_000_000_000,  # 500 kappa
        suffering_level=0,
        happiness_level=95,
        description_th="พรหมผลมหา สำหรับผู้บรรลุจตุตถฌาน มีอุเบกขา (ความวางเฉย) แทนความสุข",
        description_en="Great fruit brahma for fourth jhana attainment. Equanimity (upekkha) instead of happiness",
        buddhist_reference="Vibhanga; Abhidhammatthasangaha",
        special_abilities=["perfect_equanimity"],
        obstacles_to_enlightenment=["subtle_attachment"]
    ),
    
    Realm(
        id=23,
        name_en="Asannasatta",
        name_th="อสัญญสัตว์",
        name_pali="Asaññasattā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (อสัญญสัตว์)",
        min_kamma_score=108,
        max_kamma_score=110,
        lifespan_years=512_000_000_000_000,  # 500 kappa
        suffering_level=0,
        happiness_level=0,
        description_th="อสัญญสัตว์ ไม่มีจิต (mindless beings) สำหรับผู้เกลียดจิต ต้องการหนีจิต เป็นภพที่ไม่มีประโยชน์",
        description_en="Mindless beings realm for those who hate consciousness and want to escape mind. Useless realm",
        buddhist_reference="Dīgha Nikāya 1; Majjhima Nikāya 102",
        special_abilities=[],
        obstacles_to_enlightenment=["no_consciousness", "cannot_practice", "wrong_path"]
    ),
    
    # Suddhavasa (Pure Abodes) - 5 realms (only accessible to Anagami - Non-returners)
    Realm(
        id=24,
        name_en="Aviha (Pure Abodes 1)",
        name_th="อวิหา",
        name_pali="Avīhā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (สุทธาวาส ชั้นที่ 1)",
        min_kamma_score=110,
        max_kamma_score=112,
        lifespan_years=1_024_000_000_000_000,  # 1000 kappa
        suffering_level=0,
        happiness_level=90,
        description_th="สุทธาวาสภูมิชั้นที่ 1 ที่อยู่ของพระอนาคามี (ผู้ไม่กลับมา) เท่านั้น จะบรรลุพระอรหันต์ที่นี่",
        description_en="First Pure Abode, only for Anagamis (Non-returners). Will attain Arahantship here",
        buddhist_reference="Majjhima Nikāya 6; Aṅguttara Nikāya 4.123-126",
        special_abilities=["anagami_only", "guaranteed_arahantship"],
        obstacles_to_enlightenment=[]  # Will definitely attain!
    ),
    
    Realm(
        id=25,
        name_en="Atappa (Pure Abodes 2)",
        name_th="อตัปปา",
        name_pali="Atappā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (สุทธาวาส ชั้นที่ 2)",
        min_kamma_score=112,
        max_kamma_score=114,
        lifespan_years=2_048_000_000_000_000,  # 2000 kappa
        suffering_level=0,
        happiness_level=90,
        description_th="สุทธาวาสภูมิชั้นที่ 2 สำหรับพระอนาคามีที่มีกิเลสเบาบางกว่า",
        description_en="Second Pure Abode for Anagamis with lighter defilements",
        buddhist_reference="Majjhima Nikāya 6; Aṅguttara Nikāya 4.123-126",
        special_abilities=["anagami_only", "rapid_progress"],
        obstacles_to_enlightenment=[]
    ),
    
    Realm(
        id=26,
        name_en="Sudassa (Pure Abodes 3)",
        name_th="สุทัสสา",
        name_pali="Sudassā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (สุทธาวาส ชั้นที่ 3)",
        min_kamma_score=114,
        max_kamma_score=116,
        lifespan_years=4_096_000_000_000_000,  # 4000 kappa
        suffering_level=0,
        happiness_level=90,
        description_th="สุทธาวาสภูมิชั้นที่ 3 พรหมที่เห็นได้ชัด",
        description_en="Third Pure Abode, clearly visible brahmas",
        buddhist_reference="Majjhima Nikāya 6; Aṅguttara Nikāya 4.123-126",
        special_abilities=["anagami_only", "clear_vision"],
        obstacles_to_enlightenment=[]
    ),
    
    Realm(
        id=27,
        name_en="Sudassi (Pure Abodes 4)",
        name_th="สุทัสสี",
        name_pali="Sudassī",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (สุทธาวาส ชั้นที่ 4)",
        min_kamma_score=116,
        max_kamma_score=118,
        lifespan_years=8_192_000_000_000_000,  # 8000 kappa
        suffering_level=0,
        happiness_level=90,
        description_th="สุทธาวาสภูมิชั้นที่ 4 พรหมผู้มีจักษุดี",
        description_en="Fourth Pure Abode, brahmas with excellent vision",
        buddhist_reference="Majjhima Nikāya 6; Aṅguttara Nikāya 4.123-126",
        special_abilities=["anagami_only", "excellent_insight"],
        obstacles_to_enlightenment=[]
    ),
    
    Realm(
        id=28,
        name_en="Akanittha (Pure Abodes 5)",
        name_th="อกนิฏฐา",
        name_pali="Akaniṭṭhā",
        category=RealmCategory.RUPA_BRAHMA,
        category_name_th="รูปพรหมภูมิ (สุทธาวาส ชั้นที่ 5 - สูงสุด)",
        min_kamma_score=118,
        max_kamma_score=120,
        lifespan_years=16_384_000_000_000_000,  # 16000 kappa
        suffering_level=0,
        happiness_level=90,
        description_th="สุทธาวาสภูมิชั้นที่ 5 และสูงสุดของรูปพรหม พรหมผู้ไม่มีใครเหนือกว่า เมื่อโลกแตกด้วยลมพรหมเหล่านี้รอด",
        description_en="Highest Pure Abode and highest fine-material realm. Peerless brahmas. Survive world destruction by wind",
        buddhist_reference="Majjhima Nikāya 6; Aṅguttara Nikāya 4.123-126",
        special_abilities=["anagami_only", "survive_wind_destruction", "peak_brahma_realm"],
        obstacles_to_enlightenment=[]
    ),
    
    # ========================================
    # อรูปพรหมภูมิ (ARUPA BRAHMA) - Formless Realms (29-31)
    # ========================================
    
    Realm(
        id=29,
        name_en="Akasanancayatana",
        name_th="อากาสานัญจายตนะ",
        name_pali="Ākāsānañcāyatana",
        category=RealmCategory.ARUPA_BRAHMA,
        category_name_th="อรูปพรหมภูมิ (ฌาน 5 - อากาสานัญจายตนะ)",
        min_kamma_score=120,
        max_kamma_score=122,
        lifespan_years=20_000_000_000_000_000,  # 20,000 kappa
        suffering_level=0,
        happiness_level=50,
        description_th="อรูปพรหมภูมิที่ 1 ฌานที่ 5 ไม่มีร่างกาย มีเพียงจิตที่มีอารมณ์เป็นอากาศไม่มีที่สิ้นสุด",
        description_en="First formless realm, fifth jhana. No body, only mind taking infinite space as object",
        buddhist_reference="Dīgha Nikāya 15; Majjhima Nikāya 106",
        special_abilities=["no_form", "infinite_space_consciousness"],
        obstacles_to_enlightenment=["subtle_clinging", "wrong_view_as_nibbana"]
    ),
    
    Realm(
        id=30,
        name_en="Vinnanancayatana",
        name_th="วิญญาณัญจายตนะ",
        name_pali="Viññāṇañcāyatana",
        category=RealmCategory.ARUPA_BRAHMA,
        category_name_th="อรูปพรหมภูมิ (ฌาน 6 - วิญญาณัญจายตนะ)",
        min_kamma_score=122,
        max_kamma_score=124,
        lifespan_years=40_000_000_000_000_000,  # 40,000 kappa
        suffering_level=0,
        happiness_level=30,
        description_th="อรูปพรหมภูมิที่ 2 ฌานที่ 6 มีจิตที่มีอารมณ์เป็นวิญญาณไม่มีที่สิ้นสุด",
        description_en="Second formless realm, sixth jhana. Mind taking infinite consciousness as object",
        buddhist_reference="Dīgha Nikāya 15; Majjhima Nikāya 106",
        special_abilities=["no_form", "infinite_consciousness"],
        obstacles_to_enlightenment=["very_subtle_clinging"]
    ),
    
    Realm(
        id=31,
        name_en="Akincannayatana",
        name_th="อากิญจัญญายตนะ",
        name_pali="Ākiñcaññāyatana",
        category=RealmCategory.ARUPA_BRAHMA,
        category_name_th="อรูปพรหมภูมิ (ฌาน 7 - อากิญจัญญายตนะ)",
        min_kamma_score=124,
        max_kamma_score=126,
        lifespan_years=60_000_000_000_000_000,  # 60,000 kappa
        suffering_level=0,
        happiness_level=10,
        description_th="อรูปพรหมภูมิที่ 3 ฌานที่ 7 มีจิตที่มีอารมณ์เป็นความว่างเปล่า ไม่มีอะไรเลย",
        description_en="Third formless realm, seventh jhana. Mind taking nothingness as object",
        buddhist_reference="Dīgha Nikāya 15; Majjhima Nikāya 106",
        special_abilities=["no_form", "nothingness_consciousness"],
        obstacles_to_enlightenment=["extremely_subtle_clinging", "mistaken_as_nibbana"]
    ),
    
    # Note: Nevasannanasannayatana (ฌาน 8) ไม่นับเป็นภพภูมิ เพราะเป็นฌานที่สูงที่สุด
    # ผู้ที่บรรลุฌานนี้มักจะเข้าใจผิดว่าบรรลุพระนิพพานแล้ว
    # ในทางเทคนิค beings ที่บรรลุฌานที่ 8 จะเกิดในอากิญจัญญายตนะ (realm 31)
]


# ========================================
# HELPER FUNCTIONS
# ========================================

def get_realm_by_id(realm_id: int) -> Optional[Realm]:
    """Get realm by ID (1-31)"""
    for realm in THIRTY_ONE_REALMS:
        if realm.id == realm_id:
            return realm
    return None


def get_realms_by_category(category: RealmCategory) -> List[Realm]:
    """Get all realms in a category"""
    return [realm for realm in THIRTY_ONE_REALMS if realm.category == category]


def search_realms_by_kamma_score(kamma_score: float) -> List[dict]:
    """
    Search for probable realms based on kamma score
    Returns realms sorted by match probability
    
    Returns:
        List of dicts with keys: realm (Realm), match_strength (float), probability (float)
    """
    matching_realms = []
    
    for realm in THIRTY_ONE_REALMS:
        if realm.min_kamma_score <= kamma_score <= realm.max_kamma_score:
            # Exact match
            match_strength = 1.0
        elif kamma_score < realm.min_kamma_score:
            # Below range
            distance = realm.min_kamma_score - kamma_score
            match_strength = max(0, 1.0 - (distance / 20))  # 20 points tolerance
        else:
            # Above range
            distance = kamma_score - realm.max_kamma_score
            match_strength = max(0, 1.0 - (distance / 20))
        
        if match_strength > 0:
            matching_realms.append({
                "realm": realm,
                "match_strength": match_strength,
                "probability": match_strength * 100
            })
    
    # Sort by match strength
    matching_realms.sort(key=lambda x: x["match_strength"], reverse=True)
    
    return matching_realms


def get_realm_statistics() -> dict:
    """Get statistics about 31 realms"""
    return {
        "total_realms": len(THIRTY_ONE_REALMS),
        "apaya_bhumi": len(get_realms_by_category(RealmCategory.APAYA_BHUMI)),
        "kama_sugati": len(get_realms_by_category(RealmCategory.KAMA_SUGATI)),
        "rupa_brahma": len(get_realms_by_category(RealmCategory.RUPA_BRAHMA)),
        "arupa_brahma": len(get_realms_by_category(RealmCategory.ARUPA_BRAHMA)),
        "human_realm_id": 6,
        "best_for_enlightenment": 6,  # Human realm
        "pure_abodes": [24, 25, 26, 27, 28],  # Anagami only
        "highest_realm_id": 31,
        "lowest_realm_id": 1,
    }
