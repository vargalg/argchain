"""
Example usage of argchain - demonstrating the piping concept.
"""

from argchain import Pipeline, operation


# Example 1: Basic operations with manual pass-through (unchanged)
@operation()
def add_one(value: int, **kwargs) -> dict:
    """Add 1 to value and pass through all other kwargs."""
    return {**kwargs, 'value': value + 1}


@operation()
def multiply(value: int, factor: int = 2, **kwargs) -> dict:
    """Multiply value by factor."""
    return {**kwargs, 'value': value * factor}


@operation()
def to_string(value: int, **kwargs) -> dict:
    """Convert value to string and add metadata."""
    result = {**kwargs, 'value': str(value), 'converted_to_string': True}
    # We can also delete keys we don't want to pass on
    # For example: result.pop('intermediate_flag', None)
    return result


# Example 2: Using the new @operation(passthrough=True) for automatic pass-through
@operation(passthrough=True)
def double_count(count: int) -> dict:
    """Double count - everything else passes through automatically."""
    return {'count': count * 2}


@operation(passthrough=True)
def add_greeting(name: str) -> dict:
    """Add greeting - everything else passes through automatically."""
    return {'name': f"Hello, {name}!", 'greeted': True}


# Example 3: Using @operation(delete=[...]) to selectively delete keys
@operation(delete=['internal_flag'])
def validate_and_filter(value: int, internal_flag: bool = False, **kwargs) -> dict:
    """
    Validate value and selectively delete internal flags.
    This shows how to remove keys you don't want to pass down.
    """
    if value < 0:
        return {**kwargs, 'value': abs(value), 'was_negative': True}
    return {**kwargs, 'value': value, 'was_negative': False}
    # Note: internal_flag is deleted by the decorator, so it won't be passed to next op


def example_basic_pipeline():
    """Example 1: Basic Pipeline (Manual Passthrough) - unchanged."""
    print("=" * 60)
    print("Example 1: Basic Pipeline (Manual Passthrough)")
    print("=" * 60)

    # Create a pipeline
    pipeline = Pipeline()
    pipeline.pipe(add_one).pipe(multiply).pipe(to_string)

    # Execute the pipeline
    result = pipeline(value=5, metadata="example1")
    print(f"Input: value=5, metadata='example1'")
    print(f"Pipeline: add_one -> multiply -> to_string")
    print(f"Output: {result}")
    print()


def example_new_passthrough_decorator():
    """Example 2: Using the new @operation(passthrough=True)."""
    print("=" * 60)
    print("Example 2: Using @operation(passthrough=True)")
    print("=" * 60)

    result = (Pipeline()
              .pipe(double_count)
              .pipe(add_greeting)
              (count=5, name="World", source="test"))

    print(f"Input: count=5, name='World', source='test'")
    print(f"Pipeline: double_count -> add_greeting")
    print(f"Output: {result}")
    print()


def example_selective_deletion():
    """Example 3: Using @operation(delete=[...]) for selective deletion."""
    print("=" * 60)
    print("Example 3: Using @operation(delete=[...])")
    print("=" * 60)

    result = (Pipeline()
              .pipe(validate_and_filter)
              (value=-42, internal_flag=True, user_id=123))

    print(f"Input: value=-42, internal_flag=True, user_id=123")
    print(f"Pipeline: validate_and_filter")
    print(f"Output: {result}")
    print(f"Note: 'internal_flag' was deleted by decorator")
    print()


def example_combined_features():
    """Example 4: Combining features - passthrough with deletion."""
    print("=" * 60)
    print("Example 4: Combined Features")
    print("=" * 60)

    @operation(passthrough=True, delete=['temp'])
    def process_with_cleanup(value: int, temp: str = "temporary") -> dict:
        """Process value, auto pass-through, but delete temp data."""
        return {'value': value * 3, 'processed': True}

    result = (Pipeline()
              .pipe(process_with_cleanup)
              (value=7, temp="will_be_deleted", user_id=456, metadata="test"))

    print(f"Input: value=7, temp='will_be_deleted', user_id=456, metadata='test'")
    print(f"Pipeline: process_with_cleanup")
    print(f"Output: {result}")
    print(f"Note: 'temp' deleted, others passed through automatically")
    print()


if __name__ == "__main__":
    example_basic_pipeline()
    example_new_passthrough_decorator()
    example_selective_deletion()
    example_combined_features()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)

