# argchain - Quick Start Guide

## 30-Second Overview

**argchain** lets you chain Python operations together where data flows through like a pipe:

```
Input Dict → Operation 1 → Operation 2 → Operation 3 → Output Dict
```

Each operation:
- Takes `**kwargs` (dictionary as arguments)
- Returns a `dict`
- Can modify, create, or delete keys
- Automatically passes through unchanged keys

## The Three Ways to Create Operations

### Option 1: Basic (Most Control)
```python
@operation()
def transform(value: int, **kwargs):
    return {**kwargs, 'value': value * 2}
```

### Option 2: Clean (Using @operation(passthrough=True))
```python
@operation(passthrough=True)
def transform(value: int):
    return {'value': value * 2}
    # Everything else passes through automatically!
```

### Option 3: With Deletion (Using @operation(delete=[...]))
```python
@operation(delete=['secret'])
def transform(value: int, secret: str = "", **kwargs):
    return {**kwargs, 'value': value * 2}
    # 'secret' is removed from output
```

## 5-Minute Tutorial

### Step 1: Create Operations
```python
from argchain import Pipeline, operation

@operation()
def validate(value: int, **kwargs):
    if value < 0:
        return {**kwargs, 'value': abs(value), 'was_negative': True}
    return {**kwargs, 'value': value, 'was_negative': False}

@operation()
def format_output(value: int, **kwargs):
    return {**kwargs, 'formatted': f"Result: {value}"}
```

### Step 2: Create a Pipeline
```python
pipeline = Pipeline()
pipeline.pipe(validate)
pipeline.pipe(format_output)
```

### Step 3: Run It
```python
result = pipeline(value=-42, user_id=123, timestamp="2026-04-17")
print(result)
# Output: {
#     'value': 42,
#     'was_negative': True,
#     'formatted': 'Result: 42',
#     'user_id': 123,
#     'timestamp': '2026-04-17'
# }
```

### Step 4: (Optional) Use Method Chaining
```python
result = (Pipeline()
    .pipe(validate)
    .pipe(format_output)
    (value=-42, user_id=123, timestamp="2026-04-17")
)
```

## Key Concepts Explained

### 🔄 Pass-Through Behavior
By default, any key in the input that you don't modify gets passed to the next operation automatically:

```python
@operation()
def process(name: str, **kwargs):  # Receives: {name: "Alice", age: 30}
    return {**kwargs, 'name': name.upper()}  # Returns: {name: "ALICE", age: 30}
```

### 🗑️ Selective Deletion
Don't include a key in your return dict to prevent it from passing forward:

```python
@operation()
def remove_secret(value: int, api_key: str = "", **kwargs):
    # api_key is intentionally not in return dict
    return {**kwargs, 'value': value * 2}

# Input: {value: 5, api_key: "secret123", user_id: 42}
# Output: {value: 10, user_id: 42}  # api_key is gone!
```

### ✨ Auto Pass-Through with @operation(passthrough=True)
This decorator automatically passes through everything except the parameters your function explicitly handles:

```python
@operation(passthrough=True)
def double_value(value: int):  # Only cares about 'value'
    return {'value': value * 2}  # Everything else passes through!

# Input: {value: 5, name: "Alice", age: 30}
# Output: {value: 10, name: "Alice", age: 30}
```

### 🎯 Selective Deletion with @operation(delete=[...])
Remove specific keys from the output:

```python
@operation(delete=['temp_data'])
def process(value: int, temp_data: str = "", **kwargs):
    return {**kwargs, 'value': value * 2}
    # temp_data is removed from output by decorator

# Input: {value: 5, temp_data: "temporary", user_id: 42}
# Output: {value: 10, user_id: 42}  # temp_data is gone!
```

### 🔧 Combined Features
Use both auto pass-through and selective deletion together:

```python
@operation(passthrough=True, delete=['secret'])
def secure_process(value: int, secret: str = "hidden"):
    return {'value': value * 3}

# Input: {value: 7, secret: "hidden", user_id: 123, metadata: "test"}
# Output: {value: 21, user_id: 123, metadata: "test"}  # secret deleted, others passed through
```

## Common Patterns

### Pattern 1: Data Transformation Pipeline
```python
pipeline = (Pipeline()
    .pipe(validate_input)
    .pipe(normalize_data)
    .pipe(enrich_data)
    .pipe(format_output)
)

result = pipeline(raw_data=data_dict)
```

### Pattern 2: Conditional Processing
```python
@operation()
def route(data_type: str, **kwargs):
    if data_type == 'user':
        return {**kwargs, 'result': process_user(kwargs)}
    elif data_type == 'product':
        return {**kwargs, 'result': process_product(kwargs)}
    return {**kwargs, 'result': kwargs}

pipeline = Pipeline().pipe(route)
```

### Pattern 3: Layered Processing
```python
# Each layer does one thing
pipeline = (Pipeline()
    .pipe(extract_fields)           # Get what we need
    .pipe(validate_fields)          # Check for errors
    .pipe(transform_types)          # Convert types
    .pipe(calculate_derived)        # Add computed values
    .pipe(filter_for_output)        # Remove internals
)
```

## Type Safety

All operations must return dicts - you'll get a clear error otherwise:

```python
@operation()
def bad_operation(**kwargs):
    return "not a dict"  # ❌ This will raise TypeError!

Pipeline().pipe(bad_operation)(value=1)
# TypeError: Operation bad_operation must return a dict, but returned str
```

## Error Handling

Operations can handle errors gracefully:

```python
@operation()
def safe_divide(numerator: int, denominator: int = 1, **kwargs):
    try:
        result = numerator / denominator
        return {**kwargs, 'result': result, 'error': None}
    except ZeroDivisionError:
        return {**kwargs, 'result': None, 'error': 'Division by zero'}

pipeline = Pipeline().pipe(safe_divide)
result = pipeline(numerator=10, denominator=0)
# {'result': None, 'error': 'Division by zero'}
```

## Running Tests

```bash
pytest tests.py -v
```

All 21 tests pass! ✅

## Running Examples

```bash
python -m examples.examples
```

Shows 4 different scenarios with full output.

---

**Ready to build your data pipelines? Start with `examples/examples.py` then create your own operations! 🚀**
