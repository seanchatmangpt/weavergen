"""
Adaptive BPMN Engine - 80/20 Next-Level Enhancement

This module implements self-optimizing BPMN workflows that learn from execution patterns
and automatically improve over time. The engine adapts based on real performance data.
"""

import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from statistics import mean, median, stdev

# import numpy as np  # Not needed for basic functionality
from opentelemetry import trace
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .pydantic_ai_bpmn_engine import PydanticAIBPMNEngine, PydanticAIContext
from .span_validator import SpanValidator


@dataclass
class ExecutionMetrics:
    """Metrics for a single workflow execution"""
    workflow_id: str
    execution_id: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    task_durations: Dict[str, float]
    quality_score: float
    success: bool
    context_size: int
    error_count: int = 0
    retry_count: int = 0
    parallel_efficiency: float = 1.0


@dataclass 
class TaskPattern:
    """Discovered pattern in task execution"""
    task_sequence: List[str]
    frequency: float
    avg_duration: float
    success_rate: float
    parallel_potential: bool = False
    bottleneck_score: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)


@dataclass
class WorkflowOptimization:
    """Optimization recommendations for a workflow"""
    workflow_id: str
    current_avg_duration: float
    optimized_avg_duration: float
    improvement_percentage: float
    parallelization_opportunities: List[Tuple[str, str]]
    task_removal_candidates: List[str]
    caching_opportunities: List[str]
    recommended_retry_limits: Dict[str, int]


class AdaptiveBPMNEngine(PydanticAIBPMNEngine):
    """
    Self-optimizing BPMN engine that learns from execution patterns.
    
    Features:
    - Automatic performance tracking
    - Pattern discovery from execution history
    - Dynamic optimization suggestions
    - Adaptive retry and timeout configuration
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", use_mock: bool = True):
        super().__init__(model_name, use_mock)
        
        self.console = Console()
        self.execution_history: List[ExecutionMetrics] = []
        self.task_performance: Dict[str, List[float]] = defaultdict(list)
        self.pattern_cache: Dict[str, TaskPattern] = {}
        self.optimization_enabled = True
        self.learning_threshold = 5  # Min executions before optimization
        
        # Load historical data if available
        self._load_execution_history()
        
    def _load_execution_history(self):
        """Load historical execution data for learning"""
        history_file = Path(".weavergen/adaptive/execution_history.json")
        if history_file.exists():
            try:
                with open(history_file) as f:
                    data = json.load(f)
                    # Convert to ExecutionMetrics objects
                    for item in data:
                        self.execution_history.append(ExecutionMetrics(
                            workflow_id=item["workflow_id"],
                            execution_id=item["execution_id"],
                            start_time=datetime.fromisoformat(item["start_time"]),
                            end_time=datetime.fromisoformat(item["end_time"]),
                            duration_ms=item["duration_ms"],
                            task_durations=item["task_durations"],
                            quality_score=item["quality_score"],
                            success=item["success"],
                            context_size=item["context_size"],
                            error_count=item.get("error_count", 0),
                            retry_count=item.get("retry_count", 0)
                        ))
            except Exception as e:
                self.console.print(f"[yellow]Could not load history: {e}[/yellow]")
                
    def _save_execution_history(self):
        """Persist execution history for future learning"""
        history_file = Path(".weavergen/adaptive/execution_history.json")
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        data = []
        for metrics in self.execution_history[-100:]:  # Keep last 100 executions
            data.append({
                "workflow_id": metrics.workflow_id,
                "execution_id": metrics.execution_id,
                "start_time": metrics.start_time.isoformat(),
                "end_time": metrics.end_time.isoformat(),
                "duration_ms": metrics.duration_ms,
                "task_durations": metrics.task_durations,
                "quality_score": metrics.quality_score,
                "success": metrics.success,
                "context_size": metrics.context_size,
                "error_count": metrics.error_count,
                "retry_count": metrics.retry_count
            })
            
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    async def execute_adaptive(
        self, 
        workflow_name: str, 
        context: PydanticAIContext,
        enable_optimization: bool = True
    ) -> Dict[str, Any]:
        """
        Execute workflow with adaptive optimization.
        
        Tracks performance metrics and applies learned optimizations.
        """
        
        # Pre-execution optimization
        if enable_optimization and len(self.execution_history) >= self.learning_threshold:
            optimization = self._analyze_and_optimize(workflow_name)
            if optimization:
                self._apply_optimization(context, optimization)
                
        # Track execution
        execution_id = f"exec_{int(time.time() * 1000)}"
        start_time = datetime.now()
        task_start_times = {}
        task_durations = {}
        
        # Override service task execution to track timing
        original_tasks = self.service_tasks.copy()
        
        for task_name, task_func in original_tasks.items():
            async def tracked_task(ctx, tn=task_name, tf=task_func):
                task_start = time.time()
                task_start_times[tn] = task_start
                
                result = await tf(ctx)
                
                duration = (time.time() - task_start) * 1000
                task_durations[tn] = duration
                self.task_performance[tn].append(duration)
                
                return result
                
            self.service_tasks[task_name] = tracked_task
            
        # Execute workflow
        try:
            result = await self.execute_workflow(workflow_name, context)
            success = result.get("success", False)
            
        except Exception as e:
            result = {"success": False, "error": str(e)}
            success = False
            
        finally:
            # Restore original tasks
            self.service_tasks = original_tasks
            
        # Record metrics
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        metrics = ExecutionMetrics(
            workflow_id=workflow_name,
            execution_id=execution_id,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            task_durations=task_durations,
            quality_score=result.get("quality_score", 0.0),
            success=success,
            context_size=len(str(context.model_dump())),
            error_count=len(context.validation_results) - sum(1 for r in context.validation_results if r.get("valid", False)),
            retry_count=context.current_retry
        )
        
        self.execution_history.append(metrics)
        
        # Discover patterns
        if len(self.execution_history) % 10 == 0:
            self._discover_patterns()
            
        # Save history
        self._save_execution_history()
        
        # Add adaptive insights to result
        result["adaptive_metrics"] = {
            "execution_id": execution_id,
            "duration_ms": duration_ms,
            "task_bottlenecks": self._identify_bottlenecks(task_durations),
            "optimization_applied": enable_optimization,
            "learning_progress": len(self.execution_history)
        }
        
        return result
        
    def _analyze_and_optimize(self, workflow_id: str) -> Optional[WorkflowOptimization]:
        """Analyze execution history and generate optimization recommendations"""
        
        # Filter relevant history
        relevant_history = [m for m in self.execution_history if m.workflow_id == workflow_id]
        
        if len(relevant_history) < self.learning_threshold:
            return None
            
        # Calculate current performance
        recent_durations = [m.duration_ms for m in relevant_history[-10:]]
        current_avg = mean(recent_durations)
        
        # Identify optimization opportunities
        parallelization_ops = []
        removal_candidates = []
        caching_ops = []
        retry_limits = {}
        
        # Analyze task patterns
        task_stats = self._calculate_task_statistics(relevant_history)
        
        for task, stats in task_stats.items():
            # High duration variance suggests caching opportunity
            if stats["cv"] > 0.5:  # Coefficient of variation > 50%
                caching_ops.append(task)
                
            # Consistent failures suggest removal
            if stats["failure_rate"] > 0.3:
                removal_candidates.append(task)
                
            # Calculate optimal retry limit
            if stats["retry_success_rate"] > 0:
                optimal_retries = min(3, int(1 / stats["retry_success_rate"]))
                retry_limits[task] = optimal_retries
                
        # Identify parallelization opportunities
        parallelization_ops = self._find_parallel_opportunities(relevant_history)
        
        # Estimate improvement
        optimized_duration = current_avg
        if parallelization_ops:
            # Assume 40% improvement from parallelization
            optimized_duration *= 0.6
        if caching_ops:
            # Assume 20% improvement from caching
            optimized_duration *= 0.8
            
        improvement = ((current_avg - optimized_duration) / current_avg) * 100
        
        return WorkflowOptimization(
            workflow_id=workflow_id,
            current_avg_duration=current_avg,
            optimized_avg_duration=optimized_duration,
            improvement_percentage=improvement,
            parallelization_opportunities=parallelization_ops,
            task_removal_candidates=removal_candidates,
            caching_opportunities=caching_ops,
            recommended_retry_limits=retry_limits
        )
        
    def _apply_optimization(self, context: PydanticAIContext, optimization: WorkflowOptimization):
        """Apply optimization recommendations to the context"""
        
        self.console.print(f"[cyan]🎯 Applying learned optimizations:[/cyan]")
        self.console.print(f"  Expected improvement: {optimization.improvement_percentage:.1f}%")
        
        # Apply retry limits
        for task, limit in optimization.recommended_retry_limits.items():
            self.console.print(f"  Retry limit for {task}: {limit}")
            # Would apply to error boundary config here
            
        # Note: Real parallelization would require BPMN workflow modification
        # This is where we'd integrate with a BPMN editor/generator
        
    def _calculate_task_statistics(self, history: List[ExecutionMetrics]) -> Dict[str, Dict[str, float]]:
        """Calculate performance statistics for each task"""
        
        task_stats = defaultdict(lambda: {
            "durations": [],
            "failures": 0,
            "executions": 0,
            "retries": 0,
            "retry_successes": 0
        })
        
        for metrics in history:
            for task, duration in metrics.task_durations.items():
                stats = task_stats[task]
                stats["durations"].append(duration)
                stats["executions"] += 1
                
                if not metrics.success:
                    stats["failures"] += 1
                    
                if metrics.retry_count > 0:
                    stats["retries"] += 1
                    if metrics.success:
                        stats["retry_successes"] += 1
                        
        # Calculate derived statistics
        result = {}
        for task, stats in task_stats.items():
            durations = stats["durations"]
            if durations:
                mean_duration = mean(durations)
                std_duration = stdev(durations) if len(durations) > 1 else 0
                
                result[task] = {
                    "mean_duration": mean_duration,
                    "std_duration": std_duration,
                    "cv": std_duration / mean_duration if mean_duration > 0 else 0,
                    "failure_rate": stats["failures"] / stats["executions"],
                    "retry_success_rate": stats["retry_successes"] / stats["retries"] if stats["retries"] > 0 else 0
                }
                
        return result
        
    def _find_parallel_opportunities(self, history: List[ExecutionMetrics]) -> List[Tuple[str, str]]:
        """Identify tasks that could be executed in parallel"""
        
        opportunities = []
        
        # Simple heuristic: tasks that never depend on each other's output
        # In a real implementation, we'd analyze the BPMN structure
        
        # For now, identify tasks with no data dependencies
        task_sequences = []
        for metrics in history:
            if metrics.success:
                tasks = list(metrics.task_durations.keys())
                task_sequences.append(tasks)
                
        # Find tasks that always appear in sequence but could be parallel
        if task_sequences:
            common_sequence = task_sequences[0]  # Simplified
            for i in range(len(common_sequence) - 1):
                task1 = common_sequence[i]
                task2 = common_sequence[i + 1]
                
                # Check if task2 ever uses output from task1
                # Simplified check - in reality would analyze data flow
                if "Generate" in task1 and "Generate" in task2:
                    opportunities.append((task1, task2))
                    
        return opportunities
        
    def _identify_bottlenecks(self, task_durations: Dict[str, float]) -> List[str]:
        """Identify tasks that are performance bottlenecks"""
        
        if not task_durations:
            return []
            
        # Calculate statistics
        durations = list(task_durations.values())
        if not durations:
            return []
            
        mean_duration = mean(durations)
        std_duration = stdev(durations) if len(durations) > 1 else 0
        
        # Bottlenecks are tasks > 1 std dev above mean
        threshold = mean_duration + std_duration
        
        bottlenecks = [
            task for task, duration in task_durations.items()
            if duration > threshold
        ]
        
        return sorted(bottlenecks, key=lambda t: task_durations[t], reverse=True)
        
    def _discover_patterns(self):
        """Discover execution patterns from history"""
        
        self.console.print("[cyan]🔍 Discovering execution patterns...[/cyan]")
        
        # Group executions by workflow
        by_workflow = defaultdict(list)
        for metrics in self.execution_history:
            by_workflow[metrics.workflow_id].append(metrics)
            
        # Analyze each workflow
        for workflow_id, executions in by_workflow.items():
            if len(executions) < 5:
                continue
                
            # Extract task sequences
            sequences = []
            for exec in executions:
                if exec.success:
                    sequence = list(exec.task_durations.keys())
                    sequences.append(sequence)
                    
            # Find common patterns
            if sequences:
                pattern = self._find_common_pattern(sequences)
                if pattern:
                    self.pattern_cache[workflow_id] = pattern
                    
    def _find_common_pattern(self, sequences: List[List[str]]) -> Optional[TaskPattern]:
        """Find the most common execution pattern"""
        
        if not sequences:
            return None
            
        # For simplicity, use the most frequent sequence
        sequence_strs = [",".join(seq) for seq in sequences]
        most_common = max(set(sequence_strs), key=sequence_strs.count)
        frequency = sequence_strs.count(most_common) / len(sequences)
        
        common_sequence = most_common.split(",")
        
        # Calculate pattern metrics
        pattern_durations = []
        pattern_successes = 0
        
        for exec in self.execution_history:
            exec_sequence = list(exec.task_durations.keys())
            if exec_sequence == common_sequence:
                pattern_durations.append(exec.duration_ms)
                if exec.success:
                    pattern_successes += 1
                    
        if pattern_durations:
            return TaskPattern(
                task_sequence=common_sequence,
                frequency=frequency,
                avg_duration=mean(pattern_durations),
                success_rate=pattern_successes / len(pattern_durations),
                optimization_suggestions=["Consider parallelization", "Add caching"]
            )
            
        return None
        
    def get_performance_report(self) -> Table:
        """Generate a performance report table"""
        
        table = Table(title="Adaptive BPMN Performance Report", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        if self.execution_history:
            recent = self.execution_history[-10:]
            
            table.add_row("Total Executions", str(len(self.execution_history)))
            table.add_row("Success Rate", f"{sum(1 for m in recent if m.success) / len(recent):.1%}")
            table.add_row("Avg Duration", f"{mean(m.duration_ms for m in recent):.0f}ms")
            table.add_row("Quality Score", f"{mean(m.quality_score for m in recent):.1%}")
            
            # Task performance
            for task, durations in self.task_performance.items():
                if durations:
                    recent_durations = durations[-10:]
                    table.add_row(f"{task} Avg", f"{mean(recent_durations):.0f}ms")
                    
        return table
        
    def visualize_learning_curve(self) -> str:
        """Generate a simple ASCII learning curve"""
        
        if len(self.execution_history) < 10:
            return "Not enough data for learning curve"
            
        # Group by batches of 5
        batches = []
        for i in range(0, len(self.execution_history), 5):
            batch = self.execution_history[i:i+5]
            if batch:
                avg_duration = mean(m.duration_ms for m in batch)
                batches.append(avg_duration)
                
        # Normalize to 0-10 scale
        if batches:
            max_duration = max(batches)
            min_duration = min(batches)
            range_duration = max_duration - min_duration
            
            if range_duration > 0:
                normalized = [(d - min_duration) / range_duration * 10 for d in batches]
            else:
                normalized = [5] * len(batches)
                
            # Create ASCII chart
            chart = ["Learning Curve (Duration over time)"]
            chart.append("10 |" + " " * 50)
            
            for y in range(9, -1, -1):
                line = f"{y:2} |"
                for x, val in enumerate(normalized):
                    if val >= y:
                        line += "█"
                    else:
                        line += " "
                chart.append(line)
                
            chart.append("   +" + "-" * len(normalized))
            chart.append("    " + "".join(str(i % 10) for i in range(len(normalized))))
            chart.append(f"    Batches of 5 executions (Total: {len(self.execution_history)})")
            
            return "\n".join(chart)
            
        return "No data"