"""
🌱 Seed Training Log Data for Digital Mind Model v1.4

Creates sample training sessions and logs for peace-mind-001
"""

import asyncio
from datetime import datetime, timedelta
from typing import List
import sys

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings
from documents import DigitalMindModel, TrainingLog


async def seed_training_logs():
    """Seed training log data for peace-mind-001"""
    
    # Connect to database
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    await init_beanie(
        database=db,
        document_models=[TrainingLog, DigitalMindModel]
    )
    
    MODEL_ID = "peace-mind-001"
    
    # Check if model exists
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == MODEL_ID)
    if not model:
        print(f"❌ Model '{MODEL_ID}' not found. Please run seed_db.py first.")
        client.close()
        sys.exit(1)
    
    print(f"✅ Found model: {MODEL_ID}")
    
    # Clear existing training logs for this model
    deleted = await TrainingLog.find(TrainingLog.model_id == MODEL_ID).delete()
    print(f"🗑️  Cleared {deleted.deleted_count} existing training logs")
    
    # Create sample training sessions
    now = datetime.utcnow()
    
    training_sessions: List[TrainingLog] = [
        # Recent session - today
        TrainingLog(
            model_id=MODEL_ID,
            training_type="MEDITATION",
            date=now - timedelta(hours=2),
            details={
                "session_id": f"TRN-{now.strftime('%Y%m%d')}-001",
                "start_time": (now - timedelta(hours=2)).isoformat(),
                "end_time": (now - timedelta(hours=1, minutes=30)).isoformat(),
                "duration_minutes": 30,
                "result": "SUCCESS",
                "quality_score": 8.5,
                "exp_gained": 120,
                "notes": "Deep vipassana session focusing on anicca",
                "modifications_applied": {
                    "sati_mastery_exp": 45,
                    "panna_mastery_exp": 40,
                    "anusaya_moha_reduced": -2
                }
            }
        ),
        
        # Yesterday - Morning meditation
        TrainingLog(
            model_id=MODEL_ID,
            training_type="MEDITATION",
            session_id=f"TRN-{(now - timedelta(days=1)).strftime('%Y%m%d')}-001",
            start_time=now - timedelta(days=1, hours=6),
            end_time=now - timedelta(days=1, hours=5, minutes=15),
            duration_minutes=45,
            result="SUCCESS",
            quality_score=9.0,
            exp_gained=150,
            notes="Morning anapanasati with excellent concentration",
            modifications_applied={
                "sati_mastery_exp": 60,
                "samadhi_parami_exp": 50,
                "anusaya_lobha_reduced": -1
            },
            date=now - timedelta(days=1, hours=6),
        ),
        
        # Yesterday - Evening generosity
        TrainingLog(
            model_id=MODEL_ID,
            training_type="GENEROSITY",
            session_id=f"TRN-{(now - timedelta(days=1)).strftime('%Y%m%d')}-002",
            start_time=now - timedelta(days=1, hours=18),
            end_time=now - timedelta(days=1, hours=17, minutes=30),
            duration_minutes=30,
            result="SUCCESS",
            quality_score=7.5,
            exp_gained=90,
            notes="Dana practice: offered food to monastery",
            modifications_applied={
                "dana_parami_exp": 80,
                "metta_parami_exp": 30,
                "anusaya_lobha_reduced": -3
            },
            date=now - timedelta(days=1, hours=18),
        ),
        
        # 2 days ago - Dhamma study
        TrainingLog(
            model_id=MODEL_ID,
            training_type="DHAMMA_STUDY",
            session_id=f"TRN-{(now - timedelta(days=2)).strftime('%Y%m%d')}-001",
            start_time=now - timedelta(days=2, hours=20),
            end_time=now - timedelta(days=2, hours=19),
            duration_minutes=60,
            result="SUCCESS",
            quality_score=8.0,
            exp_gained=110,
            notes="Studied Satipatthana Sutta with contemplation",
            modifications_applied={
                "panna_mastery_exp": 70,
                "dhamma_vicaya_exp": 45,
                "anusaya_moha_reduced": -4
            },
            date=now - timedelta(days=2, hours=20),
        ),
        
        # 3 days ago - Partial meditation (interrupted)
        TrainingLog(
            model_id=MODEL_ID,
            training_type="MEDITATION",
            session_id=f"TRN-{(now - timedelta(days=3)).strftime('%Y%m%d')}-001",
            start_time=now - timedelta(days=3, hours=7),
            end_time=now - timedelta(days=3, hours=6, minutes=45),
            duration_minutes=15,
            result="PARTIAL",
            quality_score=5.0,
            exp_gained=30,
            notes="Session interrupted by external disturbance",
            modifications_applied={
                "sati_mastery_exp": 15
            },
            date=now - timedelta(days=3, hours=7),
        ),
        
        # 4 days ago - Sila practice
        TrainingLog(
            model_id=MODEL_ID,
            training_type="SILA_PRACTICE",
            session_id=f"TRN-{(now - timedelta(days=4)).strftime('%Y%m%d')}-001",
            start_time=now - timedelta(days=4, hours=12),
            end_time=now - timedelta(days=4, hours=12),
            duration_minutes=0,
            result="SUCCESS",
            quality_score=8.0,
            exp_gained=80,
            notes="Full day observing 8 precepts",
            modifications_applied={
                "sila_parami_exp": 100,
                "adhitthana_parami_exp": 40,
                "anusaya_dosa_reduced": -2
            },
            date=now - timedelta(days=4, hours=12),
        ),
        
        # 5 days ago - Loving-kindness meditation
        TrainingLog(
            model_id=MODEL_ID,
            training_type="MEDITATION",
            session_id=f"TRN-{(now - timedelta(days=5)).strftime('%Y%m%d')}-001",
            start_time=now - timedelta(days=5, hours=19),
            end_time=now - timedelta(days=5, hours=18, minutes=15),
            duration_minutes=45,
            result="SUCCESS",
            quality_score=9.5,
            exp_gained=160,
            notes="Metta bhavana with all four brahmaviharas",
            modifications_applied={
                "metta_parami_exp": 90,
                "karuna_parami_exp": 50,
                "anusaya_dosa_reduced": -5,
                "anusaya_byapada_reduced": -3
            },
            date=now - timedelta(days=5, hours=19),
        ),
        
        # 1 week ago - Failed attempt
        TrainingLog(
            model_id=MODEL_ID,
            training_type="MEDITATION",
            session_id=f"TRN-{(now - timedelta(days=7)).strftime('%Y%m%d')}-001",
            start_time=now - timedelta(days=7, hours=6),
            end_time=now - timedelta(days=7, hours=5, minutes=55),
            duration_minutes=5,
            result="FAILED",
            quality_score=2.0,
            exp_gained=5,
            notes="Could not settle the mind; too restless",
            modifications_applied={
                "viriya_parami_exp": 5
            },
            date=now - timedelta(days=7, hours=6),
        ),
    ]
    
    # Insert training logs
    inserted_count = 0
    for log in training_sessions:
        await log.insert()
        inserted_count += 1
        print(f"✅ Created training session: {log.session_id} ({log.training_type}) - {log.result}")
    
    print(f"\n🎉 Successfully seeded {inserted_count} training log entries for {MODEL_ID}")
    
    # Verify
    all_logs = await TrainingLog.find(TrainingLog.model_id == MODEL_ID).sort(-TrainingLog.date).to_list()
    print(f"📊 Total training logs in database: {len(all_logs)}")
    
    # Summary statistics
    success_count = sum(1 for log in all_logs if log.result == "SUCCESS")
    partial_count = sum(1 for log in all_logs if log.result == "PARTIAL")
    failed_count = sum(1 for log in all_logs if log.result == "FAILED")
    total_exp = sum(log.exp_gained for log in all_logs)
    avg_quality = sum(log.quality_score for log in all_logs) / len(all_logs) if all_logs else 0
    
    print(f"\n📈 Training Statistics:")
    print(f"   - Success: {success_count}")
    print(f"   - Partial: {partial_count}")
    print(f"   - Failed: {failed_count}")
    print(f"   - Total EXP: {total_exp}")
    print(f"   - Avg Quality: {avg_quality:.2f}/10")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_training_logs())
