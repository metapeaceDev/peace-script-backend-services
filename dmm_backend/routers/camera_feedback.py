"""
Phase 2: Camera Feedback Router
Handles user feedback on AI camera suggestions for learning and improvement
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from beanie import PydanticObjectId

from documents_extra import CameraFeedback
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/camera/feedback",
    tags=["Camera Feedback"]
)


# ============================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================

class SubmitFeedbackRequest(BaseModel):
    """Request schema for submitting feedback"""
    user_id: Optional[str] = Field(None, description="User ID (optional)")
    suggestion_id: str = Field(..., description="ID of the camera suggestion")
    
    # Original suggestion context
    emotion: str = Field(..., description="Emotion context")
    intensity: str = Field(..., description="Intensity: low, medium, high")
    suggested_angle: str = Field(..., description="AI-suggested camera angle")
    suggested_lens: str = Field(..., description="AI-suggested lens type")
    suggested_shot_type: str = Field(..., description="AI-suggested shot type")
    suggested_movement: str = Field(..., description="AI-suggested movement")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence (0.0-1.0)")
    
    # User feedback
    accepted: bool = Field(..., description="Did user accept?")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    quick_feedback: Optional[str] = Field(None, description="thumbs_up, thumbs_down, neutral")
    notes: Optional[str] = Field(None, description="User notes")
    tags: List[str] = Field(default_factory=list, description="User tags")
    
    # User corrections (if any)
    actual_angle: Optional[str] = Field(None, description="User's chosen angle")
    actual_lens: Optional[str] = Field(None, description="User's chosen lens")
    actual_shot_type: Optional[str] = Field(None, description="User's chosen shot type")
    actual_movement: Optional[str] = Field(None, description="User's chosen movement")
    
    # Additional context
    session_id: Optional[str] = Field(None, description="Session ID")
    device_type: Optional[str] = Field(None, description="Device: desktop, mobile, tablet")
    scene_description: Optional[str] = Field(None, description="Scene description")
    dhamma_context: Optional[str] = Field(None, description="Dhamma context")


class FeedbackResponse(BaseModel):
    """Response after submitting feedback"""
    success: bool
    feedback_id: str
    message: str
    ai_updated: bool = False
    new_confidence: Optional[float] = None


class FeedbackHistoryResponse(BaseModel):
    """Response for feedback history"""
    feedbacks: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    has_more: bool


class FeedbackStatsResponse(BaseModel):
    """Response for feedback statistics"""
    total_feedback: int
    acceptance_rate: float
    avg_rating: float
    feedback_by_emotion: Dict[str, int]
    feedback_by_rating: Dict[int, int]
    top_corrections: Dict[str, int]


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/submit", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(request: SubmitFeedbackRequest):
    """
    Submit user feedback on AI camera suggestion
    
    This endpoint:
    1. Stores the feedback in database
    2. Updates AI confidence scores based on acceptance
    3. Returns confirmation with updated confidence
    """
    try:
        logger.info(f"Submitting feedback for suggestion: {request.suggestion_id}")
        
        # Create feedback document
        feedback = CameraFeedback(
            user_id=request.user_id,
            suggestion_id=request.suggestion_id,
            emotion=request.emotion,
            intensity=request.intensity,
            suggested_angle=request.suggested_angle,
            suggested_lens=request.suggested_lens,
            suggested_shot_type=request.suggested_shot_type,
            suggested_movement=request.suggested_movement,
            confidence=request.confidence,
            accepted=request.accepted,
            rating=request.rating,
            quick_feedback=request.quick_feedback,
            notes=request.notes,
            tags=request.tags,
            actual_angle=request.actual_angle,
            actual_lens=request.actual_lens,
            actual_shot_type=request.actual_shot_type,
            actual_movement=request.actual_movement,
            timestamp=datetime.utcnow(),
            session_id=request.session_id,
            device_type=request.device_type,
            scene_description=request.scene_description,
            dhamma_context=request.dhamma_context,
        )
        
        # Save to database
        await feedback.insert()
        
        # Calculate new confidence score based on feedback
        # Simple learning algorithm: increase/decrease confidence
        new_confidence = request.confidence
        ai_updated = False
        
        if request.accepted:
            # Increase confidence (max 1.0)
            new_confidence = min(1.0, request.confidence + 0.05)
            ai_updated = True
            logger.info(f"✅ Feedback accepted - confidence increased: {request.confidence:.2f} → {new_confidence:.2f}")
        elif not request.accepted and request.rating is not None and request.rating <= 2:
            # Decrease confidence for low ratings
            new_confidence = max(0.0, request.confidence - 0.05)
            ai_updated = True
            logger.info(f"❌ Feedback rejected - confidence decreased: {request.confidence:.2f} → {new_confidence:.2f}")
        
        return FeedbackResponse(
            success=True,
            feedback_id=str(feedback.id),
            message="Feedback submitted successfully",
            ai_updated=ai_updated,
            new_confidence=new_confidence if ai_updated else None
        )
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/history", response_model=FeedbackHistoryResponse)
async def get_feedback_history(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    emotion: Optional[str] = Query(None, description="Filter by emotion"),
    accepted: Optional[bool] = Query(None, description="Filter by accepted status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get feedback history with pagination and filters
    
    Returns list of feedback entries with optional filtering by:
    - user_id: Show specific user's feedback
    - emotion: Show feedback for specific emotion
    - accepted: Show only accepted/rejected feedback
    """
    try:
        logger.info(f"Fetching feedback history: user={user_id}, emotion={emotion}, accepted={accepted}")
        
        # Build query
        query = {}
        if user_id:
            query["user_id"] = user_id
        if emotion:
            query["emotion"] = emotion
        if accepted is not None:
            query["accepted"] = accepted
        
        # Get total count
        total = await CameraFeedback.find(query).count()
        
        # Get paginated results
        skip = (page - 1) * page_size
        feedbacks = await CameraFeedback.find(query).sort("-timestamp").skip(skip).limit(page_size).to_list()
        
        # Convert to dict
        feedback_list = [
            {
                "id": str(f.id),
                "suggestion_id": f.suggestion_id,
                "emotion": f.emotion,
                "intensity": f.intensity,
                "suggested_angle": f.suggested_angle,
                "suggested_lens": f.suggested_lens,
                "accepted": f.accepted,
                "rating": f.rating,
                "quick_feedback": f.quick_feedback,
                "notes": f.notes,
                "timestamp": f.timestamp.isoformat(),
                "actual_angle": f.actual_angle,
                "actual_lens": f.actual_lens,
            }
            for f in feedbacks
        ]
        
        has_more = (skip + page_size) < total
        
        return FeedbackHistoryResponse(
            feedbacks=feedback_list,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more
        )
        
    except Exception as e:
        logger.error(f"Error fetching feedback history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feedback history: {str(e)}"
        )


@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    emotion: Optional[str] = Query(None, description="Filter by emotion")
):
    """
    Get aggregated feedback statistics
    
    Returns:
    - Total feedback count
    - Acceptance rate (% of accepted suggestions)
    - Average rating
    - Breakdown by emotion
    - Breakdown by rating
    - Most common corrections
    """
    try:
        logger.info(f"Fetching feedback stats: user={user_id}, emotion={emotion}")
        
        # Build query
        query = {}
        if user_id:
            query["user_id"] = user_id
        if emotion:
            query["emotion"] = emotion
        
        # Get all feedback matching query
        feedbacks = await CameraFeedback.find(query).to_list()
        
        total_feedback = len(feedbacks)
        if total_feedback == 0:
            return FeedbackStatsResponse(
                total_feedback=0,
                acceptance_rate=0.0,
                avg_rating=0.0,
                feedback_by_emotion={},
                feedback_by_rating={},
                top_corrections={}
            )
        
        # Calculate statistics
        accepted_count = sum(1 for f in feedbacks if f.accepted)
        acceptance_rate = (accepted_count / total_feedback) * 100
        
        ratings = [f.rating for f in feedbacks if f.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Group by emotion
        feedback_by_emotion = {}
        for f in feedbacks:
            feedback_by_emotion[f.emotion] = feedback_by_emotion.get(f.emotion, 0) + 1
        
        # Group by rating
        feedback_by_rating = {}
        for f in feedbacks:
            if f.rating:
                feedback_by_rating[f.rating] = feedback_by_rating.get(f.rating, 0) + 1
        
        # Find most common corrections
        top_corrections = {}
        for f in feedbacks:
            if f.actual_angle and f.actual_angle != f.suggested_angle:
                key = f"angle: {f.suggested_angle} → {f.actual_angle}"
                top_corrections[key] = top_corrections.get(key, 0) + 1
            if f.actual_lens and f.actual_lens != f.suggested_lens:
                key = f"lens: {f.suggested_lens} → {f.actual_lens}"
                top_corrections[key] = top_corrections.get(key, 0) + 1
        
        # Sort and get top 5
        top_corrections = dict(sorted(top_corrections.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return FeedbackStatsResponse(
            total_feedback=total_feedback,
            acceptance_rate=round(acceptance_rate, 2),
            avg_rating=round(avg_rating, 2),
            feedback_by_emotion=feedback_by_emotion,
            feedback_by_rating=feedback_by_rating,
            top_corrections=top_corrections
        )
        
    except Exception as e:
        logger.error(f"Error fetching feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feedback stats: {str(e)}"
        )


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(feedback_id: str):
    """
    Delete a specific feedback entry
    
    Use case: User wants to remove incorrect or unwanted feedback
    """
    try:
        logger.info(f"Deleting feedback: {feedback_id}")
        
        # Find feedback
        feedback = await CameraFeedback.get(PydanticObjectId(feedback_id))
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback not found: {feedback_id}"
            )
        
        # Delete feedback
        await feedback.delete()
        
        logger.info(f"✅ Feedback deleted: {feedback_id}")
        return None  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete feedback: {str(e)}"
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "camera_feedback",
        "timestamp": datetime.utcnow().isoformat()
    }
