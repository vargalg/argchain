"""
Decorators to help create operations for the pipeline.
"""

from typing import Callable, Dict, Any, List, Optional, Union
from functools import wraps


class Operation:
    """
    A callable wrapper for pipeline operations that provides metadata methods.
    
    This class wraps a decorated function and makes it callable while adding
    methods to document expected inputs and returned keys.
    """
    
    def __init__(self, func: Callable, expected_inputs: Optional[List[str]] = None, expected_outputs: Optional[List[str]] = None):
        self._func = func
        self._expected_inputs = expected_inputs or []
        self._expected_outputs = expected_outputs or []
        # Copy over function attributes for @wraps compatibility
        self.__name__ = getattr(func, '__name__', '<operation>')
        self.__doc__ = getattr(func, '__doc__', '')
        self.__module__ = getattr(func, '__module__', '')
        self.__qualname__ = getattr(func, '__qualname__', '')
        self.__annotations__ = getattr(func, '__annotations__', {})
    
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        """Make the operation callable like the original function."""
        return self._func(*args, **kwargs)
    
    def expects(self, inputs: Optional[List[str]] = None) -> 'Operation':
        """
        Set or get the expected input keys for this operation.
        
        Args:
            inputs: List of expected input key names. If None, returns current expected inputs.
            
        Returns:
            If inputs is provided, returns self for method chaining.
            If inputs is None, returns the list of expected input keys.
        """
        if inputs is not None:
            self._expected_inputs = inputs
            return self
        return self._expected_inputs
    
    def returns(self, outputs: Optional[List[str]] = None) -> Union['Operation', List[str]]:
        """
        Set or get the expected output keys for this operation.
        
        Args:
            outputs: List of expected output key names. If None, returns current expected outputs.
            
        Returns:
            If outputs is provided, returns self for method chaining.
            If outputs is None, returns the list of expected output keys.
        """
        if outputs is not None:
            self._expected_outputs = outputs
            return self
        return self._expected_outputs
    
    def __repr__(self) -> str:
        """String representation showing the operation name and metadata."""
        inputs = self._expected_inputs
        outputs = self._expected_outputs
        return f"Operation({self.__name__}, expects={inputs}, returns={outputs})"


def operation(
    delete: Optional[List[str]] = None,
    passthrough: bool = False,
    expects: Optional[List[str]] = None,
    returns: Optional[List[str]] = None
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
        expects: List of expected input key names (for documentation)
        returns: List of expected output key names (for documentation)

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
            
        # With metadata documentation
        @operation(passthrough=True, expects=['value'], returns=['value'])
        def double(value: int) -> Dict[str, Any]:
            return {'value': value * 2}
            
        # Or set metadata after decoration
        @operation(passthrough=True)
        def triple(value: int) -> Dict[str, Any]:
            return {'value': value * 3}
        
        triple.expects(['value']).returns(['value'])
    """
    def decorator(func: Callable) -> Operation:
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

        # Return Operation wrapper with metadata
        return Operation(wrapper, expected_inputs=expects, expected_outputs=returns)

    return decorator

