# Consistent Mistakes in Weaver Forge Prototype Development

This document captures recurring mistakes made during the development of the Weaver Forge prototype, their root causes, and lessons learned.

## 1. Semantic Convention Attribute Naming

### Mistake
- **What**: Using dotted attribute names like `weaver.registry.check.path` in semantic conventions
- **Where**: `weaver-cli-semantics.yaml`, generated code
- **Frequency**: Multiple times

### Example
```yaml
# WRONG
attributes:
  - id: weaver.registry.check.path
    type: string

# CORRECT
attributes:
  - id: registry.check.path
    type: string
```

### Root Cause
Confusion between:
- Operation IDs (which use full dotted names like `weaver.registry.check`)
- Attribute IDs (which should be relative like `registry.check.path`)

### Fix
Attributes inherit their namespace from the parent group. Only use the relative path.

---

## 2. Template Variable Context

### Mistake
- **What**: Expecting custom variable names in templates instead of `ctx`
- **Where**: All Jinja2 templates
- **Frequency**: Consistently in initial implementations

### Example
```jinja
# WRONG
{% for operation in operations %}

# CORRECT
{% for operation in ctx %}
```

### Root Cause
Not understanding that Weaver passes the context as a standardized `ctx` variable, regardless of the data structure.

### Fix
Always use `ctx` as the main context variable in Weaver templates.

---

## 3. Parameter Ordering in Generated Functions

### Mistake
- **What**: Mixing required and optional parameters, causing "parameter without default follows parameter with default" errors
- **Where**: Template generation loops
- **Frequency**: Multiple times

### Example
```jinja
# WRONG - mixes required and optional
{% for attr in operation.attributes %}
{{ attr.name }}: {{ attr.type }}{% if attr.requirement_level != "required" %} = None{% endif %}
{% endfor %}

# CORRECT - required first, then optional
{% for attr in required_attrs %}...{% endfor %}
{% for attr in optional_attrs %}...{% endfor %}
```

### Root Cause
Not separating attributes by requirement level before iterating in templates.

### Fix
Always filter attributes into required and optional groups before generating parameter lists.

---

## 4. Registry Structure Assumptions

### Mistake
- **What**: Assuming a single YAML file is a valid registry
- **Where**: Runtime validation, Weaver CLI calls
- **Frequency**: Repeatedly when testing

### Example
```python
# WRONG
weaver_registry_check("my_semantics.yaml")

# CORRECT - need proper registry structure
create_registry_structure("my_semantics.yaml")
```

### Root Cause
Weaver expects a specific directory structure with `registry_manifest.yaml`, not just a standalone YAML file.

### Fix
Always create proper registry structure with manifest before calling Weaver commands.

---

## 5. Hardcoding Values in Templates

### Mistake
- **What**: Hardcoding schema URLs, versions, and other configurable values
- **Where**: Templates and generated code
- **Frequency**: Initial implementations

### Example
```yaml
# WRONG
schema_base_url: "https://opentelemetry.io/schemas"

# CORRECT - use params
schema_base_url: {{ params.schema_base_url | default("https://opentelemetry.io/schemas") }}
```

### Root Cause
Not leveraging Weaver's parameter system for configuration.

### Fix
Use `params` in `weaver.yaml` and template expressions for all configurable values.

---

## 6. Stability Field Issues

### Mistake
- **What**: Using `stability: experimental` in semantic conventions
- **Where**: `weaver-cli-semantics.yaml`
- **Frequency**: When defining new operations

### Example
```yaml
# WRONG - causes validation errors
- id: weaver.registry.diff
  type: span
  stability: experimental

# CORRECT - omit stability or use valid values
- id: weaver.registry.diff
  type: span
```

### Root Cause
Not understanding the valid stability levels in semantic conventions.

### Fix
Check Weaver documentation for valid stability values or omit the field.

---

## 7. Type Annotations in Templates

### Mistake
- **What**: Using `typing.Any` without proper imports or using `template[string]` as a Python type
- **Where**: Generated Python code
- **Frequency**: When handling generic parameters

### Example
```python
# WRONG
def func(params: template[string]):

# CORRECT
def func(params: Optional[Dict[str, str]]):
```

### Root Cause
Direct translation of semantic convention types to Python without proper mapping.

### Fix
Map semantic convention types to appropriate Python types in templates.

---

## 8. Lost Files During Refactoring

### Mistake
- **What**: Moving/deleting files without checking dependencies
- **Where**: Template reorganization
- **Frequency**: During major refactoring

### Example
Lost all template files when reorganizing directory structure, had to recreate from memory.

### Root Cause
Not using version control commands (`git mv`) or checking what depends on files before moving them.

### Fix
- Always use `git mv` for moving files
- Check for dependencies before deleting
- Commit working state before major reorganization

---

## 9. Mock vs Real Implementation Confusion

### Mistake
- **What**: Mixing mock implementations with real Weaver CLI calls
- **Where**: Operations layer
- **Frequency**: Throughout development

### Example
```python
# Started with mock
def generate_semantic():
    return "groups: []"

# Evolved to real implementation without clear transition
def generate_semantic():
    return weaver_cli_call()
```

### Root Cause
Incremental development without clear boundaries between mock and real implementations.

### Fix
- Clearly mark mock implementations with comments
- Use feature flags or separate modules for mock vs real
- Document the transition plan

---

## 10. Import Path Issues

### Mistake
- **What**: Incorrect import paths for generated modules
- **Where**: Test scripts, validation files
- **Frequency**: Consistently

### Example
```python
# WRONG
from forge import commands

# CORRECT
sys.path.insert(0, 'output')
from commands.forge import forge_semantic_generate
```

### Root Cause
Generated files in non-standard locations not on Python path.

### Fix
Always add output directory to Python path before importing generated modules.

---

## Key Lessons

1. **Read Weaver documentation thoroughly** - Many mistakes came from assumptions about how Weaver works
2. **Test with actual Weaver CLI early** - Mock implementations hide integration issues
3. **Understand the data flow** - Semantic conventions → JQ filters → Templates → Code
4. **Use proper separation** - Keep required/optional parameters, mock/real implementations clearly separated
5. **Version control discipline** - Commit working states before major changes
6. **Validate incrementally** - Test each layer of the architecture independently

## Prevention Strategies

1. **Create validation scripts** - Like `validate_80_20.py` to catch issues early
2. **Use type hints** - Helps catch type mismatches in templates
3. **Write tests first** - Especially for template generation
4. **Document assumptions** - What you expect vs what actually happens
5. **Keep examples handy** - Working Weaver templates and registries for reference