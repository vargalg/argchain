# argchain - First Version Framework

## Overview

**argchain** is a functional data-piping library that allows you to compose operations where data flows through a series of transformations. Each operation receives keyword arguments and produces a dictionary for the next operation.

## Project Structure

```
argchain/
├── argchain/
│   ├── __init__.py           # Main package exports
│   ├── pipeline.py           # Core Pipeline class
│   └── decorators.py         # @operation and @passthrough decorators
├── examples/
│   └── examples.py           # Comprehensive usage examples
├── tests/
│   ├── tests.py              # Full test suite (16 tests, all passing)
│   └── verify.py             # Quick verification
├── docs/
│   ├── README.md             # Full documentation
│   ├── QUICKSTART.md         # Quick start guide
│   ├── FRAMEWORK.md          # This framework overview
│   ├── STATUS.md             # Project status
│   └── SUMMARY.md            # Complete summary
├── README.md                 # Root README
├── pyproject.toml            # Poetry configuration
└── poetry.lock
```

## Core Concepts

### 1. **Pipeline Class** (`argchain/pipeline.py`)
- Manages a sequence of operations
- Executes operations in order, passing dictionary output to input
- Supports method chaining with `.pipe()`
- Can be called directly as a function

### 2. **@operation Decorator** (`argchain/decorators.py`)
- Validates that operations return dictionaries
- Enables clean operation definition
- Provides error handling for type safety

### 3. **@passthrough Decorator** (`argchain/decorators.py`)
- Automatically passes through unmodified kwargs
- Simplifies operation code by eliminating manual `**kwargs` merging
- Specify which parameters an operation handles, rest pass through automatically

## Key Features Implemented

✅ **Dictionary-based data flow** - Each operation gets `**kwargs`, returns `dict`  
✅ **Automatic pass-through** - Unmodified keys pass to next operation by default  
✅ **Selective deletion** - Operations can exclude keys from output  
✅ **Method chaining** - Fluent API for building pipelines  
✅ **Type validation** - Operations must return dicts or raise TypeError  
✅ **Decorator support** - `@operation` and `@passthrough` decorators  
✅ **Flexible calling** - `pipeline()` or `pipeline.execute()`  

## Usage Examples

### Basic Piping
```python
from argchain import Pipeline, operation

@operation
def add_one(value: int, **kwargs) -> dict:
    return {**kwargs, 'value': value + 1}

@operation
def multiply(value: int, factor: int = 2, **kwargs) -> dict:
    return {**kwargs, 'value': value * factor}

result = Pipeline().pipe(add_one).pipe(multiply)(value=5, metadata="test")
# result = {'metadata': 'test', 'value': 12}
```

### Using @passthrough for Cleaner Code
```python
from argchain.decorators import passthrough

@passthrough('count')
def double_count(count: int) -> dict:
    return {'count': count * 2}

result = Pipeline().pipe(double_count)(count=5, user_id=42)
# result = {'count': 10, 'user_id': 42} - everything passes through automatically
```

### Selective Deletion
```python
@operation
def filter_keys(value: int, secret: str = "", **kwargs) -> dict:
    # 'secret' is not included in output, so it doesn't pass forward
    return {**kwargs, 'value': value}

result = Pipeline().pipe(filter_keys)(value=5, secret="hidden", public="visible")
# result = {'value': 5, 'public': 'visible'} - 'secret' is gone
```

## Testing

All 16 tests pass successfully:
- ✅ Single and multiple operations
- ✅ Pass-through behavior
- ✅ Selective deletion
- ✅ Method chaining
- ✅ Error handling
- ✅ Decorator functionality
- ✅ Integration scenarios

Run tests with:
```bash
pytest tests.py -v
```

## Files Created

| File | Purpose |
|------|---------|
| `argchain/__init__.py` | Package initialization, exports Pipeline and operation |
| `argchain/pipeline.py` | Core Pipeline class - orchestrates operation sequencing |
| `argchain/decorators.py` | @operation and @passthrough decorators for operation definition |
| `examples/examples.py` | 4 comprehensive examples showing all features |
| `tests/tests.py` | 16 unit tests covering all functionality |
| `docs/README.md` | Complete API documentation and usage guide |

## Next Steps (Future Enhancements)

Potential additions for future versions:
- Operation composition/combining multiple ops into one
- Async operation support for async/await operations
- Conditional branching in pipelines
- Operation error handling strategies (retry, fallback, etc.)
- Middleware/hooks for logging, monitoring
- Type hints support for operation parameters
- Pipeline visualization tools
- Performance profiling/metrics

## Running Examples

```bash
python -m examples.examples
```

Output shows:
1. Basic pipeline with manual passthrough
2. Method chaining syntax
3. @passthrough decorator usage
4. Custom logic with selective deletion

All examples run successfully! ✅

---

**Version**: 0.1.0  
**Author**: Laszlo Varga  
**Status**: First release - core framework complete and tested
