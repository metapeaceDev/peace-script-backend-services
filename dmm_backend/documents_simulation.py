"""
Peace Script V.14 - Comprehensive Simulation System Documents
Extended data models for Scenario, SimulationChain, SimulationCluster, TeachingStep, QATestCase
Based on planning documents 2.2.48, 2.2.49, 2.2.50, 2.2.84, 2.2.85
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING, DESCENDING


# =====================================================================
# Enumerations
# =====================================================================

class ScenarioStatus(str, Enum):
    """Scenario lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    TEMPLATE = "template"
    TEACHING = "teaching"
    QA_TEST = "qa_test"


class EventType(str, Enum):
    """Extended event types for simulation"""
    KARMA = "karma"
    ACTION = "action"
    DREAM = "dream"
    CAMERA = "camera"
    ANALYTIC = "analytic"
    TEACHING = "teaching"
    QA = "qa"
    ENVIRONMENT = "environment"
    MILESTONE = "milestone"
    BRANCH_POINT = "branch_point"
    DECISION = "decision"
    REACTION = "reaction"


class ChainStatus(str, Enum):
    """Chain lifecycle and health status"""
    ACTIVE = "active"
    BROKEN = "broken"
    MERGED = "merged"
    BRANCHED = "branched"
    COMPLETED = "completed"


class QAStatus(str, Enum):
    """QA test case status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    REGRESSION = "regression"
    SKIPPED = "skipped"


# =====================================================================
# Embedded Models
# =====================================================================

class EnhancedSimulationEvent(BaseModel):
    """Enhanced simulation event with full field support"""
    event_id: str = Field(default_factory=lambda: f"EV-{uuid.uuid4().hex[:12]}")
    scenario_id: Optional[str] = None
    timeline_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: EventType
    title: str
    description: Optional[str] = None
    
    # Payload & State
    payload: Dict[str, Any] = Field(default_factory=dict)
    entity_refs: List[str] = Field(default_factory=list)
    state_change: Optional[Dict[str, Any]] = None
    
    # Chain & Branch
    parent_event_id: Optional[str] = None
    child_event_ids: List[str] = Field(default_factory=list)
    branch_id: Optional[str] = None
    chain_id: Optional[str] = None
    
    # Conditions & Logic
    condition: Optional[str] = None  # Expression or rule
    intensity: float = 0.0
    tags: List[str] = Field(default_factory=list)
    
    # Annotations & Insights
    annotation: Optional[str] = None
    teaching_note: Optional[str] = None
    dhamma_ref: Optional[str] = None
    ai_insight: Optional[str] = None
    
    # Analytics
    karma_impact: Optional[float] = None
    emotion_score: Optional[float] = None
    health_delta: Optional[float] = None
    
    # QA & Testing
    qa_result: Optional[Dict[str, Any]] = None
    expected_outcome: Optional[Dict[str, Any]] = None
    
    # Metadata
    cue_ref: Optional[str] = None
    milestone: Optional[str] = None
    reason: Optional[str] = None
    feedback: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class AnalyticSnapshot(BaseModel):
    """Snapshot of analytics at a point in time"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    karma_total: float = 0.0
    health_score: float = 1.0
    emotion_avg: float = 0.5
    chain_health: float = 1.0
    event_count: int = 0
    milestone_count: int = 0
    branch_count: int = 0
    meta: Dict[str, Any] = Field(default_factory=dict)


class TeachingAnnotation(BaseModel):
    """Teaching annotation for events/scenarios"""
    annotation_id: str = Field(default_factory=lambda: f"TA-{uuid.uuid4().hex[:8]}")
    author: Optional[str] = None
    content: str
    dhamma_refs: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QATestRun(BaseModel):
    """Single QA test run result"""
    run_id: str = Field(default_factory=lambda: f"RUN-{uuid.uuid4().hex[:8]}")
    run_at: datetime = Field(default_factory=datetime.utcnow)
    status: QAStatus
    expected: Dict[str, Any] = Field(default_factory=dict)
    actual: Dict[str, Any] = Field(default_factory=dict)
    diff: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


# =====================================================================
# Main Documents
# =====================================================================

class Scenario(Document):
    """
    Main scenario document for simulation
    Based on Peace Script 2.2.48, 2.2.50
    """
    scenario_id: str = Field(default_factory=lambda: f"SC-{uuid.uuid4().hex[:12]}")
    model_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    status: ScenarioStatus = ScenarioStatus.DRAFT
    
    # Events & Structure
    events: List[EnhancedSimulationEvent] = Field(default_factory=list)  # ✅ Embedded events
    event_ids: List[str] = Field(default_factory=list)  # Reference IDs for quick access
    timeline_id: Optional[str] = None  # Primary timeline
    chain_ids: List[str] = Field(default_factory=list)  # Associated chains
    branch_ids: List[str] = Field(default_factory=list)  # Branches created from this scenario
    
    # Teaching & QA
    teaching_notes: List[TeachingAnnotation] = Field(default_factory=list)
    qa_test_case_ids: List[str] = Field(default_factory=list)
    dhamma_refs: List[str] = Field(default_factory=list)
    
    # Cluster & Analytics
    cluster_id: Optional[str] = None
    cluster_tags: List[str] = Field(default_factory=list)
    analytic_snapshots: List[AnalyticSnapshot] = Field(default_factory=list)
    
    # Batch & Comparison
    is_template: bool = False
    parent_scenario_id: Optional[str] = None  # For cloned scenarios
    batch_group_id: Optional[str] = None  # For batch runs
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_log: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "scenarios"
        indexes = [
            IndexModel([("model_id", ASCENDING), ("status", ASCENDING), ("_id", DESCENDING)]),
            IndexModel([("cluster_id", ASCENDING)]),
            IndexModel([("tags", ASCENDING)]),
            IndexModel([("batch_group_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


class SimulationChain(Document):
    """
    Event chain document for tracking causal relationships
    Based on Peace Script 2.2.84, 2.2.85
    """
    chain_id: str = Field(default_factory=lambda: f"CH-{uuid.uuid4().hex[:12]}")
    scenario_id: Optional[str] = None
    timeline_id: Optional[str] = None
    
    # Chain Structure
    event_ids: List[str] = Field(default_factory=list)  # Ordered sequence
    parent_chain_id: Optional[str] = None
    child_chain_ids: List[str] = Field(default_factory=list)
    branch_point_event_id: Optional[str] = None  # Event where branching occurred
    
    # Status & Analytics
    status: ChainStatus = ChainStatus.ACTIVE
    chain_health: float = 1.0  # 0.0 - 1.0
    karma_total: float = 0.0
    emotion_curve: List[float] = Field(default_factory=list)
    health_curve: List[float] = Field(default_factory=list)
    
    # Teaching & QA
    teaching_annotations: List[TeachingAnnotation] = Field(default_factory=list)
    qa_flags: List[str] = Field(default_factory=list)
    dhamma_insights: List[str] = Field(default_factory=list)
    
    # What-If & Branching
    is_what_if_branch: bool = False
    what_if_condition: Optional[str] = None
    alternative_chains: List[str] = Field(default_factory=list)  # Other branch chain_ids
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_log: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "simulation_chains"
        indexes = [
            IndexModel([("scenario_id", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("timeline_id", ASCENDING)]),
            IndexModel([("parent_chain_id", ASCENDING)]),
            IndexModel([("branch_point_event_id", ASCENDING)]),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


class SimulationCluster(Document):
    """
    Cluster document for grouping and analyzing multiple scenarios
    Based on Peace Script 2.2.50
    """
    cluster_id: str = Field(default_factory=lambda: f"CL-{uuid.uuid4().hex[:12]}")
    title: str
    description: Optional[str] = None
    
    # Cluster Members
    scenario_ids: List[str] = Field(default_factory=list)
    chain_ids: List[str] = Field(default_factory=list)
    model_ids: List[str] = Field(default_factory=list)
    
    # Aggregate Analytics
    aggregate_karma: float = 0.0
    aggregate_health: float = 0.0
    emotion_avg: float = 0.0
    outcome_distribution: Dict[str, int] = Field(default_factory=dict)
    event_count_total: int = 0
    scenario_count: int = 0
    
    # Teaching & Research
    cluster_tags: List[str] = Field(default_factory=list)
    research_notes: List[str] = Field(default_factory=list)
    teaching_pack_id: Optional[str] = None
    dhamma_themes: List[str] = Field(default_factory=list)
    
    # Batch Analytics
    batch_run_history: List[Dict[str, Any]] = Field(default_factory=list)
    comparison_matrix: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_log: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "simulation_clusters"
        indexes = [
            IndexModel([("cluster_tags", ASCENDING)]),
            IndexModel([("teaching_pack_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


class TeachingStep(Document):
    """
    Teaching step document for guided learning
    Based on Peace Script 2.2.49, 2.2.50
    """
    step_id: str = Field(default_factory=lambda: f"TS-{uuid.uuid4().hex[:12]}")
    scenario_id: Optional[str] = None
    event_id: Optional[str] = None
    chain_id: Optional[str] = None
    teaching_pack_id: Optional[str] = None
    
    # Teaching Content
    title: str
    description: str
    dhamma_explain: Optional[str] = None
    ai_question: Optional[str] = None
    quiz_options: List[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    
    # Step Sequence
    step_number: int = 0
    parent_step_id: Optional[str] = None
    next_step_ids: List[str] = Field(default_factory=list)
    is_branch_point: bool = False
    
    # Student Interaction
    student_notes: List[str] = Field(default_factory=list)
    quiz_results: List[Dict[str, Any]] = Field(default_factory=list)
    feedback: Optional[str] = None
    completion_rate: float = 0.0
    
    # Resources
    references: List[str] = Field(default_factory=list)
    dhamma_refs: List[str] = Field(default_factory=list)
    related_events: List[str] = Field(default_factory=list)
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "teaching_steps"
        indexes = [
            IndexModel([("scenario_id", ASCENDING), ("step_number", ASCENDING)]),
            IndexModel([("teaching_pack_id", ASCENDING), ("step_number", ASCENDING)]),
            IndexModel([("event_id", ASCENDING)]),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


class QATestCase(Document):
    """
    QA test case document for regression testing
    Based on Peace Script 2.2.49, 2.2.50
    """
    test_case_id: str = Field(default_factory=lambda: f"QA-{uuid.uuid4().hex[:12]}")
    scenario_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    
    # Test Specification
    expected_outcome: Dict[str, Any] = Field(default_factory=dict)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    test_tags: List[str] = Field(default_factory=list)
    
    # Test Results
    status: QAStatus = QAStatus.PENDING
    actual_outcome: Optional[Dict[str, Any]] = None
    regression_diff: Optional[Dict[str, Any]] = None
    pass_rate: float = 0.0
    
    # Test History
    test_runs: List[QATestRun] = Field(default_factory=list)
    last_run_at: Optional[datetime] = None
    run_count: int = 0
    
    # Annotations
    annotations: List[str] = Field(default_factory=list)
    qa_flags: List[str] = Field(default_factory=list)
    severity: Optional[str] = None  # "low", "medium", "high", "critical"
    
    # Automation
    is_automated: bool = False
    automation_script: Optional[str] = None
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_log: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "qa_test_cases"
        indexes = [
            IndexModel([("scenario_id", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("test_tags", ASCENDING)]),
            IndexModel([("status", ASCENDING), ("last_run_at", DESCENDING)]),
            IndexModel([("severity", ASCENDING)]),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


class TeachingPack(Document):
    """
    Teaching pack document grouping multiple teaching steps
    Based on Peace Script 2.2.50
    """
    pack_id: str = Field(default_factory=lambda: f"TP-{uuid.uuid4().hex[:12]}")
    title: str
    description: Optional[str] = None
    
    # Content
    scenario_ids: List[str] = Field(default_factory=list)
    teaching_step_ids: List[str] = Field(default_factory=list)
    cluster_id: Optional[str] = None
    
    # Organization
    tags: List[str] = Field(default_factory=list)
    difficulty_level: Optional[str] = None  # "beginner", "intermediate", "advanced"
    estimated_duration_minutes: int = 60
    
    # Analytics
    completion_count: int = 0
    average_score: float = 0.0
    student_feedback: List[str] = Field(default_factory=list)
    
    # Resources
    dhamma_refs: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "teaching_packs"
        indexes = [
            IndexModel([("tags", ASCENDING)]),
            IndexModel([("cluster_id", ASCENDING)]),
            IndexModel([("difficulty_level", ASCENDING)]),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }
