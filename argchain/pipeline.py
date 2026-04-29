"""
Core Pipeline class for composing operations that pass data through a chain.
"""

from typing import Callable, Dict, Any, List, Set, Optional
from collections import defaultdict, deque
import itertools


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


class CallGraph:
    """
    A call graph that executes operations based on their dependencies.

    Unlike Pipeline which executes operations linearly, CallGraph allows for
    complex dependency relationships where operations can depend on outputs
    from multiple other operations.

    Configuration format:
    {
        'operations': {
            'op_name': operation_function,
            ...
        },
        'dependencies': {
            'dependent_op': {'input_param': 'source_op.output_key', ...},
            ...
        },
        'inputs': ['external_input1', 'external_input2', ...]  # optional
    }
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a call graph with the given configuration.

        Args:
            config: Configuration dictionary with operations, dependencies, and inputs

        Raises:
            ValueError: If configuration is invalid or contains cycles
        """
        self._config = config
        self._operations = config.get('operations', {})
        self._dependencies = config.get('dependencies', {})
        self._external_inputs = set(config.get('inputs', []))

        # Validate configuration
        self._validate_config()

        # Build dependency graph for topological sorting
        self._build_dependency_graph()

        # Perform topological sort to get execution order
        self._execution_order = self._topological_sort()

    def _validate_config(self):
        """Validate the configuration for consistency."""
        # Check that all dependency sources exist as operations
        for dep_op, deps in self._dependencies.items():
            if dep_op not in self._operations:
                raise ValueError(f"Dependent operation '{dep_op}' not found in operations")

            for input_param, source_spec in deps.items():
                if not isinstance(source_spec, str) or '.' not in source_spec:
                    raise ValueError(
                        f"Invalid dependency specification '{source_spec}' for {dep_op}.{input_param}. "
                        "Expected format: 'source_operation.output_key'"
                    )
                source_op, output_key = source_spec.split('.', 1)
                if source_op not in self._operations:
                    raise ValueError(
                        f"Source operation '{source_op}' not found in operations "
                        f"(referenced by {dep_op}.{input_param})"
                    )

    def _build_dependency_graph(self):
        """Build the dependency graph for topological sorting."""
        self._graph = defaultdict(list)  # operation -> list of operations that depend on it
        self._in_degree = defaultdict(int)  # operation -> number of dependencies

        # Initialize all operations
        for op_name in self._operations:
            if op_name not in self._in_degree:
                self._in_degree[op_name] = 0

        # Build graph from dependencies
        for dep_op, deps in self._dependencies.items():
            for source_spec in deps.values():
                source_op = source_spec.split('.', 1)[0]
                if source_op != dep_op:  # Avoid self-loops
                    self._graph[source_op].append(dep_op)
                    self._in_degree[dep_op] += 1

    def _topological_sort(self) -> List[str]:
        """
        Perform topological sort to determine execution order.

        Returns:
            List of operation names in execution order

        Raises:
            ValueError: If the graph contains cycles
        """
        # Kahn's algorithm
        queue = deque([op for op in self._operations if self._in_degree[op] == 0])
        result = []
        in_degree = dict(self._in_degree)  # Copy

        while queue:
            current = queue.popleft()
            result.append(current)

            for dependent in self._graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self._operations):
            raise ValueError("Call graph contains cycles - cannot determine execution order")

        return result

    def execute(self, **external_inputs) -> Dict[str, Any]:
        """
        Execute the call graph with external inputs.

        Args:
            **external_inputs: External data not produced by any operation

        Returns:
            Dictionary containing all operation outputs

        Raises:
            ValueError: If required inputs are missing
        """
        # Validate external inputs
        provided_inputs = set(external_inputs.keys())
        required_inputs = self._external_inputs
        missing = required_inputs - provided_inputs
        if missing:
            raise ValueError(f"Missing required external inputs: {missing}")

        # Initialize data store with external inputs
        data_store = dict(external_inputs)
        operation_outputs = {}

        # Execute operations in topological order
        for op_name in self._execution_order:
            operation = self._operations[op_name]

            # Gather inputs for this operation
            op_inputs = {}

            # Add external inputs that this operation might need
            for input_name in self._external_inputs:
                if input_name in external_inputs:
                    op_inputs[input_name] = external_inputs[input_name]

            # Add outputs from other operations that this operation depends on
            if op_name in self._dependencies:
                for input_param, source_spec in self._dependencies[op_name].items():
                    source_op, output_key = source_spec.split('.', 1)
                    if source_op in operation_outputs:
                        op_inputs[input_param] = operation_outputs[source_op].get(output_key)
                    else:
                        raise ValueError(
                            f"Operation '{op_name}' depends on '{source_op}' which hasn't been executed yet"
                        )

            # Execute the operation
            try:
                result = operation(**op_inputs)
                if not isinstance(result, dict):
                    raise TypeError(
                        f"Operation '{op_name}' must return a dict, "
                        f"but returned {type(result).__name__}"
                    )
                operation_outputs[op_name] = result

                # Merge operation output into data store for potential use by other operations
                data_store.update(result)

            except Exception as e:
                raise RuntimeError(f"Error executing operation '{op_name}': {e}") from e

        return data_store

    def __call__(self, **external_inputs) -> Dict[str, Any]:
        """Allow the call graph to be called directly like a function."""
        return self.execute(**external_inputs)

    def __repr__(self) -> str:
        """Return a string representation of the call graph."""
        ops = ", ".join(self._execution_order)
        return f"CallGraph({ops})"

