"""Seed training logs for peace-mind-001"""
import asyncio
from datetime import datetime, timedelta
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from documents import TrainingLog, DigitalMindModel

async def seed():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    await init_beanie(database=db, document_models=[TrainingLog, DigitalMindModel])
    
    model_id = "peace-mind-001"
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        print(f"❌ Model {model_id} not found")
        return
    
    print(f"✅ Found model: {model_id}")
    
    # Clear existing
    deleted = await TrainingLog.find(TrainingLog.model_id == model_id).delete()
    print(f"🗑️  Cleared {deleted.deleted_count} logs")
    
    # Create logs
    now = datetime.utcnow()
    logs = [
        TrainingLog(
            model_id=model_id,
            training_type="MEDITATION",
            date=now - timedelta(hours=2),
            details={
                "session_id": f"TRN-{now.strftime('%Y%m%d')}-001",
                "duration_minutes": 30,
                "result": "SUCCESS",
                "quality_score": 8.5,
                "exp_gained": 120,
                "notes": "Deep vipassana session"
            }
        ),
        TrainingLog(
            model_id=model_id,
            training_type="MEDITATION",
            date=now - timedelta(days=1, hours=6),
            details={
                "session_id": f"TRN-{(now - timedelta(days=1)).strftime('%Y%m%d')}-001",
                "duration_minutes": 45,
                "result": "SUCCESS",
                "quality_score": 9.0,
                "exp_gained": 150,
                "notes": "Morning anapanasati"
            }
        ),
        TrainingLog(
            model_id=model_id,
            training_type="GENEROSITY",
            date=now - timedelta(days=1, hours=18),
            details={
                "session_id": f"TRN-{(now - timedelta(days=1)).strftime('%Y%m%d')}-002",
                "duration_minutes": 30,
                "result": "SUCCESS",
                "quality_score": 7.5,
                "exp_gained": 90,
                "notes": "Dana practice"
            }
        ),
        TrainingLog(
            model_id=model_id,
            training_type="DHAMMA_STUDY",
            date=now - timedelta(days=2, hours=20),
            details={
                "session_id": f"TRN-{(now - timedelta(days=2)).strftime('%Y%m%d')}-001",
                "duration_minutes": 60,
                "result": "SUCCESS",
                "quality_score": 8.0,
                "exp_gained": 110,
                "notes": "Satipatthana Sutta study"
            }
        ),
        TrainingLog(
            model_id=model_id,
            training_type="MEDITATION",
            date=now - timedelta(days=5, hours=19),
            details={
                "session_id": f"TRN-{(now - timedelta(days=5)).strftime('%Y%m%d')}-001",
                "duration_minutes": 45,
                "result": "SUCCESS",
                "quality_score": 9.5,
                "exp_gained": 160,
                "notes": "Metta bhavana"
            }
        ),
    ]
    
    for log in logs:
        await log.insert()
        print(f"✅ {log.training_type} - {log.details.get('notes', '')}")
    
    print(f"\n🎉 Seeded {len(logs)} training logs")
    
    # Verify
    all_logs = await TrainingLog.find(TrainingLog.model_id == model_id).sort(-TrainingLog.date).to_list()
    print(f"📊 Total logs in DB: {len(all_logs)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
