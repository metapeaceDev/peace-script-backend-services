"""
⏱️ Temporal Tracking System - Appearance History
Track appearance changes over time as kamma evolves

Features:
- Log appearance snapshots at key moments
- Track kamma → appearance correlation over time
- Generate timeline visualizations
- Compare appearance states
- Detect significant changes
- Buddhist lifecycle tracking

Dependencies:
- MongoDB for history storage
- Matplotlib for timeline visualization (optional)
"""

from typing import Optional, Dict, List, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from beanie import Document
import json

from kamma_appearance_models import KammaAppearanceProfile, HealthScore, VoiceScore, DemeanorScore
from documents_actors import ExternalCharacter
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# APPEARANCE SNAPSHOT
# =============================================================================

class AppearanceSnapshot(BaseModel):
    """Single snapshot of appearance at a point in time"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_id: str
    
    # Core scores
    health_score: HealthScore
    voice_score: VoiceScore
    demeanor_score: DemeanorScore
    
    # Overall metrics
    overall_balance: float
    kusala_percentage: float
    akusala_percentage: float
    total_kamma_count: int
    
    # Key characteristics (for comparison)
    skin_tone: Optional[str] = None
    body_strength: float
    voice_quality: float
    peacefulness: float
    
    # Event that triggered this snapshot
    trigger_event: str = Field("manual", description="What caused this snapshot")
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-10-17T10:00:00Z",
                "model_id": "peace-mind-001",
                "overall_balance": 35.5,
                "kusala_percentage": 67.8,
                "trigger_event": "meditation_completion",
                "notes": "After 7-day retreat"
            }
        }


class AppearanceSnapshotDocument(Document):
    """MongoDB document for appearance snapshots"""
    snapshot: AppearanceSnapshot
    
    class Settings:
        name = "appearance_snapshots"
        indexes = [
            [("snapshot.model_id", 1), ("snapshot.timestamp", -1)]
        ]


# =============================================================================
# APPEARANCE CHANGE DETECTION
# =============================================================================

class AppearanceChange(BaseModel):
    """Detected change between two snapshots"""
    aspect: str = Field(..., description="What changed (health/voice/demeanor)")
    old_value: float
    new_value: float
    delta: float
    percentage_change: float
    significance: Literal["minor", "moderate", "major", "profound"]
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "aspect": "voice_quality",
                "old_value": 75.0,
                "new_value": 85.0,
                "delta": 10.0,
                "percentage_change": 13.33,
                "significance": "moderate",
                "description": "Voice quality improved from truthful speech practice"
            }
        }


class ComparisonResult(BaseModel):
    """Result of comparing two snapshots"""
    model_id: str
    snapshot1_timestamp: datetime
    snapshot2_timestamp: datetime
    time_elapsed: str
    
    # Overall changes
    overall_balance_change: float
    kusala_change: float
    akusala_change: float
    
    # Detailed changes
    changes: List[AppearanceChange]
    
    # Summary
    total_changes: int
    major_changes: int
    overall_trend: Literal["improving", "declining", "stable"]
    summary: str


# =============================================================================
# TEMPORAL TRACKING MANAGER
# =============================================================================

class TemporalTracker:
    """
    Manages appearance history and change tracking
    """
    
    @staticmethod
    async def create_snapshot(
        profile: KammaAppearanceProfile,
        trigger_event: str = "manual",
        notes: Optional[str] = None
    ) -> AppearanceSnapshot:
        """
        Create appearance snapshot from current profile
        
        Args:
            profile: Current kamma appearance profile
            trigger_event: What triggered this snapshot
            notes: Optional notes
            
        Returns:
            AppearanceSnapshot
        """
        logger.info(f"Creating appearance snapshot for {profile.model_id}, trigger: {trigger_event}")
        
        snapshot = AppearanceSnapshot(
            model_id=profile.model_id,
            health_score=profile.health_score,
            voice_score=profile.voice_score,
            demeanor_score=profile.demeanor_score,
            overall_balance=profile.overall_kamma_balance,
            kusala_percentage=profile.kusala_percentage,
            akusala_percentage=profile.akusala_percentage,
            total_kamma_count=profile.total_kamma_analyzed,
            body_strength=profile.health_score.body_strength,
            voice_quality=profile.voice_score.voice_quality,
            peacefulness=profile.demeanor_score.peacefulness,
            trigger_event=trigger_event,
            notes=notes
        )
        
        # Save to database
        doc = AppearanceSnapshotDocument(snapshot=snapshot)
        await doc.insert()
        
        logger.info(f"Snapshot created and saved: {snapshot.timestamp}")
        
        return snapshot
    
    @staticmethod
    async def get_history(
        model_id: str,
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AppearanceSnapshot]:
        """
        Get appearance history for model
        
        Args:
            model_id: Model to get history for
            limit: Maximum number of snapshots
            start_date: Filter from this date
            end_date: Filter until this date
            
        Returns:
            List of snapshots ordered by timestamp (newest first)
        """
        logger.info(f"Getting history for {model_id}, limit={limit}")
        
        # Build query
        query = {"snapshot.model_id": model_id}
        
        if start_date or end_date:
            time_filter = {}
            if start_date:
                time_filter["$gte"] = start_date
            if end_date:
                time_filter["$lte"] = end_date
            query["snapshot.timestamp"] = time_filter
        
        # Query database
        docs = await AppearanceSnapshotDocument.find(query).sort([("snapshot.timestamp", -1)]).limit(limit).to_list()
        
        snapshots = [doc.snapshot for doc in docs]
        
        logger.info(f"Found {len(snapshots)} snapshots")
        
        return snapshots
    
    @staticmethod
    async def get_latest_snapshot(model_id: str) -> Optional[AppearanceSnapshot]:
        """Get most recent snapshot for model"""
        snapshots = await TemporalTracker.get_history(model_id, limit=1)
        return snapshots[0] if snapshots else None
    
    @staticmethod
    def compare_snapshots(
        snapshot1: AppearanceSnapshot,
        snapshot2: AppearanceSnapshot
    ) -> ComparisonResult:
        """
        Compare two snapshots and detect changes
        
        Args:
            snapshot1: Earlier snapshot
            snapshot2: Later snapshot
            
        Returns:
            ComparisonResult with detected changes
        """
        logger.info(f"Comparing snapshots: {snapshot1.timestamp} vs {snapshot2.timestamp}")
        
        # Ensure correct order
        if snapshot2.timestamp < snapshot1.timestamp:
            snapshot1, snapshot2 = snapshot2, snapshot1
        
        # Calculate time elapsed
        time_diff = snapshot2.timestamp - snapshot1.timestamp
        time_elapsed = TemporalTracker._format_timedelta(time_diff)
        
        # Overall changes
        balance_change = snapshot2.overall_balance - snapshot1.overall_balance
        kusala_change = snapshot2.kusala_percentage - snapshot1.kusala_percentage
        akusala_change = snapshot2.akusala_percentage - snapshot1.akusala_percentage
        
        # Detect detailed changes
        changes = []
        
        # Health changes
        changes.extend(TemporalTracker._detect_health_changes(snapshot1, snapshot2))
        
        # Voice changes
        changes.extend(TemporalTracker._detect_voice_changes(snapshot1, snapshot2))
        
        # Demeanor changes
        changes.extend(TemporalTracker._detect_demeanor_changes(snapshot1, snapshot2))
        
        # Count major changes
        major_changes = len([c for c in changes if c.significance in ["major", "profound"]])
        
        # Determine overall trend
        if kusala_change > 5:
            trend = "improving"
        elif kusala_change < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        # Generate summary
        summary = TemporalTracker._generate_summary(changes, trend, time_elapsed)
        
        return ComparisonResult(
            model_id=snapshot1.model_id,
            snapshot1_timestamp=snapshot1.timestamp,
            snapshot2_timestamp=snapshot2.timestamp,
            time_elapsed=time_elapsed,
            overall_balance_change=balance_change,
            kusala_change=kusala_change,
            akusala_change=akusala_change,
            changes=changes,
            total_changes=len(changes),
            major_changes=major_changes,
            overall_trend=trend,
            summary=summary
        )
    
    @staticmethod
    def _detect_health_changes(snap1: AppearanceSnapshot, snap2: AppearanceSnapshot) -> List[AppearanceChange]:
        """Detect health-related changes"""
        changes = []
        
        # Overall health
        health_delta = snap2.health_score.overall_health - snap1.health_score.overall_health
        if abs(health_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="overall_health",
                old_value=snap1.health_score.overall_health,
                new_value=snap2.health_score.overall_health,
                delta=health_delta,
                percentage_change=(health_delta / snap1.health_score.overall_health) * 100,
                significance=TemporalTracker._assess_significance(health_delta),
                description=f"Health {'improved' if health_delta > 0 else 'declined'} by {abs(health_delta):.1f} points"
            ))
        
        # Body strength
        strength_delta = snap2.health_score.body_strength - snap1.health_score.body_strength
        if abs(strength_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="body_strength",
                old_value=snap1.health_score.body_strength,
                new_value=snap2.health_score.body_strength,
                delta=strength_delta,
                percentage_change=(strength_delta / snap1.health_score.body_strength) * 100,
                significance=TemporalTracker._assess_significance(strength_delta),
                description=f"Physical strength {'increased' if strength_delta > 0 else 'decreased'}"
            ))
        
        # Skin quality
        skin_delta = snap2.health_score.skin_quality - snap1.health_score.skin_quality
        if abs(skin_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="skin_quality",
                old_value=snap1.health_score.skin_quality,
                new_value=snap2.health_score.skin_quality,
                delta=skin_delta,
                percentage_change=(skin_delta / snap1.health_score.skin_quality) * 100,
                significance=TemporalTracker._assess_significance(skin_delta),
                description=f"Skin appearance {'improved' if skin_delta > 0 else 'worsened'}"
            ))
        
        return changes
    
    @staticmethod
    def _detect_voice_changes(snap1: AppearanceSnapshot, snap2: AppearanceSnapshot) -> List[AppearanceChange]:
        """Detect voice-related changes"""
        changes = []
        
        # Voice quality
        quality_delta = snap2.voice_score.voice_quality - snap1.voice_score.voice_quality
        if abs(quality_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="voice_quality",
                old_value=snap1.voice_score.voice_quality,
                new_value=snap2.voice_score.voice_quality,
                delta=quality_delta,
                percentage_change=(quality_delta / snap1.voice_score.voice_quality) * 100,
                significance=TemporalTracker._assess_significance(quality_delta),
                description=f"Voice quality {'improved' if quality_delta > 0 else 'declined'} - likely from speech kamma"
            ))
        
        # Vocal warmth
        warmth_delta = snap2.voice_score.vocal_warmth - snap1.voice_score.vocal_warmth
        if abs(warmth_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="vocal_warmth",
                old_value=snap1.voice_score.vocal_warmth,
                new_value=snap2.voice_score.vocal_warmth,
                delta=warmth_delta,
                percentage_change=(warmth_delta / snap1.voice_score.vocal_warmth) * 100,
                significance=TemporalTracker._assess_significance(warmth_delta),
                description=f"Voice warmth {'increased' if warmth_delta > 0 else 'decreased'} - reflects mettā practice"
            ))
        
        return changes
    
    @staticmethod
    def _detect_demeanor_changes(snap1: AppearanceSnapshot, snap2: AppearanceSnapshot) -> List[AppearanceChange]:
        """Detect demeanor-related changes"""
        changes = []
        
        # Peacefulness
        peace_delta = snap2.demeanor_score.peacefulness - snap1.demeanor_score.peacefulness
        if abs(peace_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="peacefulness",
                old_value=snap1.demeanor_score.peacefulness,
                new_value=snap2.demeanor_score.peacefulness,
                delta=peace_delta,
                percentage_change=(peace_delta / snap1.demeanor_score.peacefulness) * 100,
                significance=TemporalTracker._assess_significance(peace_delta),
                description=f"Inner peace {'increased' if peace_delta > 0 else 'decreased'} - visible in demeanor"
            ))
        
        # Loving-kindness
        metta_delta = snap2.demeanor_score.loving_kindness_score - snap1.demeanor_score.loving_kindness_score
        if abs(metta_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="loving_kindness",
                old_value=snap1.demeanor_score.loving_kindness_score,
                new_value=snap2.demeanor_score.loving_kindness_score,
                delta=metta_delta,
                percentage_change=(metta_delta / snap1.demeanor_score.loving_kindness_score) * 100,
                significance=TemporalTracker._assess_significance(metta_delta),
                description=f"Mettā {'strengthened' if metta_delta > 0 else 'weakened'} - affects facial expression"
            ))
        
        # Confidence
        conf_delta = snap2.demeanor_score.confidence_level - snap1.demeanor_score.confidence_level
        if abs(conf_delta) >= 5:
            changes.append(AppearanceChange(
                aspect="confidence",
                old_value=snap1.demeanor_score.confidence_level,
                new_value=snap2.demeanor_score.confidence_level,
                delta=conf_delta,
                percentage_change=(conf_delta / snap1.demeanor_score.confidence_level) * 100,
                significance=TemporalTracker._assess_significance(conf_delta),
                description=f"Confidence {'grew' if conf_delta > 0 else 'diminished'} - visible in posture"
            ))
        
        return changes
    
    @staticmethod
    def _assess_significance(delta: float) -> Literal["minor", "moderate", "major", "profound"]:
        """Assess significance of change"""
        abs_delta = abs(delta)
        
        if abs_delta >= 20:
            return "profound"
        elif abs_delta >= 10:
            return "major"
        elif abs_delta >= 5:
            return "moderate"
        else:
            return "minor"
    
    @staticmethod
    def _format_timedelta(td: timedelta) -> str:
        """Format timedelta to human-readable string"""
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 365:
            years = days // 365
            return f"{years} year{'s' if years > 1 else ''}"
        elif days > 30:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''}"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''}"
        elif hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
    
    @staticmethod
    def _generate_summary(changes: List[AppearanceChange], trend: str, time_elapsed: str) -> str:
        """Generate human-readable summary"""
        if not changes:
            return f"No significant changes detected over {time_elapsed}."
        
        summary_parts = []
        
        # Overall trend
        if trend == "improving":
            summary_parts.append(f"Overall improvement over {time_elapsed}")
        elif trend == "declining":
            summary_parts.append(f"Overall decline over {time_elapsed}")
        else:
            summary_parts.append(f"Stable condition over {time_elapsed}")
        
        # Major changes
        major = [c for c in changes if c.significance in ["major", "profound"]]
        if major:
            aspects = [c.aspect.replace("_", " ") for c in major]
            summary_parts.append(f"Major changes in: {', '.join(aspects)}")
        
        return ". ".join(summary_parts) + "."


# =============================================================================
# TIMELINE GENERATOR
# =============================================================================

class TimelineGenerator:
    """
    Generate timeline visualizations and data
    """
    
    @staticmethod
    def generate_timeline_data(
        snapshots: List[AppearanceSnapshot],
        metrics: List[str] = ["overall_balance", "kusala_percentage", "peacefulness"]
    ) -> Dict:
        """
        Generate timeline data for visualization
        
        Args:
            snapshots: List of snapshots (should be ordered)
            metrics: Which metrics to include
            
        Returns:
            Dict with timeline data ready for charting
        """
        logger.info(f"Generating timeline data for {len(snapshots)} snapshots")
        
        # Sort by timestamp
        sorted_snaps = sorted(snapshots, key=lambda s: s.timestamp)
        
        # Extract data points
        timeline_data = {
            "timestamps": [],
            "metrics": {}
        }
        
        for metric in metrics:
            timeline_data["metrics"][metric] = []
        
        for snap in sorted_snaps:
            timeline_data["timestamps"].append(snap.timestamp.isoformat())
            
            # Overall balance
            if "overall_balance" in metrics:
                timeline_data["metrics"]["overall_balance"].append(snap.overall_balance)
            
            # Kusala percentage
            if "kusala_percentage" in metrics:
                timeline_data["metrics"]["kusala_percentage"].append(snap.kusala_percentage)
            
            # Peacefulness
            if "peacefulness" in metrics:
                timeline_data["metrics"]["peacefulness"].append(snap.peacefulness)
            
            # Voice quality
            if "voice_quality" in metrics:
                timeline_data["metrics"]["voice_quality"].append(snap.voice_quality)
            
            # Body strength
            if "body_strength" in metrics:
                timeline_data["metrics"]["body_strength"].append(snap.body_strength)
        
        return timeline_data


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def create_appearance_snapshot(
    profile: KammaAppearanceProfile,
    trigger: str = "manual",
    notes: Optional[str] = None
) -> AppearanceSnapshot:
    """
    Convenience function to create snapshot
    
    Example:
        >>> snapshot = await create_appearance_snapshot(
        ...     profile,
        ...     trigger="meditation_completion",
        ...     notes="After 7-day retreat"
        ... )
    """
    return await TemporalTracker.create_snapshot(profile, trigger, notes)


async def get_appearance_history(
    model_id: str,
    limit: int = 50
) -> List[AppearanceSnapshot]:
    """
    Convenience function to get history
    
    Example:
        >>> history = await get_appearance_history("peace-mind-001")
        >>> print(f"Found {len(history)} snapshots")
    """
    return await TemporalTracker.get_history(model_id, limit=limit)


async def compare_appearance_over_time(
    model_id: str,
    days_ago: int = 7
) -> Optional[ComparisonResult]:
    """
    Compare current appearance to N days ago
    
    Example:
        >>> comparison = await compare_appearance_over_time("peace-mind-001", days_ago=7)
        >>> if comparison:
        ...     print(comparison.summary)
    """
    history = await TemporalTracker.get_history(model_id, limit=100)
    
    if len(history) < 2:
        logger.warning(f"Not enough history to compare (only {len(history)} snapshots)")
        return None
    
    # Latest snapshot
    latest = history[0]
    
    # Find snapshot closest to N days ago
    target_date = datetime.utcnow() - timedelta(days=days_ago)
    old_snapshot = min(history[1:], key=lambda s: abs((s.timestamp - target_date).total_seconds()))
    
    return TemporalTracker.compare_snapshots(old_snapshot, latest)
