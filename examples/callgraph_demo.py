#!/usr/bin/env python3
"""Demonstration of the CallGraph functionality for dependency-based execution."""

from argchain import CallGraph, operation

print("🔗 argchain CallGraph Demo")
print("=" * 50)


# Define operations for a data processing workflow
@operation(expects=['filename'], returns=['data', 'metadata'])
def load_data(filename: str):
    """Load data from a file."""
    print(f"  📂 Loading data from {filename}")
    # Simulate loading data
    data = [1, 2, 3, 4, 5]
    metadata = {'source': filename, 'count': len(data)}
    return {'data': data, 'metadata': metadata}


@operation(expects=['data'], returns=['processed', 'stats'])
def process_data(data: list):
    """Process the loaded data."""
    print(f"  ⚙️  Processing {len(data)} items")
    # Simulate processing
    processed = [x * 2 for x in data]
    stats = {'original_count': len(data), 'processed_count': len(processed)}
    return {'processed': processed, 'stats': stats}


@operation(expects=['processed'], returns=['filtered'])
def filter_data(processed: list):
    """Filter the processed data."""
    print(f"  🔍 Filtering {len(processed)} items")
    # Filter out values > 6
    filtered = [x for x in processed if x <= 6]
    return {'filtered': filtered}


@operation(expects=['filtered', 'stats'], returns=['results'])
def analyze_results(filtered: list, stats: dict):
    """Analyze the final results."""
    print(f"  📊 Analyzing {len(filtered)} filtered items")
    analysis = {
        'final_count': len(filtered),
        'efficiency': len(filtered) / stats['original_count'],
        'data': filtered
    }
    return {'results': analysis}


@operation(expects=['results', 'output_path'], returns=['saved'])
def save_results(results: dict, output_path: str):
    """Save results to file."""
    print(f"  💾 Saving results to {output_path}")
    # Simulate saving
    print(f"    Saved: {results}")
    return {'saved': True}


def example_simple_call_graph():
    """Example 1: Simple linear dependency chain."""
    print("\n1. Simple Linear Call Graph")
    print("-" * 30)

    config = {
        'operations': {
            'load': load_data,
            'process': process_data,
            'filter': filter_data,
            'analyze': analyze_results,
            'save': save_results
        },
        'dependencies': {
            'process': {'data': 'load.data'},
            'filter': {'processed': 'process.processed'},
            'analyze': {
                'filtered': 'filter.filtered',
                'stats': 'process.stats'
            },
            'save': {
                'results': 'analyze.results',
                'output_path': 'load.metadata'  # This will fail - metadata is a dict, not str
            }
        },
        'inputs': ['filename', 'output_path']
    }

    try:
        graph = CallGraph(config)
        print(f"Execution order: {graph._execution_order}")

        result = graph.execute(filename="data.txt", output_path="results.json")
        print(f"Final result keys: {list(result.keys())}")

    except Exception as e:
        print(f"Error: {e}")


def example_parallel_operations():
    """Example 2: Operations that can run in parallel."""
    print("\n2. Parallel Operations Call Graph")
    print("-" * 35)

    @operation(expects=['data'], returns=['sum'])
    def calculate_sum(data: list):
        print(f"  ➕ Calculating sum of {data}")
        return {'sum': sum(data)}

    @operation(expects=['data'], returns=['average'])
    def calculate_average(data: list):
        print(f"  📈 Calculating average of {data}")
        return {'average': sum(data) / len(data)}

    @operation(expects=['sum', 'average'], returns=['report'])
    def generate_report(sum: float, average: float):
        print("  📋 Generating report")
        return {'report': {'total': sum, 'mean': average}}

    config = {
        'operations': {
            'load': load_data,
            'sum_op': calculate_sum,
            'avg_op': calculate_average,
            'report': generate_report
        },
        'dependencies': {
            'sum_op': {'data': 'load.data'},
            'avg_op': {'data': 'load.data'},
            'report': {
                'sum': 'sum_op.sum',
                'average': 'avg_op.average'
            }
        },
        'inputs': ['filename']
    }

    graph = CallGraph(config)
    print(f"Execution order: {graph._execution_order}")

    result = graph.execute(filename="parallel_data.txt")
    print(f"Final result: {result}")


def example_complex_dependencies():
    """Example 3: More complex dependency patterns."""
    print("\n3. Complex Dependencies")
    print("-" * 25)

    @operation(expects=['base'], returns=['step1'])
    def step1(base: int):
        return {'step1': base + 1}

    @operation(expects=['base'], returns=['step2'])
    def step2(base: int):
        return {'step2': base * 2}

    @operation(expects=['step1', 'step2'], returns=['combined'])
    def combine(step1: int, step2: int):
        return {'combined': step1 + step2}

    @operation(expects=['combined'], returns=['final'])
    def finalize(combined: int):
        return {'final': combined * 10}

    config = {
        'operations': {
            's1': step1,
            's2': step2,
            'comb': combine,
            'fin': finalize
        },
        'dependencies': {
            'comb': {
                'step1': 's1.step1',
                'step2': 's2.step2'
            },
            'fin': {'combined': 'comb.combined'}
        },
        'inputs': ['base']
    }

    graph = CallGraph(config)
    print(f"Execution order: {graph._execution_order}")

    result = graph.execute(base=5)
    print(f"Result: {result}")


def example_error_handling():
    """Example 4: Error handling and validation."""
    print("\n4. Error Handling")
    print("-" * 18)

    # Test missing external input
    config = {
        'operations': {'load': load_data},
        'dependencies': {},
        'inputs': ['filename', 'required_param']
    }

    try:
        graph = CallGraph(config)
        graph.execute(filename="test.txt")  # Missing required_param
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Test cycle detection
    config_with_cycle = {
        'operations': {'op1': load_data, 'op2': process_data},
        'dependencies': {
            'op1': {'data': 'op2.processed'},  # op1 depends on op2
            'op2': {'data': 'op1.data'}       # op2 depends on op1 (cycle!)
        },
        'inputs': ['filename']
    }

    try:
        graph = CallGraph(config_with_cycle)
    except ValueError as e:
        print(f"Caught cycle error: {e}")


if __name__ == "__main__":
    example_simple_call_graph()
    example_parallel_operations()
    example_complex_dependencies()
    example_error_handling()

    print("\n✅ CallGraph functionality working!")
    print("=" * 50)
