# WeaverGen v2.0 - Quick Start Implementation Guide

## 🚀 Day 1: Start Here

### Immediate Actions (First 4 Hours)
```bash
# 1. Create v2 branch
git checkout -b feature/v2-consolidation

# 2. Set up new structure
mkdir -p src/weavergen/{cli,engine,generators,validation,core}
mkdir -p src/weavergen/cli/commands
mkdir -p src/weavergen/generators/languages
mkdir -p src/weavergen/validation/agents

# 3. Create unified CLI entry point
touch src/weavergen/cli/main.py
touch src/weavergen/cli/__init__.py

# 4. Start consolidation script
python scripts/consolidate_v2.py  # You'll create this
```

### Consolidation Script Template
```python
# scripts/consolidate_v2.py
"""Automated consolidation helper for v2.0"""

import os
import ast
from pathlib import Path
from collections import defaultdict

class CodeConsolidator:
    def __init__(self):
        self.functions = defaultdict(list)
        self.classes = defaultdict(list)
        self.imports = set()
        
    def analyze_file(self, filepath: Path):
        """Extract reusable components"""
        with open(filepath) as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.functions[node.name].append({
                    'file': filepath,
                    'node': node,
                    'lines': self._get_lines(node)
                })
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name].append({
                    'file': filepath,
                    'node': node,
                    'lines': self._get_lines(node)
                })
    
    def find_duplicates(self):
        """Identify duplicate implementations"""
        duplicates = {}
        
        # Find duplicate functions
        for name, implementations in self.functions.items():
            if len(implementations) > 1:
                duplicates[f"function:{name}"] = implementations
                
        # Find duplicate classes  
        for name, implementations in self.classes.items():
            if len(implementations) > 1:
                duplicates[f"class:{name}"] = implementations
                
        return duplicates
    
    def generate_consolidation_plan(self):
        """Create actionable consolidation plan"""
        plan = []
        duplicates = self.find_duplicates()
        
        for item, implementations in duplicates.items():
            plan.append({
                'action': 'merge',
                'item': item,
                'files': [impl['file'] for impl in implementations],
                'recommendation': self._recommend_best(implementations)
            })
            
        return plan

# Run consolidation analysis
consolidator = CodeConsolidator()
for pyfile in Path('src/weavergen').rglob('*.py'):
    consolidator.analyze_file(pyfile)

plan = consolidator.generate_consolidation_plan()
print(f"Found {len(plan)} consolidation opportunities")
```

---

## 📋 Week 1 Checklist

### Day 1-2: Foundation
- [ ] Create v2 branch and new directory structure
- [ ] Run consolidation analysis
- [ ] Merge all CLI implementations into unified CLI
- [ ] Create base BPMN engine class
- [ ] Set up test framework with pytest

### Day 3-4: Core Consolidation  
- [ ] Merge core.py variants into single module
- [ ] Consolidate BPMN engine implementations
- [ ] Create unified validation framework
- [ ] Implement telemetry base classes
- [ ] Add type hints everywhere

### Day 5: Testing & Documentation
- [ ] Write integration tests for unified CLI
- [ ] Create span-based validation tests
- [ ] Document architecture decisions
- [ ] Update README for v2
- [ ] Create migration guide

---

## 🔧 Core Components to Build

### 1. Unified CLI (Priority 1)
```python
# src/weavergen/cli/main.py
import typer
from rich.console import Console
from rich.table import Table

from ..engine import WeaverGenEngine
from ..core.telemetry import init_telemetry

app = typer.Typer(
    name="weavergen",
    help="BPMN-driven code generation platform v2.0"
)
console = Console()

@app.callback()
def callback():
    """Initialize WeaverGen v2.0"""
    init_telemetry()

@app.command()
def generate(
    source: Path,
    language: List[str] = typer.Option(["python"]),
    output: Path = typer.Option("./generated"),
    process: Optional[Path] = None,
    validate: bool = True,
    parallel: bool = True
):
    """Generate code using BPMN orchestration"""
    engine = WeaverGenEngine()
    
    # Load process or use default
    if process:
        engine.load_process(process)
    else:
        engine.load_default_process()
    
    # Execute with progress
    with console.status("Generating code..."):
        result = engine.generate(
            source=source,
            languages=language,
            output=output,
            parallel=parallel
        )
    
    # Display results
    display_results(result)
    
    # Optional validation
    if validate:
        validation_result = engine.validate(result)
        display_validation(validation_result)

if __name__ == "__main__":
    app()
```

### 2. BPMN Engine Core (Priority 1)
```python
# src/weavergen/engine/bpmn.py
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.parser import BpmnParser
from SpiffWorkflow.bpmn.serializer import BpmnSerializer

from ..core.telemetry import trace_span
from .registry import ServiceRegistry

class WeaverGenEngine:
    """Unified BPMN engine for v2.0"""
    
    def __init__(self):
        self.parser = BpmnParser()
        self.serializer = BpmnSerializer()
        self.registry = ServiceRegistry()
        self.workflow_spec = None
        
        # Register default services
        self._register_default_services()
    
    def load_process(self, bpmn_file: Path):
        """Load BPMN process definition"""
        self.parser.add_bpmn_file(str(bpmn_file))
        self.workflow_spec = self.parser.get_spec('main')
        
    def load_default_process(self):
        """Load default generation process"""
        default = Path(__file__).parent / "processes" / "default.bpmn"
        self.load_process(default)
        
    async def generate(self, **kwargs) -> GenerationResult:
        """Execute generation workflow"""
        with trace_span("engine.generate") as span:
            workflow = BpmnWorkflow(self.workflow_spec)
            workflow.data.update(kwargs)
            
            # Run workflow
            self.workflow.run_all()
            
            # Collect results
            return GenerationResult(
                files=workflow.data.get('generated_files', []),
                spans=span.get_children(),
                metrics=self._collect_metrics(workflow)
            )
```

### 3. Service Registry (Priority 2)
```python
# src/weavergen/engine/registry.py
from typing import Protocol, Dict, Any, Callable
import asyncio

class ServiceHandler(Protocol):
    """Protocol for service handlers"""
    async def execute(self, context: Dict[str, Any]) -> Any:
        ...

class ServiceRegistry:
    """Central registry for BPMN services"""
    
    def __init__(self):
        self._services: Dict[str, ServiceHandler] = {}
        self._middleware: List[Middleware] = []
        
    def register(self, name: str, handler: ServiceHandler):
        """Register a service handler"""
        self._services[name] = handler
        
    def get(self, name: str) -> ServiceHandler:
        """Get service handler by name"""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered")
        return self._services[name]
        
    async def execute(self, name: str, context: Dict[str, Any]) -> Any:
        """Execute service with middleware"""
        handler = self.get(name)
        
        # Apply pre-execution middleware
        for mw in self._middleware:
            context = await mw.before(name, context)
            
        # Execute service
        result = await handler.execute(context)
        
        # Apply post-execution middleware
        for mw in reversed(self._middleware):
            result = await mw.after(name, result)
            
        return result
```

### 4. Multi-Agent Validator (Priority 2)
```python
# src/weavergen/validation/orchestrator.py
import asyncio
from typing import List, Dict, Any

from .agents import (
    OTelComplianceAgent,
    PerformanceAgent,
    SecurityAgent,
    APIDesignAgent,
    DocumentationAgent
)

class ValidationOrchestrator:
    """Orchestrate multi-agent validation"""
    
    def __init__(self):
        self.agents = {
            'otel': OTelComplianceAgent(),
            'performance': PerformanceAgent(),
            'security': SecurityAgent(),
            'api': APIDesignAgent(),
            'docs': DocumentationAgent()
        }
        
    async def validate_parallel(self, code: GeneratedCode) -> ValidationReport:
        """Run all agents in parallel"""
        tasks = []
        
        for name, agent in self.agents.items():
            task = asyncio.create_task(
                self._run_agent(name, agent, code)
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        
        return self._aggregate_results(results)
        
    async def _run_agent(self, name: str, agent: Any, code: GeneratedCode):
        """Run single agent with telemetry"""
        with trace_span(f"validation.{name}") as span:
            result = await agent.validate(code)
            span.set_attribute("findings", len(result.findings))
            return (name, result)
```

---

## 📊 Daily Progress Tracking

### Metrics Dashboard Template
```yaml
# metrics/daily_progress.yaml
day_1:
  files_consolidated: 0
  tests_written: 0
  coverage: 0%
  
day_2:
  files_consolidated: 15
  tests_written: 5
  coverage: 35%
  
# Update daily...
```

### Standup Template
```markdown
## Daily Standup - Day X

### Yesterday
- Consolidated X files
- Implemented Y feature
- Wrote Z tests

### Today  
- Consolidating [component]
- Implementing [feature]
- Testing [module]

### Blockers
- [Any blockers]

### Metrics
- Files: 161 → X (Y% reduction)
- Coverage: Z%
- Performance: A ms average
```

---

## 🚨 Common Pitfalls & Solutions

### Pitfall 1: Over-Engineering
**Problem**: Trying to make everything perfect from start  
**Solution**: MVP first, enhance iteratively

### Pitfall 2: Breaking Changes
**Problem**: v2 not backward compatible  
**Solution**: Compatibility layer for transition

### Pitfall 3: Test Coverage Gaps
**Problem**: Not testing during consolidation  
**Solution**: Write tests BEFORE consolidating

### Pitfall 4: Lost Functionality
**Problem**: Features lost during merge  
**Solution**: Feature inventory checklist

---

## 🎯 Quick Wins (Implement First)

1. **Single CLI Entry Point** (2 hours)
   - Immediate user experience improvement
   - Foundation for all other work

2. **Telemetry Framework** (4 hours)
   - Enables span-based validation
   - Performance tracking from day 1

3. **Consolidation Script** (2 hours)
   - Automates duplicate detection
   - Saves days of manual analysis

4. **Basic BPMN Engine** (1 day)
   - Core functionality working
   - Services can be added incrementally

5. **Integration Tests** (4 hours)
   - Catch regressions early
   - Build confidence in changes

---

## 📚 Resources & References

### Internal Resources
- v1 Innovation documents
- BPMN architecture specs  
- Multi-agent patterns
- Existing test cases

### External Resources
- [SpiffWorkflow Docs](https://spiffworkflow.readthedocs.io/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Typer CLI Framework](https://typer.tiangolo.com/)
- [Pydantic v2 Migration](https://docs.pydantic.dev/latest/migration/)

### Team Contacts
- Architecture: [Lead Architect]
- BPMN Expert: [Process Specialist]
- Testing: [QA Lead]
- DevOps: [Infrastructure Lead]

---

## ✅ Definition of Done for v2.0

A feature is DONE when:
1. Code is consolidated (no duplicates)
2. Tests written (>90% coverage)
3. Types added (mypy passes)
4. Documentation updated
5. Performance benchmarked
6. Telemetry instrumented
7. Integration tests pass
8. Code review complete
9. CI/CD pipeline green
10. Metrics dashboard updated

---

*"The journey of a thousand miles begins with a single step. In v2.0, that step is a unified CLI."*

**Start with Day 1 actions. Build momentum. Transform the platform.**

Ready? Let's build v2.0! 🚀