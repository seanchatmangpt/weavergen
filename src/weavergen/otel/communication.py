"""OTel span-based communication system for WeaverGen agents."""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Set
from enum import Enum

from opentelemetry import trace
from opentelemetry.trace import Span

from .spans import span_manager

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """Types of messages in the communication system."""
    STATEMENT = "statement"
    MOTION = "motion"
    SECOND = "second"
    VOTE = "vote"
    REPORT = "report"
    QUERY = "query"
    RESPONSE = "response"
    NOTIFICATION = "notification"

class Priority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class OTelMessage:
    """Message structure for OTel span-based communication."""
    
    id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    trace_id: str
    span_id: str
    priority: Priority = Priority.NORMAL
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        sender_id: str,
        receiver_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "OTelMessage":
        """Create a new message with auto-generated fields."""
        current_span = trace.get_current_span()
        span_context = current_span.get_span_context()
        
        return cls(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.utcnow(),
            trace_id=f"{span_context.trace_id:032x}",
            span_id=f"{span_context.span_id:016x}",
            priority=priority,
            metadata=metadata or {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for span attributes."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class OTelCommunicationBus:
    """Communication bus using OTel spans for agent coordination."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[OTelMessage] = []
        self.active_agents: Set[str] = set()
        
    def register_agent(self, agent_id: str) -> None:
        """Register an agent with the communication bus."""
        self.active_agents.add(agent_id)
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        logger.info(f"Agent {agent_id} registered with communication bus")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the communication bus."""
        self.active_agents.discard(agent_id)
        self.subscribers.pop(agent_id, None)
        logger.info(f"Agent {agent_id} unregistered from communication bus")
    
    def subscribe(
        self, 
        agent_id: str, 
        handler: Callable[[OTelMessage], None]
    ) -> None:
        """Subscribe an agent to receive messages."""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(handler)
        logger.debug(f"Agent {agent_id} subscribed to messages")
    
    async def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OTelMessage:
        """Send a message via OTel spans.
        
        Args:
            sender_id: Sender agent ID
            receiver_id: Receiver agent ID  
            message_type: Type of message
            content: Message content
            priority: Message priority
            metadata: Additional metadata
            
        Returns:
            OTelMessage: The sent message
        """
        message = OTelMessage.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            priority=priority,
            metadata=metadata
        )
        
        # Create communication span
        with span_manager.communication_span(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type.value,
            attributes={
                "message.id": message.id,
                "message.priority": priority.value,
                "message.content_size": len(json.dumps(content)),
                **message.to_dict()
            }
        ) as span:
            # Store message in history
            self.message_history.append(message)
            
            # Deliver to subscribers
            await self._deliver_message(message, span)
            
            logger.info(
                f"Message {message.id} sent from {sender_id} to {receiver_id} "
                f"(type: {message_type.value})"
            )
            
        return message
    
    async def _deliver_message(self, message: OTelMessage, span: Span) -> None:
        """Deliver message to appropriate handlers."""
        receivers = []
        
        # Targeted delivery
        if message.receiver_id in self.subscribers:
            receivers.extend(self.subscribers[message.receiver_id])
        
        # Broadcast delivery (receiver_id = "all")
        if message.receiver_id == "all":
            for agent_id, handlers in self.subscribers.items():
                if agent_id != message.sender_id:  # Don't send to sender
                    receivers.extend(handlers)
        
        # Deliver to all handlers
        delivery_tasks = []
        for handler in receivers:
            task = asyncio.create_task(self._safe_deliver(handler, message))
            delivery_tasks.append(task)
        
        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)
            span.set_attribute("message.delivered_count", len(delivery_tasks))
        else:
            logger.warning(f"No handlers found for message {message.id}")
            span.set_attribute("message.delivered_count", 0)
    
    async def _safe_deliver(
        self, 
        handler: Callable[[OTelMessage], None], 
        message: OTelMessage
    ) -> None:
        """Safely deliver message to handler with error handling."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
        except Exception as e:
            logger.error(f"Error delivering message {message.id}: {e}")
    
    def broadcast_message(
        self,
        sender_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> asyncio.Task:
        """Broadcast message to all agents.
        
        Args:
            sender_id: Sender agent ID
            message_type: Type of message
            content: Message content
            priority: Message priority
            metadata: Additional metadata
            
        Returns:
            asyncio.Task: Task for the broadcast operation
        """
        return asyncio.create_task(
            self.send_message(
                sender_id=sender_id,
                receiver_id="all",
                message_type=message_type,
                content=content,
                priority=priority,
                metadata=metadata
            )
        )
    
    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: Optional[int] = None
    ) -> List[OTelMessage]:
        """Get message history with optional filtering.
        
        Args:
            agent_id: Filter by sender or receiver
            message_type: Filter by message type
            limit: Limit number of results
            
        Returns:
            List[OTelMessage]: Filtered message history
        """
        messages = self.message_history
        
        if agent_id:
            messages = [
                m for m in messages 
                if m.sender_id == agent_id or m.receiver_id == agent_id
            ]
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        # Sort by timestamp (newest first)
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        
        if limit:
            messages = messages[:limit]
        
        return messages
    
    def get_stats(self) -> Dict[str, Any]:
        """Get communication bus statistics."""
        return {
            "active_agents": len(self.active_agents),
            "total_messages": len(self.message_history),
            "message_types": {
                msg_type.value: len([
                    m for m in self.message_history 
                    if m.message_type == msg_type
                ])
                for msg_type in MessageType
            },
            "agents": list(self.active_agents)
        }
    
    def clear_history(self) -> None:
        """Clear message history."""
        self.message_history.clear()
        logger.info("Communication bus message history cleared")

# Global communication bus instance
communication_bus = OTelCommunicationBus()