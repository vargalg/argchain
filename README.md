# argchain - Pipe Python Operations

A lightweight Python library for composing operations that pass data through a pipeline, enabling elegant functional data flow.

## 📚 Documentation

All documentation is located in the [`docs/`](./docs/) directory:

- **[README.md](./docs/README.md)** - Complete API reference and documentation
- **[QUICKSTART.md](./docs/QUICKSTART.md)** - 30-second overview + 5-minute tutorial
- **[CHEATSHEET.md](./docs/CHEATSHEET.md)** - Quick reference for common patterns
- **[INDEX.md](./docs/INDEX.md)** - Complete documentation index

## 🚀 Quick Start

```bash
# Install dependencies
pip install -e .

# Run examples
python -m examples.examples

# Run tests
python -m pytest tests/

# Run verification
python -m tests.verify
```

## 📁 Project Structure

```
argchain/
├── argchain/           # Core library package
├── examples/           # Example usage scripts
├── tests/             # Unit tests and verification
├── docs/              # Documentation
├── pyproject.toml     # Project configuration
└── poetry.lock        # Dependency lock
```

## 🎯 Key Features

- **Operation Pipelines**: Chain operations that pass dictionary data
- **Automatic Pass-through**: Unmodified data flows through automatically
- **Selective Deletion**: Remove specific keys from the pipeline
- **Type Safety**: Operations must return dictionaries
- **Fluent API**: Method chaining for building pipelines

## 📖 Learn More

Start with the [documentation index](./docs/INDEX.md) or jump directly to:

- **Getting Started**: [`docs/QUICKSTART.md`](./docs/QUICKSTART.md)
- **API Reference**: [`docs/README.md`](./docs/README.md)
- **Examples**: [`examples/examples.py`](./examples/examples.py)

---

**Version**: 0.1.0 | **Status**: Production Ready
