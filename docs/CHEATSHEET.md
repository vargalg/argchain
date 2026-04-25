# argchain - Developer Cheat Sheet

## One-Line Summary
Pipe Python operations together where each operation takes `**kwargs` and returns a dict, enabling elegant functional data flow.

## 30-Second Setup

```python
from argchain import Pipeline, operation

@operation
def my_op(value: int, **kwargs):
    return {**kwargs, 'value': value * 2}

result = Pipeline().pipe(my_op)(value=5)  # {'value': 10}
```

## Three Ways to Write Operations

### Option 1: Basic (Most Control)
```python
@operation
def transform(value: int, **kwargs):
    return {**kwargs, 'value': value * 2}
```

### Option 2: Clean (Using @passthrough)
```python
@passthrough('value')
def transform(value: int):
    return {'value': value * 2}
```

### Option 3: Plain (No Decorators)
```python
def transform(**kwargs):
    return {**kwargs, 'value': kwargs.get('value', 0) * 2}
```

## Common Patterns

### Chain Multiple Operations
```python
result = (Pipeline()
    .pipe(operation1)
    .pipe(operation2)
    .pipe(operation3)
    (value=10, user_id=42)
)
```

### Pass Additional Data Through Pipeline
```python
# Data flows through automatically!
@operation
def only_change_value(value: int, **kwargs):
    return {**kwargs, 'value': value * 2}

# Input: {value: 5, name: "Alice", metadata: "x"}
# Output: {value: 10, name: "Alice", metadata: "x"}
```

### Remove Data From Pipeline
```python
@operation
def remove_secret(value: int, api_key: str = "", **kwargs):
    # api_key is intentionally not in return dict
    return {**kwargs, 'value': value}

# Input: {value: 5, api_key: "secret123", user_id: 42}
# Output: {value: 5, user_id: 42}  # api_key is gone!
```

### Conditional Processing
```python
@operation
def route(data_type: str, **kwargs):
    if data_type == 'user':
        return {**kwargs, 'result': process_user(kwargs)}
    return {**kwargs, 'result': process_other(kwargs)}
```

### Add Computed Fields
```python
@operation
def add_computed(value1: int, value2: int, **kwargs):
    return {
        **kwargs,
        'value1': value1,
        'value2': value2,
        'sum': value1 + value2,
        'product': value1 * value2
    }
```

### Handle Errors Gracefully
```python
@operation
def safe_operation(value: int, **kwargs):
    try:
        result = some_risky_operation(value)
        return {**kwargs, 'result': result, 'error': None}
    except Exception as e:
        return {**kwargs, 'result': None, 'error': str(e)}
```

## Key Concepts

| Concept | Example |
|---------|---------|
| **Pass-through** | Unmodified keys continue to output automatically |
| **Selective Deletion** | Don't include a key in output to remove it |
| **Method Chaining** | `.pipe(op1).pipe(op2)` for fluent API |
| **Type Safety** | Operations must return dicts |
| **Default Arguments** | Works with default parameter values |

## API Reference

### Pipeline
```python
Pipeline()                          # Create pipeline
    .pipe(operation)                # Add operation
    .pipe(operation2)               # Chain more
    (key=value, key2=value2)        # Execute with initial data
    
# Or:
Pipeline().execute(**initial_data)  # Alternative execution
```

### Decorators
```python
@operation                          # Validates dict return
def my_op(**kwargs):
    return dict

@passthrough('param1', 'param2')    # Auto pass-through of others
def my_op(param1, param2):
    return dict
```

## Common Mistakes & Solutions

### ❌ Forgetting to return a dict
```python
@operation
def bad(**kwargs):
    return kwargs['value'] * 2  # Wrong! Returns int, not dict
```
**✅ Fix:**
```python
@operation
def good(**kwargs):
    return {**kwargs, 'value': kwargs['value'] * 2}  # Right! Returns dict
```

### ❌ Manually handling pass-through with @passthrough
```python
@passthrough('value')
def bad(value: int, **kwargs):  # Don't add **kwargs!
    return {**kwargs, 'value': value * 2}
```
**✅ Fix:**
```python
@passthrough('value')
def good(value: int):  # Just the params you care about
    return {'value': value * 2}
```

### ❌ Losing data by not returning it
```python
@operation
def bad(value: int, **kwargs):
    return {'value': value * 2}  # Lost all the other kwargs!
```
**✅ Fix:**
```python
@operation
def good(value: int, **kwargs):
    return {**kwargs, 'value': value * 2}  # Include {**kwargs}
```

## Import Statements

```python
# Core imports
from argchain import Pipeline, operation

# Decorator imports
from argchain.decorators import passthrough

# Full imports
from argchain import Pipeline, operation
from argchain.decorators import passthrough, operation  # Both available
```

## Quick Reference: What Each Part Does

```python
@operation  # ← Says "this is an operation, validate it returns dict"
def double(  # ← Function name
    value: int,  # ← Specific parameter this operation cares about
    **kwargs  # ← Everything else passes through
) -> dict:  # ← Must return dict
    return {  # ← Build output dict
        **kwargs,  # ← Include everything else
        'value': value * 2  # ← Modify what we care about
    }
```

## Testing an Operation

```python
# Test directly
result = double(value=5, name="test", age=30)
assert result == {'value': 10, 'name': 'test', 'age': 30}

# Test in pipeline
pipeline = Pipeline().pipe(double)
result = pipeline(value=5, name="test")
assert result['value'] == 10
assert result['name'] == 'test'
```

## Debugging Tips

```python
# See pipeline structure
print(pipeline)  # Pipeline(op1, op2, op3)

# Print intermediate results
@operation
def debug(value: int, **kwargs):
    result = {**kwargs, 'value': value * 2}
    print(f"Result: {result}")  # Debug output
    return result

# Verify data is flowing
@operation
def inspect(**kwargs):
    print(f"Keys present: {list(kwargs.keys())}")
    return kwargs
```

## Performance Tips

1. **Operations are fast** - Just dict unpacking/merging
2. **No external dependencies** - Minimal overhead
3. **Use @passthrough** - Slightly cleaner than manual `**kwargs`
4. **Combine operations** - Pipe many simple operations, not few complex

## Real-World Examples

### Data Transformation Pipeline
```python
pipeline = (Pipeline()
    .pipe(validate_input)
    .pipe(normalize_format)
    .pipe(enrich_with_metadata)
    .pipe(format_for_output)
)

result = pipeline(raw_data=data_dict)
```

### Request Processing
```python
pipeline = (Pipeline()
    .pipe(extract_auth_token)
    .pipe(verify_token)
    .pipe(extract_request_body)
    .pipe(validate_body)
    .pipe(process_business_logic)
    .pipe(format_response)
)

response = pipeline(request=http_request)
```

### Data ETL
```python
pipeline = (Pipeline()
    .pipe(extract_from_source)
    .pipe(transform_types)
    .pipe(clean_missing_data)
    .pipe(add_computed_fields)
    .pipe(filter_sensitive_data)
    .pipe(load_to_destination)
)

result = pipeline(source_data=raw_data)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `TypeError: must return a dict` | Check operation returns `dict`, not other type |
| Data missing in output | Use `{**kwargs, ...}` to include all input |
| Can't access parameter | Make sure it's in the function signature |
| `**kwargs` appearing in output | Don't forget `**kwargs` in return statement |

## Quick Commands

```bash
# Run examples
python -m examples.examples

# Run tests
pytest tests/tests.py -v

# Check imports
python -c "from argchain import Pipeline, operation; print('✓')"

# Interactive testing
python  # Then: from argchain import *; p = Pipeline().pipe(...)
```

---

**Save this cheat sheet and refer back often!** 📝

For full docs, see: `README.md`  
For getting started: `QUICKSTART.md`  
For examples: `python -m examples.examples`
