"""
Unit tests for argchain library.
"""

import pytest
from argchain import Pipeline, operation


class TestPipeline:
    """Tests for the Pipeline class."""

    def test_single_operation(self):
        """Test pipeline with a single operation."""
        @operation()
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
        @operation()
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
        @operation()
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
