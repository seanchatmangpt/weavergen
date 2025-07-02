"""Workflow instance with span support."""

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.specs.mixins.events.event_types import CatchingEvent

from ..enhanced_instrumentation import (
    add_span_event,
    get_current_span
)


class Instance:

    def __init__(self, wf_id, workflow, save=None):
        self.wf_id = wf_id
        self.workflow = workflow
        self.step = False
        self.task_filter = {}
        self.filtered_tasks = []
        self._save = save

    @property
    def name(self):
        return self.workflow.spec.name

    @property
    def tasks(self):
        return self.workflow.get_tasks()

    @property
    def ready_tasks(self):
        return self.workflow.get_tasks(state=TaskState.READY)

    @property
    def ready_human_tasks(self):
        return self.workflow.get_tasks(state=TaskState.READY, manual=True)

    @property
    def ready_engine_tasks(self):
        return self.workflow.get_tasks(state=TaskState.READY, manual=False)

    @property
    def waiting_tasks(self):
        return self.workflow.get_tasks(state=TaskState.WAITING)

    @property
    def finished_tasks(self):
        return self.workflow.get_tasks(state=TaskState.FINISHED_MASK)

    @property
    def running_subprocesses(self):
        return [sp for sp in self.workflow.subprocesses.values() if not sp.is_completed()]

    @property
    def subprocesses(self):
        return [sp for sp in self.workflow.subprocesses.values()]

    @property
    def data(self):
        return self.workflow.data

    def get_task_display_info(self, task):
        return {
            'depth': task.depth,
            'state': TaskState.get_name(task.state),
            'name': task.task_spec.bpmn_name or task.task_spec.name,
            'lane': task.task_spec.lane,
        }

    def update_task_filter(self, task_filter=None):
        if task_filter is not None:
            self.task_filter.update(task_filter)
        self.filtered_tasks = [t for t in self.workflow.get_tasks(**self.task_filter)]

    def run_task(self, task, data=None):
        """Run a single task with span tracking."""
        add_span_event("task.run_start", {
            "task_id": task.id,
            "task_name": task.task_spec.name,
            "task_state": TaskState.get_name(task.state)
        })
        
        if data is not None:
            task.set_data(**data)
            add_span_event("task.data_set", {"task_id": task.id})
            
        task.run()
        
        add_span_event("task.run_complete", {
            "task_id": task.id,
            "task_state": TaskState.get_name(task.state)
        })
        
        if not self.step:
            self.run_until_user_input_required()
        else:
            self.update_task_filter()

    def run_until_user_input_required(self):
        """Run workflow until user input is required, with span tracking."""
        add_span_event("workflow.auto_run_start", {
            "workflow_id": self.wf_id,
            "ready_tasks": len(self.ready_engine_tasks)
        })
        
        tasks_executed = 0
        task = self.workflow.get_next_task(state=TaskState.READY, manual=False)
        
        while task is not None:
            add_span_event("task.auto_run", {
                "task_id": task.id,
                "task_name": task.task_spec.name
            })
            
            task.run()
            tasks_executed += 1
            
            self.run_ready_events()
            task = self.workflow.get_next_task(state=TaskState.READY, manual=False)
        
        add_span_event("workflow.auto_run_complete", {
            "workflow_id": self.wf_id,
            "tasks_executed": tasks_executed,
            "is_completed": self.workflow.is_completed()
        })
        
        # Add span attributes
        span = get_current_span()
        if span:
            span.set_attribute("workflow.tasks_executed", tasks_executed)
            span.set_attribute("workflow.manual_tasks_waiting", len(self.ready_human_tasks))
        
        self.update_task_filter()

    def run_ready_events(self):
        self.workflow.refresh_waiting_tasks()
        task = self.workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
        while task is not None:
            task.run()
            task = self.workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
        self.update_task_filter()

    def save(self):
        self._save(self)

