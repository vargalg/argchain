#!/usr/bin/env python3
"""Demonstration of the new Operation metadata functionality."""

from argchain import Pipeline, operation

print("🎯 argchain Operation Metadata Demo")
print("=" * 50)

# Example 1: Setting metadata in the decorator
print("\n1. Metadata set in decorator:")
@operation(passthrough=True, expects=['value'], returns=['value', 'doubled'])
def double_with_metadata(value: int):
    return {'value': value * 2, 'doubled': True}

print(f"   Expects: {double_with_metadata.expects()}")
print(f"   Returns: {double_with_metadata.returns()}")
print(f"   Function call: {double_with_metadata(value=5)}")

# Example 2: Setting metadata after decoration
print("\n2. Metadata set after decoration:")
@operation(passthrough=True)
def triple(value: int):
    return {'value': value * 3}

# Set metadata using method chaining
triple.expects(['value']).returns(['value'])
print(f"   Expects: {triple.expects()}")
print(f"   Returns: {triple.returns()}")
print(f"   Function call: {triple(value=4)}")

# Example 3: Using metadata in a pipeline
print("\n3. Pipeline with metadata operations:")
pipeline = Pipeline().pipe(double_with_metadata).pipe(triple)

print("   Pipeline operations:")
for op in pipeline._operations:
    print(f"     {op}")

result = pipeline(value=2, metadata="test")
print(f"   Pipeline result: {result}")

# Example 4: Dynamic metadata updates
print("\n4. Dynamic metadata updates:")
@operation()
def add_numbers(a: int, b: int, **kwargs):
    return {**kwargs, 'sum': a + b}

print(f"   Initial expects: {add_numbers.expects()}")
add_numbers.expects(['a', 'b'])
print(f"   After setting expects: {add_numbers.expects()}")
add_numbers.returns(['sum'])
print(f"   After setting returns: {add_numbers.returns()}")

result = add_numbers(a=3, b=7, extra="data")
print(f"   Function call: {result}")

print("\n✅ All metadata functionality working!")
print("=" * 50)
