"""Service task environment for WeaverGen BPMN workflows with span support."""

import json
import logging
from datetime import datetime
from typing import Any, Dict

from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from ..enhanced_instrumentation import (
    service_task_span, 
    add_span_event,
    get_current_span
)
from ..semconv import (
    COMPONENT_TYPE, COMPONENT_TYPE__GENERATOR,
    FILES_GENERATED, LANGUAGE, SEMANTIC_COMPLIANCE
)

logger = logging.getLogger(__name__)


class WeaverGenServiceEnvironment(TaskDataEnvironment):
    """Service task environment for WeaverGen operations with OpenTelemetry spans."""

    def __init__(self, extra_context: Dict[str, Any] = None):
        context = {
            'datetime': datetime,
            'json': json,
        }
        if extra_context:
            context.update(extra_context)
        super().__init__(context)

    def call_service(self, task_data: Dict[str, Any], operation_name: str, operation_params: Dict[str, Any]) -> str:
        """Handle service task calls for WeaverGen operations with span tracking."""
        
        with service_task_span(operation_name, operation_params) as span:
            logger.info(f"Calling service: {operation_name} with params: {operation_params}")
            
            # Add task data size as span attribute
            if task_data:
                span.set_attribute("task_data.size", len(json.dumps(task_data)))
            
            try:
                if operation_name == 'generate_semantic_code':
                    result = self._generate_semantic_code(operation_params, span)
                elif operation_name == 'validate_semantic_convention':
                    result = self._validate_semantic_convention(operation_params, span)
                elif operation_name == 'execute_weaver_forge':
                    result = self._execute_weaver_forge(operation_params, span)
                else:
                    raise ValueError(f"Unknown service operation: {operation_name}")
                
                # Add result size to span
                result_json = json.dumps(result)
                span.set_attribute("result.size", len(result_json))
                span.set_attribute("result.status", result.get('status', 'unknown'))
                
                return result_json
                
            except Exception as e:
                span.record_exception(e)
                logger.error(f"Service task failed: {e}")
                raise
    
    def _generate_semantic_code(self, params: Dict[str, Any], span) -> Dict[str, Any]:
        """Generate semantic code with span tracking."""
        add_span_event("generate_semantic_code.start", {
            "semantic_file": params.get('semantic_file', 'unknown'),
            "target_language": params.get('target_language', 'unknown')
        })
        
        # Placeholder for actual implementation
        generated_files = [
            f"{params.get('semantic_file', 'output')}.{params.get('target_language', 'py')}"
        ]
        
        span.set_attribute(FILES_GENERATED, len(generated_files))
        span.set_attribute(LANGUAGE, params.get('target_language', 'unknown'))
        
        add_span_event("generate_semantic_code.complete", {
            "files_generated": len(generated_files)
        })
        
        return {
            'status': 'success',
            'operation': 'generate_semantic_code',
            'generated_files': generated_files,
            'language': params.get('target_language', 'python')
        }
    
    def _validate_semantic_convention(self, params: Dict[str, Any], span) -> Dict[str, Any]:
        """Validate semantic convention with span tracking."""
        add_span_event("validate_semantic_convention.start", {
            "semantic_file": params.get('semantic_file', 'unknown')
        })
        
        # Placeholder validation logic
        is_valid = True
        validation_errors = []
        
        span.set_attribute("validation.valid", is_valid)
        span.set_attribute("validation.error_count", len(validation_errors))
        
        add_span_event("validate_semantic_convention.complete", {
            "is_valid": is_valid,
            "error_count": len(validation_errors)
        })
        
        return {
            'status': 'success',
            'operation': 'validate_semantic_convention',
            'valid': is_valid,
            'errors': validation_errors
        }
    
    def _execute_weaver_forge(self, params: Dict[str, Any], span) -> Dict[str, Any]:
        """Execute Weaver Forge with span tracking."""
        add_span_event("execute_weaver_forge.start", {
            "input_files": str(params.get('generated_files', []))
        })
        
        # Placeholder for Weaver Forge execution
        output_message = 'Weaver Forge executed successfully'
        
        span.set_attribute("weaver_forge.status", "success")
        span.set_attribute("weaver_forge.output_length", len(output_message))
        
        add_span_event("execute_weaver_forge.complete", {
            "status": "success"
        })
        
        return {
            'status': 'success',
            'operation': 'execute_weaver_forge',
            'output': output_message,
            'processed_files': params.get('generated_files', [])
        }