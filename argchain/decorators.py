"""
Decorators to help create operations for the pipeline.
"""

from typing import Callable, Dict, Any, List, Optional, Union
import inspect


class Operation:
    """
    A callable wrapper for pipeline operations that provides metadata methods.
    
    This class wraps a decorated function and makes it callable while adding
    methods to document expected inputs and returned keys. All execution logic
    (passthrough, deletion, validation) is encapsulated within this class.
    """
    
    def __init__(
        self,
        func: Callable,
        delete: Optional[List[str]] = None,
        passthrough: bool = True,
        expected_inputs: Optional[List[str]] = None,
        expected_outputs: Optional[List[str]] = None
    ):
        self._func = func
        self._delete = delete or []
        self._passthrough = passthrough
        self._expected_inputs = expected_inputs or []
        self._expected_outputs = expected_outputs or []
        # Copy over function attributes for introspection
        self.__name__ = getattr(func, '__name__', '<operation>')
        self.__doc__ = getattr(func, '__doc__', '')
        self.__module__ = getattr(func, '__module__', '')
        self.__qualname__ = getattr(func, '__qualname__', '')
        self.__annotations__ = getattr(func, '__annotations__', {})
    
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the operation with passthrough, deletion, and validation logic.

        Returns:
            A dictionary containing the operation's output and any passed-through keys.

        Raises:
            TypeError: If the operation doesn't return a dictionary.
        """
        if self._passthrough:
            # Auto pass-through mode: extract only parameters the function actually uses
            sig = inspect.signature(self._func)
            # Get parameter names (excluding **kwargs if present)
            param_names = set()
            for param_name, param in sig.parameters.items():
                if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                    param_names.add(param_name)

            # Extract handled parameters
            handled = {}
            for param_name in param_names:
                if param_name in kwargs:
                    handled[param_name] = kwargs[param_name]

            # Call function with only the parameters it handles
            result = self._func(**handled)

        else:
            # Manual mode: pass all kwargs to function
            result = self._func(**kwargs)

        # Validate return type
        if not isinstance(result, dict):
            raise TypeError(
                f"Operation {self.__name__} must return a dict, "
                f"but returned {type(result).__name__}"
            )

        # Return all input kwargs, with function output taking precedence for overlapping keys
        final_result = {**kwargs, **result}

        # Handle deletions after merging
        if self._delete:
            for key in self._delete:
                final_result.pop(key, None)

        return final_result

    def expects(self, inputs: Optional[List[str]] = None) -> Union['Operation', List[str]]:
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
    passthrough: bool = True,
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

    Returns:
        A decorator function that wraps the target function in an Operation.

    Examples:
        # Basic operation with manual pass-through
        @operation(passthrough=False)
        def multiply(value: int, factor: int = 2, **kwargs) -> Dict[str, Any]:
            return {**kwargs, 'value': value * factor}

        # Delete specific keys from output
        @operation(delete=['temp_data'])
        def process(value: int, temp_data: str = "") -> Dict[str, Any]:
            return {'value': value * 2}

        # Auto pass-through everything except handled parameters (default)
        @operation()
        def add_one(value: int) -> Dict[str, Any]:
            return {'value': value + 1}
            
        # With metadata documentation
        @operation(expects=['value'], returns=['value', 'result'])
        def double(value: int) -> Dict[str, Any]:
            return {'value': value * 2, 'result': value * 2}

        # Or set metadata after decoration
        @operation()
        def triple(value: int) -> Dict[str, Any]:
            return {'value': value * 3}
        
        triple.expects(['value']).returns(['value'])
    """
    def decorator(func: Callable) -> Operation:
        return Operation(
            func,
            delete=delete,
            passthrough=passthrough,
            expected_inputs=expects,
            expected_outputs=returns
        )

    return decorator

