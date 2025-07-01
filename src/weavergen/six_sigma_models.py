"""
Pydantic Models for Design for Lean Six Sigma DMEDI Training

This module contains comprehensive data models for all phases of the DMEDI methodology:
- Define: Charter, MGPP, Risk Management, Communication Plan
- Measure: VOC, QFD, Target Costing, Scorecards, Statistics
- Explore: Concept Generation, TRIZ, DOE, Statistical Analysis
- Develop: Detailed Design, Advanced DOE, Lean Integration
- Implement: Prototyping, Process Control, Implementation
"""

from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, validator
import uuid


# Enums for controlled vocabularies
class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PhaseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REWORK = "needs_rework"


class CustomerPriority(str, Enum):
    BASIC = "basic"
    PERFORMANCE = "performance"
    EXCITEMENT = "excitement"


class DOEType(str, Enum):
    FULL_FACTORIAL = "full_factorial"
    FRACTIONAL_FACTORIAL = "fractional_factorial"
    CENTRAL_COMPOSITE = "central_composite"
    BOX_BEHNKEN = "box_behnken"
    MIXTURE = "mixture"
    TAGUCHI = "taguchi"


class DistributionType(str, Enum):
    NORMAL = "normal"
    UNIFORM = "uniform"
    EXPONENTIAL = "exponential"
    WEIBULL = "weibull"
    POISSON = "poisson"


# ================================
# DEFINE PHASE MODELS
# ================================

class Stakeholder(BaseModel):
    """Individual stakeholder in the project"""
    name: str = Field(..., description="Stakeholder name")
    role: str = Field(..., description="Organizational role")
    department: str = Field(..., description="Department or function")
    influence: str = Field(..., description="High, Medium, Low")
    interest: str = Field(..., description="High, Medium, Low")
    responsibility: List[str] = Field(default_factory=list, description="RACI responsibilities")
    contact_info: str = Field(default="", description="Contact information")


class ProjectCharter(BaseModel):
    """Six Sigma project charter with all required elements"""
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str = Field(..., description="Project title")
    
    # Business case
    business_case: str = Field(..., description="Business justification")
    problem_statement: str = Field(..., description="Clear problem definition")
    goal_statement: str = Field(..., description="Project objectives")
    scope: Dict[str, List[str]] = Field(..., description="In-scope and out-of-scope items")
    
    # Financial impact
    expected_savings: float = Field(default=0.0, description="Expected annual savings")
    investment_required: float = Field(default=0.0, description="Required investment")
    roi_target: float = Field(default=0.0, description="Target ROI percentage")
    
    # Timeline
    start_date: date = Field(..., description="Project start date")
    target_completion: date = Field(..., description="Target completion date")
    milestones: List[Dict[str, Union[str, date]]] = Field(default_factory=list)
    
    # Team and stakeholders
    project_champion: str = Field(..., description="Executive sponsor")
    black_belt: str = Field(..., description="Black Belt lead")
    team_members: List[str] = Field(default_factory=list)
    stakeholders: List[Stakeholder] = Field(default_factory=list)
    
    # Success criteria
    success_metrics: List[str] = Field(default_factory=list)
    critical_success_factors: List[str] = Field(default_factory=list)
    
    # Approvals
    approved_by: Optional[str] = None
    approval_date: Optional[date] = None
    status: ProjectStatus = ProjectStatus.PLANNING


class MGPPAssessment(BaseModel):
    """Management Guided Problem and Project assessment"""
    project_id: str = Field(..., description="Reference to project charter")
    
    # Strategic alignment
    strategic_priority: str = Field(..., description="High, Medium, Low")
    business_unit_alignment: str = Field(..., description="Alignment with BU strategy")
    resource_availability: str = Field(..., description="Resource assessment")
    
    # Complexity assessment
    technical_complexity: str = Field(..., description="High, Medium, Low")
    organizational_complexity: str = Field(..., description="Change complexity")
    timeline_complexity: str = Field(..., description="Schedule risk")
    
    # Resource allocation
    black_belt_allocation: float = Field(..., description="% time allocation")
    team_size: int = Field(..., description="Core team size")
    budget_allocated: float = Field(default=0.0, description="Project budget")
    
    # Executive sponsorship
    sponsor_commitment: str = Field(..., description="Sponsor engagement level")
    steering_committee: List[str] = Field(default_factory=list)
    
    approval_status: bool = Field(default=False)
    assessment_date: date = Field(default_factory=date.today)


class RiskItem(BaseModel):
    """Individual risk item"""
    risk_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = Field(..., description="Risk description")
    category: str = Field(..., description="Risk category")
    probability: RiskLevel = Field(..., description="Likelihood of occurrence")
    impact: RiskLevel = Field(..., description="Impact if it occurs")
    
    mitigation_strategy: str = Field(default="", description="Risk mitigation plan")
    contingency_plan: str = Field(default="", description="Contingency if risk occurs")
    owner: str = Field(..., description="Risk owner")
    status: str = Field(default="open", description="Risk status")
    
    created_date: date = Field(default_factory=date.today)
    review_date: Optional[date] = None


class RiskManagementPlan(BaseModel):
    """Comprehensive risk management plan"""
    project_id: str = Field(..., description="Reference to project")
    
    risks: List[RiskItem] = Field(default_factory=list)
    risk_tolerance: str = Field(..., description="Organization risk tolerance")
    escalation_criteria: List[str] = Field(default_factory=list)
    review_frequency: str = Field(default="weekly", description="Risk review cadence")
    
    created_by: str = Field(..., description="Plan creator")
    created_date: date = Field(default_factory=date.today)
    last_updated: date = Field(default_factory=date.today)


class CommunicationPlan(BaseModel):
    """Project communication plan"""
    project_id: str = Field(..., description="Reference to project")
    
    # Communication matrix
    stakeholder_communications: List[Dict[str, str]] = Field(default_factory=list)
    reporting_schedule: Dict[str, str] = Field(default_factory=dict)
    escalation_process: List[str] = Field(default_factory=list)
    
    # Channels and methods
    primary_channels: List[str] = Field(default_factory=list)
    meeting_cadence: str = Field(default="weekly")
    dashboard_location: str = Field(default="")
    
    # Change management
    change_communication_strategy: str = Field(default="")
    training_plan: List[str] = Field(default_factory=list)
    
    plan_owner: str = Field(..., description="Communication plan owner")
    created_date: date = Field(default_factory=date.today)


# ================================
# MEASURE PHASE MODELS
# ================================

class CustomerRequirement(BaseModel):
    """Voice of Customer requirement"""
    requirement_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_voice: str = Field(..., description="Customer's actual words")
    interpreted_need: str = Field(..., description="Translated requirement")
    
    priority: CustomerPriority = Field(..., description="Kano model classification")
    importance_rating: float = Field(..., ge=1, le=10, description="1-10 importance")
    satisfaction_rating: float = Field(..., ge=1, le=10, description="Current satisfaction")
    
    ctq_elements: List[str] = Field(default_factory=list, description="Critical to Quality")
    measurement_approach: str = Field(default="", description="How to measure")
    
    source: str = Field(..., description="Customer segment or individual")
    collection_method: str = Field(..., description="Interview, survey, observation")
    collected_date: date = Field(default_factory=date.today)


class VOCAnalysis(BaseModel):
    """Voice of Customer analysis and summary"""
    project_id: str = Field(..., description="Reference to project")
    
    customer_segments: List[str] = Field(default_factory=list)
    requirements: List[CustomerRequirement] = Field(default_factory=list)
    
    # Analysis results
    top_priorities: List[str] = Field(default_factory=list)
    satisfaction_gaps: List[Dict[str, float]] = Field(default_factory=list)
    ctq_characteristics: List[str] = Field(default_factory=list)
    
    # Collection metadata
    sample_size: int = Field(default=0)
    collection_methods: List[str] = Field(default_factory=list)
    collection_period: str = Field(default="")
    
    analysis_date: date = Field(default_factory=date.today)
    analyst: str = Field(..., description="Who performed the analysis")


class QFDRelationship(BaseModel):
    """Relationship between customer requirement and engineering characteristic"""
    customer_requirement_id: str = Field(..., description="Customer requirement ID")
    engineering_characteristic: str = Field(..., description="Engineering feature")
    relationship_strength: int = Field(..., ge=0, le=9, description="0=None, 1=Weak, 3=Medium, 9=Strong")
    
    target_value: Optional[float] = None
    specification_limit_lower: Optional[float] = None
    specification_limit_upper: Optional[float] = None


class QFDMatrix(BaseModel):
    """Quality Function Deployment House of Quality"""
    project_id: str = Field(..., description="Reference to project")
    matrix_name: str = Field(..., description="QFD matrix name")
    
    # Customer requirements (WHATs)
    customer_requirements: List[CustomerRequirement] = Field(default_factory=list)
    
    # Engineering characteristics (HOWs)
    engineering_characteristics: List[str] = Field(default_factory=list)
    
    # Relationship matrix
    relationships: List[QFDRelationship] = Field(default_factory=list)
    
    # Correlation matrix (roof)
    characteristic_correlations: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    
    # Competitive analysis
    competitive_benchmarks: Dict[str, List[float]] = Field(default_factory=dict)
    
    # Targets and priorities
    engineering_targets: Dict[str, float] = Field(default_factory=dict)
    characteristic_priorities: Dict[str, float] = Field(default_factory=dict)
    
    created_by: str = Field(..., description="QFD creator")
    created_date: date = Field(default_factory=date.today)


class TargetCost(BaseModel):
    """Target costing analysis"""
    project_id: str = Field(..., description="Reference to project")
    product_name: str = Field(..., description="Product or service name")
    
    # Market analysis
    target_market_price: float = Field(..., description="Market-acceptable price")
    target_profit_margin: float = Field(..., description="Required profit margin %")
    target_cost: float = Field(..., description="Calculated target cost")
    
    # Current cost breakdown
    current_costs: Dict[str, float] = Field(default_factory=dict)
    current_total_cost: float = Field(default=0.0)
    cost_gap: float = Field(default=0.0, description="Current vs target cost gap")
    
    # Value engineering opportunities
    cost_reduction_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    value_improvement_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Implementation plan
    cost_reduction_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    risk_assessment: str = Field(default="")
    
    analysis_date: date = Field(default_factory=date.today)
    analyst: str = Field(..., description="Cost analyst")


class KPI(BaseModel):
    """Key Performance Indicator definition"""
    kpi_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = Field(..., description="KPI name")
    description: str = Field(..., description="What it measures")
    
    # Measurement details
    formula: str = Field(..., description="Calculation method")
    data_source: str = Field(..., description="Where data comes from")
    frequency: str = Field(..., description="Measurement frequency")
    
    # Targets and thresholds
    target_value: float = Field(..., description="Target performance")
    upper_specification_limit: Optional[float] = None
    lower_specification_limit: Optional[float] = None
    
    # Responsibility
    owner: str = Field(..., description="KPI owner")
    data_collector: str = Field(..., description="Who collects data")
    
    # Current performance
    baseline_value: Optional[float] = None
    current_value: Optional[float] = None
    last_measured: Optional[date] = None


class BalancedScorecard(BaseModel):
    """Balanced scorecard for project tracking"""
    project_id: str = Field(..., description="Reference to project")
    scorecard_name: str = Field(..., description="Scorecard identifier")
    
    # Four perspectives
    financial_kpis: List[KPI] = Field(default_factory=list)
    customer_kpis: List[KPI] = Field(default_factory=list)
    process_kpis: List[KPI] = Field(default_factory=list)
    learning_growth_kpis: List[KPI] = Field(default_factory=list)
    
    # Overall performance
    overall_score: Optional[float] = Field(None, ge=0, le=100)
    performance_trend: str = Field(default="stable")  # improving, declining, stable
    
    # Reviews
    review_frequency: str = Field(default="monthly")
    last_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    
    created_by: str = Field(..., description="Scorecard creator")
    created_date: date = Field(default_factory=date.today)


class StatisticalTest(BaseModel):
    """Statistical test results"""
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    test_name: str = Field(..., description="Type of statistical test")
    test_purpose: str = Field(..., description="What the test is checking")
    
    # Test parameters
    significance_level: float = Field(default=0.05, description="Alpha level")
    power: float = Field(default=0.8, description="Statistical power")
    sample_size: int = Field(..., description="Sample size used")
    
    # Results
    test_statistic: float = Field(..., description="Calculated test statistic")
    p_value: float = Field(..., description="P-value")
    confidence_interval: Optional[Dict[str, float]] = None
    
    # Conclusions
    null_hypothesis: str = Field(..., description="H0 statement")
    alternative_hypothesis: str = Field(..., description="H1 statement")
    conclusion: str = Field(..., description="Test conclusion")
    practical_significance: str = Field(default="", description="Practical implications")
    
    # Metadata
    data_source: str = Field(..., description="Source of data")
    software_used: str = Field(default="Minitab", description="Analysis software")
    analyst: str = Field(..., description="Who performed the test")
    test_date: date = Field(default_factory=date.today)


class ProcessCapabilityStudy(BaseModel):
    """Process capability analysis results"""
    study_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    process_name: str = Field(..., description="Process being studied")
    characteristic: str = Field(..., description="Quality characteristic")
    
    # Specification limits
    lower_spec_limit: Optional[float] = None
    upper_spec_limit: Optional[float] = None
    target_value: Optional[float] = None
    
    # Sample data summary
    sample_size: int = Field(..., description="Number of measurements")
    mean: float = Field(..., description="Process mean")
    standard_deviation: float = Field(..., description="Process standard deviation")
    
    # Capability indices
    cp: Optional[float] = Field(None, description="Potential capability")
    cpk: Optional[float] = Field(None, description="Actual capability")
    pp: Optional[float] = Field(None, description="Process performance")
    ppk: Optional[float] = Field(None, description="Process performance index")
    
    # Distribution analysis
    distribution_type: DistributionType = Field(default=DistributionType.NORMAL)
    normality_test_p_value: Optional[float] = None
    
    # Performance metrics
    defect_rate_ppm: float = Field(default=0.0, description="Defects per million")
    sigma_level: float = Field(default=0.0, description="Sigma quality level")
    
    # Recommendations
    capability_assessment: str = Field(..., description="Overall capability assessment")
    improvement_recommendations: List[str] = Field(default_factory=list)
    
    study_date: date = Field(default_factory=date.today)
    analyst: str = Field(..., description="Capability analyst")


# ================================
# EXPLORE PHASE MODELS
# ================================

class ConceptIdea(BaseModel):
    """Individual concept or idea"""
    idea_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = Field(..., description="Concept title")
    description: str = Field(..., description="Detailed description")
    
    # Generation details
    generation_method: str = Field(..., description="How it was generated")
    contributor: str = Field(..., description="Who contributed it")
    session_id: str = Field(..., description="Brainstorming session ID")
    
    # Evaluation
    feasibility_score: Optional[float] = Field(None, ge=1, le=10)
    novelty_score: Optional[float] = Field(None, ge=1, le=10)
    value_score: Optional[float] = Field(None, ge=1, le=10)
    
    # Development status
    selected_for_development: bool = Field(default=False)
    development_notes: str = Field(default="")
    
    created_date: date = Field(default_factory=date.today)


class ConceptGenerationSession(BaseModel):
    """Concept generation session results"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    session_name: str = Field(..., description="Session identifier")
    
    # Session details
    method_used: str = Field(..., description="Brainstorming method")
    participants: List[str] = Field(default_factory=list)
    duration_minutes: int = Field(..., description="Session duration")
    
    # Results
    concepts_generated: List[ConceptIdea] = Field(default_factory=list)
    total_ideas: int = Field(default=0)
    unique_ideas: int = Field(default=0)
    
    # Quality metrics
    idea_diversity_score: Optional[float] = Field(None, ge=0, le=1)
    participant_satisfaction: Optional[float] = Field(None, ge=1, le=10)
    
    facilitator: str = Field(..., description="Session facilitator")
    session_date: date = Field(default_factory=date.today)


class TRIZPrinciple(BaseModel):
    """TRIZ inventive principle application"""
    principle_number: int = Field(..., ge=1, le=40, description="TRIZ principle number")
    principle_name: str = Field(..., description="Principle name")
    description: str = Field(..., description="Principle description")
    
    # Application to problem
    problem_context: str = Field(..., description="Specific problem context")
    contradiction_type: str = Field(..., description="Type of contradiction")
    application_idea: str = Field(..., description="How to apply this principle")
    
    # Evaluation
    applicability_score: float = Field(..., ge=1, le=10)
    implementation_difficulty: str = Field(..., description="Easy, Medium, Hard")
    potential_impact: str = Field(..., description="Low, Medium, High")
    
    analyst: str = Field(..., description="TRIZ analyst")
    analysis_date: date = Field(default_factory=date.today)


class TRIZAnalysis(BaseModel):
    """Complete TRIZ analysis for a problem"""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    
    # Problem definition
    problem_statement: str = Field(..., description="Clear problem statement")
    contradiction_matrix_position: Optional[str] = None
    improving_parameter: str = Field(default="")
    worsening_parameter: str = Field(default="")
    
    # Analysis results
    applicable_principles: List[TRIZPrinciple] = Field(default_factory=list)
    recommended_solutions: List[str] = Field(default_factory=list)
    
    # Innovation assessment
    inventive_level: int = Field(..., ge=1, le=5, description="Innovation level 1-5")
    solution_novelty: str = Field(..., description="Incremental, Significant, Breakthrough")
    
    analyst: str = Field(..., description="TRIZ expert")
    analysis_date: date = Field(default_factory=date.today)


class PughMatrixCriterion(BaseModel):
    """Pugh matrix evaluation criterion"""
    criterion_name: str = Field(..., description="Evaluation criterion")
    weight: float = Field(default=1.0, ge=0, le=10, description="Criterion weight")
    description: str = Field(default="", description="Criterion description")


class PughMatrixEvaluation(BaseModel):
    """Pugh matrix concept evaluation"""
    concept_id: str = Field(..., description="Concept being evaluated")
    criterion_scores: Dict[str, int] = Field(..., description="Scores vs baseline")  # +1, 0, -1
    
    total_positives: int = Field(default=0)
    total_negatives: int = Field(default=0)
    total_zeros: int = Field(default=0)
    weighted_score: float = Field(default=0.0)


class PughMatrix(BaseModel):
    """Pugh concept selection matrix"""
    matrix_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    
    # Matrix setup
    baseline_concept: str = Field(..., description="Baseline concept for comparison")
    evaluation_criteria: List[PughMatrixCriterion] = Field(default_factory=list)
    
    # Evaluations
    concept_evaluations: List[PughMatrixEvaluation] = Field(default_factory=list)
    
    # Results
    top_concepts: List[str] = Field(default_factory=list)
    selected_concept: Optional[str] = None
    selection_rationale: str = Field(default="")
    
    # Process
    evaluation_team: List[str] = Field(default_factory=list)
    evaluation_date: date = Field(default_factory=date.today)
    facilitator: str = Field(..., description="Matrix facilitator")


class ExperimentalFactor(BaseModel):
    """Factor in experimental design"""
    factor_name: str = Field(..., description="Factor name")
    factor_type: str = Field(..., description="Continuous, Discrete, Categorical")
    
    # Levels
    low_level: Union[float, str] = Field(..., description="Low level setting")
    high_level: Union[float, str] = Field(..., description="High level setting")
    center_point: Optional[Union[float, str]] = None
    
    # Constraints
    controllable: bool = Field(default=True, description="Can be controlled")
    measurement_uncertainty: Optional[float] = None
    cost_to_change: str = Field(default="low", description="Low, Medium, High")


class ExperimentalResponse(BaseModel):
    """Response variable in experimental design"""
    response_name: str = Field(..., description="Response variable name")
    measurement_unit: str = Field(..., description="Units of measurement")
    
    # Target
    target_value: Optional[float] = None
    target_type: str = Field(default="target", description="target, minimize, maximize")
    
    # Measurement
    measurement_method: str = Field(..., description="How to measure")
    measurement_precision: Optional[float] = None
    cost_to_measure: str = Field(default="low", description="Low, Medium, High")


class ExperimentalRun(BaseModel):
    """Individual experimental run"""
    run_number: int = Field(..., description="Run sequence number")
    factor_settings: Dict[str, Union[float, str]] = Field(..., description="Factor levels")
    response_values: Dict[str, float] = Field(default_factory=dict, description="Measured responses")
    
    # Execution details
    run_date: Optional[date] = None
    operator: str = Field(default="", description="Who ran the experiment")
    notes: str = Field(default="", description="Run notes or issues")
    
    # Quality
    run_completed: bool = Field(default=False)
    data_quality: str = Field(default="good", description="good, questionable, bad")


class DOEDesign(BaseModel):
    """Design of Experiments specification"""
    design_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    design_name: str = Field(..., description="DOE name")
    
    # Design specification
    design_type: DOEType = Field(..., description="Type of experimental design")
    factors: List[ExperimentalFactor] = Field(default_factory=list)
    responses: List[ExperimentalResponse] = Field(default_factory=list)
    
    # Design parameters
    number_of_runs: int = Field(..., description="Total experimental runs")
    number_of_blocks: int = Field(default=1, description="Number of blocks")
    number_of_replicates: int = Field(default=1, description="Number of replicates")
    randomization_used: bool = Field(default=True)
    
    # Execution
    experimental_runs: List[ExperimentalRun] = Field(default_factory=list)
    
    # Analysis
    significant_factors: List[str] = Field(default_factory=list)
    optimal_settings: Dict[str, Union[float, str]] = Field(default_factory=dict)
    predicted_response: Dict[str, float] = Field(default_factory=dict)
    
    # Metadata
    designed_by: str = Field(..., description="Who designed the experiment")
    design_date: date = Field(default_factory=date.today)
    status: str = Field(default="planned", description="planned, running, completed, analyzed")


# ================================
# DEVELOP PHASE MODELS
# ================================

class DetailedDesignSpecification(BaseModel):
    """Detailed design specifications"""
    design_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    design_name: str = Field(..., description="Design specification name")
    
    # Design requirements
    functional_requirements: List[str] = Field(default_factory=list)
    performance_requirements: Dict[str, float] = Field(default_factory=dict)
    constraint_requirements: List[str] = Field(default_factory=list)
    
    # Design parameters
    design_parameters: Dict[str, float] = Field(default_factory=dict)
    material_specifications: List[str] = Field(default_factory=list)
    manufacturing_processes: List[str] = Field(default_factory=list)
    
    # Optimization results
    optimized_parameters: Dict[str, float] = Field(default_factory=dict)
    predicted_performance: Dict[str, float] = Field(default_factory=dict)
    design_margin: Dict[str, float] = Field(default_factory=dict)
    
    # Documentation
    design_drawings: List[str] = Field(default_factory=list)
    specifications: List[str] = Field(default_factory=list)
    test_protocols: List[str] = Field(default_factory=list)
    
    designer: str = Field(..., description="Lead designer")
    design_date: date = Field(default_factory=date.today)
    approval_status: str = Field(default="draft")


class RobustDesignAnalysis(BaseModel):
    """Robust design (Taguchi) analysis"""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    
    # Design factors
    control_factors: List[ExperimentalFactor] = Field(default_factory=list)
    noise_factors: List[ExperimentalFactor] = Field(default_factory=list)
    
    # Signal-to-noise ratios
    sn_ratios: Dict[str, float] = Field(default_factory=dict)
    quality_characteristic_type: str = Field(..., description="nominal-is-best, smaller-is-better, larger-is-better")
    
    # Optimization results
    optimal_control_settings: Dict[str, Union[float, str]] = Field(default_factory=dict)
    predicted_sn_ratio: float = Field(..., description="Predicted S/N ratio")
    robustness_improvement: float = Field(default=0.0, description="% improvement in robustness")
    
    # Validation
    confirmation_runs: List[ExperimentalRun] = Field(default_factory=list)
    actual_sn_ratio: Optional[float] = None
    prediction_accuracy: Optional[float] = None
    
    analyst: str = Field(..., description="Robust design analyst")
    analysis_date: date = Field(default_factory=date.today)


# ================================
# IMPLEMENT PHASE MODELS
# ================================

class PrototypeSpecification(BaseModel):
    """Prototype specification and results"""
    prototype_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    prototype_name: str = Field(..., description="Prototype identifier")
    
    # Prototype details
    prototype_type: str = Field(..., description="Concept, functional, production")
    build_specifications: Dict[str, Any] = Field(default_factory=dict)
    materials_used: List[str] = Field(default_factory=list)
    manufacturing_method: str = Field(..., description="How it was made")
    
    # Testing results
    test_results: Dict[str, float] = Field(default_factory=dict)
    performance_vs_target: Dict[str, float] = Field(default_factory=dict)
    issues_identified: List[str] = Field(default_factory=list)
    
    # Validation
    requirements_met: Dict[str, bool] = Field(default_factory=dict)
    overall_success: bool = Field(default=False)
    next_iteration_needed: bool = Field(default=False)
    
    # Metadata
    build_cost: float = Field(default=0.0)
    build_time_hours: float = Field(default=0.0)
    builder: str = Field(..., description="Who built the prototype")
    build_date: date = Field(default_factory=date.today)


class PilotStudy(BaseModel):
    """Pilot study design and results"""
    pilot_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    pilot_name: str = Field(..., description="Pilot study name")
    
    # Study design
    pilot_scope: str = Field(..., description="What's included in pilot")
    duration_weeks: int = Field(..., description="Pilot duration")
    sample_size: int = Field(..., description="Number of units/participants")
    
    # Success criteria
    success_metrics: List[str] = Field(default_factory=list)
    target_performance: Dict[str, float] = Field(default_factory=dict)
    
    # Results
    actual_performance: Dict[str, float] = Field(default_factory=dict)
    success_criteria_met: Dict[str, bool] = Field(default_factory=dict)
    lessons_learned: List[str] = Field(default_factory=list)
    
    # Scaling considerations
    scale_up_factors: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    pilot_manager: str = Field(..., description="Pilot study manager")
    start_date: date = Field(..., description="Pilot start date")
    completion_date: Optional[date] = None


class ControlPlan(BaseModel):
    """Process control plan"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    process_name: str = Field(..., description="Process being controlled")
    
    # Control points
    control_characteristics: List[str] = Field(default_factory=list)
    control_methods: Dict[str, str] = Field(default_factory=dict)
    measurement_frequency: Dict[str, str] = Field(default_factory=dict)
    
    # Specifications and targets
    specifications: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # LSL, USL, Target
    control_limits: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # UCL, LCL
    
    # Response plan
    out_of_control_actions: Dict[str, List[str]] = Field(default_factory=dict)
    escalation_procedures: List[str] = Field(default_factory=list)
    
    # Responsibilities
    process_owner: str = Field(..., description="Process owner")
    quality_contact: str = Field(..., description="Quality contact")
    operators: List[str] = Field(default_factory=list)
    
    # Implementation
    training_required: List[str] = Field(default_factory=list)
    documentation: List[str] = Field(default_factory=list)
    review_frequency: str = Field(default="monthly")
    
    created_by: str = Field(..., description="Control plan creator")
    created_date: date = Field(default_factory=date.today)
    approval_date: Optional[date] = None


class ImplementationPlan(BaseModel):
    """Full implementation plan"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = Field(..., description="Reference to project")
    
    # Rollout strategy
    implementation_approach: str = Field(..., description="Phased, big-bang, pilot-then-rollout")
    rollout_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    
    # Resources
    budget_required: float = Field(default=0.0)
    personnel_required: List[str] = Field(default_factory=list)
    equipment_needed: List[str] = Field(default_factory=list)
    
    # Change management
    stakeholder_impact: Dict[str, str] = Field(default_factory=dict)
    training_plan: List[Dict[str, Any]] = Field(default_factory=list)
    communication_plan: List[str] = Field(default_factory=list)
    
    # Risk mitigation
    implementation_risks: List[RiskItem] = Field(default_factory=list)
    contingency_plans: List[str] = Field(default_factory=list)
    
    # Monitoring
    progress_metrics: List[str] = Field(default_factory=list)
    review_checkpoints: List[date] = Field(default_factory=list)
    
    plan_manager: str = Field(..., description="Implementation manager")
    created_date: date = Field(default_factory=date.today)


# ================================
# CAPSTONE PROJECT MODEL
# ================================

class DMEDICapstoneProject(BaseModel):
    """Complete DMEDI capstone project"""
    capstone_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    student_name: str = Field(..., description="Black Belt candidate")
    project_title: str = Field(..., description="Capstone project title")
    
    # Project components
    charter: ProjectCharter
    mgpp_assessment: MGPPAssessment
    risk_plan: RiskManagementPlan
    communication_plan: CommunicationPlan
    
    voc_analysis: VOCAnalysis
    qfd_matrix: QFDMatrix
    target_costing: TargetCost
    scorecard: BalancedScorecard
    capability_study: ProcessCapabilityStudy
    
    concept_generation: ConceptGenerationSession
    triz_analysis: TRIZAnalysis
    concept_selection: PughMatrix
    doe_design: DOEDesign
    
    detailed_design: DetailedDesignSpecification
    robust_design: RobustDesignAnalysis
    
    prototype: PrototypeSpecification
    pilot_study: PilotStudy
    control_plan: ControlPlan
    implementation_plan: ImplementationPlan
    
    # Project outcomes
    financial_impact: Dict[str, float] = Field(default_factory=dict)
    quality_improvements: Dict[str, float] = Field(default_factory=dict)
    process_improvements: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
    
    # Certification
    presentation_date: Optional[date] = None
    certification_status: str = Field(default="in_progress")
    certification_date: Optional[date] = None
    
    # Evaluation
    evaluator_feedback: str = Field(default="")
    final_score: Optional[float] = Field(None, ge=0, le=100)
    
    start_date: date = Field(default_factory=date.today)
    completion_date: Optional[date] = None
    mentor: str = Field(..., description="Black Belt mentor/coach")


# ================================
# VALIDATION AND RELATIONSHIPS
# ================================

# Add custom validators
@validator('roi_target', 'expected_savings', 'investment_required')
def validate_financial_positive(cls, v):
    if v < 0:
        raise ValueError('Financial values must be positive')
    return v


# Helper functions for model creation
def create_sample_charter() -> ProjectCharter:
    """Create a sample project charter for testing"""
    return ProjectCharter(
        project_name="Reduce Order Processing Time",
        business_case="Customer complaints about long order processing times",
        problem_statement="Current order processing takes 5+ days, target is 2 days",
        goal_statement="Reduce order processing time by 60% within 6 months",
        scope={"in_scope": ["Order entry", "Credit check", "Inventory allocation"], 
               "out_of_scope": ["Shipping", "Billing"]},
        start_date=date.today(),
        target_completion=date(2024, 12, 31),
        project_champion="VP Operations",
        black_belt="John Smith"
    )


def create_sample_voc() -> VOCAnalysis:
    """Create sample VOC analysis"""
    requirements = [
        CustomerRequirement(
            customer_voice="I want my orders processed quickly",
            interpreted_need="Fast order processing",
            priority=CustomerPriority.PERFORMANCE,
            importance_rating=9.0,
            satisfaction_rating=4.0,
            source="Enterprise customers"
        )
    ]
    
    return VOCAnalysis(
        project_id="test-project",
        customer_segments=["Enterprise", "SMB", "Consumer"],
        requirements=requirements,
        analyst="Jane Doe"
    )


if __name__ == "__main__":
    # Test model creation
    charter = create_sample_charter()
    voc = create_sample_voc()
    
    print("✅ All Pydantic models created successfully!")
    print(f"Charter: {charter.project_name}")
    print(f"VOC Requirements: {len(voc.requirements)}")