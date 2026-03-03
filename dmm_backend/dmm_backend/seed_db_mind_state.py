"""
Seed Database Script for MindState and SimulationHistory
Creates initial data for testing and development

Usage:
    python -m seed_db_mind_state
"""

import asyncio
from datetime import datetime, timedelta
from typing import List
import motor.motor_asyncio
from beanie import init_beanie

from config import settings
from documents import MindState, SimulationHistory
from core.logging_config import get_logger

logger = get_logger(__name__)


async def init_db_connection():
    """Initialize database connection"""
    logger.info("Connecting to MongoDB...")
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    database = client.get_database(settings.MONGO_DB_NAME)
    
    await init_beanie(
        database=database,
        document_models=[MindState, SimulationHistory]
    )
    logger.info("Database connection established")
    return database


async def seed_mind_states():
    """Create sample MindState documents"""
    logger.info("Creating sample MindStates...")
    
    # Sample users with different spiritual levels
    mind_states = [
        # Beginner - Puthujjana (Worldling)
        MindState(
            user_id="user_001",
            sila=3.5,
            samadhi=2.0,
            panna=2.5,
            sati_strength=3.0,
            current_anusaya={
                "lobha": 5.5,  # Greed
                "dosa": 4.0,   # Anger
                "moha": 6.0,   # Delusion
                "mana": 4.5,   # Conceit
                "ditthi": 5.0, # Wrong view
                "vicikiccha": 4.0,  # Doubt
                "uddhacca": 5.5     # Restlessness
            },
            kusala_count_today=2,
            akusala_count_today=8,
            kusala_count_total=150,
            akusala_count_total=450,
            active_hindrances={
                "kamacchanda": 6.0,  # Sensual desire
                "byapada": 3.0,      # Ill-will
                "thina_middha": 5.0, # Sloth and torpor
                "uddhacca_kukkucca": 5.5,  # Restlessness and worry
                "vicikiccha": 4.0    # Doubt
            },
            current_bhumi="puthujjana",
            days_of_practice=30,
            meditation_minutes_total=600
        ),
        
        # Intermediate - Practicing Seriously
        MindState(
            user_id="user_002",
            sila=6.5,
            samadhi=5.0,
            panna=5.5,
            sati_strength=6.0,
            current_anusaya={
                "lobha": 3.5,
                "dosa": 2.5,
                "moha": 3.0,
                "mana": 3.0,
                "ditthi": 2.0,
                "vicikiccha": 2.0,
                "uddhacca": 3.0
            },
            kusala_count_today=15,
            akusala_count_today=3,
            kusala_count_total=2500,
            akusala_count_total=800,
            active_hindrances={
                "kamacchanda": 2.5,
                "byapada": 1.5,
                "thina_middha": 2.0,
                "uddhacca_kukkucca": 2.5,
                "vicikiccha": 1.5
            },
            current_bhumi="puthujjana",
            days_of_practice=365,
            meditation_minutes_total=18000
        ),
        
        # Advanced - Stream-Enterer (Sotāpanna)
        MindState(
            user_id="user_003",
            sila=8.5,
            samadhi=7.5,
            panna=8.0,
            sati_strength=8.5,
            current_anusaya={
                "lobha": 2.0,
                "dosa": 1.5,
                "moha": 1.0,
                "mana": 2.0,
                "ditthi": 0.0,  # Eliminated in Sotāpanna
                "vicikiccha": 0.0,  # Eliminated in Sotāpanna
                "uddhacca": 1.5
            },
            kusala_count_today=28,
            akusala_count_today=0,
            kusala_count_total=15000,
            akusala_count_total=500,
            active_hindrances={
                "kamacchanda": 1.0,
                "byapada": 0.5,
                "thina_middha": 0.5,
                "uddhacca_kukkucca": 1.0,
                "vicikiccha": 0.0  # No doubt
            },
            current_bhumi="sotapanna",
            days_of_practice=1825,  # 5 years
            meditation_minutes_total=180000
        )
    ]
    
    # Insert all mind states
    for mind_state in mind_states:
        try:
            await mind_state.insert()
            logger.info(f"Created MindState for {mind_state.user_id} (bhumi: {mind_state.current_bhumi})")
        except Exception as e:
            logger.error(f"Failed to create MindState for {mind_state.user_id}: {e}")
    
    logger.info(f"Successfully seeded {len(mind_states)} MindStates")
    return mind_states


async def seed_simulation_history(mind_states: List[MindState]):
    """Create sample SimulationHistory documents"""
    logger.info("Creating sample SimulationHistory records...")
    
    simulations = [
        # User 001 - Beginner facing temptation
        SimulationHistory(
            simulation_id="sim_001_001",
            user_id="user_001",
            scenario_id="scenario_temptation_001",
            choice_index=1,
            choice_id="choice_take_money",
            choice_type="akusala",
            choice_label="เก็บเงินไว้ด้วยความเงียบ",
            choice_description="เก็บเงินที่พบไว้โดยไม่บอกใคร หวังจะใช้ประโยชน์ส่วนตัว",
            citta_generated="lobha_mula_citta",
            citta_quality="akusala",
            kamma_generated=4.5,
            sati_intervened=False,
            sati_strength_at_choice=2.0,
            panna_intervened=False,
            state_before={
                "sila": 3.5,
                "samadhi": 2.0,
                "panna": 2.5,
                "lobha_anusaya": 5.5
            },
            state_after={
                "sila": 3.0,  # Decreased
                "samadhi": 2.0,
                "panna": 2.5,
                "lobha_anusaya": 6.0  # Increased
            },
            state_changes=[
                "Sīla decreased by 0.5",
                "Lobha anusaya strengthened (+0.5)",
                "Akusala count +1"
            ],
            immediate_consequences="รู้สึกผิดเล็กน้อย แต่ยังมีความต้องการในทรัพย์สิน",
            short_term_consequences="ความวิตกกังวลเพิ่มขึ้นว่าจะถูกจับได้ ความเป็นกลางลดลง",
            long_term_consequences="กรรมลักขโมยจะส่งผลในภพหน้า อาจเกิดในภพที่ยากจน หรือเป็นหนี้คนอื่น",
            wisdom_gained="การกระทำที่เกิดจากโลภะจะนำมาซึ่งทุกข์ในอนาคต แม้จะดูเหมือนได้ประโยชน์ในขณะนั้น",
            practice_tip="เมื่อเผชิญกับสิ่งล่อใจ ให้หยุดและสังเกตความต้องการที่เกิดขึ้นด้วยสติ พิจารณาผลในระยะยาว",
            pali_term_explained="Lobha-mūla-citta (โลภะมูลจิต): จิตที่มีโลภะเป็นรากเหง้า นำไปสู่การกระทำเพื่อแสวงหาสิ่งที่ต้องการโดยไม่คำนึงถึงศีลธรรม",
            anusaya_before={"lobha": 5.5, "dosa": 4.0, "moha": 6.0},
            anusaya_after={"lobha": 6.0, "dosa": 4.0, "moha": 6.0},
            anusaya_changes={"lobha": +0.5},
            duration_seconds=45,
            timestamp=datetime.utcnow() - timedelta(hours=2)
        ),
        
        # User 002 - Intermediate practicing Sati
        SimulationHistory(
            simulation_id="sim_002_001",
            user_id="user_002",
            scenario_id="scenario_anger_001",
            choice_index=0,
            choice_id="choice_breathe_mindfully",
            choice_type="kusala",
            choice_label="หยุดและสังเกตลมหายใจ",
            choice_description="รู้ตัวว่ากำลังโกรธ หยุดและสังเกตลมหายใจด้วยสติ",
            citta_generated="kusala_citta_with_panna",
            citta_quality="kusala",
            kamma_generated=6.5,
            sati_intervened=True,
            sati_strength_at_choice=6.0,
            panna_intervened=True,
            state_before={
                "sila": 6.5,
                "samadhi": 5.0,
                "panna": 5.5,
                "dosa_anusaya": 2.5
            },
            state_after={
                "sila": 6.5,
                "samadhi": 5.5,  # Increased
                "panna": 6.0,    # Increased
                "dosa_anusaya": 2.0  # Decreased
            },
            state_changes=[
                "Samādhi increased by 0.5",
                "Paññā increased by 0.5",
                "Dosa anusaya weakened (-0.5)",
                "Kusala count +1"
            ],
            immediate_consequences="ความโกรธลดลงอย่างรวดเร็ว จิตใจสงบและเป็นกลาง",
            short_term_consequences="ความสามารถในการควบคุมอารมณ์เพิ่มขึ้น ความสัมพันธ์กับผู้อื่นดีขึ้น",
            long_term_consequences="กรรมดีนี้จะนำมาซึ่งความสงบสุขและปัญญาในภพหน้า อาจเกิดในภพที่มีสติปัญญาดี",
            wisdom_gained="สติคือเครื่องมือที่ทรงพลังในการป้องกันไม่ให้กิเลสควบคุมจิต เมื่อมีสติ เราสามารถเลือกการตอบสนองได้",
            practice_tip="ฝึกสังเกตลมหายใจเป็นประจำ เพื่อสร้างความแข็งแกร่งของสติ เมื่อเผชิญกับความโกรธ สติจะเข้ามาช่วยทันที",
            pali_term_explained="Sati (สติ): ความระลึกได้ ความตื่นตัว เป็นปัจจัยสำคัญในการไม่ให้กิเลสเข้าครอบงำจิต",
            anusaya_before={"lobha": 3.5, "dosa": 2.5, "moha": 3.0},
            anusaya_after={"lobha": 3.5, "dosa": 2.0, "moha": 3.0},
            anusaya_changes={"dosa": -0.5},
            duration_seconds=120,
            timestamp=datetime.utcnow() - timedelta(hours=1)
        ),
        
        # User 003 - Advanced practicing Mettā
        SimulationHistory(
            simulation_id="sim_003_001",
            user_id="user_003",
            scenario_id="scenario_difficult_person_001",
            choice_index=2,
            choice_id="choice_metta_practice",
            choice_type="kusala",
            choice_label="ปลูกเมตตาต่อผู้นั้น",
            choice_description="พิจารณาว่าผู้นั้นก็ต้องการความสุขเหมือนเรา ปลูกเมตตาจิตอย่างจริงจัง",
            citta_generated="sobhana_citta_with_metta",
            citta_quality="kusala",
            kamma_generated=9.0,
            sati_intervened=True,
            sati_strength_at_choice=8.5,
            panna_intervened=True,
            state_before={
                "sila": 8.5,
                "samadhi": 7.5,
                "panna": 8.0,
                "dosa_anusaya": 1.5
            },
            state_after={
                "sila": 8.5,
                "samadhi": 8.0,  # Increased
                "panna": 8.5,    # Increased
                "dosa_anusaya": 1.0  # Decreased
            },
            state_changes=[
                "Samādhi increased by 0.5",
                "Paññā increased by 0.5",
                "Dosa anusaya further weakened (-0.5)",
                "Kusala count +1",
                "Mettā (Loving-kindness) strengthened"
            ],
            immediate_consequences="จิตเต็มไปด้วยเมตตา ความเครียดหายไป รู้สึกสงบและมีพลัง",
            short_term_consequences="ความสัมพันธ์กับผู้อื่นดีขึ้นอย่างมาก สามารถช่วยเหลือผู้อื่นได้ดีขึ้น",
            long_term_consequences="กรรมเมตตานี้จะนำมาซึ่งความเป็นที่รักของมวลมนุษย์และเทวดา ในภพหน้าจะเกิดในภพที่สูงส่ง มีความสุขและปัญญา",
            wisdom_gained="เมตตาคือยาวิเศษที่รักษาทั้งตนเองและผู้อื่น เมื่อใจเต็มไปด้วยเมตตา โทสะไม่มีที่อยู่",
            practice_tip="ฝึกเมตตาภาวนาทุกวัน เริ่มจากตนเอง จากนั้นขยายไปสู่คนที่รัก คนเป็นกลาง และสุดท้ายคนที่ไม่ชอบ",
            pali_term_explained="Mettā (เมตตา): ความปรารถนาดีต่อสรรพสัตว์ ต้องการให้ผู้อื่นมีความสุข เป็นพรหมวิหารที่สำคัญ",
            user_reflection="การปลูกเมตตาต่อคนที่ยากเป็นประสบการณ์ที่ท้าทายแต่มีคุณค่ามาก ทำให้เห็นว่าทุกคนต่างต้องการความสุข",
            user_rating=5,
            anusaya_before={"lobha": 2.0, "dosa": 1.5, "moha": 1.0},
            anusaya_after={"lobha": 2.0, "dosa": 1.0, "moha": 1.0},
            anusaya_changes={"dosa": -0.5},
            duration_seconds=300,
            timestamp=datetime.utcnow() - timedelta(minutes=30)
        )
    ]
    
    # Insert all simulation records
    for simulation in simulations:
        try:
            await simulation.insert()
            logger.info(f"Created SimulationHistory {simulation.simulation_id} for {simulation.user_id}")
        except Exception as e:
            logger.error(f"Failed to create SimulationHistory {simulation.simulation_id}: {e}")
    
    logger.info(f"Successfully seeded {len(simulations)} SimulationHistory records")
    return simulations


async def main():
    """Main seed function"""
    try:
        # Initialize database
        await init_db_connection()
        
        # Seed data
        logger.info("=" * 60)
        logger.info("Starting database seeding...")
        logger.info("=" * 60)
        
        mind_states = await seed_mind_states()
        simulations = await seed_simulation_history(mind_states)
        
        logger.info("=" * 60)
        logger.info("Database seeding completed successfully!")
        logger.info(f"Total MindStates created: {len(mind_states)}")
        logger.info(f"Total SimulationHistory records created: {len(simulations)}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
