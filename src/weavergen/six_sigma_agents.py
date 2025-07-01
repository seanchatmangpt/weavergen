"""
Six Sigma AI Agents for DMEDI Training

This module implements specialized AI agents for Design for Lean Six Sigma training
using Pydantic AI. Each agent has specific expertise and provides structured outputs
for different aspects of the DMEDI methodology.

Agents:
- BlackBeltTrainerAgent: Delivers training content and assessments
- MasterBlackBeltAgent: Provides advanced coaching and project guidance
- ChampionAgent: Focuses on strategic alignment and resource support
- DMEDICoachAgent: Specialized guidance through DMEDI phases
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
import json

try:
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models import Model
    import os
    
    # Check model availability in priority order
    if os.environ.get("OPENAI_API_KEY"):
        MODEL_NAME = "gpt-4o-mini"
        PYDANTIC_AI_AVAILABLE = True
    else:
        # Try qwen3 with ollama as fallback
        try:
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            if 'qwen2.5' in result.stdout:
                MODEL_NAME = "ollama:qwen2.5"
                PYDANTIC_AI_AVAILABLE = True
            elif result.returncode == 0:
                MODEL_NAME = "ollama:llama3.2"  # fallback to any available ollama model
                PYDANTIC_AI_AVAILABLE = True
            else:
                PYDANTIC_AI_AVAILABLE = False
                print("Warning: No AI model available (no OpenAI key, no ollama), using mock agents")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            PYDANTIC_AI_AVAILABLE = False
            print("Warning: No AI model available (no OpenAI key, ollama not found), using mock agents")
        
except ImportError:
    # Mock classes for when pydantic_ai is not available
    class Agent:
        def __init__(self, model, system_prompt: str = "", **kwargs):
            self.model = model
            self.system_prompt = system_prompt
    
    class RunContext:
        pass
    
    PYDANTIC_AI_AVAILABLE = False
    MODEL_NAME = "mock"

from .six_sigma_models import (
    ProjectCharter, MGPPAssessment, RiskManagementPlan, CommunicationPlan,
    VOCAnalysis, QFDMatrix, TargetCost, BalancedScorecard,
    ConceptGenerationSession, TRIZAnalysis, PughMatrix, DOEDesign,
    DetailedDesignSpecification, RobustDesignAnalysis,
    PrototypeSpecification, PilotStudy, ControlPlan, ImplementationPlan,
    DMEDICapstoneProject, PhaseStatus, ProjectStatus
)


# ================================
# AGENT OUTPUT MODELS
# ================================

class TrainingAssessment(BaseModel):
    """Training assessment results"""
    module_name: str = Field(..., description="Training module assessed")
    participant_name: str = Field(..., description="Participant being assessed")
    
    # Assessment scores
    knowledge_score: float = Field(..., ge=0, le=100, description="Knowledge test score")
    application_score: float = Field(..., ge=0, le=100, description="Application exercise score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall module score")
    
    # Competency areas
    competencies_demonstrated: List[str] = Field(default_factory=list)
    competencies_needs_work: List[str] = Field(default_factory=list)
    
    # Feedback
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    specific_feedback: str = Field(..., description="Detailed feedback")
    
    # Recommendations
    next_steps: List[str] = Field(default_factory=list)
    additional_resources: List[str] = Field(default_factory=list)
    
    passed: bool = Field(..., description="Whether participant passed")
    certification_ready: bool = Field(default=False, description="Ready for certification")
    
    assessment_date: date = Field(default_factory=date.today)
    assessor: str = Field(default="BlackBeltTrainer", description="Who performed assessment")


class ProjectGuidance(BaseModel):
    """Project guidance from Master Black Belt"""
    project_id: str = Field(..., description="Project being guided")
    guidance_type: str = Field(..., description="Type of guidance provided")
    
    # Analysis
    current_status_assessment: str = Field(..., description="Current project status")
    strengths_identified: List[str] = Field(default_factory=list)
    risks_identified: List[str] = Field(default_factory=list)
    gaps_identified: List[str] = Field(default_factory=list)
    
    # Recommendations
    immediate_actions: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)
    tool_recommendations: List[str] = Field(default_factory=list)
    
    # Resources
    recommended_training: List[str] = Field(default_factory=list)
    expert_consultations: List[str] = Field(default_factory=list)
    reference_materials: List[str] = Field(default_factory=list)
    
    # Follow-up
    next_review_date: date = Field(..., description="When to review again")
    success_metrics: List[str] = Field(default_factory=list)
    
    guidance_date: date = Field(default_factory=date.today)
    master_black_belt: str = Field(default="MasterBlackBelt", description="Guidance provider")


class StrategicAlignment(BaseModel):
    """Strategic alignment assessment from Champion"""
    project_id: str = Field(..., description="Project being assessed")
    
    # Business alignment
    strategic_fit_score: float = Field(..., ge=1, le=10, description="Strategic fit rating")
    business_priority: str = Field(..., description="High, Medium, Low")
    financial_justification: str = Field(..., description="Financial case assessment")
    
    # Resource alignment
    resource_availability: str = Field(..., description="Resource assessment")
    budget_approval_status: str = Field(..., description="Budget status")
    stakeholder_support: str = Field(..., description="Stakeholder alignment")
    
    # Organizational impact
    change_readiness: str = Field(..., description="Organization readiness for change")
    cultural_fit: str = Field(..., description="Cultural alignment assessment")
    capability_gaps: List[str] = Field(default_factory=list)
    
    # Recommendations
    strategic_recommendations: List[str] = Field(default_factory=list)
    resource_recommendations: List[str] = Field(default_factory=list)
    timeline_recommendations: str = Field(default="", description="Timeline guidance")
    
    # Approval
    champion_approval: bool = Field(..., description="Champion approves project")
    approval_conditions: List[str] = Field(default_factory=list)
    
    assessment_date: date = Field(default_factory=date.today)
    champion: str = Field(default="Champion", description="Champion providing assessment")


class PhaseGuidance(BaseModel):
    """Phase-specific guidance from DMEDI Coach"""
    project_id: str = Field(..., description="Project being coached")
    current_phase: str = Field(..., description="Current DMEDI phase")
    
    # Phase assessment
    phase_completion: float = Field(..., ge=0, le=100, description="% completion of phase")
    deliverables_status: Dict[str, bool] = Field(default_factory=dict)
    quality_gates_met: Dict[str, bool] = Field(default_factory=dict)
    
    # Guidance
    current_focus: str = Field(..., description="What to focus on now")
    next_actions: List[str] = Field(default_factory=list)
    tools_to_use: List[str] = Field(default_factory=list)
    common_pitfalls: List[str] = Field(default_factory=list)
    
    # Quality
    quality_checklist: List[Dict[str, bool]] = Field(default_factory=list)
    review_criteria: List[str] = Field(default_factory=list)
    
    # Transition
    ready_for_next_phase: bool = Field(..., description="Ready to advance")
    gate_review_requirements: List[str] = Field(default_factory=list)
    
    coaching_date: date = Field(default_factory=date.today)
    coach: str = Field(default="DMEDICoach", description="Coach providing guidance")


# ================================
# MOCK AGENT IMPLEMENTATIONS
# ================================

class MockBlackBeltTrainerAgent:
    """Mock Black Belt Trainer Agent for when Pydantic AI is not available"""
    
    def __init__(self):
        self.role = "Black Belt Trainer"
        self.expertise = [
            "DMEDI methodology", "Statistical analysis", "DOE", "FMEA",
            "Training delivery", "Assessment", "Certification"
        ]
    
    def assess_participant(self, module_name: str, participant_name: str, 
                          assessment_data: Dict[str, Any]) -> TrainingAssessment:
        """Mock assessment of training participant"""
        
        # Simulate assessment logic
        knowledge_score = assessment_data.get('knowledge_test_score', 85.0)
        application_score = assessment_data.get('application_score', 82.0)
        overall_score = (knowledge_score + application_score) / 2
        
        competencies_demonstrated = []
        competencies_needs_work = []
        
        if module_name.lower() in ['define', 'charter']:
            competencies_demonstrated = ["Problem Definition", "Charter Development", "Stakeholder Analysis"]
            if overall_score < 80:
                competencies_needs_work = ["Business Case Development"]
        elif module_name.lower() in ['measure', 'voc', 'qfd']:
            competencies_demonstrated = ["Voice of Customer", "QFD", "Measurement Systems"]
            if overall_score < 80:
                competencies_needs_work = ["Statistical Thinking"]
        elif module_name.lower() in ['explore', 'triz', 'doe']:
            competencies_demonstrated = ["Concept Generation", "TRIZ", "Experimental Design"]
            if overall_score < 80:
                competencies_needs_work = ["Statistical Analysis"]
        
        return TrainingAssessment(
            module_name=module_name,
            participant_name=participant_name,
            knowledge_score=knowledge_score,
            application_score=application_score,
            overall_score=overall_score,
            competencies_demonstrated=competencies_demonstrated,
            competencies_needs_work=competencies_needs_work,
            strengths=[
                f"Strong performance in {module_name} fundamentals",
                "Good practical application skills"
            ],
            improvement_areas=competencies_needs_work if competencies_needs_work else ["Continue practicing"],
            specific_feedback=f"Participant demonstrates solid understanding of {module_name} concepts. "
                            f"Overall score of {overall_score:.1f}% indicates {'strong' if overall_score >= 85 else 'adequate'} competency.",
            next_steps=[
                f"Continue to next module" if overall_score >= 80 else f"Review {module_name} materials",
                "Practice with real project scenarios"
            ],
            additional_resources=[
                f"{module_name} study guide",
                "Practice exercises",
                "Industry case studies"
            ],
            passed=overall_score >= 80,
            certification_ready=overall_score >= 85
        )
    
    def recommend_learning_path(self, participant_profile: Dict[str, Any]) -> List[str]:
        """Recommend personalized learning path"""
        experience_level = participant_profile.get('experience_level', 'beginner')
        role = participant_profile.get('role', 'engineer')
        
        if experience_level == 'beginner':
            return [
                "Six Sigma Fundamentals",
                "Statistics Refresher", 
                "DMEDI Overview",
                "Define Phase Deep Dive",
                "Measure Phase Tools",
                "Explore Phase Methods",
                "Develop Phase Techniques",
                "Implement Phase Planning"
            ]
        else:
            return [
                "Advanced DMEDI Techniques",
                "Design of Experiments Mastery",
                "Advanced Statistical Methods",
                "Leadership in Six Sigma",
                "Coaching and Mentoring"
            ]


class MockMasterBlackBeltAgent:
    """Mock Master Black Belt Agent"""
    
    def __init__(self):
        self.role = "Master Black Belt"
        self.expertise = [
            "Advanced statistics", "Project coaching", "Organizational change",
            "Strategic alignment", "Mentoring", "Complex problem solving"
        ]
    
    def provide_project_guidance(self, project_data: Dict[str, Any]) -> ProjectGuidance:
        """Provide expert project guidance"""
        
        project_id = project_data.get('project_id', 'unknown')
        current_phase = project_data.get('current_phase', 'define')
        issues = project_data.get('issues', [])
        
        # Analyze project status
        status_assessment = f"Project is in {current_phase} phase. "
        
        if len(issues) == 0:
            status_assessment += "Progressing well with no major issues."
            strengths = ["Clear project definition", "Strong team engagement", "Good progress"]
            risks = ["Maintain momentum", "Ensure quality gates"]
        else:
            status_assessment += f"Facing {len(issues)} challenges that need attention."
            strengths = ["Team committed to success", "Clear problem identification"]
            risks = issues + ["Timeline pressure", "Resource constraints"]
        
        # Phase-specific recommendations
        if current_phase.lower() == 'define':
            immediate_actions = [
                "Finalize project charter",
                "Secure stakeholder buy-in",
                "Complete MGPP assessment"
            ]
            tools = ["Project Charter template", "MGPP assessment", "RACI matrix"]
        elif current_phase.lower() == 'measure':
            immediate_actions = [
                "Complete VOC analysis",
                "Develop QFD matrix",
                "Establish measurement systems"
            ]
            tools = ["VOC interview guide", "QFD matrix", "MSA protocols"]
        else:
            immediate_actions = [
                f"Focus on {current_phase} deliverables",
                "Review quality gates",
                "Update project timeline"
            ]
            tools = [f"{current_phase} toolkit", "Quality checklists"]
        
        return ProjectGuidance(
            project_id=project_id,
            guidance_type="Expert Coaching",
            current_status_assessment=status_assessment,
            strengths_identified=strengths,
            risks_identified=risks,
            gaps_identified=issues,
            immediate_actions=immediate_actions,
            strategic_recommendations=[
                "Maintain focus on customer value",
                "Ensure data-driven decisions",
                "Keep stakeholders engaged"
            ],
            tool_recommendations=tools,
            recommended_training=[
                f"Advanced {current_phase} techniques",
                "Statistical analysis methods"
            ],
            expert_consultations=[
                "Industry subject matter expert",
                "Statistical consultant if needed"
            ],
            reference_materials=[
                f"{current_phase} phase guide",
                "Best practices library",
                "Case study examples"
            ],
            next_review_date=date.today().replace(day=min(date.today().day + 14, 28)),
            success_metrics=[
                f"{current_phase} deliverables completed",
                "Quality gates passed",
                "Stakeholder satisfaction maintained"
            ]
        )


class MockChampionAgent:
    """Mock Champion Agent"""
    
    def __init__(self):
        self.role = "Champion"
        self.expertise = [
            "Strategic planning", "Resource allocation", "Change management",
            "Business case development", "Executive communication"
        ]
    
    def assess_strategic_alignment(self, project_data: Dict[str, Any]) -> StrategicAlignment:
        """Assess project strategic alignment"""
        
        project_id = project_data.get('project_id', 'unknown')
        business_impact = project_data.get('business_impact', 'medium')
        financial_benefit = project_data.get('financial_benefit', 100000)
        
        # Strategic fit assessment
        if business_impact.lower() == 'high' and financial_benefit > 500000:
            strategic_fit = 9.0
            priority = "High"
        elif business_impact.lower() == 'medium' and financial_benefit > 100000:
            strategic_fit = 7.0
            priority = "Medium"
        else:
            strategic_fit = 5.0
            priority = "Low"
        
        # Resource assessment
        resource_status = "Adequate" if strategic_fit >= 7 else "Limited"
        budget_status = "Approved" if strategic_fit >= 8 else "Under Review"
        
        return StrategicAlignment(
            project_id=project_id,
            strategic_fit_score=strategic_fit,
            business_priority=priority,
            financial_justification=f"Expected benefit: ${financial_benefit:,.0f}. Strong ROI potential.",
            resource_availability=resource_status,
            budget_approval_status=budget_status,
            stakeholder_support="Strong" if strategic_fit >= 8 else "Moderate",
            change_readiness="Good" if strategic_fit >= 7 else "Needs Development",
            cultural_fit="Aligned with continuous improvement culture",
            capability_gaps=["Advanced statistics training"] if strategic_fit < 7 else [],
            strategic_recommendations=[
                "Align with annual strategic objectives",
                "Communicate value proposition clearly",
                "Ensure adequate resource allocation"
            ],
            resource_recommendations=[
                "Dedicated project team",
                "Statistical software licenses",
                "External consultant if needed"
            ],
            timeline_recommendations="Accelerated timeline given strategic importance" if strategic_fit >= 8 else "Standard timeline appropriate",
            champion_approval=strategic_fit >= 6,
            approval_conditions=[] if strategic_fit >= 8 else ["Enhanced business case required"]
        )


class MockDMEDICoachAgent:
    """Mock DMEDI Coach Agent"""
    
    def __init__(self):
        self.role = "DMEDI Coach"
        self.expertise = [
            "DMEDI methodology", "Phase transitions", "Quality gates",
            "Deliverable assessment", "Process coaching"
        ]
    
    def provide_phase_guidance(self, project_data: Dict[str, Any]) -> PhaseGuidance:
        """Provide phase-specific coaching guidance"""
        
        project_id = project_data.get('project_id', 'unknown')
        current_phase = project_data.get('current_phase', 'define')
        deliverables_completed = project_data.get('deliverables_completed', [])
        
        # Phase-specific guidance
        phase_info = {
            'define': {
                'key_deliverables': ['Charter', 'MGPP', 'Risk Plan', 'Communication Plan'],
                'tools': ['Project Charter Template', 'MGPP Assessment', 'Risk Register'],
                'pitfalls': ['Unclear problem statement', 'Weak business case', 'Poor stakeholder buy-in'],
                'focus': 'Clear problem definition and strong foundation'
            },
            'measure': {
                'key_deliverables': ['VOC Analysis', 'QFD Matrix', 'Measurement System', 'Baseline Data'],
                'tools': ['VOC Interview Guide', 'QFD Matrix', 'MSA Study', 'Control Charts'],
                'pitfalls': ['Poor VOC quality', 'Inadequate measurement system', 'Insufficient baseline data'],
                'focus': 'Understanding customer needs and establishing measurement capability'
            },
            'explore': {
                'key_deliverables': ['Concept Generation', 'TRIZ Analysis', 'Concept Selection', 'DOE Plan'],
                'tools': ['Brainstorming', 'TRIZ Matrix', 'Pugh Matrix', 'DOE Software'],
                'pitfalls': ['Limited creativity', 'Poor concept evaluation', 'Inadequate DOE design'],
                'focus': 'Creative problem solving and systematic experimentation'
            },
            'develop': {
                'key_deliverables': ['Detailed Design', 'DOE Results', 'Optimization', 'Robust Design'],
                'tools': ['CAD Software', 'Statistical Software', 'RSM', 'Taguchi Methods'],
                'pitfalls': ['Over-engineering', 'Poor optimization', 'Ignoring robustness'],
                'focus': 'Optimized and robust solution development'
            },
            'implement': {
                'key_deliverables': ['Prototype', 'Pilot Study', 'Control Plan', 'Implementation Plan'],
                'tools': ['Prototyping', 'Pilot Protocol', 'SPC', 'Change Management'],
                'pitfalls': ['Poor pilot design', 'Inadequate controls', 'Change resistance'],
                'focus': 'Successful deployment and sustainability'
            }
        }
        
        current_info = phase_info.get(current_phase.lower(), phase_info['define'])
        
        # Calculate completion percentage
        total_deliverables = len(current_info['key_deliverables'])
        completed_deliverables = len([d for d in deliverables_completed if d in current_info['key_deliverables']])
        completion = (completed_deliverables / total_deliverables) * 100 if total_deliverables > 0 else 0
        
        # Deliverables status
        deliverables_status = {
            deliverable: deliverable in deliverables_completed 
            for deliverable in current_info['key_deliverables']
        }
        
        # Quality gates
        quality_gates = {
            f"{current_phase}_deliverables_complete": completion >= 80,
            f"{current_phase}_quality_review": completion >= 90,
            f"{current_phase}_stakeholder_approval": completion >= 95
        }
        
        return PhaseGuidance(
            project_id=project_id,
            current_phase=current_phase,
            phase_completion=completion,
            deliverables_status=deliverables_status,
            quality_gates_met=quality_gates,
            current_focus=current_info['focus'],
            next_actions=[
                f"Complete remaining {current_phase} deliverables",
                f"Prepare for {current_phase} phase gate review",
                "Update project stakeholders"
            ],
            tools_to_use=current_info['tools'],
            common_pitfalls=current_info['pitfalls'],
            quality_checklist=[
                {"item": f"All {current_phase} deliverables completed", "completed": completion >= 100},
                {"item": f"Quality standards met", "completed": completion >= 90},
                {"item": f"Stakeholder review conducted", "completed": completion >= 80}
            ],
            review_criteria=[
                f"{current_phase} objectives achieved",
                "Quality standards met",
                "Ready for next phase"
            ],
            ready_for_next_phase=completion >= 90 and all(quality_gates.values()),
            gate_review_requirements=[
                f"Complete {current_phase} deliverables",
                "Pass quality review",
                "Stakeholder sign-off"
            ]
        )


# ================================
# REAL PYDANTIC AI AGENTS (when available)
# ================================

if PYDANTIC_AI_AVAILABLE:
    
    # Black Belt Trainer Agent
    black_belt_trainer = Agent(
        MODEL_NAME,
        result_type=TrainingAssessment,
        system_prompt="""You are an expert Six Sigma Black Belt Trainer with 15+ years of experience 
        delivering Design for Lean Six Sigma training. You specialize in DMEDI methodology and have 
        trained over 1000 Black Belt candidates.

        Your expertise includes:
        - DMEDI methodology (Define, Measure, Explore, Develop, Implement)
        - Statistical analysis and DOE
        - Training delivery and adult learning principles
        - Assessment and certification
        - Practical application of Six Sigma tools

        When assessing participants, provide detailed, constructive feedback that helps them improve.
        Focus on both technical competency and practical application skills. Be encouraging but honest
        about areas needing improvement."""
    )

    # Master Black Belt Agent
    master_black_belt = Agent(
        MODEL_NAME,
        result_type=ProjectGuidance,
        system_prompt="""You are a Master Black Belt with 20+ years of Six Sigma experience, having 
        led organizational transformations and coached hundreds of Black Belt projects. You have deep 
        expertise in advanced statistical methods, organizational change, and strategic deployment.

        Your expertise includes:
        - Advanced statistical analysis and experimental design
        - Complex project coaching and mentoring
        - Organizational change management
        - Strategic alignment of improvement initiatives
        - Deployment of Six Sigma programs

        When providing guidance, think strategically about the project's impact on the organization.
        Provide practical, actionable advice that considers both technical and organizational factors.
        Help project teams navigate complex challenges and achieve breakthrough results."""
    )

    # Champion Agent
    champion = Agent(
        MODEL_NAME,
        result_type=StrategicAlignment,
        system_prompt="""You are an executive Champion with deep business acumen and strategic thinking.
        You have successfully sponsored dozens of Six Sigma projects and understand how to align 
        improvement initiatives with business strategy.

        Your expertise includes:
        - Strategic business planning and execution
        - Resource allocation and budgeting
        - Change management and organizational development
        - Executive communication and stakeholder management
        - Business case development and financial analysis

        When assessing projects, focus on strategic value, resource requirements, and organizational
        readiness. Ensure projects align with business priorities and have adequate support for success.
        Think like a senior executive who needs to balance multiple competing priorities."""
    )

    # DMEDI Coach Agent
    dmedi_coach = Agent(
        MODEL_NAME, 
        result_type=PhaseGuidance,
        system_prompt="""You are a specialized DMEDI Coach with expert knowledge of the Design for 
        Lean Six Sigma methodology. You have guided hundreds of projects through all five DMEDI phases
        and understand the critical success factors for each phase.

        Your expertise includes:
        - Deep knowledge of DMEDI phase requirements and deliverables
        - Quality gate criteria and phase transition management
        - Practical application of DMEDI tools and techniques
        - Common pitfalls and how to avoid them
        - Project coaching and facilitation

        When providing guidance, be specific about what needs to be accomplished in the current phase.
        Help teams understand the quality standards required and prepare for successful phase transitions.
        Focus on practical, actionable advice that keeps projects on track."""
    )


# ================================
# AGENT FACTORY AND INTERFACE
# ================================

class SixSigmaAgentFactory:
    """Factory for creating Six Sigma AI agents"""
    
    @staticmethod
    def create_black_belt_trainer():
        """Create Black Belt Trainer agent"""
        if PYDANTIC_AI_AVAILABLE:
            return black_belt_trainer
        else:
            return MockBlackBeltTrainerAgent()
    
    @staticmethod
    def create_master_black_belt():
        """Create Master Black Belt agent"""
        if PYDANTIC_AI_AVAILABLE:
            return master_black_belt
        else:
            return MockMasterBlackBeltAgent()
    
    @staticmethod
    def create_champion():
        """Create Champion agent"""
        if PYDANTIC_AI_AVAILABLE:
            return champion
        else:
            return MockChampionAgent()
    
    @staticmethod
    def create_dmedi_coach():
        """Create DMEDI Coach agent"""
        if PYDANTIC_AI_AVAILABLE:
            return dmedi_coach
        else:
            return MockDMEDICoachAgent()


class SixSigmaAgentOrchestrator:
    """Orchestrates multiple Six Sigma agents for comprehensive support"""
    
    def __init__(self):
        self.trainer = SixSigmaAgentFactory.create_black_belt_trainer()
        self.master_black_belt = SixSigmaAgentFactory.create_master_black_belt()
        self.champion = SixSigmaAgentFactory.create_champion()
        self.coach = SixSigmaAgentFactory.create_dmedi_coach()
    
    async def assess_training_participant(self, module_name: str, participant_name: str, 
                                        assessment_data: Dict[str, Any]) -> TrainingAssessment:
        """Assess training participant using Black Belt Trainer"""
        if PYDANTIC_AI_AVAILABLE:
            return await self.trainer.run(
                f"Assess {participant_name}'s performance in {module_name} module",
                assessment_data=assessment_data
            )
        else:
            return self.trainer.assess_participant(module_name, participant_name, assessment_data)
    
    async def get_project_guidance(self, project_data: Dict[str, Any]) -> ProjectGuidance:
        """Get project guidance from Master Black Belt"""
        if PYDANTIC_AI_AVAILABLE:
            return await self.master_black_belt.run(
                "Provide expert guidance for this Six Sigma project",
                project_data=project_data
            )
        else:
            return self.master_black_belt.provide_project_guidance(project_data)
    
    async def assess_strategic_alignment(self, project_data: Dict[str, Any]) -> StrategicAlignment:
        """Assess strategic alignment using Champion"""
        if PYDANTIC_AI_AVAILABLE:
            return await self.champion.run(
                "Assess the strategic alignment and business value of this project",
                project_data=project_data
            )
        else:
            return self.champion.assess_strategic_alignment(project_data)
    
    async def get_phase_guidance(self, project_data: Dict[str, Any]) -> PhaseGuidance:
        """Get phase-specific guidance from DMEDI Coach"""
        if PYDANTIC_AI_AVAILABLE:
            return await self.coach.run(
                "Provide phase-specific coaching guidance for this DMEDI project",
                project_data=project_data
            )
        else:
            return self.coach.provide_phase_guidance(project_data)
    
    async def comprehensive_project_review(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive review from all agents"""
        
        # Run all assessments
        guidance = await self.get_project_guidance(project_data)
        alignment = await self.assess_strategic_alignment(project_data)
        phase_guide = await self.get_phase_guidance(project_data)
        
        return {
            "master_black_belt_guidance": guidance.dict(),
            "champion_alignment": alignment.dict(),
            "coach_guidance": phase_guide.dict(),
            "overall_recommendation": self._synthesize_recommendations(guidance, alignment, phase_guide)
        }
    
    def _synthesize_recommendations(self, guidance: ProjectGuidance, 
                                  alignment: StrategicAlignment, 
                                  phase_guide: PhaseGuidance) -> str:
        """Synthesize recommendations from all agents"""
        
        if not alignment.champion_approval:
            return "❌ STOP: Champion approval required before proceeding"
        
        if not phase_guide.ready_for_next_phase and phase_guide.phase_completion < 80:
            return f"⚠️  FOCUS: Complete current {phase_guide.current_phase} phase deliverables before advancing"
        
        if alignment.strategic_fit_score >= 8 and phase_guide.ready_for_next_phase:
            return "✅ ACCELERATE: High strategic value project ready for next phase"
        
        return "➡️  CONTINUE: Maintain steady progress with regular reviews"


# ================================
# TESTING AND EXAMPLES
# ================================

def create_sample_assessment_data() -> Dict[str, Any]:
    """Create sample assessment data for testing"""
    return {
        'knowledge_test_score': 87.5,
        'application_score': 84.0,
        'participation_score': 90.0,
        'case_study_score': 82.0,
        'areas_demonstrated': ['Statistical thinking', 'Problem solving', 'Communication'],
        'areas_needs_work': ['Advanced DOE'],
        'instructor_notes': 'Strong analytical skills, good team collaboration'
    }


def create_sample_project_data() -> Dict[str, Any]:
    """Create sample project data for testing"""
    return {
        'project_id': 'PROJ-001',
        'project_name': 'Reduce Order Processing Time',
        'current_phase': 'measure',
        'business_impact': 'high',
        'financial_benefit': 750000,
        'deliverables_completed': ['Charter', 'MGPP', 'VOC Analysis'],
        'issues': ['Data quality concerns', 'Resource constraints'],
        'timeline_status': 'on_track',
        'stakeholder_engagement': 'good'
    }


async def demo_six_sigma_agents():
    """Demonstrate Six Sigma agents functionality"""
    
    print("🎯 Six Sigma AI Agents Demo")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = SixSigmaAgentOrchestrator()
    
    # Demo training assessment
    print("\n📚 Training Assessment Demo:")
    assessment_data = create_sample_assessment_data()
    assessment = await orchestrator.assess_training_participant(
        module_name="Measure Phase - VOC and QFD",
        participant_name="John Smith",
        assessment_data=assessment_data
    )
    print(f"Overall Score: {assessment.overall_score:.1f}%")
    print(f"Passed: {assessment.passed}")
    print(f"Feedback: {assessment.specific_feedback}")
    
    # Demo project guidance
    print("\n🎯 Project Guidance Demo:")
    project_data = create_sample_project_data()
    
    comprehensive_review = await orchestrator.comprehensive_project_review(project_data)
    print(f"Overall Recommendation: {comprehensive_review['overall_recommendation']}")
    
    return {
        'assessment': assessment,
        'comprehensive_review': comprehensive_review
    }


if __name__ == "__main__":
    import asyncio
    
    # Run demonstration
    results = asyncio.run(demo_six_sigma_agents())
    print("\n✅ Six Sigma Agents demonstration completed successfully!")