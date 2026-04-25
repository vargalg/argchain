#!/usr/bin/env python3
"""Final verification test for argchain framework."""

from argchain import Pipeline, operation

print("\n" + "="*60)
print("ARGCHAIN FRAMEWORK - FINAL VERIFICATION")
print("="*60 + "\n")

# Quick verification test
@operation(passthrough=True)
def add_one(x):
    return {'x': x + 1}

@operation(passthrough=True)
def multiply(x):
    return {'x': x * 2}

result = Pipeline().pipe(add_one).pipe(multiply)(x=5, metadata='test')
expected = {'x': 12, 'metadata': 'test'}

if result == expected:
    print("✓ All systems operational!")
    print("✓ Input: x=5, metadata='test'")
    print("✓ Pipeline: add_one → multiply")
    print(f"✓ Output: {result}")
    print("✓ Computation: (5+1)*2 = 12")
    print("✓ Pass-through: metadata preserved")
    print("\n" + "="*60)
    print("✨ ARGCHAIN v0.1.0 IS READY TO USE ✨")
    print("="*60 + "\n")
else:
    print("✗ Unexpected result!")
    print(f"Expected: {expected}")
    print(f"Got: {result}")
