"""
Six Sigma BPMN Service Tasks with qwen3 Integration
==================================================

BPMN service tasks for Six Sigma DMEDI training following WeaverGen patterns:
- ai_validation decorators for enhanced instrumentation
- semantic_span decorators for OpenTelemetry integration
- qwen3 model integration via OpenAIModel
- Structured output with Pydantic models
- SpiffWorkflow integration
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.service import SpiffServiceTask

# Import WeaverGen's instrumentation patterns
from .instrumentation import semantic_span, ai_validation, layer_span, resource_span

# Set up qwen3 environment following WeaverGen patterns
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"

tracer = trace.get_tracer(__name__)


# Structured Output Models for Six Sigma BPMN Tasks
class SixSigmaCharterAnalysis(BaseModel):
    """Charter analysis result from qwen3"""
    charter_quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall charter quality")
    problem_statement_score: float = Field(..., ge=0.0, le=1.0, description="Problem statement clarity")
    goal_statement_score: float = Field(..., ge=0.0, le=1.0, description="Goal statement quality")
    scope_definition_score: float = Field(..., ge=0.0, le=1.0, description="Scope definition adequacy")
    team_structure_score: float = Field(..., ge=0.0, le=1.0, description="Team structure completeness")
    timeline_realism_score: float = Field(..., ge=0.0, le=1.0, description="Timeline realism assessment")
    success_metrics_score: float = Field(..., ge=0.0, le=1.0, description="Success metrics measurability")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    certification_ready: bool = Field(..., description="Ready for Black Belt certification")


class SixSigmaVOCAnalysis(BaseModel):
    """Voice of Customer analysis from qwen3"""
    customer_segments: List[str] = Field(..., description="Identified customer segments")
    collection_methods: List[str] = Field(..., description="Recommended VOC collection methods")
    critical_to_quality: List[str] = Field(..., description="CTQ characteristics")
    kano_classification: Dict[str, str] = Field(..., description="Kano model results")
    prioritized_requirements: List[str] = Field(..., description="Prioritized customer needs")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    implementation_plan: List[str] = Field(..., description="Implementation steps")


class SixSigmaTRIZSolution(BaseModel):
    """TRIZ innovation solution from qwen3"""
    problem_type: str = Field(..., description="Type of technical problem")
    contradiction_analysis: str = Field(..., description="Identified contradictions")
    applicable_principles: List[str] = Field(..., description="TRIZ principles applied")
    innovative_concepts: List[str] = Field(..., description="Generated solution concepts")
    implementation_roadmap: List[str] = Field(..., description="Implementation steps")
    innovation_score: float = Field(..., ge=0.0, le=1.0, description="Innovation potential")
    feasibility_assessment: str = Field(..., description="Technical feasibility")


class SixSigmaDOEDesign(BaseModel):
    """Design of Experiments from qwen3"""
    design_type: str = Field(..., description="Type of experimental design")
    factors: List[Dict[str, Any]] = Field(..., description="Experimental factors")
    responses: List[str] = Field(..., description="Response variables")
    design_matrix: List[List[Any]] = Field(..., description="Experimental matrix")
    sample_size: int = Field(..., ge=1, description="Required sample size")
    power_analysis: Dict[str, float] = Field(..., description="Statistical power")
    optimization_strategy: str = Field(..., description="Optimization approach")
    resource_requirements: Dict[str, Any] = Field(..., description="Required resources")


class SixSigmaImplementationPlan(BaseModel):
    """Implementation plan from qwen3"""
    prototype_strategy: str = Field(..., description="Prototype development approach")
    pilot_design: Dict[str, Any] = Field(..., description="Pilot test structure")
    scale_up_phases: List[str] = Field(..., description="Scale-up phases")
    control_methods: List[str] = Field(..., description="Process control approaches")
    risk_mitigation: List[str] = Field(..., description="Risk mitigation strategies")
    success_metrics: List[str] = Field(..., description="Success measurement")
    timeline_milestones: List[str] = Field(..., description="Key milestones")
    sustainability_plan: List[str] = Field(..., description="Long-term sustainability")


# Six Sigma BPMN Service Tasks with qwen3 Integration
class SixSigmaCharterAnalysisTask(SpiffServiceTask):
    """Analyze project charter using qwen3 following WeaverGen patterns"""
    
    def __init__(self):
        super().__init__("SixSigmaCharterAnalysis")
        self.ollama_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )
        self.agent = Agent(
            self.ollama_model,
            result_type=SixSigmaCharterAnalysis,
            system_prompt="""You are an expert Six Sigma Master Black Belt evaluating project charters for Black Belt certification.
            
            Evaluate charters against these criteria:
            1. Problem statement clarity and business impact
            2. SMART goal statement compliance
            3. Scope definition with clear boundaries
            4. Team structure adequacy and roles
            5. Timeline realism and milestone clarity
            6. Success metrics measurability and relevance
            
            Provide scores (0.0-1.0) for each criterion, specific recommendations, and certification readiness assessment.
            Focus on practical implementation and business value."""
        )
    
    @semantic_span("sixsigma.bpmn", "charter_analysis")
    @ai_validation("qwen3:latest", "SixSigmaCharterAnalysis")
    @layer_span("bpmn_service")
    @resource_span("charter", "analyze")
    async def _execute_task_logic(self, task: Task, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute charter analysis with qwen3"""
        
        charter_data = task_data.get("charter", {})
        
        prompt = f"""
        Analyze this Six Sigma project charter for Black Belt certification readiness:
        
        Charter Details:
        - Problem Statement: {charter_data.get('problem_statement', 'Not provided')}
        - Goal Statement: {charter_data.get('goal_statement', 'Not provided')}
        - Scope Definition: {charter_data.get('scope_definition', 'Not provided')}
        - Team Structure: {charter_data.get('team_structure', 'Not provided')}
        - Timeline: {charter_data.get('timeline_milestones', 'Not provided')}
        - Success Metrics: {charter_data.get('success_metrics', 'Not provided')}
        
        Industry Context: {charter_data.get('industry', 'manufacturing')}
        Project Type: {charter_data.get('project_type', 'process_improvement')}
        
        Provide comprehensive analysis with scores and actionable recommendations.
        """
        
        result = await self.agent.run(prompt)
        analysis = result.data
        
        return {
            "charter_analysis": analysis.dict(),
            "overall_quality": analysis.charter_quality_score,
            "certification_ready": analysis.certification_ready,
            "model_used": "qwen3:latest",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }


class SixSigmaVOCAnalysisTask(SpiffServiceTask):
    """Conduct Voice of Customer analysis using qwen3 following WeaverGen patterns"""
    
    def __init__(self):
        super().__init__("SixSigmaVOCAnalysis")
        self.ollama_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )
        self.agent = Agent(
            self.ollama_model,
            result_type=SixSigmaVOCAnalysis,
            system_prompt="""You are an expert Six Sigma Black Belt specializing in Voice of Customer (VOC) analysis and Quality Function Deployment.
            
            Your expertise includes:
            - Customer segmentation and persona development
            - VOC collection methodology selection
            - Critical-to-Quality (CTQ) identification
            - Kano model application and analysis
            - Customer requirements prioritization
            - Implementation planning for VOC insights
            
            Generate comprehensive VOC analyses that drive data-driven design decisions and customer value creation."""
        )
    
    @semantic_span("sixsigma.bpmn", "voc_analysis")
    @ai_validation("qwen3:latest", "SixSigmaVOCAnalysis")
    @layer_span("bpmn_service")
    @resource_span("voc", "analyze")
    async def _execute_task_logic(self, task: Task, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute VOC analysis with qwen3"""
        
        voc_context = task_data.get("voc_context", {})
        
        prompt = f"""
        Conduct comprehensive Voice of Customer (VOC) analysis for this context:
        
        Product/Service: {voc_context.get('product_service', 'manufacturing process')}
        Industry: {voc_context.get('industry', 'manufacturing')}
        Customer Base: {voc_context.get('customer_base', 'internal and external customers')}
        Current Challenges: {voc_context.get('current_challenges', 'quality and delivery issues')}
        Business Objectives: {voc_context.get('business_objectives', 'improve customer satisfaction')}
        
        Project Context:
        - Scope: {voc_context.get('scope', 'process improvement')}
        - Timeline: {voc_context.get('timeline', '3-6 months')}
        - Resources: {voc_context.get('resources', 'cross-functional team')}
        
        Provide actionable VOC analysis with practical implementation guidance.
        """
        
        result = await self.agent.run(prompt)
        analysis = result.data
        
        return {
            "voc_analysis": analysis.dict(),
            "customer_segments_count": len(analysis.customer_segments),
            "ctq_characteristics_count": len(analysis.critical_to_quality),
            "confidence_score": analysis.confidence_score,
            "model_used": "qwen3:latest",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }


class SixSigmaTRIZInnovationTask(SpiffServiceTask):
    """Apply TRIZ methodology for innovation using qwen3 following WeaverGen patterns"""
    
    def __init__(self):
        super().__init__("SixSigmaTRIZInnovation")
        self.ollama_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )
        self.agent = Agent(
            self.ollama_model,
            result_type=SixSigmaTRIZSolution,
            system_prompt="""You are an expert TRIZ methodology specialist and Six Sigma Black Belt instructor.
            
            Your expertise includes:
            - TRIZ 40 principles and contradiction matrix
            - Technical and physical contradiction identification
            - Substance-field modeling and transformation
            - Algorithm of Inventive Problem Solving (ARIZ)
            - Patterns of technical system evolution
            - Creative problem-solving integration with Six Sigma
            
            Generate innovative, practical solutions using systematic TRIZ methodology while maintaining Six Sigma rigor."""
        )
    
    @semantic_span("sixsigma.bpmn", "triz_innovation")
    @ai_validation("qwen3:latest", "SixSigmaTRIZSolution")
    @layer_span("bpmn_service")
    @resource_span("triz", "solve")
    async def _execute_task_logic(self, task: Task, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute TRIZ innovation with qwen3"""
        
        problem_context = task_data.get("problem_context", {})
        
        prompt = f"""
        Apply TRIZ methodology to solve this technical problem:
        
        Problem Description: {problem_context.get('problem_description', 'Process optimization challenge')}
        Current Solution Limitations: {problem_context.get('current_limitations', 'Trade-offs between cost and quality')}
        Desired Outcomes: {problem_context.get('desired_outcomes', 'Improved performance without increased cost')}
        Technical Constraints: {problem_context.get('technical_constraints', 'Existing equipment and processes')}
        Business Constraints: {problem_context.get('business_constraints', 'Budget and timeline limitations')}
        
        System Context:
        - Industry: {problem_context.get('industry', 'manufacturing')}
        - Technology Level: {problem_context.get('technology_level', 'intermediate')}
        - Innovation Scope: {problem_context.get('innovation_scope', 'process improvement')}
        
        Apply systematic TRIZ analysis to generate breakthrough solutions with implementation roadmap.
        """
        
        result = await self.agent.run(prompt)
        solution = result.data
        
        return {
            "triz_solution": solution.dict(),
            "innovation_score": solution.innovation_score,
            "principles_applied_count": len(solution.applicable_principles),
            "concepts_generated_count": len(solution.innovative_concepts),
            "model_used": "qwen3:latest",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }


class SixSigmaDOEDesignTask(SpiffServiceTask):
    """Design comprehensive experiments using qwen3 following WeaverGen patterns"""
    
    def __init__(self):
        super().__init__("SixSigmaDOEDesign")
        self.ollama_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )
        self.agent = Agent(
            self.ollama_model,
            result_type=SixSigmaDOEDesign,
            system_prompt="""You are an expert statistician and Six Sigma Master Black Belt specializing in Design of Experiments (DOE).
            
            Your expertise includes:
            - Full factorial and fractional factorial designs
            - Response surface methodology (RSM)
            - Optimal design selection and optimization
            - Statistical power analysis and sample size calculation
            - Multi-response optimization strategies
            - Practical DOE implementation and resource planning
            
            Generate statistically sound, resource-efficient experimental designs with clear optimization strategies."""
        )
    
    @semantic_span("sixsigma.bpmn", "doe_design")
    @ai_validation("qwen3:latest", "SixSigmaDOEDesign")
    @layer_span("bpmn_service")
    @resource_span("doe", "design")
    async def _execute_task_logic(self, task: Task, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DOE design with qwen3"""
        
        doe_objectives = task_data.get("doe_objectives", {})
        
        prompt = f"""
        Design a comprehensive Design of Experiments (DOE) for these objectives:
        
        Process/Product: {doe_objectives.get('process_product', 'Manufacturing process optimization')}
        Primary Objective: {doe_objectives.get('primary_objective', 'Optimize quality and efficiency')}
        Key Factors: {doe_objectives.get('key_factors', 'Temperature, Pressure, Time, Speed')}
        Response Variables: {doe_objectives.get('response_variables', 'Quality score, Cycle time, Cost')}
        
        Experimental Constraints:
        - Budget: {doe_objectives.get('budget_level', 'Moderate')}
        - Timeline: {doe_objectives.get('timeline', '4-6 weeks')}
        - Resource Availability: {doe_objectives.get('resources', 'Standard lab equipment')}
        - Sample Constraints: {doe_objectives.get('sample_constraints', 'Material cost considerations')}
        
        Optimization Goals:
        - Primary: {doe_objectives.get('primary_goal', 'Maximize quality')}
        - Secondary: {doe_objectives.get('secondary_goal', 'Minimize cost')}
        
        Generate a practical, statistically rigorous experimental design with implementation guidance.
        """
        
        result = await self.agent.run(prompt)
        design = result.data
        
        return {
            "doe_design": design.dict(),
            "design_type": design.design_type,
            "factors_count": len(design.factors),
            "responses_count": len(design.responses),
            "sample_size": design.sample_size,
            "model_used": "qwen3:latest",
            "design_timestamp": datetime.utcnow().isoformat()
        }


class SixSigmaImplementationPlanTask(SpiffServiceTask):
    """Develop implementation plan using qwen3 following WeaverGen patterns"""
    
    def __init__(self):
        super().__init__("SixSigmaImplementationPlan")
        self.ollama_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )
        self.agent = Agent(
            self.ollama_model,
            result_type=SixSigmaImplementationPlan,
            system_prompt="""You are an expert Six Sigma Master Black Belt specializing in implementation planning and change management.
            
            Your expertise includes:
            - Prototype development and validation strategies
            - Pilot testing methodologies and scale-up planning
            - Process control system design and implementation
            - Change management and stakeholder engagement
            - Risk assessment and mitigation planning
            - Sustainability and continuous improvement systems
            
            Generate comprehensive, executable implementation plans with high success probability and long-term sustainability."""
        )
    
    @semantic_span("sixsigma.bpmn", "implementation_planning")
    @ai_validation("qwen3:latest", "SixSigmaImplementationPlan")
    @layer_span("bpmn_service")
    @resource_span("implementation", "plan")
    async def _execute_task_logic(self, task: Task, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute implementation planning with qwen3"""
        
        implementation_context = task_data.get("implementation_context", {})
        
        prompt = f"""
        Develop a comprehensive implementation plan for this Six Sigma solution:
        
        Solution Overview: {implementation_context.get('solution_overview', 'Process improvement solution')}
        Organization Context: {implementation_context.get('organization_context', 'Medium manufacturing company')}
        Implementation Scope: {implementation_context.get('implementation_scope', 'Single production line')}
        
        Project Parameters:
        - Timeline: {implementation_context.get('timeline', '6-12 months')}
        - Budget Level: {implementation_context.get('budget_level', 'Moderate investment')}
        - Team Size: {implementation_context.get('team_size', '5-8 people')}
        - Stakeholder Groups: {implementation_context.get('stakeholders', 'Operations, Quality, Management')}
        
        Success Criteria:
        - Primary Metrics: {implementation_context.get('primary_metrics', 'Quality improvement, Cost reduction')}
        - Secondary Metrics: {implementation_context.get('secondary_metrics', 'Efficiency, Customer satisfaction')}
        
        Risk Factors:
        - Technical Risks: {implementation_context.get('technical_risks', 'Equipment compatibility')}
        - Organizational Risks: {implementation_context.get('organizational_risks', 'Change resistance')}
        
        Generate a detailed, actionable implementation plan with clear milestones and risk mitigation.
        """
        
        result = await self.agent.run(prompt)
        plan = result.data
        
        return {
            "implementation_plan": plan.dict(),
            "prototype_strategy": plan.prototype_strategy,
            "scale_up_phases_count": len(plan.scale_up_phases),
            "control_methods_count": len(plan.control_methods),
            "milestones_count": len(plan.timeline_milestones),
            "model_used": "qwen3:latest",
            "plan_timestamp": datetime.utcnow().isoformat()
        }


# Six Sigma Assessment and Validation Task
class SixSigmaTrainingAssessmentTask(SpiffServiceTask):
    """Assess Six Sigma training progress using qwen3 following WeaverGen patterns"""
    
    def __init__(self):
        super().__init__("SixSigmaTrainingAssessment")
        self.ollama_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )
        self.agent = Agent(
            self.ollama_model,
            result_type=dict,
            system_prompt="""You are an expert Six Sigma Master Black Belt instructor and assessor specializing in comprehensive training evaluation.
            
            Your expertise includes:
            - DMEDI phase competency assessment
            - Black Belt certification requirements evaluation
            - Practical application assessment
            - Learning progress analysis and recommendations
            - Personalized training path optimization
            
            Provide fair, comprehensive assessments with specific feedback and actionable improvement recommendations."""
        )
    
    @semantic_span("sixsigma.bpmn", "training_assessment")
    @ai_validation("qwen3:latest", "TrainingAssessment")
    @layer_span("bpmn_service")
    @resource_span("assessment", "evaluate")
    async def _execute_task_logic(self, task: Task, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute training assessment with qwen3"""
        
        assessment_context = task_data.get("assessment_context", {})
        
        prompt = f"""
        Assess Six Sigma training progress for this participant:
        
        Participant Profile:
        - ID: {assessment_context.get('participant_id', 'Unknown')}
        - Current Phase: {assessment_context.get('current_phase', 'define')}
        - Modules Completed: {assessment_context.get('modules_completed', [])}
        - Completion Percentage: {assessment_context.get('completion_percentage', 0.0)}
        
        Performance Data:
        - Charter Analysis Score: {assessment_context.get('charter_score', 'Not available')}
        - VOC Analysis Score: {assessment_context.get('voc_score', 'Not available')}
        - TRIZ Innovation Score: {assessment_context.get('triz_score', 'Not available')}
        - DOE Design Score: {assessment_context.get('doe_score', 'Not available')}
        - Implementation Score: {assessment_context.get('implementation_score', 'Not available')}
        
        Learning Objectives:
        - Target Certification: {assessment_context.get('target_certification', 'Black Belt')}
        - Industry Focus: {assessment_context.get('industry_focus', 'Manufacturing')}
        - Learning Style: {assessment_context.get('learning_style', 'Mixed')}
        
        Provide comprehensive assessment with:
        1. Overall competency score (0.0-1.0)
        2. Phase-specific scores and feedback
        3. Strengths and improvement areas
        4. Certification readiness assessment
        5. Personalized next steps and recommendations
        """
        
        result = await self.agent.run(prompt)
        assessment = result.data
        
        return {
            "training_assessment": assessment,
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "model_used": "qwen3:latest",
            "assessment_type": "comprehensive_six_sigma_evaluation"
        }