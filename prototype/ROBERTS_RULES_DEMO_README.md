# Roberts Rules of Order - Autonomous Code Generation Demo

This demo showcases how the WeaverGen semantic quine architecture can generate a complete parliamentary procedure system from semantic conventions, with full type safety, telemetry, and intelligent agent behavior.

## 🚀 Quick Start

### Prerequisites

1. **Install Dependencies**
```bash
pip install pydantic pydantic-ai openai
```

2. **Install and Run Ollama**
```bash
# Install from https://ollama.ai/download
# Then pull the model:
ollama pull llama3.2

# Start Ollama server (if not already running):
ollama serve
```

3. **Install Weaver CLI** (for code generation)
```bash
cargo install weaver_forge
# Or download from OpenTelemetry Weaver releases
```

### Running the Demo

#### Step 1: Generate the 4-Layer Architecture
```bash
# Generate Roberts Rules implementation from semantic conventions
python generate_roberts_rules.py
```

This creates:
- `output/roberts/commands/` - Telemetry layer
- `output/roberts/operations/` - Business logic  
- `output/roberts/runtime/` - Side effects
- `output/roberts/contracts/` - Validation

#### Step 2: Install Integrated Operations
```bash
# This bridges the generated code with Pydantic models
python roberts_integrated_operations.py
```

#### Step 3: Run the Agent Demo
```bash
# Run the complete demo with Ollama
python roberts_rules_pydantic_ai_demo.py
```

## 📁 File Structure

```
prototype/
├── Semantic Definitions
│   ├── roberts-rules-simple.yaml    # Parliamentary semantic conventions
│   └── weaver-forge.yaml           # Self-referential semantics
│
├── Generated Code (via Weaver)
│   └── output/roberts/
│       ├── commands/forge.py       # Auto-telemetry
│       ├── operations/forge.py     # Business logic
│       ├── runtime/roberts.py      # State management
│       └── contracts/forge.py      # Validation
│
├── Pydantic Models
│   └── roberts_rules_models.py     # Type-safe domain models
│
├── Agent Systems
│   ├── roberts_pydantic_agents.py  # Basic agent demo
│   └── roberts_rules_pydantic_ai_demo.py  # Full pydantic-ai demo
│
└── Integration
    └── roberts_integrated_operations.py  # Bridges all components
```

## 🔄 The Complete Flow

### 1. Semantic Conventions → Code Generation
```yaml
# roberts-rules-simple.yaml defines:
- id: roberts.meeting.start
  attributes:
    - meeting_id
    - meeting_type  
    - quorum
    # ... etc
```

### 2. Weaver Generation → 4-Layer Architecture
```python
# Generated commands layer with telemetry:
def roberts_meeting_start(...) -> ForgeResult:
    with tracer.start_span("roberts.meeting.start"):
        # Auto-instrumented
```

### 3. Pydantic Models → Type Safety
```python
class Meeting(BaseModel):
    id: str
    type: MeetingType
    quorum: int
    
    @property
    def has_quorum(self) -> bool:
        return self.members_present >= self.quorum
```

### 4. Pydantic-AI Agents → Intelligence
```python
@chair_agent.tool
async def start_meeting(...) -> Dict[str, Any]:
    # Uses generated functions + Pydantic models
    result = roberts_meeting_start(...)
    meeting = Meeting(...)
```

## 🎭 Demo Scenarios

### Basic Meeting Flow
1. Chair starts meeting with quorum check
2. Member makes a motion
3. Another member seconds
4. Chair calls for vote
5. Secretary records results
6. System maintains full state + telemetry

### Motion Precedence Demo
- Shows how subsidiary motions can interrupt main motions
- Privileged motions take precedence over all
- System enforces Roberts Rules automatically

### Streaming & Iteration
- Stream agent responses in real-time
- Iterate through agent execution graph
- Full visibility into decision process

## 🔍 Key Features Demonstrated

### 1. **Semantic-Driven Development**
- Define domain rules as semantic conventions
- Generate implementation automatically
- Maintain single source of truth

### 2. **Type Safety Throughout**
- Pydantic models validate all data
- Type hints guide development
- Runtime validation via contracts

### 3. **Full Observability**
- Every operation has OpenTelemetry traces
- No manual instrumentation needed
- Performance metrics included

### 4. **Intelligent Agents**
- Role-based permissions (Chair, Secretary, Member)
- Understand parliamentary procedure
- Enforce rules automatically

### 5. **Local LLM Execution**
- Uses Ollama for privacy
- No cloud dependencies
- Fast response times

## 🛠️ Customization

### Adding New Parliamentary Rules
1. Update `roberts-rules-simple.yaml`
2. Regenerate with `python generate_roberts_rules.py`
3. Update operations in `roberts_integrated_operations.py`

### Changing the LLM
```python
# Use OpenAI instead of Ollama:
from pydantic_ai.models.openai import OpenAIModel
model = OpenAIModel('gpt-4o')

# Or use any OpenAI-compatible API:
model = OpenAIModel(
    'model-name',
    provider=OpenAIProvider(base_url='https://your-api.com')
)
```

### Extending Agent Capabilities
```python
@member_agent.tool
async def make_amendment(ctx: RunContext[RobertsRulesDeps], ...):
    # Add new parliamentary procedures
```

## 📊 Telemetry & Monitoring

The system automatically generates telemetry for every operation:

```csv
# telemetry.csv
roberts.meeting.start,True,0.002
roberts.motion.make,True,0.001
roberts.vote.record,True,0.003
```

Use this data to:
- Monitor system performance
- Identify bottlenecks
- Track usage patterns
- Enable self-improvement

## 🚨 Troubleshooting

### "Ollama connection refused"
```bash
# Make sure Ollama is running:
ollama serve

# Test with:
curl http://localhost:11434/api/tags
```

### "Module not found" errors
```bash
# Ensure you're in the prototype directory
cd prototype/

# Add to Python path if needed:
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### "Weaver not found"
```bash
# Install via Cargo:
cargo install weaver_forge

# Or check PATH:
which weaver
```

## 🎯 Next Steps

1. **Extend the Domain**: Add more parliamentary procedures
2. **Multi-Agent Debates**: Create complex meeting simulations
3. **Web Interface**: Build a UI for the system
4. **Production Deployment**: Package for real-world use

## 📚 Resources

- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/concepts/semantic-conventions/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pydantic-AI Documentation](https://ai.pydantic.dev/)
- [Roberts Rules of Order](https://robertsrules.org/)

---

This demonstration proves that complex domain logic can be:
- **Defined** semantically
- **Generated** automatically  
- **Validated** comprehensively
- **Executed** intelligently

The future of software is semantic-first development! 🚀