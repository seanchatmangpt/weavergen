# Practical Migration Steps - Prototype to src/weavergen

## Quick Start Commands

```bash
# 1. First, create a backup
cp -r prototype prototype_backup

# 2. Start migration in a new branch
git checkout -b feature/prototype-migration

# 3. Run prototype tests to ensure everything works
cd prototype && python -m pytest test_*.py -v
```

## Step-by-Step Migration

### Step 1: Migrate Core Weaver Wrapper Methods

```bash
# Compare and merge weaver_wrapper.py methods into core.py
# Key methods to add:
# - registry_check()
# - registry_resolve() 
# - registry_stats()
# - Enhanced error handling
```

**Manual merge required for `src/weavergen/core.py`:**
- Add methods from `prototype/weaver_wrapper.py`
- Preserve existing WeaverGen class structure
- Integrate subprocess handling improvements

### Step 2: Create Semantic Generation Module

```bash
# Create new semantic generation module
touch src/weavergen/semantic.py

# Copy semantic models and generator logic
# From: prototype/semantic-generator.py
# To: src/weavergen/semantic.py
```

### Step 3: Extend Models

```bash
# Add semantic convention models to models.py
# Key models to add:
# - AttributeType, RequirementLevel, Stability enums
# - Attribute, Group, SemanticConvention classes
# - ForgeResult model
```

### Step 4: Create Layers Module

```bash
# Create 4-layer architecture structure
mkdir -p src/weavergen/layers
touch src/weavergen/layers/__init__.py
touch src/weavergen/layers/commands.py
touch src/weavergen/layers/operations.py
touch src/weavergen/layers/runtime.py
touch src/weavergen/layers/contracts.py
```

### Step 5: Migrate Templates

```bash
# Copy template structure
cp -r prototype/templates src/weavergen/

# Ensure template paths are updated in code
# Update template resolution in core.py
```

### Step 6: Update Dependencies

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
semantic = [
    "pydantic-ai>=0.1.0",
    "ollama>=0.1.0",
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
    "icontract>=2.6.0",
]
```

### Step 7: Migrate Tests

```bash
# Create test files
touch tests/test_semantic.py
touch tests/test_layers.py
touch tests/test_integration.py

# Migrate test logic from prototype
# Key test files to migrate:
# - test_weaver_wrapper.py → test_core.py (merge)
# - test_weaver_forge.py → test_layers.py
# - test_integration_full_workflow.py → test_integration.py
```

## Verification Checklist

- [ ] Core wrapper methods integrated
- [ ] Semantic generation working
- [ ] Models extended with new types
- [ ] 4-layer architecture implemented
- [ ] Templates migrated and accessible
- [ ] Tests passing
- [ ] CLI updated with new commands
- [ ] Documentation updated

## Testing After Each Step

```bash
# Run tests after each major change
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# Check test coverage
pytest tests/ -v --cov=weavergen --cov-report=term-missing
```

## Common Issues & Solutions

### Issue: Import errors after migration
**Solution:** Update `__init__.py` files and ensure proper module structure

### Issue: Template paths not found
**Solution:** Update path resolution in core.py to handle new template location

### Issue: Weaver binary not found
**Solution:** Ensure the enhanced binary detection from prototype is migrated

## Rollback Plan

If issues arise:
```bash
# Revert to backup
git checkout main
rm -rf src/weavergen/layers src/weavergen/templates
git checkout -- src/weavergen/
```

## Next Actions

1. Start with core.py enhancement (highest impact)
2. Test each component individually
3. Run integration tests
4. Update documentation
5. Create PR for review