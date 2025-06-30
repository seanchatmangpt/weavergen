"""Enterprise Workflow Orchestration Engine.

This module implements the workflow orchestration engine for enterprise Scrum
with support for complex multi-step processes, event-driven automation,
and scalable execution patterns.
"""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, Union
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from .models import (
    Sprint, UserStory, Task, Team, Project, Meeting, Impediment,
    SprintStatus, TaskStatus, UserStoryStatus, MeetingType, Priority
)
from .agents import (
    ScrumAgentOrchestrator, AgentContext, ScrumMasterAgent,
    ProductOwnerAgent, DeveloperAgent, QAAgent, ExecutiveAgent
)


# ============================================================================
# Workflow Definition Models
# ============================================================================

class WorkflowEventType(str, Enum):
    """Types of workflow events."""
    SPRINT_STARTED = "sprint_started"
    SPRINT_ENDED = "sprint_ended"
    STORY_COMPLETED = "story_completed"
    TASK_BLOCKED = "task_blocked"
    IMPEDIMENT_RAISED = "impediment_raised"
    VELOCITY_THRESHOLD = "velocity_threshold"
    QUALITY_GATE_FAILED = "quality_gate_failed"
    DEADLINE_APPROACHING = "deadline_approaching"
    BUDGET_THRESHOLD = "budget_threshold"
    DAILY_STANDUP_DUE = "daily_standup_due"
    RETROSPECTIVE_DUE = "retrospective_due"


class WorkflowActionType(str, Enum):
    """Types of workflow actions."""
    SEND_NOTIFICATION = "send_notification"
    SCHEDULE_MEETING = "schedule_meeting"
    UPDATE_STATUS = "update_status"
    ASSIGN_TASK = "assign_task"
    ESCALATE_ISSUE = "escalate_issue"
    GENERATE_REPORT = "generate_report"
    RUN_AGENT_ANALYSIS = "run_agent_analysis"
    TRIGGER_INTEGRATION = "trigger_integration"
    APPLY_POLICY = "apply_policy"
    CREATE_AUDIT_ENTRY = "create_audit_entry"


class WorkflowCondition(BaseModel):
    """Condition for workflow triggers."""
    field: str
    operator: str  # eq, neq, gt, lt, gte, lte, in, contains
    value: Any
    logical_operator: Optional[str] = None  # and, or
    
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate condition against data."""
        field_value = data.get(self.field)
        
        if self.operator == "eq":
            return field_value == self.value
        elif self.operator == "neq":
            return field_value != self.value
        elif self.operator == "gt":
            return field_value > self.value
        elif self.operator == "lt":
            return field_value < self.value
        elif self.operator == "gte":
            return field_value >= self.value
        elif self.operator == "lte":
            return field_value <= self.value
        elif self.operator == "in":
            return field_value in self.value
        elif self.operator == "contains":
            return self.value in field_value
        
        return False


class WorkflowAction(BaseModel):
    """Workflow action definition."""
    id: UUID = Field(default_factory=uuid4)
    type: WorkflowActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    delay_seconds: int = 0
    retry_count: int = 0
    timeout_seconds: int = 300
    
    # Conditional execution
    conditions: List[WorkflowCondition] = Field(default_factory=list)
    
    # Error handling
    on_error_action: Optional[str] = None
    continue_on_error: bool = False


class WorkflowRule(BaseModel):
    """Workflow rule that defines triggers and actions."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    event_type: WorkflowEventType
    
    # Trigger conditions
    conditions: List[WorkflowCondition] = Field(default_factory=list)
    
    # Actions to execute
    actions: List[WorkflowAction]
    
    # Rule metadata
    is_active: bool = True
    priority: int = Field(default=50, ge=1, le=100)
    tags: List[str] = Field(default_factory=list)
    
    # Multi-tenancy
    tenant_id: UUID
    organization_scope: bool = False  # If true, applies to entire org
    
    # Execution tracking
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    success_rate: float = 100.0


class WorkflowExecution(BaseModel):
    """Workflow execution instance."""
    id: UUID = Field(default_factory=uuid4)
    rule_id: UUID
    tenant_id: UUID
    
    # Execution context
    triggered_by: WorkflowEventType
    trigger_data: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution state
    status: str = "pending"  # pending, running, completed, failed, cancelled
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Action tracking
    actions_executed: List[Dict[str, Any]] = Field(default_factory=list)
    current_action_index: int = 0
    
    # Results and errors
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0


# ============================================================================
# Workflow Engine Core
# ============================================================================

@dataclass
class EventData:
    """Event data container."""
    event_type: WorkflowEventType
    entity_id: UUID
    entity_type: str
    tenant_id: UUID
    user_id: UUID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None


class WorkflowEngine:
    """Enterprise workflow orchestration engine."""
    
    def __init__(self):
        """Initialize the workflow engine."""
        self.rules: Dict[UUID, WorkflowRule] = {}
        self.executions: Dict[UUID, WorkflowExecution] = {}
        self.event_handlers: Dict[WorkflowEventType, List[Callable]] = {}
        self.action_handlers: Dict[WorkflowActionType, Callable] = {}
        self.agents = ScrumAgentOrchestrator()
        
        # Performance tracking
        self.metrics = {
            "events_processed": 0,
            "rules_executed": 0,
            "actions_completed": 0,
            "average_execution_time": 0.0
        }
        
        # Initialize built-in action handlers
        self._register_built_in_handlers()
    
    def _register_built_in_handlers(self):
        """Register built-in action handlers."""
        self.action_handlers = {
            WorkflowActionType.SEND_NOTIFICATION: self._handle_send_notification,
            WorkflowActionType.SCHEDULE_MEETING: self._handle_schedule_meeting,
            WorkflowActionType.UPDATE_STATUS: self._handle_update_status,
            WorkflowActionType.ASSIGN_TASK: self._handle_assign_task,
            WorkflowActionType.ESCALATE_ISSUE: self._handle_escalate_issue,
            WorkflowActionType.GENERATE_REPORT: self._handle_generate_report,
            WorkflowActionType.RUN_AGENT_ANALYSIS: self._handle_run_agent_analysis,
            WorkflowActionType.TRIGGER_INTEGRATION: self._handle_trigger_integration,
            WorkflowActionType.APPLY_POLICY: self._handle_apply_policy,
            WorkflowActionType.CREATE_AUDIT_ENTRY: self._handle_create_audit_entry,
        }
    
    def register_rule(self, rule: WorkflowRule):
        """Register a workflow rule."""
        self.rules[rule.id] = rule
    
    def register_event_handler(self, event_type: WorkflowEventType, handler: Callable):
        """Register custom event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def process_event(self, event: EventData) -> List[WorkflowExecution]:
        """Process an event and trigger applicable workflows."""
        self.metrics["events_processed"] += 1
        
        # Find applicable rules
        applicable_rules = self._find_applicable_rules(event)
        
        # Execute rules
        executions = []
        for rule in applicable_rules:
            execution = await self._execute_rule(rule, event)
            if execution:
                executions.append(execution)
        
        # Call custom event handlers
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Event handler error: {e}")
        
        return executions
    
    def _find_applicable_rules(self, event: EventData) -> List[WorkflowRule]:
        """Find rules that should be triggered by the event."""
        applicable_rules = []
        
        for rule in self.rules.values():
            if not rule.is_active:
                continue
            
            # Check tenant isolation
            if rule.tenant_id != event.tenant_id and not rule.organization_scope:
                continue
            
            # Check event type
            if rule.event_type != event.event_type:
                continue
            
            # Check conditions
            if self._evaluate_conditions(rule.conditions, event.data):
                applicable_rules.append(rule)
        
        # Sort by priority (higher priority first)
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        return applicable_rules
    
    def _evaluate_conditions(self, conditions: List[WorkflowCondition], data: Dict[str, Any]) -> bool:
        """Evaluate all conditions for a rule."""
        if not conditions:
            return True
        
        # Simple AND logic for now (could be enhanced for complex boolean logic)
        return all(condition.evaluate(data) for condition in conditions)
    
    async def _execute_rule(self, rule: WorkflowRule, event: EventData) -> Optional[WorkflowExecution]:
        """Execute a workflow rule."""
        execution = WorkflowExecution(
            rule_id=rule.id,
            tenant_id=event.tenant_id,
            triggered_by=event.event_type,
            trigger_data=event.data,
            context={
                "event_id": str(event.entity_id),
                "event_type": event.event_type,
                "user_id": str(event.user_id)
            }
        )
        
        self.executions[execution.id] = execution
        
        try:
            execution.status = "running"
            await self._execute_actions(execution, rule.actions, event)
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            
            # Update rule statistics
            rule.execution_count += 1
            rule.last_executed = datetime.utcnow()
            
            self.metrics["rules_executed"] += 1
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            # Update rule success rate
            rule.success_rate = (rule.success_rate * (rule.execution_count - 1) + 0) / rule.execution_count
        
        return execution
    
    async def _execute_actions(self, execution: WorkflowExecution, actions: List[WorkflowAction], event: EventData):
        """Execute all actions for a workflow."""
        for i, action in enumerate(actions):
            execution.current_action_index = i
            
            try:
                # Apply delay if specified
                if action.delay_seconds > 0:
                    await asyncio.sleep(action.delay_seconds)
                
                # Check action conditions
                if action.conditions and not self._evaluate_conditions(action.conditions, event.data):
                    continue
                
                # Execute action with timeout
                result = await asyncio.wait_for(
                    self._execute_action(action, execution, event),
                    timeout=action.timeout_seconds
                )
                
                # Record successful execution
                execution.actions_executed.append({
                    "action_id": str(action.id),
                    "action_type": action.type,
                    "result": result,
                    "executed_at": datetime.utcnow().isoformat(),
                    "status": "success"
                })
                
                self.metrics["actions_completed"] += 1
                
            except Exception as e:
                # Record failed execution
                execution.actions_executed.append({
                    "action_id": str(action.id),
                    "action_type": action.type,
                    "error": str(e),
                    "executed_at": datetime.utcnow().isoformat(),
                    "status": "failed"
                })
                
                if not action.continue_on_error:
                    raise
    
    async def _execute_action(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> Any:
        """Execute a single workflow action."""
        handler = self.action_handlers.get(action.type)
        if not handler:
            raise ValueError(f"No handler registered for action type: {action.type}")
        
        return await handler(action, execution, event)
    
    # ========================================================================
    # Built-in Action Handlers
    # ========================================================================
    
    async def _handle_send_notification(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle send notification action."""
        params = action.parameters
        notification_type = params.get("type", "email")
        recipients = params.get("recipients", [])
        message = params.get("message", "")
        subject = params.get("subject", "Workflow Notification")
        
        # In real implementation, this would integrate with notification service
        print(f"NOTIFICATION [{notification_type}] to {recipients}: {subject} - {message}")
        
        return f"Notification sent to {len(recipients)} recipients"
    
    async def _handle_schedule_meeting(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle schedule meeting action."""
        params = action.parameters
        meeting_type = params.get("meeting_type", MeetingType.DAILY_STANDUP)
        attendees = params.get("attendees", [])
        duration = params.get("duration_minutes", 30)
        
        # Create meeting record
        meeting = Meeting(
            title=f"Auto-scheduled {meeting_type}",
            type=meeting_type,
            project_id=UUID(event.data.get("project_id", str(uuid4()))),
            scheduled_at=datetime.utcnow() + timedelta(hours=1),
            duration_minutes=duration,
            organizer_id=event.user_id,
            required_attendees=set(UUID(uid) for uid in attendees),
            tenant_id=event.tenant_id,
            created_by=event.user_id
        )
        
        # In real implementation, this would save to database and send calendar invites
        print(f"MEETING SCHEDULED: {meeting.title} with {len(attendees)} attendees")
        
        return f"Meeting scheduled: {meeting.id}"
    
    async def _handle_update_status(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle update status action."""
        params = action.parameters
        entity_type = params.get("entity_type")
        entity_id = params.get("entity_id", event.entity_id)
        new_status = params.get("status")
        
        # In real implementation, this would update the database
        print(f"STATUS UPDATE: {entity_type} {entity_id} -> {new_status}")
        
        return f"Updated {entity_type} status to {new_status}"
    
    async def _handle_assign_task(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle assign task action."""
        params = action.parameters
        task_id = params.get("task_id")
        assignee_id = params.get("assignee_id")
        
        # In real implementation, this would update task assignment
        print(f"TASK ASSIGNMENT: Task {task_id} -> User {assignee_id}")
        
        return f"Task {task_id} assigned to {assignee_id}"
    
    async def _handle_escalate_issue(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle escalate issue action."""
        params = action.parameters
        issue_id = params.get("issue_id", event.entity_id)
        escalation_level = params.get("level", "manager")
        
        # Create escalation record
        escalation = {
            "issue_id": str(issue_id),
            "escalated_to": escalation_level,
            "escalated_at": datetime.utcnow().isoformat(),
            "escalated_by": "workflow_engine",
            "reason": params.get("reason", "Automatic escalation")
        }
        
        print(f"ESCALATION: Issue {issue_id} escalated to {escalation_level}")
        
        return f"Issue escalated to {escalation_level}"
    
    async def _handle_generate_report(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle generate report action."""
        params = action.parameters
        report_type = params.get("type", "sprint_summary")
        format_type = params.get("format", "pdf")
        
        # In real implementation, this would generate actual reports
        print(f"REPORT GENERATION: {report_type} in {format_type} format")
        
        return f"Report generated: {report_type}.{format_type}"
    
    async def _handle_run_agent_analysis(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle run agent analysis action."""
        params = action.parameters
        agent_type = params.get("agent_type", "scrum_master")
        analysis_type = params.get("analysis_type", "general")
        
        # Create agent context
        context = AgentContext(
            tenant_id=event.tenant_id,
            user_id=event.user_id,
            user_roles={"workflow_engine"},
            organization_features={"ai_analysis"}
        )
        
        # Run appropriate agent analysis
        result = None
        if agent_type == "scrum_master" and analysis_type == "sprint_health":
            sprint_id = UUID(params.get("sprint_id", str(event.entity_id)))
            result = await self.agents.scrum_master.analyze_daily_standup(context, sprint_id, [])
        elif agent_type == "executive" and analysis_type == "portfolio":
            result = await self.agents.executive.generate_portfolio_insights(context, [], [], {})
        
        print(f"AGENT ANALYSIS: {agent_type} - {analysis_type}")
        
        return f"Agent analysis completed: {agent_type}"
    
    async def _handle_trigger_integration(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle trigger integration action."""
        params = action.parameters
        integration_type = params.get("type", "webhook")
        endpoint = params.get("endpoint")
        
        # In real implementation, this would call external APIs
        print(f"INTEGRATION TRIGGER: {integration_type} -> {endpoint}")
        
        return f"Integration triggered: {integration_type}"
    
    async def _handle_apply_policy(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle apply policy action."""
        params = action.parameters
        policy_name = params.get("policy")
        
        # In real implementation, this would apply governance policies
        print(f"POLICY APPLICATION: {policy_name}")
        
        return f"Policy applied: {policy_name}"
    
    async def _handle_create_audit_entry(self, action: WorkflowAction, execution: WorkflowExecution, event: EventData) -> str:
        """Handle create audit entry action."""
        params = action.parameters
        audit_type = params.get("type", "workflow_action")
        
        audit_entry = {
            "type": audit_type,
            "entity_id": str(event.entity_id),
            "tenant_id": str(event.tenant_id),
            "user_id": str(event.user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "details": params.get("details", {}),
            "workflow_execution_id": str(execution.id)
        }
        
        # In real implementation, this would write to audit log
        print(f"AUDIT ENTRY: {audit_type} for {event.entity_id}")
        
        return f"Audit entry created: {audit_type}"


# ============================================================================
# Predefined Enterprise Workflows
# ============================================================================

class EnterpriseWorkflowTemplates:
    """Predefined workflow templates for common enterprise scenarios."""
    
    @staticmethod
    def create_sprint_automation_workflows(tenant_id: UUID) -> List[WorkflowRule]:
        """Create standard sprint automation workflows."""
        workflows = []
        
        # Sprint Started Workflow
        sprint_started = WorkflowRule(
            name="Sprint Started Automation",
            description="Automatically sets up sprint activities when a sprint starts",
            event_type=WorkflowEventType.SPRINT_STARTED,
            tenant_id=tenant_id,
            actions=[
                WorkflowAction(
                    type=WorkflowActionType.SCHEDULE_MEETING,
                    parameters={
                        "meeting_type": MeetingType.DAILY_STANDUP,
                        "duration_minutes": 15,
                        "attendees": ["team_members"]
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.SEND_NOTIFICATION,
                    parameters={
                        "type": "email",
                        "recipients": ["team_members"],
                        "subject": "Sprint Started - Daily Standups Scheduled",
                        "message": "Your sprint has started. Daily standups have been scheduled."
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.CREATE_AUDIT_ENTRY,
                    parameters={
                        "type": "sprint_lifecycle",
                        "details": {"action": "sprint_started", "automated": True}
                    }
                )
            ]
        )
        workflows.append(sprint_started)
        
        # Impediment Escalation Workflow
        impediment_escalation = WorkflowRule(
            name="Impediment Escalation",
            description="Escalates impediments based on severity and duration",
            event_type=WorkflowEventType.IMPEDIMENT_RAISED,
            tenant_id=tenant_id,
            conditions=[
                WorkflowCondition(field="severity", operator="in", value=["high", "critical"])
            ],
            actions=[
                WorkflowAction(
                    type=WorkflowActionType.SEND_NOTIFICATION,
                    parameters={
                        "type": "urgent",
                        "recipients": ["scrum_master", "product_owner"],
                        "subject": "Critical Impediment Raised",
                        "message": "A critical impediment has been raised and requires immediate attention."
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.ESCALATE_ISSUE,
                    parameters={
                        "level": "management",
                        "reason": "Critical impediment requires management attention"
                    },
                    delay_seconds=3600  # Escalate after 1 hour
                )
            ]
        )
        workflows.append(impediment_escalation)
        
        # Quality Gate Failure Workflow
        quality_gate_failure = WorkflowRule(
            name="Quality Gate Failure Response",
            description="Responds to quality gate failures with appropriate actions",
            event_type=WorkflowEventType.QUALITY_GATE_FAILED,
            tenant_id=tenant_id,
            actions=[
                WorkflowAction(
                    type=WorkflowActionType.UPDATE_STATUS,
                    parameters={
                        "entity_type": "user_story",
                        "status": "blocked"
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.ASSIGN_TASK,
                    parameters={
                        "task_type": "quality_fix",
                        "assignee_type": "qa_lead"
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.RUN_AGENT_ANALYSIS,
                    parameters={
                        "agent_type": "qa",
                        "analysis_type": "root_cause"
                    }
                )
            ]
        )
        workflows.append(quality_gate_failure)
        
        # Sprint End Workflow
        sprint_end = WorkflowRule(
            name="Sprint Completion Automation",
            description="Automates sprint closure activities",
            event_type=WorkflowEventType.SPRINT_ENDED,
            tenant_id=tenant_id,
            actions=[
                WorkflowAction(
                    type=WorkflowActionType.GENERATE_REPORT,
                    parameters={
                        "type": "sprint_summary",
                        "format": "pdf",
                        "include_metrics": True
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.SCHEDULE_MEETING,
                    parameters={
                        "meeting_type": MeetingType.RETROSPECTIVE,
                        "duration_minutes": 90
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.RUN_AGENT_ANALYSIS,
                    parameters={
                        "agent_type": "scrum_master",
                        "analysis_type": "sprint_analysis"
                    }
                )
            ]
        )
        workflows.append(sprint_end)
        
        return workflows
    
    @staticmethod
    def create_compliance_workflows(tenant_id: UUID) -> List[WorkflowRule]:
        """Create compliance and governance workflows."""
        workflows = []
        
        # SOX Compliance Workflow
        sox_compliance = WorkflowRule(
            name="SOX Compliance Monitoring",
            description="Ensures SOX compliance for financial system changes",
            event_type=WorkflowEventType.STORY_COMPLETED,
            tenant_id=tenant_id,
            conditions=[
                WorkflowCondition(field="components", operator="contains", value="financial")
            ],
            actions=[
                WorkflowAction(
                    type=WorkflowActionType.CREATE_AUDIT_ENTRY,
                    parameters={
                        "type": "sox_compliance",
                        "details": {
                            "change_type": "financial_system",
                            "requires_approval": True
                        }
                    }
                ),
                WorkflowAction(
                    type=WorkflowActionType.SEND_NOTIFICATION,
                    parameters={
                        "type": "compliance",
                        "recipients": ["compliance_officer"],
                        "subject": "SOX Compliance Review Required",
                        "message": "A financial system change has been completed and requires compliance review."
                    }
                )
            ]
        )
        workflows.append(sox_compliance)
        
        return workflows