import curses
import logging

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Assuming enhanced_instrumentation is available in the parent weavergen module
from ..enhanced_instrumentation import semantic_span

tracer = trace.get_tracer(__name__)

from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine
from SpiffWorkflow.task import TaskState

from .instance import Instance


logger = logging.getLogger('spiff_engine')

class BpmnEngine:
    
    def __init__(self, parser, serializer, script_env=None, instance_cls=None):

        self.parser = parser
        self.serializer = serializer
        # Ideally this would be recreated for each instance
        self._script_engine = PythonScriptEngine(script_env)
        self.instance_cls = instance_cls or Instance

    @semantic_span("bpmn_engine", "add_spec")
    def add_spec(self, process_id, bpmn_files, dmn_files):
        self.add_files(bpmn_files, dmn_files)
        try:
            spec = self.parser.get_spec(process_id)
            dependencies = {}  # Simple implementation for now
        except Exception as exc:
            raise exc
        spec_id = self.serializer.create_workflow_spec(spec, dependencies)
        logger.info(f'Added {process_id} with id {spec_id}')
        return spec_id

    def add_collaboration(self, collaboration_id, bpmn_files, dmn_files=None):
        self.add_files(bpmn_files, dmn_files)
        try:
            # Simple implementation - treat collaboration as process for now
            spec = self.parser.get_spec(collaboration_id)
            dependencies = {}
        except Exception as exc:
            raise exc
        spec_id = self.serializer.create_workflow_spec(spec, dependencies)
        logger.info(f'Added {collaboration_id} with id {spec_id}')
        return spec_id

    def add_files(self, bpmn_files, dmn_files):
        self.parser.add_bpmn_files(bpmn_files)
        if dmn_files is not None:
            self.parser.add_dmn_files(dmn_files)

    def list_specs(self):
        return self.serializer.list_specs()

    def delete_workflow_spec(self, spec_id):
        self.serializer.delete_workflow_spec(spec_id)
        logger.info(f'Deleted workflow spec with id {spec_id}')

    @semantic_span("bpmn_engine", "start_workflow")
    def start_workflow(self, spec_id):
        spec, sp_specs = self.serializer.get_workflow_spec(spec_id)
        wf = BpmnWorkflow(spec, sp_specs, script_engine=self._script_engine)
        wf_id = self.serializer.create_workflow(wf, spec_id)
        logger.info(f'Created workflow with id {wf_id}')
        return self.instance_cls(wf_id, wf, save=self.update_workflow)

    def get_workflow(self, wf_id):
        wf = self.serializer.get_workflow(wf_id)
        wf.script_engine = self._script_engine
        return self.instance_cls(wf_id, wf, save=self.update_workflow)

    def update_workflow(self, instance):
        logger.info(f'Saved workflow {instance.wf_id}')
        self.serializer.update_workflow(instance.workflow, instance.wf_id)

    def list_workflows(self, include_completed=False):
        return self.serializer.list_workflows(include_completed)

    def delete_workflow(self, wf_id):
        self.serializer.delete_workflow(wf_id)
        logger.info(f'Deleted workflow with id {wf_id}')

