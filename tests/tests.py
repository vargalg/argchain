"""
Unit tests for argchain library.
"""

import pytest
from argchain import Pipeline, operation, CallGraph


class TestPipeline:
    """Tests for the Pipeline class."""

    def test_single_operation(self):
        """Test pipeline with a single operation."""
        @operation(passthrough=False)
        def add_value(**kwargs):
            return {**kwargs, 'result': kwargs.get('value', 0) + 1}

        pipeline = Pipeline().pipe(add_value)
        result = pipeline(value=5)
        assert result['result'] == 6

    def test_multiple_operations(self):
        """Test pipeline with multiple operations in sequence."""
        @operation()
        def increment(value: int, **kwargs):
            return {**kwargs, 'value': value + 1}

        @operation()
        def double(value: int, **kwargs):
            return {**kwargs, 'value': value * 2}

        pipeline = Pipeline().pipe(increment).pipe(double)
        result = pipeline(value=5)
        assert result['value'] == 12  # (5 + 1) * 2

    def test_passthrough_kwargs(self):
        """Test that unmodified kwargs pass through the pipeline."""
        @operation()
        def transform(value: int, **kwargs):
            return {**kwargs, 'value': value * 2}

        pipeline = Pipeline().pipe(transform)
        result = pipeline(value=5, metadata="test", user_id=42)

        assert result['value'] == 10
        assert result['metadata'] == "test"
        assert result['user_id'] == 42

    def test_selective_deletion(self):
        """Test that operations can selectively delete keys."""
        @operation()
        def filter_keys(value: int, secret: str = "", **kwargs):
            # secret is intentionally not included in output
            return {**kwargs, 'value': value}

        pipeline = Pipeline().pipe(filter_keys)
        result = pipeline(value=5, secret="shhh", public="visible")

        assert result['value'] == 5
        assert result['public'] == "visible"
        assert 'secret' not in result

    def test_callable_syntax(self):
        """Test that pipeline can be called directly."""
        @operation(passthrough=False)
        def double(**kwargs):
            return {**kwargs, 'value': kwargs.get('value', 0) * 2}

        pipeline = Pipeline().pipe(double)
        result = pipeline(value=10)
        assert result['value'] == 20

    def test_error_non_dict_return(self):
        """Test that non-dict returns raise TypeError."""
        @operation()
        def bad_operation(**kwargs):
            return "not a dict"  # Invalid return type

        pipeline = Pipeline().pipe(bad_operation)
        with pytest.raises(TypeError, match="must return a dict"):
            pipeline(value=1)

    def test_method_chaining(self):
        """Test method chaining syntax."""
        @operation()
        def add_one(value: int, **kwargs):
            return {**kwargs, 'value': value + 1}

        @operation()
        def multiply(value: int, **kwargs):
            return {**kwargs, 'value': value * 2}

        result = (Pipeline()
                  .pipe(add_one)
                  .pipe(multiply)
                  (value=5))

        assert result['value'] == 12

    def test_empty_pipeline(self):
        """Test pipeline with no operations returns input unchanged."""
        pipeline = Pipeline()
        result = pipeline(value=5, name="test")
        assert result == {'value': 5, 'name': 'test'}

    def test_repr(self):
        """Test pipeline string representation."""
        @operation()
        def op1(**kwargs):
            return kwargs

        @operation()
        def op2(**kwargs):
            return kwargs

        pipeline = Pipeline().pipe(op1).pipe(op2)
        repr_str = repr(pipeline)
        assert "op1" in repr_str
        assert "op2" in repr_str


class TestOperationDecorator:
    """Tests for the @operation decorator."""

    def test_operation_basic(self):
        """Test basic operation decorator."""
        @operation(passthrough=False)
        def simple(**kwargs):
            return {'result': 'success'}

        result = simple(value=1)
        assert result == {'result': 'success'}

    def test_operation_type_checking(self):
        """Test that operation decorator validates return type."""
        @operation()
        def bad_return(**kwargs):
            return [1, 2, 3]  # Returns list instead of dict

        with pytest.raises(TypeError, match="must return a dict"):
            bad_return()

    def test_operation_delete_keys(self):
        """Test @operation(delete=[...]) removes specified keys."""
        @operation(delete=['secret'])
        def process_with_deletion(value: int, secret: str = "", **kwargs):
            return {**kwargs, 'value': value * 2}

        result = process_with_deletion(value=5, secret="hidden", public="visible")
        assert result['value'] == 10
        assert result['public'] == "visible"
        assert 'secret' not in result

    def test_operation_passthrough(self):
        """Test @operation(passthrough=True) auto passes through unhandled params."""
        @operation(passthrough=True)
        def double(value: int):
            return {'value': value * 2}

        result = double(value=5, metadata="test", user_id=42)
        assert result['value'] == 10
        assert result['metadata'] == "test"
        assert result['user_id'] == 42

    def test_operation_passthrough_with_defaults(self):
        """Test passthrough with default parameter values."""
        @operation(passthrough=True)
        def triple(count: int = 1):
            return {'count': count * 3}

        result = triple(other="value")
        assert result['count'] == 3  # default 1 * 3
        assert result['other'] == "value"

    def test_operation_combined_delete_and_passthrough(self):
        """Test combining delete and passthrough features."""
        @operation(passthrough=True, delete=['temp'])
        def process_and_cleanup(value: int, temp: str = "temporary"):
            return {'value': value * 3, 'processed': True}

        result = process_and_cleanup(
            value=7,
            temp="will_be_deleted",
            user_id=456,
            metadata="test"
        )

        assert result['value'] == 21
        assert result['processed'] == True
        assert result['user_id'] == 456
        assert result['metadata'] == "test"
        assert 'temp' not in result

    def test_operation_passthrough_in_pipeline(self):
        """Test passthrough operations in a pipeline."""
        @operation(passthrough=True)
        def add_one(value: int):
            return {'value': value + 1}

        @operation(passthrough=True)
        def multiply(value: int):
            return {'value': value * 2}

        result = (Pipeline()
                  .pipe(add_one)
                  .pipe(multiply)
                  (value=5, metadata="test"))

        assert result['value'] == 12
        assert result['metadata'] == "test"


class TestOperationMetadata:
    """Tests for the Operation wrapper metadata methods."""

    def test_operation_expects_method(self):
        """Test the expects() method for setting and getting expected inputs."""
        @operation()
        def my_op(value: int, **kwargs):
            return {**kwargs, 'value': value * 2}

        # Initially empty
        assert my_op.expects() == []

        # Set expected inputs
        my_op.expects(['value', 'factor'])
        assert my_op.expects() == ['value', 'factor']

        # Method chaining
        result = my_op.expects(['value']).expects()
        assert result == ['value']

    def test_operation_returns_method(self):
        """Test the returns() method for setting and getting expected outputs."""
        @operation()
        def my_op(value: int, **kwargs):
            return {**kwargs, 'value': value * 2}

        # Initially empty
        assert my_op.returns() == []

        # Set expected outputs
        my_op.returns(['value', 'metadata'])
        assert my_op.returns() == ['value', 'metadata']

        # Method chaining
        result = my_op.returns(['value']).returns()
        assert result == ['value']

    def test_operation_metadata_in_decorator(self):
        """Test setting metadata directly in the decorator."""
        @operation(expects=['value'], returns=['value', 'doubled'])
        def double(value: int):
            return {'value': value * 2, 'doubled': True}

        assert double.expects() == ['value']
        assert double.returns() == ['value', 'doubled']

        # Function still works
        result = double(value=5)
        assert result == {'value': 10, 'doubled': True}

    def test_operation_repr(self):
        """Test string representation of Operation objects."""
        @operation(expects=['input'], returns=['output'])
        def my_op(**kwargs):
            return {'output': 'result'}

        repr_str = repr(my_op)
        assert 'my_op' in repr_str
        assert 'expects=[' in repr_str
        assert 'returns=[' in repr_str

    def test_operation_callable(self):
        """Test that Operation objects are still callable like functions."""
        @operation()
        def add(value: int, **kwargs):
            return {**kwargs, 'value': value + 1}

        # Should work like a regular function
        result = add(value=5, metadata="test")
        assert result == {'value': 6, 'metadata': 'test'}

        # Should have function attributes
        assert add.__name__ == 'add'
        assert callable(add)

    def test_operation_metadata_with_passthrough(self):
        """Test metadata methods work with passthrough operations."""
        @operation(passthrough=True, expects=['count'], returns=['count'])
        def increment(count: int):
            return {'count': count + 1}

        assert increment.expects() == ['count']
        assert increment.returns() == ['count']

        # Test functionality
        result = increment(count=5, other="data")
        assert result == {'count': 6, 'other': 'data'}


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_complex_pipeline(self):
        """Test a complex pipeline with multiple operations and features."""
        @operation()
        def validate(value: int, **kwargs):
            if value < 0:
                return {**kwargs, 'value': abs(value), 'was_negative': True}
            return {**kwargs, 'value': value, 'was_negative': False}

        @operation(passthrough=True)
        def double(value: int):
            return {'value': value * 2}

        @operation()
        def format_result(value: int, format_type: str = 'int', **kwargs):
            if format_type == 'string':
                return {**kwargs, 'value': str(value)}
            return {**kwargs, 'value': value}

        result = (Pipeline()
                  .pipe(validate)
                  .pipe(double)
                  .pipe(format_result)
                  (value=-5, format_type='string', user_id=123))

        assert result['value'] == '10'
        assert result['was_negative'] == True
        assert result['user_id'] == 123


class TestCallGraph:
    """Tests for the CallGraph class."""

    def test_simple_linear_dependencies(self):
        """Test call graph with simple linear dependencies."""
        @operation(expects=['input'], returns=['output'])
        def op1(input: int):
            return {'output': input + 1}

        @operation(expects=['data'], returns=['result'])
        def op2(data: int):
            return {'result': data * 2}

        config = {
            'operations': {'first': op1, 'second': op2},
            'dependencies': {'second': {'data': 'first.output'}},
            'inputs': ['input']
        }

        graph = CallGraph(config)
        result = graph.execute(input=5)

        assert result['output'] == 6  # 5 + 1
        assert result['result'] == 12  # 6 * 2

    def test_parallel_operations(self):
        """Test operations that can run in parallel."""
        @operation(expects=['value'], returns=['doubled'])
        def double(value: int):
            return {'doubled': value * 2}

        @operation(expects=['value'], returns=['squared'])
        def square(value: int):
            return {'squared': value ** 2}

        @operation(expects=['doubled', 'squared'], returns=['combined'])
        def combine(doubled: int, squared: int):
            return {'combined': doubled + squared}

        config = {
            'operations': {'double': double, 'square': square, 'combine': combine},
            'dependencies': {
                'combine': {
                    'doubled': 'double.doubled',
                    'squared': 'square.squared'
                }
            },
            'inputs': ['value']
        }

        graph = CallGraph(config)
        result = graph.execute(value=3)

        assert result['doubled'] == 6
        assert result['squared'] == 9
        assert result['combined'] == 15  # 6 + 9

    def test_topological_sort(self):
        """Test that operations are executed in correct dependency order."""
        execution_order = []

        @operation(returns=['a'])
        def op_a():
            execution_order.append('a')
            return {'a': 1}

        @operation(returns=['b'])
        def op_b():
            execution_order.append('b')
            return {'b': 2}

        @operation(expects=['a', 'b'], returns=['c'])
        def op_c(a: int, b: int):
            execution_order.append('c')
            return {'c': a + b}

        config = {
            'operations': {'a': op_a, 'b': op_b, 'c': op_c},
            'dependencies': {'c': {'a': 'a.a', 'b': 'b.b'}}
        }

        graph = CallGraph(config)
        graph.execute()

        # Should execute independent ops first, then dependent
        assert execution_order.index('c') > execution_order.index('a')
        assert execution_order.index('c') > execution_order.index('b')

    def test_missing_external_input(self):
        """Test error when required external input is missing."""
        @operation(expects=['required'], returns=['output'])
        def op(required: str):
            return {'output': required.upper()}

        config = {
            'operations': {'op': op},
            'dependencies': {},
            'inputs': ['required']
        }

        graph = CallGraph(config)

        with pytest.raises(ValueError, match="Missing required external inputs"):
            graph.execute()  # Missing 'required' input

    def test_invalid_dependency_format(self):
        """Test error for invalid dependency specification."""
        @operation(returns=['output'])
        def op():
            return {'output': 42}

        config = {
            'operations': {'op': op},
            'dependencies': {'op': {'input': 'invalid_format'}}  # Missing dot
        }

        with pytest.raises(ValueError, match="Invalid dependency specification"):
            CallGraph(config)

    def test_cycle_detection(self):
        """Test that cycles in dependencies are detected."""
        @operation(expects=['dep'], returns=['output'])
        def op1(dep: int):
            return {'output': dep + 1}

        @operation(expects=['dep'], returns=['output'])
        def op2(dep: int):
            return {'output': dep * 2}

        config = {
            'operations': {'op1': op1, 'op2': op2},
            'dependencies': {
                'op1': {'dep': 'op2.output'},  # op1 depends on op2
                'op2': {'dep': 'op1.output'}   # op2 depends on op1 (cycle!)
            }
        }

        with pytest.raises(ValueError, match="contains cycles"):
            CallGraph(config)

    def test_operation_error_propagation(self):
        """Test that operation errors are properly propagated."""
        @operation(returns=['output'])
        def failing_op():
            raise ValueError("Operation failed")

        config = {
            'operations': {'fail': failing_op},
            'dependencies': {}
        }

        graph = CallGraph(config)

        with pytest.raises(RuntimeError, match="Error executing operation 'fail'"):
            graph.execute()

    def test_non_dict_return_error(self):
        """Test error when operation doesn't return a dict."""
        @operation()
        def bad_op():
            return "not a dict"

        config = {
            'operations': {'bad': bad_op},
            'dependencies': {}
        }

        graph = CallGraph(config)

        with pytest.raises(RuntimeError, match="must return a dict"):
            graph.execute()

    def test_callable_interface(self):
        """Test that CallGraph can be called directly like a function."""
        @operation(expects=['x'], returns=['y'])
        def simple_op(x: int):
            return {'y': x + 1}

        config = {
            'operations': {'simple': simple_op},
            'dependencies': {},
            'inputs': ['x']
        }

        graph = CallGraph(config)
        result = graph(x=5)  # Direct call

        assert result['y'] == 6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
