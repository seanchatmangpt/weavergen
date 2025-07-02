# Ultra-Advanced Base ServiceTask PRD

## Executive Summary

This PRD defines the requirements for an ultra-advanced, elegant base ServiceTask class that provides automatic OpenTelemetry instrumentation, intelligent filepath tracking, performance monitoring, and sophisticated error handling. This base class will serve as the foundation for all service tasks in the WeaverGen BPMN workflow system, ensuring consistent observability, maintainability, and developer experience.

## Mission Statement

**Create an intelligent, self-instrumenting base ServiceTask that automatically captures context, performance metrics, and operational insights while providing an elegant, developer-friendly interface for implementing business logic in BPMN workflows.**

## Core Vision

Transform service task development from manual instrumentation and boilerplate code to an elegant, declarative experience where developers focus on business logic while the framework automatically handles observability, performance monitoring, and operational excellence.

## Target Users

### Primary Users
- **BPMN Workflow Developers**: Engineers implementing service tasks for business processes
- **DevOps Engineers**: Teams monitoring and maintaining workflow performance
- **SRE Teams**: Site reliability engineers managing production workflows

### Secondary Users
- **AI Code Assistants**: AI tools that generate service task implementations
- **Code Reviewers**: Engineers reviewing service task implementations
- **Platform Architects**: Engineers designing workflow patterns and standards

## Key Requirements

### 1. Automatic OpenTelemetry Instrumentation

#### 1.1 Context-Aware Span Creation
- **Automatic span naming**: Generate meaningful span names from class and method names
- **Context inheritance**: Automatically inherit parent span context from workflow
- **Span attributes**: Auto-populate common attributes (class, method, workflow_id, etc.)
- **Custom attributes**: Support for declarative attribute definition

#### 1.2 Filepath and Resource Tracking
- **Automatic filepath detection**: Detect and track file operations from method parameters
- **Resource monitoring**: Track file sizes, modification times, and access patterns
- **Dependency tracking**: Automatically identify and track external dependencies
- **I/O metrics**: Capture read/write operations, file counts, and data volumes

#### 1.3 Performance Metrics
- **Execution timing**: Automatic duration tracking with percentile analysis
- **Memory usage**: Track memory allocation and garbage collection patterns
- **CPU utilization**: Monitor CPU usage during task execution
- **Resource consumption**: Track disk I/O, network calls, and external API usage

### 2. Intelligent Error Handling

#### 2.1 Contextual Error Capture
- **Error classification**: Automatically categorize errors (validation, I/O, network, etc.)
- **Error context**: Capture relevant context at error time (input data, file paths, etc.)
- **Error correlation**: Link errors to specific workflow instances and data
- **Recovery suggestions**: Provide intelligent recovery recommendations

#### 2.2 Graceful Degradation
- **Retry mechanisms**: Intelligent retry with exponential backoff
- **Circuit breaker**: Automatic circuit breaker for external dependencies
- **Fallback strategies**: Configurable fallback mechanisms
- **Error propagation**: Proper error propagation through workflow hierarchy

### 3. Elegant Developer Experience

#### 3.1 Declarative Configuration
- **Decorator-based configuration**: Use decorators for task configuration
- **Type hints integration**: Full type hint support with runtime validation
- **Configuration inheritance**: Inherit configuration from base classes
- **Environment-aware**: Automatic configuration based on environment

#### 3.2 Intuitive API Design
- **Fluent interface**: Chainable method calls for complex operations
- **Context managers**: Elegant context management for resource handling
- **Async support**: Native async/await support for I/O operations
- **Batch operations**: Support for batch processing with progress tracking

### 4. Advanced Monitoring and Analytics

#### 4.1 Real-time Metrics
- **Custom metrics**: Support for custom business metrics
- **Histograms**: Automatic histogram creation for performance data
- **Counters**: Track operation counts and success/failure rates
- **Gauges**: Monitor resource usage and system state

#### 4.2 Predictive Analytics
- **Performance prediction**: Predict execution time based on input size
- **Resource forecasting**: Forecast resource requirements
- **Anomaly detection**: Detect performance anomalies and unusual patterns
- **Trend analysis**: Analyze performance trends over time

## Technical Architecture

### 1. Base ServiceTask Class Design

```python
@dataclass
class ServiceTaskConfig:
    """Configuration for service task behavior."""
    name: str
    description: str = ""
    timeout: Optional[float] = None
    retry_count: int = 3
    retry_backoff: float = 1.5
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    enable_performance_tracking: bool = True
    enable_file_tracking: bool = True
    enable_memory_tracking: bool = True
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: List[str] = field(default_factory=list)


class UltraAdvancedServiceTask:
    """Ultra-advanced base class for all service tasks."""
    
    def __init__(self, config: ServiceTaskConfig):
        self.config = config
        self._tracer = trace.get_tracer(self.__class__.__name__)
        self._metrics = self._setup_metrics()
        self._circuit_breaker = self._setup_circuit_breaker()
        self._file_tracker = self._setup_file_tracker()
        self._performance_tracker = self._setup_performance_tracker()
    
    @contextmanager
    def task_span(self, operation_name: str, **attributes):
        """Create a task span with automatic context and attributes."""
        with self._tracer.start_as_current_span(
            f"{self.config.name}.{operation_name}",
            attributes=self._build_span_attributes(attributes)
        ) as span:
            try:
                # Auto-detect file operations
                self._file_tracker.start_tracking(span)
                
                # Start performance monitoring
                self._performance_tracker.start_monitoring(span)
                
                yield span
                
                # Record success metrics
                self._record_success_metrics(span)
                
            except Exception as e:
                # Record error metrics and context
                self._record_error_metrics(span, e)
                raise
    
    def execute_with_retry(self, operation: Callable, *args, **kwargs):
        """Execute operation with intelligent retry logic."""
        for attempt in range(self.config.retry_count + 1):
            try:
                with self.task_span("execute_with_retry") as span:
                    span.set_attribute("retry.attempt", attempt)
                    
                    # Check circuit breaker
                    if self._circuit_breaker.is_open():
                        raise CircuitBreakerOpenError("Circuit breaker is open")
                    
                    result = operation(*args, **kwargs)
                    
                    # Record success
                    self._circuit_breaker.record_success()
                    return result
                    
            except Exception as e:
                self._circuit_breaker.record_failure()
                
                if attempt == self.config.retry_count:
                    raise
                
                # Exponential backoff
                wait_time = self.config.retry_backoff ** attempt
                time.sleep(wait_time)
    
    def track_file_operations(self, file_paths: List[Path]):
        """Track file operations with automatic metrics."""
        with self.task_span("track_file_operations") as span:
            for file_path in file_paths:
                if file_path.exists():
                    stat = file_path.stat()
                    span.set_attribute(f"file.{file_path.name}.size", stat.st_size)
                    span.set_attribute(f"file.{file_path.name}.modified", stat.st_mtime)
                    span.set_attribute(f"file.{file_path.name}.permissions", oct(stat.st_mode))
    
    def measure_performance(self, operation_name: str):
        """Decorator for measuring operation performance."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.task_span(f"measure_performance.{operation_name}") as span:
                    start_time = time.perf_counter()
                    start_memory = psutil.Process().memory_info().rss
                    
                    try:
                        result = func(*args, **kwargs)
                        
                        # Record performance metrics
                        duration = time.perf_counter() - start_time
                        memory_used = psutil.Process().memory_info().rss - start_memory
                        
                        span.set_attribute("performance.duration_ms", duration * 1000)
                        span.set_attribute("performance.memory_bytes", memory_used)
                        
                        return result
                        
                    except Exception as e:
                        span.record_exception(e)
                        raise
            
            return wrapper
        return decorator
```

### 2. File Tracking System

```python
class IntelligentFileTracker:
    """Intelligent file operation tracking and analysis."""
    
    def __init__(self):
        self._file_cache = {}
        self._operation_history = []
    
    def start_tracking(self, span):
        """Start tracking file operations for a span."""
        self._current_span = span
        self._current_operations = []
    
    def track_file_read(self, file_path: Path, content_length: int = None):
        """Track file read operations."""
        operation = {
            'type': 'read',
            'path': str(file_path),
            'size': content_length or file_path.stat().st_size if file_path.exists() else 0,
            'timestamp': time.time()
        }
        self._current_operations.append(operation)
        
        # Add to span attributes
        self._current_span.set_attribute(f"file.read.{file_path.name}", operation['size'])
    
    def track_file_write(self, file_path: Path, content_length: int = None):
        """Track file write operations."""
        operation = {
            'type': 'write',
            'path': str(file_path),
            'size': content_length or 0,
            'timestamp': time.time()
        }
        self._current_operations.append(operation)
        
        # Add to span attributes
        self._current_span.set_attribute(f"file.write.{file_path.name}", operation['size'])
    
    def analyze_file_patterns(self):
        """Analyze file operation patterns for optimization."""
        patterns = {
            'read_heavy': [],
            'write_heavy': [],
            'large_files': [],
            'frequent_access': []
        }
        
        for operation in self._operation_history:
            if operation['size'] > 1024 * 1024:  # 1MB
                patterns['large_files'].append(operation['path'])
            
            # Analyze access patterns
            access_count = sum(1 for op in self._operation_history 
                             if op['path'] == operation['path'])
            if access_count > 10:
                patterns['frequent_access'].append(operation['path'])
        
        return patterns
```

### 3. Performance Tracking System

```python
class AdvancedPerformanceTracker:
    """Advanced performance tracking and analysis."""
    
    def __init__(self):
        self._metrics = {}
        self._baselines = {}
        self._anomaly_detector = self._setup_anomaly_detector()
    
    def start_monitoring(self, span):
        """Start performance monitoring for a span."""
        self._current_span = span
        self._start_time = time.perf_counter()
        self._start_memory = psutil.Process().memory_info()
        self._start_cpu = psutil.Process().cpu_percent()
    
    def end_monitoring(self):
        """End performance monitoring and record metrics."""
        duration = time.perf_counter() - self._start_time
        end_memory = psutil.Process().memory_info()
        end_cpu = psutil.Process().cpu_percent()
        
        # Calculate metrics
        memory_delta = end_memory.rss - self._start_memory.rss
        cpu_usage = (end_cpu + self._start_cpu) / 2
        
        # Record metrics
        self._current_span.set_attribute("performance.duration_ms", duration * 1000)
        self._current_span.set_attribute("performance.memory_delta_bytes", memory_delta)
        self._current_span.set_attribute("performance.cpu_percent", cpu_usage)
        
        # Check for anomalies
        self._check_performance_anomalies(duration, memory_delta, cpu_usage)
    
    def _check_performance_anomalies(self, duration, memory_delta, cpu_usage):
        """Check for performance anomalies."""
        operation_name = self._current_span.name
        
        if operation_name not in self._baselines:
            self._baselines[operation_name] = {
                'duration': duration,
                'memory': memory_delta,
                'cpu': cpu_usage
            }
            return
        
        baseline = self._baselines[operation_name]
        
        # Check for significant deviations
        duration_ratio = duration / baseline['duration']
        memory_ratio = memory_delta / baseline['memory'] if baseline['memory'] != 0 else 1
        
        if duration_ratio > 2.0 or memory_ratio > 2.0:
            self._current_span.add_event("performance.anomaly_detected", {
                "duration_ratio": duration_ratio,
                "memory_ratio": memory_ratio,
                "baseline_duration": baseline['duration'],
                "baseline_memory": baseline['memory']
            })
```

### 4. Circuit Breaker Implementation

```python
class IntelligentCircuitBreaker:
    """Intelligent circuit breaker with adaptive thresholds."""
    
    def __init__(self, threshold: int, timeout: float):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return False
            return True
        return False
    
    def record_success(self):
        """Record a successful operation."""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.threshold:
            self.state = "OPEN"
```

## Usage Examples

### 1. Basic Service Task Implementation

```python
class FileProcessingTask(UltraAdvancedServiceTask):
    """Example file processing service task."""
    
    def __init__(self):
        config = ServiceTaskConfig(
            name="file_processing",
            description="Process files with automatic tracking",
            timeout=30.0,
            retry_count=3,
            enable_file_tracking=True,
            enable_performance_tracking=True
        )
        super().__init__(config)
    
    @measure_performance("process_files")
    def process_files(self, input_files: List[Path], output_dir: Path):
        """Process files with automatic instrumentation."""
        with self.task_span("process_files") as span:
            # Track input files
            self.track_file_operations(input_files)
            
            # Process files
            results = []
            for file_path in input_files:
                result = self.execute_with_retry(
                    self._process_single_file, file_path, output_dir
                )
                results.append(result)
            
            # Track output directory
            self.track_file_operations([output_dir])
            
            span.set_attribute("files.processed", len(results))
            return results
    
    def _process_single_file(self, file_path: Path, output_dir: Path):
        """Process a single file."""
        with self.task_span("process_single_file") as span:
            span.set_attribute("input_file", str(file_path))
            span.set_attribute("output_dir", str(output_dir))
            
            # File processing logic here
            output_file = output_dir / f"processed_{file_path.name}"
            # ... processing logic ...
            
            return str(output_file)
```

### 2. Advanced Service Task with Custom Metrics

```python
class DataAnalysisTask(UltraAdvancedServiceTask):
    """Advanced data analysis service task."""
    
    def __init__(self):
        config = ServiceTaskConfig(
            name="data_analysis",
            description="Analyze data with custom metrics",
            custom_metrics=["data_quality_score", "processing_efficiency"],
            custom_attributes={
                "analysis_type": "statistical",
                "data_source": "database"
            }
        )
        super().__init__(config)
    
    def analyze_dataset(self, dataset_path: Path, analysis_config: Dict):
        """Analyze dataset with advanced tracking."""
        with self.task_span("analyze_dataset") as span:
            # Track dataset file
            self.track_file_operations([dataset_path])
            
            # Custom metrics
            quality_score = self._calculate_quality_score(dataset_path)
            efficiency = self._calculate_efficiency(analysis_config)
            
            span.set_attribute("custom.data_quality_score", quality_score)
            span.set_attribute("custom.processing_efficiency", efficiency)
            
            # Analysis logic
            results = self.execute_with_retry(
                self._perform_analysis, dataset_path, analysis_config
            )
            
            return results
```

## Success Metrics

### 1. Developer Experience Metrics
- **Time to implement**: Reduce service task implementation time by 70%
- **Code reduction**: Reduce boilerplate code by 80%
- **Error reduction**: Reduce instrumentation errors by 90%
- **Developer satisfaction**: Achieve 4.5+ rating on developer experience surveys

### 2. Observability Metrics
- **Span coverage**: Achieve 100% span coverage for all service tasks
- **Attribute completeness**: Ensure 95% of spans have relevant attributes
- **Error tracking**: Capture 100% of errors with full context
- **Performance visibility**: Provide real-time performance insights

### 3. Operational Metrics
- **Performance improvement**: 20% reduction in average execution time
- **Error rate reduction**: 50% reduction in service task failures
- **Resource optimization**: 30% reduction in resource usage
- **Mean time to resolution**: 60% reduction in MTTR for issues

## Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-4)
- Implement base ServiceTask class
- Add basic OpenTelemetry instrumentation
- Create file tracking system
- Implement circuit breaker pattern

### Phase 2: Advanced Features (Weeks 5-8)
- Add performance tracking system
- Implement intelligent error handling
- Create declarative configuration system
- Add async support

### Phase 3: Analytics and Optimization (Weeks 9-12)
- Implement predictive analytics
- Add anomaly detection
- Create performance optimization recommendations
- Add advanced monitoring dashboards

### Phase 4: Integration and Testing (Weeks 13-16)
- Integrate with existing BPMN workflows
- Comprehensive testing and validation
- Performance benchmarking
- Documentation and training

## Risk Assessment

### Technical Risks
- **Performance overhead**: Risk of instrumentation adding significant overhead
- **Complexity**: Risk of making the system too complex for simple use cases
- **Compatibility**: Risk of breaking existing service task implementations

### Mitigation Strategies
- **Performance testing**: Comprehensive performance testing and optimization
- **Gradual migration**: Provide migration path for existing implementations
- **Backward compatibility**: Maintain compatibility with existing patterns
- **Documentation**: Comprehensive documentation and examples

## Conclusion

The Ultra-Advanced Base ServiceTask will revolutionize service task development in the WeaverGen BPMN workflow system by providing automatic instrumentation, intelligent error handling, and elegant developer experience. This foundation will enable developers to focus on business logic while the framework handles all aspects of observability, performance monitoring, and operational excellence.

The implementation will follow the BPMN-first philosophy while providing the most advanced and elegant service task framework available, setting new standards for workflow development and observability in the industry.

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintainer**: WeaverGen Development Team 