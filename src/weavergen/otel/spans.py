"""Span utilities for enhanced tracing in WeaverGen."""

import functools
import logging
from contextlib import contextmanager
from typing import Any, Dict, Optional, Union, Callable
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .instrumentation import get_tracer

logger = logging.getLogger(__name__)

class SpanManager:
    """Manages span creation and context for WeaverGen operations."""
    
    def __init__(self, tracer_name: str = "weavergen"):
        self.tracer = get_tracer(tracer_name)
    
    @contextmanager
    def operation_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        component: Optional[str] = None
    ):
        """Create a span for a WeaverGen operation.
        
        Args:
            name: Span name
            attributes: Additional span attributes
            component: Component name (agents, meetings, etc.)
        """
        span_attributes = {
            "weavergen.operation": name,
            "weavergen.version": "0.1.0",
        }
        
        if component:
            span_attributes["weavergen.component"] = component
            
        if attributes:
            span_attributes.update(attributes)
        
        with self.tracer.start_as_current_span(
            name=f"weavergen.{name}",
            attributes=span_attributes
        ) as span:
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    @contextmanager 
    def agent_span(
        self,
        agent_id: str,
        action: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Create a span for agent operations.
        
        Args:
            agent_id: Unique agent identifier
            action: Action being performed
            attributes: Additional attributes
        """
        span_attributes = {
            "agent.id": agent_id,
            "agent.action": action,
            "weavergen.component": "agents",
        }
        
        if attributes:
            span_attributes.update(attributes)
            
        with self.operation_span(
            f"agent.{action}",
            attributes=span_attributes,
            component="agents"
        ) as span:
            yield span

    @contextmanager
    def meeting_span(
        self,
        meeting_id: str,
        meeting_type: str,
        action: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Create a span for meeting operations.
        
        Args:
            meeting_id: Unique meeting identifier
            meeting_type: Type of meeting (roberts, scrum, dev)
            action: Action being performed  
            attributes: Additional attributes
        """
        span_attributes = {
            "meeting.id": meeting_id,
            "meeting.type": meeting_type,
            "meeting.action": action,
            "weavergen.component": "meetings",
        }
        
        if attributes:
            span_attributes.update(attributes)
            
        with self.operation_span(
            f"meeting.{action}",
            attributes=span_attributes,
            component="meetings"
        ) as span:
            yield span

    @contextmanager
    def communication_span(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Create a span for agent communication.
        
        Args:
            sender_id: Sender agent ID
            receiver_id: Receiver agent ID  
            message_type: Type of message
            attributes: Additional attributes
        """
        span_attributes = {
            "communication.sender": sender_id,
            "communication.receiver": receiver_id,
            "communication.type": message_type,
            "weavergen.component": "communication",
        }
        
        if attributes:
            span_attributes.update(attributes)
            
        with self.operation_span(
            f"communication.{message_type}",
            attributes=span_attributes,
            component="communication"
        ) as span:
            yield span

# Global span manager instance
span_manager = SpanManager()

def create_operation_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    component: Optional[str] = None
):
    """Convenience function to create operation spans.
    
    Args:
        name: Span name
        attributes: Additional attributes
        component: Component name
        
    Returns:
        Context manager for the span
    """
    return span_manager.operation_span(name, attributes, component)

def trace_operation(
    name: Optional[str] = None,
    component: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
):
    """Decorator to trace function execution.
    
    Args:
        name: Custom span name (defaults to function name)
        component: Component name
        attributes: Additional span attributes
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            span_name = name or func.__name__
            span_attributes = attributes or {}
            
            with span_manager.operation_span(
                span_name, 
                span_attributes, 
                component
            ) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.record_exception(e)
                    raise
                    
        return wrapper
    return decorator

async def trace_async_operation(
    name: Optional[str] = None,
    component: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
):
    """Decorator to trace async function execution.
    
    Args:
        name: Custom span name (defaults to function name)
        component: Component name
        attributes: Additional span attributes
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            span_name = name or func.__name__
            span_attributes = attributes or {}
            
            with span_manager.operation_span(
                span_name,
                span_attributes,
                component
            ) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                span.set_attribute("function.async", True)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.record_exception(e)
                    raise
                    
        return wrapper
    return decorator