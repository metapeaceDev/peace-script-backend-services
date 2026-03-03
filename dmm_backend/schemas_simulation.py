"""
Peace Script V.14 - Simulation System Pydantic Schemas
API request/response models for scenarios, chains, clusters, teaching, QA
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =====================================================================
# Response Schemas (used by routers)
# =====================================================================

class ScenarioResponse(BaseModel):
    """Response schema for Scenario"""
    scenario_id: str
    title: str
    description: Optional[str] = None
    status: str
    model_id: Optional[str] = None
    cluster_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    event_ids: List[str] = Field(default_factory=list)
    chain_ids: List[str] = Field(default_factory=list)
    qa_test_case_ids: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    meta_info: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    """Response schema for EnhancedSimulationEvent"""
    event_id: str
    scenario_id: Optional[str] = None
    type: str
    title: str
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    parent_event_id: Optional[str] = None
    child_event_ids: List[str] = Field(default_factory=list)
    chain_id: Optional[str] = None
    intensity: float = 0.5
    karma_impact: Optional[float] = None
    emotion_score: Optional[float] = None
    health_delta: Optional[float] = None
    annotation: Optional[str] = None
    teaching_note: Optional[str] = None
    dhamma_ref: Optional[str] = None
    ai_insight: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"from_attributes": True}


class ChainResponse(BaseModel):
    """Response schema for SimulationChain"""
    chain_id: str
    scenario_id: Optional[str] = None
    event_ids: List[str] = Field(default_factory=list)
    parent_chain_id: Optional[str] = None
    child_chain_ids: List[str] = Field(default_factory=list)
    branch_point_event_id: Optional[str] = None
    status: str
    chain_health: float = 0.5
    karma_total: float = 0.0
    emotion_curve: List[float] = Field(default_factory=list)
    health_curve: List[float] = Field(default_factory=list)
    is_what_if_branch: bool = False
    what_if_condition: Optional[str] = None
    alternative_chains: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class ClusterResponse(BaseModel):
    """Response schema for SimulationCluster"""
    cluster_id: str
    title: str
    description: Optional[str] = None
    scenario_ids: List[str] = Field(default_factory=list)
    chain_ids: List[str] = Field(default_factory=list)
    aggregate_karma: float = 0.0
    aggregate_health: float = 0.0
    emotion_avg: float = 0.0
    outcome_distribution: Dict[str, Any] = Field(default_factory=dict)
    teaching_pack_id: Optional[str] = None
    dhamma_themes: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class TeachingStepResponse(BaseModel):
    """Response schema for TeachingStep"""
    step_id: str
    scenario_id: Optional[str] = None
    event_id: Optional[str] = None
    teaching_pack_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    dhamma_explain: Optional[str] = None
    ai_question: Optional[str] = None
    quiz_options: List[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    step_number: int = 1
    parent_step_id: Optional[str] = None
    next_step_ids: List[str] = Field(default_factory=list)
    is_branch_point: bool = False
    student_notes: List[str] = Field(default_factory=list)
    quiz_results: List[Dict] = Field(default_factory=list)
    completion_rate: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class QATestCaseResponse(BaseModel):
    """Response schema for QATestCase"""
    test_case_id: str
    scenario_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    expected_outcome: Dict[str, Any]
    actual_outcome: Optional[Dict[str, Any]] = None
    conditions: Dict[str, Any] = Field(default_factory=dict)
    status: str
    test_runs: List[Dict] = Field(default_factory=list)
    pass_rate: float = 0.0
    severity: Optional[str] = None
    is_automated: bool = False
    regression_diff: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class TeachingPackResponse(BaseModel):
    """Response schema for TeachingPack"""
    pack_id: str
    title: str
    scenario_ids: List[str] = Field(default_factory=list)
    teaching_step_ids: List[str] = Field(default_factory=list)
    cluster_id: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_duration_minutes: int = 30
    completion_count: int = 0
    average_score: float = 0.0
    student_feedback: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):
    """Response schema for analytics"""
    scenario_id: str
    karma_trend: List[float] = Field(default_factory=list)
    health_trend: List[float] = Field(default_factory=list)
    emotion_trend: List[float] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)


class ChainHealthResponse(BaseModel):
    """Response schema for chain health analytics"""
    chain_id: str
    chain_health: float
    karma_total: float
    emotion_curve: List[float] = Field(default_factory=list)
    health_curve: List[float] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)


class ClusterAnalyticsResponse(BaseModel):
    """Response schema for cluster analytics"""
    cluster_id: str
    aggregate_karma: float
    aggregate_health: float
    emotion_avg: float
    outcome_distribution: Dict[str, Any]
    comparison_matrix: Dict[str, Any]
    insights: List[str] = Field(default_factory=list)


class ExportResponse(BaseModel):
    """Response schema for export operations"""
    export_url: str
    filename: str
    format: str
    generated_at: datetime


class BatchRunResponse(BaseModel):
    """Response schema for batch run"""
    scenarios: List[ScenarioResponse]
    comparison_matrix: Optional[Dict[str, Any]] = None
    analytics: Optional[Dict[str, Any]] = None


class WhatIfBranchResponse(BaseModel):
    """Response schema for what-if branching"""
    original_chain: ChainResponse
    branched_chain: ChainResponse
    comparison: Dict[str, Any]


class CompareChainsResponse(BaseModel):
    """Response schema for chain comparison"""
    chains: List[ChainResponse]
    comparison_matrix: Dict[str, Any]
    insights: List[str] = Field(default_factory=list)


class TeachingQAGenerateResponse(BaseModel):
    """Response schema for AI-generated teaching Q&A"""
    step_id: str
    ai_question: str
    quiz_options: List[str]
    correct_answer: str
    explanation: str


class TeachingQuizResult(BaseModel):
    """Response schema for quiz submission"""
    step_id: str
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    score: float


class QARunTestResponse(BaseModel):
    """Response schema for QA test run"""
    test_case_id: str
    passed: bool
    actual_outcome: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    details: List[str] = Field(default_factory=list)


class QARegressionResponse(BaseModel):
    """Response schema for regression analysis"""
    test_case_id: str
    has_regression: bool
    regression_diff: Optional[Dict[str, Any]] = None
    test_runs_count: int
    pass_rate: float
    insights: List[str] = Field(default_factory=list)


class QABatchRegressionResponse(BaseModel):
    """Response schema for batch regression"""
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]


class EventAnnotateRequest(BaseModel):
    """Request schema for event annotation"""
    annotation: Optional[str] = None
    teaching_note: Optional[str] = None
    dhamma_ref: Optional[str] = None
    ai_insight: Optional[str] = None


# =====================================================================
# Request Schemas
# =====================================================================

class ScenarioCreate(BaseModel):
    """Request schema for creating a scenario"""
    model_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    status: Optional[str] = "draft"
    cluster_id: Optional[str] = None
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class ScenarioUpdate(BaseModel):
    """Request schema for updating a scenario"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    event_ids: Optional[List[str]] = None
    chain_ids: Optional[List[str]] = None
    cluster_id: Optional[str] = None
    qa_test_case_ids: Optional[List[str]] = None
    meta_info: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class ScenarioCloneRequest(BaseModel):
    """Request schema for cloning a scenario"""
    new_title: Optional[str] = None
    new_description: Optional[str] = None
    include_events: bool = True
    include_chains: bool = True
    what_if_condition: Optional[str] = None


class BatchRunRequest(BaseModel):
    """Request schema for batch scenario runs"""
    scenario_ids: List[str]
    compare_outcomes: bool = True
    generate_analytics: bool = True


class EventCreate(BaseModel):
    """Request schema for creating a simulation event"""
    scenario_id: str
    type: str
    title: str
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    parent_event_id: Optional[str] = None
    chain_id: Optional[str] = None
    intensity: Optional[float] = 0.5
    karma_impact: Optional[float] = None
    emotion_score: Optional[float] = None
    health_delta: Optional[float] = None
    annotation: Optional[str] = None
    teaching_note: Optional[str] = None
    dhamma_ref: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventUpdate(BaseModel):
    """Request schema for updating an event"""
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    timestamp: Optional[datetime] = None
    parent_event_id: Optional[str] = None
    chain_id: Optional[str] = None
    intensity: Optional[float] = None
    karma_impact: Optional[float] = None
    emotion_score: Optional[float] = None
    health_delta: Optional[float] = None
    annotation: Optional[str] = None
    teaching_note: Optional[str] = None
    dhamma_ref: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class ChainCreate(BaseModel):
    """Request schema for creating a simulation chain"""
    scenario_id: Optional[str] = None
    event_ids: List[str] = Field(default_factory=list)
    parent_chain_id: Optional[str] = None
    branch_point_event_id: Optional[str] = None
    status: Optional[str] = "active"
    is_what_if_branch: Optional[bool] = False
    what_if_condition: Optional[str] = None
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class ChainUpdate(BaseModel):
    """Request schema for updating a chain"""
    event_ids: Optional[List[str]] = None
    status: Optional[str] = None
    chain_health: Optional[float] = None
    karma_total: Optional[float] = None
    meta_info: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class WhatIfBranchRequest(BaseModel):
    """Request schema for creating what-if branch"""
    branch_point_event_id: str
    alternative_events: List[Dict[str, Any]] = Field(default_factory=list)
    what_if_condition: str


class CompareChainsRequest(BaseModel):
    """Request schema for comparing chains"""
    chain_ids: List[str]


class ClusterCreate(BaseModel):
    """Request schema for creating a cluster"""
    title: str
    description: Optional[str] = None
    scenario_ids: List[str] = Field(default_factory=list)
    chain_ids: List[str] = Field(default_factory=list)
    teaching_pack_id: Optional[str] = None
    dhamma_themes: List[str] = Field(default_factory=list)
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class ClusterUpdate(BaseModel):
    """Request schema for updating a cluster"""
    title: Optional[str] = None
    description: Optional[str] = None
    scenario_ids: Optional[List[str]] = None
    chain_ids: Optional[List[str]] = None
    teaching_pack_id: Optional[str] = None
    dhamma_themes: Optional[List[str]] = None
    meta_info: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class TeachingStepCreate(BaseModel):
    """Request schema for creating a teaching step"""
    scenario_id: Optional[str] = None
    event_id: Optional[str] = None
    teaching_pack_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    dhamma_explain: Optional[str] = None
    ai_question: Optional[str] = None
    quiz_options: List[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    step_number: int = 1
    parent_step_id: Optional[str] = None
    is_branch_point: bool = False
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class TeachingStepUpdate(BaseModel):
    """Request schema for updating a teaching step"""
    title: Optional[str] = None
    description: Optional[str] = None
    dhamma_explain: Optional[str] = None
    ai_question: Optional[str] = None
    quiz_options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    step_number: Optional[int] = None
    meta_info: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class TeachingQAGenerateRequest(BaseModel):
    """Request schema for generating AI Q&A"""
    difficulty: str = "medium"
    language: str = "th"


class TeachingQuizSubmit(BaseModel):
    """Request schema for quiz submission"""
    student_id: str
    student_answer: str


class QATestCaseCreate(BaseModel):
    """Request schema for creating a QA test case"""
    scenario_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    expected_outcome: Dict[str, Any]
    conditions: Dict[str, Any] = Field(default_factory=dict)
    severity: Optional[str] = "medium"
    is_automated: bool = False
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class QATestCaseUpdate(BaseModel):
    """Request schema for updating a QA test case"""
    title: Optional[str] = None
    description: Optional[str] = None
    expected_outcome: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    is_automated: Optional[bool] = None
    meta_info: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class QARunTestRequest(BaseModel):
    """Request schema for running a QA test"""
    custom_conditions: Dict[str, Any] = Field(default_factory=dict)


class QABatchRegressionRequest(BaseModel):
    """Request schema for batch regression testing"""
    test_case_ids: List[str]
    scenario_id: Optional[str] = None


class ExportRequest(BaseModel):
    """Request schema for export operations"""
    format: str = "json"  # json, csv, pdf
    include_analytics: bool = True
    include_scenarios: bool = True
    include_events: bool = True
    include_chains: bool = False
    meta_log: Dict[str, Any] = Field(default_factory=dict)


class ChainUpdate(BaseModel):
    """Request schema for updating a chain"""
    event_ids: Optional[List[str]] = None
    child_chain_ids: Optional[List[str]] = None
    status: Optional[str] = None
    chain_health: Optional[float] = None
    karma_total: Optional[float] = None
    emotion_curve: Optional[List[float]] = None
    health_curve: Optional[List[float]] = None
    qa_flags: Optional[List[str]] = None
    dhamma_insights: Optional[List[str]] = None
    alternative_chains: Optional[List[str]] = None
    meta_log: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class ClusterCreate(BaseModel):
    """Request schema for creating a simulation cluster"""
    title: str
    description: Optional[str] = None
    scenario_ids: List[str] = Field(default_factory=list)
    chain_ids: List[str] = Field(default_factory=list)
    model_ids: List[str] = Field(default_factory=list)
    cluster_tags: List[str] = Field(default_factory=list)
    dhamma_themes: List[str] = Field(default_factory=list)
    meta_log: Dict[str, Any] = Field(default_factory=dict)


class ClusterUpdate(BaseModel):
    """Request schema for updating a cluster"""
    title: Optional[str] = None
    description: Optional[str] = None
    scenario_ids: Optional[List[str]] = None
    chain_ids: Optional[List[str]] = None
    model_ids: Optional[List[str]] = None
    cluster_tags: Optional[List[str]] = None
    research_notes: Optional[List[str]] = None
    teaching_pack_id: Optional[str] = None
    dhamma_themes: Optional[List[str]] = None
    aggregate_karma: Optional[float] = None
    aggregate_health: Optional[float] = None
    emotion_avg: Optional[float] = None
    outcome_distribution: Optional[Dict[str, int]] = None
    meta_log: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class TeachingStepCreate(BaseModel):
    """Request schema for creating a teaching step"""
    scenario_id: Optional[str] = None
    event_id: Optional[str] = None
    chain_id: Optional[str] = None
    teaching_pack_id: Optional[str] = None
    title: str
    description: str
    dhamma_explain: Optional[str] = None
    ai_question: Optional[str] = None
    quiz_options: List[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    step_number: int = 0
    parent_step_id: Optional[str] = None
    is_branch_point: bool = False
    references: List[str] = Field(default_factory=list)
    dhamma_refs: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class TeachingStepUpdate(BaseModel):
    """Request schema for updating a teaching step"""
    title: Optional[str] = None
    description: Optional[str] = None
    dhamma_explain: Optional[str] = None
    ai_question: Optional[str] = None
    quiz_options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    step_number: Optional[int] = None
    next_step_ids: Optional[List[str]] = None
    student_notes: Optional[List[str]] = None
    quiz_results: Optional[List[Dict[str, Any]]] = None
    feedback: Optional[str] = None
    completion_rate: Optional[float] = None
    references: Optional[List[str]] = None
    dhamma_refs: Optional[List[str]] = None
    related_events: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class QATestCaseCreate(BaseModel):
    """Request schema for creating a QA test case"""
    scenario_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    expected_outcome: Dict[str, Any] = Field(default_factory=dict)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    test_tags: List[str] = Field(default_factory=list)
    severity: Optional[str] = None
    is_automated: bool = False
    automation_script: Optional[str] = None
    meta_log: Dict[str, Any] = Field(default_factory=dict)


class QATestCaseUpdate(BaseModel):
    """Request schema for updating a QA test case"""
    title: Optional[str] = None
    description: Optional[str] = None
    expected_outcome: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    test_tags: Optional[List[str]] = None
    status: Optional[str] = None
    actual_outcome: Optional[Dict[str, Any]] = None
    regression_diff: Optional[Dict[str, Any]] = None
    annotations: Optional[List[str]] = None
    qa_flags: Optional[List[str]] = None
    severity: Optional[str] = None
    is_automated: Optional[bool] = None
    automation_script: Optional[str] = None
    meta_log: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


class TeachingPackCreate(BaseModel):
    """Request schema for creating a teaching pack"""
    title: str
    description: Optional[str] = None
    scenario_ids: List[str] = Field(default_factory=list)
    teaching_step_ids: List[str] = Field(default_factory=list)
    cluster_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    difficulty_level: Optional[str] = None
    estimated_duration_minutes: int = 60
    dhamma_refs: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class TeachingPackUpdate(BaseModel):
    """Request schema for updating a teaching pack"""
    title: Optional[str] = None
    description: Optional[str] = None
    scenario_ids: Optional[List[str]] = None
    teaching_step_ids: Optional[List[str]] = None
    cluster_id: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    student_feedback: Optional[List[str]] = None
    dhamma_refs: Optional[List[str]] = None
    references: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None
    
    model_config = {"extra": "ignore"}


# =====================================================================
# Operation Request Schemas
# =====================================================================

class BatchRunRequest(BaseModel):
    """Request schema for batch running scenarios"""
    scenario_ids: List[str]
    run_config: Dict[str, Any] = Field(default_factory=dict)
    compare_outcomes: bool = True
    generate_analytics: bool = True


class BatchRunResponse(BaseModel):
    """Response schema for batch run results"""
    batch_id: str
    scenario_count: int
    results: List[Dict[str, Any]]
    comparison_matrix: Dict[str, Any] = Field(default_factory=dict)
    aggregate_analytics: Dict[str, Any] = Field(default_factory=dict)
    status: str


class WhatIfBranchRequest(BaseModel):
    """Request schema for creating what-if branch"""
    source_chain_id: str
    branch_point_event_id: str
    what_if_condition: str
    alternative_events: List[Dict[str, Any]] = Field(default_factory=list)
    run_simulation: bool = True


class WhatIfBranchResponse(BaseModel):
    """Response schema for what-if branch"""
    branch_chain_id: str
    source_chain_id: str
    branch_point_event_id: str
    what_if_condition: str
    outcome_diff: Dict[str, Any] = Field(default_factory=dict)
    karma_diff: float = 0.0
    health_diff: float = 0.0
    status: str


class CompareScenarios(BaseModel):
    """Request schema for comparing scenarios"""
    scenario_ids: List[str]
    compare_fields: List[str] = ["karma_total", "health_score", "emotion_avg", "event_count"]


class CompareResult(BaseModel):
    """Response schema for scenario comparison"""
    scenario_id: str
    metrics: Dict[str, Any]


class CompareScenariosResponse(BaseModel):
    """Response schema for comparing scenarios"""
    comparison_matrix: Dict[str, List[CompareResult]]
    winner_scenario_id: Optional[str] = None
    insights: List[str] = Field(default_factory=list)


class ExportRequest(BaseModel):
    """Request schema for export operations"""
    export_format: str = "json"  # json, csv, pdf
    include_analytics: bool = True
    include_events: bool = True
    include_chains: bool = False
    include_teaching: bool = False
    include_qa: bool = False


class AIInsightRequest(BaseModel):
    """Request schema for AI insight generation"""
    event_id: Optional[str] = None
    chain_id: Optional[str] = None
    scenario_id: Optional[str] = None
    insight_type: str = "general"  # general, dhamma, karma, health, teaching


class AIInsightResponse(BaseModel):
    """Response schema for AI insights"""
    insight: str
    dhamma_refs: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    confidence: float = 0.5


class TeachingQAGenerateRequest(BaseModel):
    """Request schema for generating teaching Q&A"""
    teaching_step_id: Optional[str] = None
    event_id: Optional[str] = None
    qa_count: int = 5
    difficulty: str = "medium"  # easy, medium, hard


class TeachingQAGenerateResponse(BaseModel):
    """Response schema for generated teaching Q&A"""
    questions: List[Dict[str, Any]]
    dhamma_insights: List[str] = Field(default_factory=list)


class QARunTestRequest(BaseModel):
    """Request schema for running QA test"""
    test_case_id: str
    run_config: Dict[str, Any] = Field(default_factory=dict)
    save_results: bool = True


class QARunTestResponse(BaseModel):
    """Response schema for QA test run"""
    run_id: str
    test_case_id: str
    status: str
    expected: Dict[str, Any]
    actual: Dict[str, Any]
    diff: Dict[str, Any]
    passed: bool
    notes: Optional[str] = None
