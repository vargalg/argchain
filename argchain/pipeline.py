"""
Core Pipeline class for composing operations that pass data through a chain.
"""

from typing import Callable, Dict, Any, List


class Pipeline:
    """
    A pipeline that chains operations together, passing dictionary data
    through a sequence of operations.
    
    Each operation receives the previous operation's output as **kwargs,
    processes it, and returns a new dictionary for the next operation.
    """
    
    def __init__(self):
        """Initialize an empty pipeline."""
        self._operations: List[Callable] = []
    
    def add_operation(self, operation: Callable) -> "Pipeline":
        """
        Add an operation to the pipeline.
        
        Args:
            operation: A callable that takes **kwargs and returns a dict
            
        Returns:
            self for method chaining
        """
        self._operations.append(operation)
        return self
    
    def pipe(self, operation: Callable) -> "Pipeline":
        """
        Alias for add_operation for more intuitive piping syntax.
        
        Args:
            operation: A callable that takes **kwargs and returns a dict
            
        Returns:
            self for method chaining
        """
        return self.add_operation(operation)
    
    def execute(self, **initial_data) -> Dict[str, Any]:
        """
        Execute the pipeline with initial data.
        
        Args:
            **initial_data: Initial keyword arguments to pass to the first operation
            
        Returns:
            The final dictionary output after all operations have been applied
        """
        result = initial_data
        
        for operation in self._operations:
            # Unpack the current result as kwargs to the next operation
            result = operation(**result)
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                raise TypeError(
                    f"Operation {operation.__name__} must return a dict, "
                    f"but returned {type(result).__name__}"
                )
        
        return result
    
    def __call__(self, **initial_data) -> Dict[str, Any]:
        """Allow the pipeline to be called directly like a function."""
        return self.execute(**initial_data)
    
    def __repr__(self) -> str:
        """Return a string representation of the pipeline."""
        ops = ", ".join(op.__name__ for op in self._operations)
        return f"Pipeline({ops})"

