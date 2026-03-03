"""
Teaching Router - Teaching Mode & Learning Management
=====================================================
ตามแผน Peace Script V.14 - Step 2.2.49 (UI/UX/Batch/Teaching)

Router นี้จัดการ:
- CRUD operations สำหรับ Teaching Steps
- AI Q&A generation (สร้างคำถาม-คำตอบอัตโนมัติ)
- Quiz submission (ส่งคำตอบ quiz)
- Teaching pack generation (สร้าง course จาก scenario)

Routes:
    POST   /api/v1/teaching/steps              - สร้าง teaching step
    GET    /api/v1/teaching/steps              - List teaching steps
    GET    /api/v1/teaching/steps/{id}         - Get teaching step
    PATCH  /api/v1/teaching/steps/{id}         - Update teaching step
    GET    /api/v1/teaching/steps/{id}/ai-qa   - Generate AI Q&A
    POST   /api/v1/teaching/steps/{id}/quiz    - Submit quiz answer
    POST   /api/v1/scenarios/{id}/teaching-pack - Generate teaching pack
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from documents_simulation import TeachingStep, TeachingPack, Scenario
from documents import DigitalMindModel
from schemas_simulation import (
    TeachingStepCreate,
    TeachingStepUpdate,
    TeachingStepResponse,
    TeachingQAGenerateRequest,
    TeachingQAGenerateResponse,
    TeachingQuizSubmit,
    TeachingQuizResult,
    TeachingPackResponse
)
from modules.kamma_engine import log_new_kamma
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/teaching", tags=["Teaching"])


@router.post("/steps", response_model=TeachingStepResponse, status_code=status.HTTP_201_CREATED)
async def create_teaching_step(step_data: TeachingStepCreate) -> TeachingStepResponse:
    """
    สร้าง Teaching Step ใหม่
    
    Args:
        step_data: ข้อมูล teaching step
        
    Returns:
        TeachingStepResponse: Teaching step ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "scenario_id": "SC-001",
            "title": "เรื่องเจตนาในการให้ทาน",
            "description": "อธิบายความสำคัญของเจตนา",
            "dhamma_explain": "เจตนาคือปัจจัยสำคัญ...",
            "step_number": 1
        }
        ```
    """
    try:
        step = TeachingStep(
            scenario_id=getattr(step_data, 'scenario_id', None),
            event_id=getattr(step_data, 'event_id', None),
            teaching_pack_id=getattr(step_data, 'teaching_pack_id', None),
            title=step_data.title,
            description=step_data.description,
            dhamma_explain=getattr(step_data, 'dhamma_explain', None),
            ai_question=getattr(step_data, 'ai_question', None),
            quiz_options=getattr(step_data, 'quiz_options', []),
            correct_answer=getattr(step_data, 'correct_answer', None),
            explanation=getattr(step_data, 'explanation', None),
            step_number=step_data.step_number,
            parent_step_id=getattr(step_data, 'parent_step_id', None),
            is_branch_point=getattr(step_data, 'is_branch_point', False),
            meta=getattr(step_data, 'meta_info', {})  # ✅ ใช้ getattr เพื่อ handle optional field
        )
        
        await step.insert()
        
        return TeachingStepResponse.model_validate(step)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create teaching step: {str(e)}"
        )


@router.get("/steps", response_model=List[TeachingStepResponse])
async def list_teaching_steps(
    scenario_id: Optional[str] = Query(None, description="Filter by scenario"),
    teaching_pack_id: Optional[str] = Query(None, description="Filter by teaching pack"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[TeachingStepResponse]:
    """
    List Teaching Steps
    
    Query Parameters:
        - scenario_id: SC-xxxxx
        - teaching_pack_id: TP-xxxxx
        - limit, skip: pagination
        
    Returns:
        List[TeachingStepResponse]: รายการ teaching steps
    """
    try:
        query = {}
        
        if scenario_id:
            query["scenario_id"] = scenario_id
            
        if teaching_pack_id:
            query["teaching_pack_id"] = teaching_pack_id
        
        steps = await TeachingStep.find(query).skip(skip).limit(limit).to_list()
        
        return [TeachingStepResponse.model_validate(s) for s in steps]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list teaching steps: {str(e)}"
        )


@router.get("/steps/{step_id}", response_model=TeachingStepResponse)
async def get_teaching_step(step_id: str) -> TeachingStepResponse:
    """
    Get Teaching Step by ID
    
    Args:
        step_id: TS-xxxxx
        
    Returns:
        TeachingStepResponse: Teaching step data
    """
    try:
        step = await TeachingStep.find_one({"step_id": step_id})
        
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teaching step {step_id} not found"
            )
        
        return TeachingStepResponse.model_validate(step)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teaching step: {str(e)}"
        )


@router.patch("/steps/{step_id}", response_model=TeachingStepResponse)
async def update_teaching_step(step_id: str, update_data: TeachingStepUpdate) -> TeachingStepResponse:
    """
    Update Teaching Step
    
    Args:
        step_id: TS-xxxxx
        update_data: ข้อมูลที่ต้องการอัปเดต
        
    Returns:
        TeachingStepResponse: Teaching step ที่อัปเดตแล้ว
    """
    try:
        step = await TeachingStep.find_one({"step_id": step_id})
        
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teaching step {step_id} not found"
            )
        
        update_dict = update_data.model_dump(exclude_none=True)
        
        for field, value in update_dict.items():
            setattr(step, field, value)
        
        step.updated_at = datetime.utcnow()
        await step.save()
        
        return TeachingStepResponse.model_validate(step)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update teaching step: {str(e)}"
        )


@router.get("/steps/{step_id}/ai-qa", response_model=TeachingQAGenerateResponse)
async def generate_ai_qa(step_id: str, qa_request: Optional[TeachingQAGenerateRequest] = None) -> TeachingQAGenerateResponse:
    """
    Generate AI Q&A for Teaching Step
    
    Args:
        step_id: TS-xxxxx
        qa_request: (optional) difficulty, language preferences
        
    Returns:
        TeachingQAGenerateResponse: AI-generated questions, options, explanations
        
    Process:
        - วิเคราะห์เนื้อหา teaching step
        - Generate คำถาม + ตัวเลือก
        - สร้างคำอธิบายธรรม
    """
    try:
        step = await TeachingStep.find_one({"step_id": step_id})
        
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teaching step {step_id} not found"
            )
        
        # Implement actual AI Q&A generation
        # Use step content to generate contextual questions
        
        # Analyze dhamma content
        dhamma_content = step.dhamma_explain
        step_title = step.title
        
        # Generate AI question based on Buddhist principles
        # For now, use template-based generation
        # In production, integrate with GPT/Claude API
        
        question_templates = {
            "generosity": {
                "question": f"จากเนื้อหา '{step_title}' ข้อใดคือองค์ประกอบสำคัญของทานบารมี?",
                "options": [
                    "เจตนาที่บริสุทธิ์ (Pure intention)",
                    "ปริมาณของการให้ (Quantity given)",
                    "เวลาที่เหมาะสม (Timing)",
                    "ผู้รับที่คู่ควร (Worthy recipient)"
                ],
                "correct": "เจตนาที่บริสุทธิ์ (Pure intention)",
                "explanation": "เจตนา (cetanā) เป็นปัจจัยสำคัญที่สุดในการสร้างกุศลกรรม ตามหลักอภิธรรม เพราะเป็นตัวกำหนดคุณภาพของกรรม"
            },
            "wisdom": {
                "question": f"จากเนื้อหา '{step_title}' อะไรคือหลักสำคัญของปัญญาบารมี?",
                "options": [
                    "ความรู้ในไตรลักษณ์ (Tilakkhana wisdom)",
                    "ความรู้ในศาสตร์ต่างๆ (Academic knowledge)",
                    "ความจำที่ดี (Good memory)",
                    "การคิดเร็ว (Quick thinking)"
                ],
                "correct": "ความรู้ในไตรลักษณ์ (Tilakkhana wisdom)",
                "explanation": "ปัญญาในพระพุทธศาสนาหมายถึงความรู้แจ้งในอนิจจัง ทุกขัง อนัตตา ซึ่งนำไปสู่การดับทุกข์"
            },
            "default": {
                "question": f"จากเนื้อหา '{step_title}' ข้อใดสอดคล้องกับหลักธรรม?",
                "options": [
                    "ปฏิบัติด้วยสติและปัญญา",
                    "ทำด้วยกำลังใจ",
                    "ทำตามความรู้สึก",
                    "ทำตามธรรมชาติ"
                ],
                "correct": "ปฏิบัติด้วยสติและปัญญา",
                "explanation": f"หลักธรรมใน {step_title} เน้นการปฏิบัติที่มีสติระลึกรู้และปัญญาเห็นแจ้ง"
            }
        }
        
        # Determine topic from title or content (step_type field doesn't exist)
        topic = "default"
        step_title_lower = (step_title or "").lower()
        dhamma_lower = (dhamma_content or "").lower()
        
        if "dana" in step_title_lower or "generosity" in dhamma_lower:
            topic = "generosity"
        elif "wisdom" in step_title_lower or "panna" in dhamma_lower:
            topic = "wisdom"
        
        template = question_templates[topic]
        
        ai_question = template["question"]
        quiz_options = template["options"]
        correct_answer = template["correct"]
        explanation = template["explanation"]
        
        # Update step with generated Q&A
        step.ai_question = ai_question
        step.quiz_options = quiz_options
        step.correct_answer = correct_answer
        step.explanation = explanation
        await step.save()
        
        # ✅ Return with 'questions' field to match schema at line 767
        return TeachingQAGenerateResponse(
            questions=[{
                "step_id": step.step_id,
                "ai_question": ai_question,
                "quiz_options": quiz_options,
                "correct_answer": correct_answer,
                "explanation": explanation
            }],
            dhamma_insights=[
                "เจตนาเป็นปัจจัยสำคัญที่สุดในการสร้างกุศลกรรม",
                "กรรมที่ทำด้วยเจตนาบริสุทธิ์จะให้ผลบุญมากกว่า"
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI Q&A: {str(e)}"
        )


@router.post("/steps/{step_id}/quiz", response_model=TeachingQuizResult)
async def submit_quiz(step_id: str, quiz_submit: TeachingQuizSubmit) -> TeachingQuizResult:
    """
    Submit Quiz Answer
    
    Args:
        step_id: TS-xxxxx
        quiz_submit: student_answer, student_id
        
    Returns:
        TeachingQuizResult: is_correct, explanation, score
        
    Example:
        ```json
        {
            "student_id": "student-001",
            "student_answer": "เจตนาที่บริสุทธิ์"
        }
        ```
    """
    try:
        step = await TeachingStep.find_one({"step_id": step_id})
        
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teaching step {step_id} not found"
            )
        
        # Check answer
        is_correct = quiz_submit.student_answer == step.correct_answer
        score = 1.0 if is_correct else 0.0
        
        # Record quiz result
        quiz_result = {
            "student_id": quiz_submit.student_id,
            "student_answer": quiz_submit.student_answer,
            "is_correct": is_correct,
            "score": score,
            "submitted_at": datetime.utcnow()
        }
        
        step.quiz_results.append(quiz_result)
        
        # Update completion rate
        total_attempts = len(step.quiz_results)
        correct_attempts = sum(1 for r in step.quiz_results if r.get("is_correct"))
        step.completion_rate = correct_attempts / total_attempts if total_attempts > 0 else 0.0
        
        await step.save()
        
        # ===================================================================
        # KAMMA INTEGRATION: Log teaching quiz completion as kamma
        # ===================================================================
        try:
            # Get model_id from quiz_submit or context
            model_id = quiz_submit.student_id  # Assume student_id is model_id
            
            if model_id:
                profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
                if profile:
                    profile_dict = profile.model_dump()
                    
                    # Correct answer = kusala, incorrect = learning opportunity (neutral/small akusala)
                    is_kusala = is_correct
                    intensity = score * 2.0  # Scale score to intensity
                    
                    kamma_id = log_new_kamma(
                        profile=profile_dict,
                        action_type="teaching",
                        details={
                            "step_id": step.step_id,
                            "title": step.title,
                            "is_correct": is_correct,
                            "score": score,
                            "student_answer": quiz_submit.student_answer
                        },
                        is_kusala=is_kusala,
                        intensity=intensity
                    )
                    
                    # Update profile
                    profile.CoreProfile = profile_dict.get("CoreProfile", {})
                    await profile.save()
                    
                    logger.info(f"Kamma logged for teaching quiz: {kamma_id}")
        except Exception as kamma_err:
            logger.warning(f"Failed to log kamma for teaching quiz: {kamma_err}")
        
        return TeachingQuizResult(
            step_id=step.step_id,
            is_correct=is_correct,
            correct_answer=step.correct_answer,
            explanation=step.explanation,
            score=score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit quiz: {str(e)}"
        )


@router.post("/scenarios/{scenario_id}/teaching-pack", response_model=TeachingPackResponse, status_code=status.HTTP_201_CREATED)
async def generate_teaching_pack(scenario_id: str) -> TeachingPackResponse:
    """
    Generate Teaching Pack from Scenario
    
    Args:
        scenario_id: SC-xxxxx
        
    Returns:
        TeachingPackResponse: Teaching pack พร้อม steps
        
    Process:
        - วิเคราะห์ scenario events
        - สร้าง teaching steps จาก events
        - Generate AI Q&A สำหรับแต่ละ step
        - จัดเรียง steps ตามลำดับ
    """
    try:
        scenario = await Scenario.find_one({"scenario_id": scenario_id})
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )
        
        # Create teaching pack
        teaching_pack = TeachingPack(
            title=f"Teaching: {scenario.title}",
            scenario_ids=[scenario.scenario_id],
            teaching_step_ids=[],
            difficulty_level="intermediate",
            estimated_duration_minutes=30
        )
        
        await teaching_pack.insert()
        
        # Generate teaching steps from scenario events
        # Analyze scenario structure and create educational steps
        
        teaching_steps = []
        
        # Step 1: Introduction - Overview of scenario
        intro_step = TeachingStep(
            step_id=f"TS-{scenario.scenario_id}-01",
            pack_id=teaching_pack.pack_id,
            scenario_id=scenario.scenario_id,
            sequence_number=1,
            title=f"Introduction: {scenario.title}",
            step_type="introduction",
            dhamma_explain=f"This scenario teaches about {scenario.category}. "
                          f"Context: {scenario.description}. "
                          "Let's explore the Buddhist psychology principles involved.",
            ai_question="What is the main teaching theme of this scenario?",
            quiz_options=[
                scenario.category,
                "Meditation practice",
                "Ritual observance",
                "Social customs"
            ],
            correct_answer=scenario.category
        )
        await intro_step.insert()
        teaching_steps.append(intro_step.step_id)
        
        # Step 2: Analysis - Explain sensory input and mental factors
        if hasattr(scenario, 'sensory_input') and scenario.sensory_input:
            analysis_step = TeachingStep(
                step_id=f"TS-{scenario.scenario_id}-02",
                pack_id=teaching_pack.pack_id,
                scenario_id=scenario.scenario_id,
                sequence_number=2,
                title="Sensory Contact and Perception",
                step_type="analysis",
                dhamma_explain="According to Abhidhamma, consciousness arises when sense door (dvāra) meets sense object (ārammaṇa). "
                              f"In this scenario, sensory contact occurs through {getattr(scenario.sensory_input, 'dvara', 'visual door')}. "
                              "This triggers a cognitive process (citta-vīthi) leading to perception and response.",
                ai_question="What triggers the initial consciousness moment in this scenario?",
                quiz_options=[
                    "Sensory contact (phassa)",
                    "Memory recall",
                    "Imagination",
                    "Emotional reaction"
                ],
                correct_answer="Sensory contact (phassa)"
            )
            await analysis_step.insert()
            teaching_steps.append(analysis_step.step_id)
        
        # Step 3: Choices - Explain kusala/akusala decision points
        if scenario.choices and len(scenario.choices) > 0:
            choice_step = TeachingStep(
                step_id=f"TS-{scenario.scenario_id}-03",
                pack_id=teaching_pack.pack_id,
                scenario_id=scenario.scenario_id,
                sequence_number=3,
                title="Decision Points: Kusala vs Akusala",
                step_type="practice",
                dhamma_explain=f"This scenario presents {len(scenario.choices)} choices. "
                              "Each choice has different karmic qualities (kusala/akusala/kiriya). "
                              "The quality depends on the mental factors (cetasika) present at the moment of decision. "
                              "Wholesome choices arise from non-greed (alobha), non-hatred (adosa), and wisdom (amoha).",
                ai_question="What determines whether a choice creates wholesome (kusala) or unwholesome (akusala) kamma?",
                quiz_options=[
                    "The mental factors (cetasika) present",
                    "The physical action alone",
                    "The outcome result",
                    "Social approval"
                ],
                correct_answer="The mental factors (cetasika) present"
            )
            await choice_step.insert()
            teaching_steps.append(choice_step.step_id)
        
        # Update teaching pack with generated steps
        teaching_pack.teaching_step_ids = teaching_steps
        await teaching_pack.save()
        
        return TeachingPackResponse(
            pack_id=teaching_pack.pack_id,
            title=teaching_pack.title,
            scenario_ids=teaching_pack.scenario_ids,
            teaching_step_ids=teaching_pack.teaching_step_ids,
            difficulty_level=teaching_pack.difficulty_level,
            estimated_duration_minutes=teaching_pack.estimated_duration_minutes,
            completion_count=teaching_pack.completion_count,
            average_score=teaching_pack.average_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate teaching pack: {str(e)}"
        )
