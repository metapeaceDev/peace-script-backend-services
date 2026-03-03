"""
Integration Test Data Seeding Script
=====================================
Seeds comprehensive test data for E2E integration testing

Usage:
    python seed_integration_test.py
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings
from documents import DigitalMindModel
from documents_simulation import (
    Scenario,
    EnhancedSimulationEvent,
    SimulationChain,
    SimulationCluster,
    EventType,
    TeachingPack,
    TeachingStep,
    QATestCase,
    QAStatus
)
from core.logging_config import get_logger

logger = get_logger(__name__)


async def init_db():
    """Initialize database connection"""
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    await init_beanie(
        database=db,
        document_models=[
            DigitalMindModel,
            Scenario,
            EnhancedSimulationEvent,
            SimulationChain,
            SimulationCluster,
            TeachingPack,
            TeachingStep,
            QATestCase
        ]
    )
    
    logger.info(f"✓ Connected to database: {settings.MONGO_DB_NAME}")


async def create_test_model() -> DigitalMindModel:
    """Create or get test Digital Mind Model"""
    model_id = "integration-test-001"
    
    existing = await DigitalMindModel.find_one({"_id": model_id})
    if existing:
        logger.info(f"✓ Using existing model: {model_id}")
        return existing
    
    model = DigitalMindModel(
        _id=model_id,
        name="Integration Test Model",
        version="1.0.0",
        status="active",
        core_profile={
            "PhysicalBody": {
                "age": 30,
                "health": 0.8,
                "vitality": 0.7
            },
            "SpiritualAssets": {
                "KammaLedger": {
                    "kusala_stock_points": 500,
                    "akusala_stock_points": 200,
                    "kiriya_actions_count": 50,
                    "pending_vipaka_seeds": [],
                    "dominant_pending_kamma": [],
                    "kamma_log": []
                }
            }
        }
    )
    
    await model.insert()
    logger.info(f"✓ Created test model: {model_id}")
    return model


async def seed_scenarios(model: DigitalMindModel) -> List[Scenario]:
    """Seed test scenarios"""
    logger.info("\n1️⃣ Seeding Scenarios...")
    
    scenarios = []
    scenario_data = [
        {
            "title": "Mindful Decision Making",
            "description": "Practice making decisions with full awareness",
            "initial_state": {
                "consciousness_level": 0.7,
                "emotional_state": "neutral",
                "environment": "workplace"
            },
            "expected_outcomes": {
                "kusala_delta": 50,
                "consciousness_improvement": 0.1,
                "mindfulness_score": 0.8
            }
        },
        {
            "title": "Compassionate Action",
            "description": "Exercise compassion in challenging situations",
            "initial_state": {
                "consciousness_level": 0.6,
                "emotional_state": "stressed",
                "environment": "social"
            },
            "expected_outcomes": {
                "kusala_delta": 100,
                "consciousness_improvement": 0.15,
                "compassion_score": 0.9
            }
        },
        {
            "title": "Wisdom Cultivation",
            "description": "Develop insight through reflection",
            "initial_state": {
                "consciousness_level": 0.8,
                "emotional_state": "calm",
                "environment": "meditation"
            },
            "expected_outcomes": {
                "kusala_delta": 75,
                "consciousness_improvement": 0.2,
                "wisdom_score": 0.85
            }
        }
    ]
    
    for data in scenario_data:
        scenario = Scenario(
            title=data["title"],
            description=data["description"],
            initial_state=data["initial_state"],
            expected_outcomes=data["expected_outcomes"],
            status="active"
        )
        await scenario.insert()
        scenarios.append(scenario)
        logger.info(f"   ✓ Created: {scenario.title} ({scenario.scenario_id})")
    
    return scenarios


async def seed_events(scenarios: List[Scenario]) -> List[EnhancedSimulationEvent]:
    """Seed simulation events"""
    logger.info("\n2️⃣ Seeding Simulation Events...")
    
    events = []
    
    # Create events for first scenario
    scenario = scenarios[0]
    event_templates = [
        {
            "type": "decision",
            "title": "Choice Point",
            "description": "Faced with ethical dilemma at work",
            "intensity": 0.7,
            "karma_impact": 0.5,
            "emotion_score": 0.6
        },
        {
            "type": "reflection",
            "title": "Mindful Pause",
            "description": "Taking moment to reflect before acting",
            "intensity": 0.5,
            "karma_impact": 0.3,
            "emotion_score": 0.8
        },
        {
            "type": "action",
            "title": "Compassionate Response",
            "description": "Choosing to act with kindness",
            "intensity": 0.8,
            "karma_impact": 0.7,
            "emotion_score": 0.9
        },
        {
            "type": "consequence",
            "title": "Positive Outcome",
            "description": "Witnessing beneficial results",
            "intensity": 0.6,
            "karma_impact": 0.4,
            "emotion_score": 0.85
        },
        {
            "type": "insight",
            "title": "Wisdom Gained",
            "description": "Understanding cause and effect",
            "intensity": 0.9,
            "karma_impact": 0.6,
            "emotion_score": 0.95
        }
    ]
    
    for i, template in enumerate(event_templates):
        event = EnhancedSimulationEvent(
            scenario_id=scenario.scenario_id,
            type=template["type"],
            title=template["title"],
            description=template["description"],
            timestamp=datetime.utcnow() + timedelta(seconds=i * 10),
            intensity=template["intensity"],
            karma_impact=template["karma_impact"],
            emotion_score=template["emotion_score"],
            parent_event_id=events[i-1].event_id if i > 0 else None,
            payload={
                "sequence": i,
                "test": True
            }
        )
        await event.insert()
        events.append(event)
        logger.info(f"   ✓ Created: {event.title} ({event.type}) - {event.event_id}")
    
    return events


async def seed_chains(events: List[EnhancedSimulationEvent]) -> List[SimulationChain]:
    """Seed simulation chains"""
    logger.info("\n3️⃣ Seeding Simulation Chains...")
    
    chains = []
    
    # Create karmic chain linking first 3 events
    chain = SimulationChain(
        title="Mindful Action Chain",
        description="Chain showing cause-effect of mindful decision making",
        event_ids=[e.event_id for e in events[:3]],
        chain_type="karmic",
        strength=0.8,
        metadata={"test": True, "theme": "mindfulness"}
    )
    await chain.insert()
    chains.append(chain)
    logger.info(f"   ✓ Created: {chain.title} ({chain.chain_id})")
    logger.info(f"      → Linked {len(chain.event_ids)} events")
    
    return chains


async def seed_clusters(
    scenarios: List[Scenario],
    chains: List[SimulationChain]
) -> List[SimulationCluster]:
    """Seed simulation clusters"""
    logger.info("\n4️⃣ Seeding Simulation Clusters...")
    
    clusters = []
    
    cluster = SimulationCluster(
        title="Integration Test Cluster",
        description="Comprehensive test cluster for E2E validation",
        scenario_ids=[s.scenario_id for s in scenarios],
        chain_ids=[c.chain_id for c in chains],
        dhamma_themes=["mindfulness", "compassion", "wisdom"],
        cluster_type="thematic",
        metadata={"test": True, "purpose": "integration"}
    )
    await cluster.insert()
    clusters.append(cluster)
    logger.info(f"   ✓ Created: {cluster.title} ({cluster.cluster_id})")
    logger.info(f"      → {len(cluster.scenario_ids)} scenarios")
    logger.info(f"      → {len(cluster.chain_ids)} chains")
    logger.info(f"      → {len(cluster.dhamma_themes)} themes")
    
    return clusters


async def seed_teaching_packs() -> List[TeachingPack]:
    """Seed teaching packs"""
    logger.info("\n5️⃣ Seeding Teaching Packs...")
    
    packs = []
    
    pack = TeachingPack(
        title="Introduction to Mindful Living",
        description="Foundational teaching on mindfulness practice",
        difficulty="beginner",
        dhamma_topics=["mindfulness", "awareness", "present moment"],
        learning_objectives=[
            "Understand basic mindfulness principles",
            "Practice present moment awareness",
            "Recognize mental patterns"
        ],
        estimated_duration=30
    )
    await pack.insert()
    packs.append(pack)
    logger.info(f"   ✓ Created: {pack.title} ({pack.pack_id})")
    
    # Create teaching steps
    step_data = [
        {
            "title": "What is Mindfulness?",
            "description": "Understanding the essence of mindful awareness",
            "dhamma_explain": "มิณติ (mindfulness) คือการระลึกรู้อยู่กับปัจจุบันขณะ",
            "quiz_options": [
                "Being aware of present moment",
                "Thinking about the future",
                "Dwelling in the past"
            ],
            "correct_answer": "Being aware of present moment"
        },
        {
            "title": "Practicing Awareness",
            "description": "Techniques for developing mindful observation",
            "dhamma_explain": "สติปัฏฐาน 4: กายานุปัสสนา เวทนานุปัสสนา จิตตานุปัสสนา ธัมมานุปัสสนา",
            "quiz_options": [
                "Observe body, feelings, mind, phenomena",
                "Only watch thoughts",
                "Focus on breathing only"
            ],
            "correct_answer": "Observe body, feelings, mind, phenomena"
        },
        {
            "title": "Integration in Daily Life",
            "description": "Applying mindfulness in everyday activities",
            "dhamma_explain": "สัมปชัญญะ - ความรู้ตัวอย่างชัดเจนในการกระทำทุกอย่าง",
            "quiz_options": [
                "Be aware during all activities",
                "Only practice during meditation",
                "Mindfulness is just for monks"
            ],
            "correct_answer": "Be aware during all activities"
        }
    ]
    
    for i, data in enumerate(step_data):
        step = TeachingStep(
            teaching_pack_id=pack.pack_id,
            title=data["title"],
            description=data["description"],
            dhamma_explain=data["dhamma_explain"],
            step_number=i,
            quiz_options=data["quiz_options"],
            correct_answer=data["correct_answer"],
            explanation=f"Explanation for step {i+1}"
        )
        await step.insert()
        logger.info(f"      ✓ Step {i+1}: {step.title} ({step.step_id})")
    
    return packs


async def seed_qa_test_cases(scenarios: List[Scenario]) -> List[QATestCase]:
    """Seed QA test cases"""
    logger.info("\n6️⃣ Seeding QA Test Cases...")
    
    test_cases = []
    
    for i, scenario in enumerate(scenarios):
        test_case = QATestCase(
            scenario_id=scenario.scenario_id,
            title=f"Integration Test: {scenario.title}",
            description=f"Validate {scenario.title.lower()} produces expected outcomes",
            expected_outcome={
                "consciousness_level": 0.8 + (i * 0.05),
                "kusala_score": 100 + (i * 25),
                "emotional_state": ["peaceful", "joyful", "insightful"][i]
            },
            conditions={
                "initial_state": scenario.initial_state,
                "environment": "test"
            },
            status=QAStatus.PENDING,
            severity=["low", "medium", "high"][i % 3],
            is_automated=True,
            tags=["integration", "e2e", scenario.title.lower().replace(" ", "-")]
        )
        await test_case.insert()
        test_cases.append(test_case)
        logger.info(f"   ✓ Created: {test_case.title} ({test_case.test_case_id})")
    
    return test_cases


async def main():
    """Main seeding function"""
    try:
        print("🌱 Integration Test Data Seeding")
        print("=" * 70)
        
        # Initialize database
        await init_db()
        
        # Create test model
        model = await create_test_model()
        
        # Seed all data
        scenarios = await seed_scenarios(model)
        events = await seed_events(scenarios)
        chains = await seed_chains(events)
        clusters = await seed_clusters(scenarios, chains)
        packs = await seed_teaching_packs()
        test_cases = await seed_qa_test_cases(scenarios)
        
        # Summary
        print("\n" + "=" * 70)
        print("\n✅ Integration Test Data Seeding Complete!")
        print(f"\n📦 Created:")
        print(f"   - 1 Digital Mind Model")
        print(f"   - {len(scenarios)} Scenarios")
        print(f"   - {len(events)} Simulation Events")
        print(f"   - {len(chains)} Simulation Chains")
        print(f"   - {len(clusters)} Simulation Clusters")
        print(f"   - {len(packs)} Teaching Packs (with 3 steps each)")
        print(f"   - {len(test_cases)} QA Test Cases")
        print(f"\n🎯 Ready for E2E Integration Testing!")
        print(f"\n👉 Test with:")
        print(f"   - Browser: http://127.0.0.1:5178")
        print(f"   - API: http://127.0.0.1:8000/api/v1/")
        print(f"   - Model ID: {model.id}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
