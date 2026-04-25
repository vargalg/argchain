# argchain - Pipe Python Operations

A lightweight Python library for composing operations that pass data through a pipeline, enabling elegant functional data flow.

## Concept

**argchain** allows you to chain Python operations together where:
- Each operation receives a dictionary of keyword arguments (`**kwargs`)
- Each operation returns a dictionary that becomes the input for the next operation
- Operations can:
  - **Create** new keys in the output
  - **Modify** existing keys from the input
  - **Delete** keys by simply not including them in the output
  - **Pass through** unchanged keys to the next operation

## Basic Usage

### Simple Pipeline

```python
from argchain import Pipeline, operation

@operation()
def add_one(value: int, **kwargs) -> dict:
    """Add 1 to value and pass through all other kwargs."""
    return {**kwargs, 'value': value + 1}

@operation()
def multiply(value: int, factor: int = 2, **kwargs) -> dict:
    """Multiply value by factor."""
    return {**kwargs, 'value': value * factor}

# Create and execute pipeline
pipeline = Pipeline().pipe(add_one).pipe(multiply)
result = pipeline(value=5, metadata="example")
# result = {'value': 10, 'metadata': 'example'}
```

### Using the New Unified @operation Decorator

The `@operation` decorator now supports optional parameters for automatic pass-through and selective deletion:

```python
from argchain import Pipeline, operation

# Auto pass-through everything except handled parameters
@operation(passthrough=True)
def double_count(count: int) -> dict:
    """Double count - everything else passes through automatically."""
    return {'count': count * 2}

# Delete specific keys from output
@operation(delete=['secret'])
def process_data(value: int, secret: str = "", **kwargs) -> dict:
    return {**kwargs, 'value': value * 2}
    # 'secret' will be removed from output

# Combine both features
@operation(passthrough=True, delete=['temp'])
def cleanup_and_process(value: int, temp: str = "temporary") -> dict:
    return {'value': value * 3, 'processed': True}
    # Auto pass-through, but delete 'temp'
```

### Method Chaining

Chain operations fluently:

```python
result = (Pipeline()
          .pipe(add_one)
          .pipe(multiply)
          .pipe(to_string)
          (value=5, metadata="data"))
```

## Key Features

### 1. **Dictionary Pass-Through**
By default, any key in the input that an operation doesn't modify is automatically passed to the next operation:

```python
@operation()
def process_name(name: str, **kwargs) -> dict:
    return {**kwargs, 'name': name.upper()}

# Even though we only care about 'name', other keys pass through
result = Pipeline().pipe(process_name)(name="alice", age=30, city="NYC")
# result = {'name': 'ALICE', 'age': 30, 'city': 'NYC'}
```

### 2. **Automatic Pass-Through with @operation(passthrough=True)**
The new decorator automatically passes through all parameters not explicitly handled by the function:

```python
@operation(passthrough=True)
def double_value(value: int) -> dict:
    return {'value': value * 2}
    # No need to manually handle **kwargs!

result = Pipeline().pipe(double_value)(value=5, name="test", age=30)
# result = {'value': 10, 'name': 'test', 'age': 30}
```

### 3. **Selective Deletion with @operation(delete=[...])**
Remove specific keys from the output:

```python
@operation(delete=['api_key'])
def secure_process(value: int, api_key: str = "", **kwargs) -> dict:
    return {**kwargs, 'value': value * 2}
    # api_key is removed from output

result = Pipeline().pipe(secure_process)(value=5, api_key="secret", user_id=42)
# result = {'value': 10, 'user_id': 42}  # api_key is gone!
```

### 4. **Combined Features**
Use both pass-through and deletion together:

```python
@operation(passthrough=True, delete=['temp'])
def process_and_cleanup(value: int, temp: str = "temporary") -> dict:
    return {'value': value * 3, 'processed': True}

result = process_and_cleanup(value=7, temp="delete_me", user_id=123, metadata="test")
# result = {'value': 21, 'processed': True, 'user_id': 123, 'metadata': 'test'}
# 'temp' is deleted, others pass through automatically
```

### 5. **Type Safety**
Operations must return dictionaries. Type errors are caught early:

```python
@operation()
def bad_operation(**kwargs):
    return "not a dict"  # ❌ This will raise TypeError!

Pipeline().pipe(bad_operation)(value=1)  # Raises: "Operation bad_operation must return a dict"
```

## Creating Operations

### Option 1: Manual with @operation() (Most Control)
```python
from argchain import operation

@operation()
def my_operation(param1: str, param2: int = 10, **kwargs) -> dict:
    result = {**kwargs, 'processed': param1, 'multiplied': param2 * 2}
    return result
```

### Option 2: With @operation(passthrough=True) (Cleanest)
```python
from argchain import operation

@operation(passthrough=True)
def my_operation(param1: str, param2: int = 10) -> dict:
    return {'processed': param1, 'multiplied': param2 * 2}
    # Everything else passes through automatically!
```

### Option 3: With @operation(delete=[...]) (For Security)
```python
from argchain import operation

@operation(delete=['sensitive_data'])
def my_operation(value: int, sensitive_data: str = "", **kwargs) -> dict:
    return {**kwargs, 'value': value * 2}
    # sensitive_data is removed from output
```

### Option 4: Plain functions (Works too!)
Operations don't have to be decorated if you handle the passthrough manually:

```python
def my_operation(**kwargs) -> dict:
    value = kwargs.pop('value', 0)
    return {**kwargs, 'result': value + 1}
```

## API Reference

### Pipeline

```python
class Pipeline:
    def __init__(self): ...
    
    def add_operation(self, operation: Callable) -> 'Pipeline': ...
    
    def pipe(self, operation: Callable) -> 'Pipeline': ...
    
    def execute(self, **initial_data) -> Dict[str, Any]: ...
    
    def __call__(self, **initial_data) -> Dict[str, Any]: ...
```

### @operation Decorator

```python
def operation(
    delete: Optional[List[str]] = None,
    passthrough: bool = False
) -> Callable:
    """
    Decorator to mark a function as a pipeline operation.

    Args:
        delete: List of keys to delete from the output (they won't pass to next operation)
        passthrough: If True, automatically pass through all kwargs not explicitly handled

    Examples:
        @operation()  # Basic usage
        @operation(passthrough=True)  # Auto pass-through
        @operation(delete=['key'])  # Delete specific keys
        @operation(passthrough=True, delete=['temp'])  # Both features
    """
```

## Examples

See `../examples/examples.py` for complete working examples including:
- Basic pipeline operations with manual pass-through
- Using @operation(passthrough=True) for automatic pass-through
- Using @operation(delete=[...]) for selective deletion
- Combining both features together

## Installation

```bash
pip install argchain
```

Or with Poetry:

```bash
poetry add argchain
```

## Requirements

- Python 3.10+

## License

MIT
