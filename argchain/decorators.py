"""
Decorators to help create operations for the pipeline.
"""

from typing import Callable, Dict, Any, List, Optional
from functools import wraps


def operation(
    delete: Optional[List[str]] = None,
    passthrough: bool = False
) -> Callable:
    """
    Decorator to mark a function as a pipeline operation.

    An operation is a function that:
    - Accepts **kwargs (arbitrary keyword arguments)
    - Returns a dict that becomes the input for the next operation
    - Can selectively pass through unchanged keys or modify them

    Args:
        delete: List of keys to delete from the output (they won't pass to next operation)
        passthrough: If True, automatically pass through all kwargs not explicitly handled

    Examples:
        # Basic operation with manual pass-through
        @operation()
        def multiply(value: int, factor: int = 2, **kwargs) -> Dict[str, Any]:
            return {**kwargs, 'value': value * factor}

        # Delete specific keys from output
        @operation(delete=['temp_data'])
        def process(value: int, temp_data: str = "", **kwargs) -> Dict[str, Any]:
            return {**kwargs, 'value': value * 2}

        # Auto pass-through everything except handled parameters
        @operation(passthrough=True)
        def add_one(value: int) -> Dict[str, Any]:
            return {'value': value + 1}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(**kwargs) -> Dict[str, Any]:
            remaining = {}  # Initialize to avoid linter warning

            if passthrough:
                # Auto pass-through mode: extract parameters the function actually uses
                import inspect
                sig = inspect.signature(func)
                # Get parameter names (excluding **kwargs if present)
                param_names = set()
                for param_name, param in sig.parameters.items():
                    if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                        param_names.add(param_name)

                # Extract handled parameters
                handled = {}
                remaining = kwargs.copy()
                for param_name in param_names:
                    if param_name in remaining:
                        handled[param_name] = remaining.pop(param_name)

                # Call function with only the parameters it handles
                result = func(**handled)

            else:
                # Manual mode: pass all kwargs to function
                result = func(**kwargs)

            # Validate return type
            if not isinstance(result, dict):
                raise TypeError(
                    f"Operation {func.__name__} must return a dict, "
                    f"but returned {type(result).__name__}"
                )

            # Handle deletions
            if delete:
                for key in delete:
                    result.pop(key, None)

            # Auto pass-through for passthrough mode
            if passthrough:
                # Merge remaining kwargs into result
                result = {**remaining, **result}

            return result

        return wrapper

    return decorator

