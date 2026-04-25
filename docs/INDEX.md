# argchain Documentation Index

## 📚 Complete Documentation Guide

Welcome to **argchain v0.1.0**! This document indexes all available resources.

---

## 🚀 Getting Started (Start Here!)

### For Absolute Beginners
1. **Read**: [`QUICKSTART.md`](QUICKSTART.md) - 30-second overview
2. **Run**: `python -m examples.examples` - See it in action
3. **Copy**: Use examples as templates

### For Experienced Developers
1. **Skim**: [`QUICKSTART.md`](QUICKSTART.md) - Architecture
2. **Read**: [`README.md`](README.md) - Full API reference
3. **Check**: [`CHEATSHEET.md`](CHEATSHEET.md) - Quick patterns

### For Library Maintainers
1. **Review**: [`FRAMEWORK.md`](FRAMEWORK.md) - Architecture
2. **Study**: `../argchain/pipeline.py` - Core implementation
3. **Check**: `../tests/tests.py` - Test coverage
4. **See**: [`STATUS.md`](STATUS.md) - Project status

---

## 📖 Main Documentation

| File | Purpose | Read Time |
|------|---------|-----------|
| **[QUICKSTART.md](QUICKSTART.md)** | 30-second overview + 5-minute tutorial + patterns | 5 min |
| **[README.md](README.md)** | Complete API reference and feature documentation | 10 min |
| **[CHEATSHEET.md](CHEATSHEET.md)** | Quick reference for common patterns and pitfalls | 3 min |
| **[FRAMEWORK.md](FRAMEWORK.md)** | Architecture, design overview, next steps | 5 min |
| **[STATUS.md](STATUS.md)** | Project status, verification checklist | 3 min |
| **[SUMMARY.md](SUMMARY.md)** | This complete summary of what's included | 5 min |

---

## 💻 Code Files

### Core Library (argchain package)
```
argchain/
├── __init__.py           # Package initialization, exports
├── pipeline.py           # Pipeline class (main orchestrator)
└── decorators.py         # @operation decorator
```

### Examples & Tests
```
examples/
├── __init__.py
└── examples.py              # 4 working examples with explanations

tests/
├── __init__.py
├── tests.py                # 16 unit tests, all passing
└── verify.py               # Quick verification test
```

### Configuration
```
pyproject.toml          # Poetry project configuration
poetry.lock             # Dependency lock file
```

---

## 🎯 Quick Reference by Use Case

### "I want to understand the concept"
→ Read: [`QUICKSTART.md`](QUICKSTART.md) (sections 1-2)

### "I want to see it in action"
→ Run: `python -m examples.examples`

### "I want to write my first operation"
→ Read: [`QUICKSTART.md`](QUICKSTART.md) (section 2: Tutorial)

### "I want a quick cheat sheet"
→ Read: [`CHEATSHEET.md`](CHEATSHEET.md)

### "I want to understand the architecture"
→ Read: [`FRAMEWORK.md`](FRAMEWORK.md)

### "I want complete API documentation"
→ Read: [`README.md`](README.md)

### "I want to see test examples"
→ Read: `../tests/tests.py` (16 test cases)

### "I want to learn advanced patterns"
→ Read: [`CHEATSHEET.md`](CHEATSHEET.md) (Common Patterns & Real-World Examples)

### "I want to know the current status"
→ Read: [`STATUS.md`](STATUS.md)

---

## 🧪 Testing & Verification

### Run All Tests
```bash
pytest tests/tests.py -v
```
**Result**: 16/16 tests passing ✅

### Run Examples
```bash
python -m examples.examples
```
**Result**: 4/4 examples working ✅

### Run Verification
```bash
python -m tests.verify
```
**Result**: Framework operational ✅

---

## 📚 Documentation Sections

### QUICKSTART.md
- 30-Second Overview
- The Three Ways to Create Operations
- 5-Minute Tutorial
- Key Concepts Explained
- Common Patterns
- Type Safety
- Error Handling
- Running Tests & Examples

### README.md
- Concept Overview
- Basic Usage
- Method Chaining
- Key Features
- Creating Operations
- API Reference
- Examples
- Installation & Requirements

### CHEATSHEET.md
- One-Line Summary
- 30-Second Setup
- Three Ways to Write Operations
- Common Patterns (9 patterns)
- Key Concepts (table)
- API Reference
- Common Mistakes & Solutions
- Import Statements
- Testing
- Debugging Tips
- Performance Tips
- Real-World Examples
- Troubleshooting

### FRAMEWORK.md
- Overview
- Project Structure
- Core Concepts
- Key Features
- Testing Results
- Usage Examples
- Next Steps

### STATUS.md
- Project Status
- What's Included (Core Library, Documentation, Examples)
- Core Features Implemented
- Test Results
- Architecture Overview
- Design Principles
- File Structure
- Verification Checklist
- Requirements
- Installation & Imports
- Support & Documentation

---

## 🎨 Core Concepts Reference

### The Pipeline Class
```python
from argchain import Pipeline

Pipeline()                      # Create empty pipeline
    .pipe(operation1)           # Add operation
    .pipe(operation2)           # Chain more operations
    (key=value, key2=value2)    # Execute with initial data
```

### @operation Decorator
```python
from argchain import operation

@operation
def my_operation(value: int, **kwargs) -> dict:
    return {**kwargs, 'value': value * 2}
```

### Key Principle: Dictionary Flow
```
Input Dict → Unpacked as **kwargs → Operation → Processes → Returns Dict
    ↓
Output Dict becomes input for next operation
```

---

## 📊 Project Statistics

- **Core Library**: ~150 lines of code
- **Documentation**: ~1500 lines
- **Tests**: 16 tests, 100% passing
- **Examples**: 4 complete, working examples
- **External Dependencies**: 0 (for core library)

---

## ✅ Feature Checklist

- ✅ Pipeline class with operation sequencing
- ✅ @operation decorator for validation
- ✅ Automatic dictionary pass-through
- ✅ Selective key deletion
- ✅ Method chaining
- ✅ Type validation and error handling
- ✅ Comprehensive documentation
- ✅ Full test coverage
- ✅ Working examples

---

## 🔗 Import Guide

### Basic Imports
```python
from argchain import Pipeline, operation
```

### What Each Export Is
- **`Pipeline`** - The orchestrator class
- **`operation`** - Decorator for operations

---

## 🎓 Learning Path

### Beginner Path (15 minutes)
1. Read: QUICKSTART.md (sections 1-2)
2. Run: `python -m examples.examples`
3. Try: Create your first operation in REPL

### Intermediate Path (30 minutes)
1. Read: QUICKSTART.md (complete)
2. Read: CHEATSHEET.md
3. Study: ../examples/examples.py code
4. Try: Modify ../examples/examples.py

### Advanced Path (1 hour)
1. Read: README.md
2. Read: FRAMEWORK.md
3. Study: ../argchain/pipeline.py and ../argchain/decorators.py
4. Study: ../tests/tests.py
5. Create: Your own complete pipeline

---

## 💡 Pro Tips

1. **Start Simple** - Use `@operation(passthrough=True)` for your first operations
2. **Use Pass-through** - Let data flow automatically unless you delete it
3. **Test Early** - Write operations that return dicts
4. **Chain Often** - Build complex pipelines from simple operations
5. **Debug with Inspect** - Add debug operations to see data flow

---

## 🐛 Troubleshooting

| Issue | First Check | Second Check | Documentation |
|-------|-------------|--------------|---|
| Import errors | Is `argchain/` directory present? | Run `python -m tests.verify` | README.md |
| Operation fails | Does it return a dict? | Check ../tests/tests.py | CHEATSHEET.md |
| Data missing | Using `{**kwargs, ...}`? | Check ../examples/examples.py | QUICKSTART.md |
| Type errors | Is operation decorated? | Check return type | README.md |

---

## 🚀 Quick Commands

```bash
# Verify everything works
python -m tests.verify

# Run all examples
python -m examples.examples

# Run all tests
pytest tests/tests.py -v

# Interactive Python
python
>>> from argchain import Pipeline, operation
>>> # Build your pipeline here
```

---

## 📞 Support Resources

1. **API Help** → [`README.md`](README.md)
2. **Quick Help** → [`CHEATSHEET.md`](CHEATSHEET.md)
3. **Getting Started** → [`QUICKSTART.md`](QUICKSTART.md)
4. **Architecture** → [`FRAMEWORK.md`](FRAMEWORK.md)
5. **Examples** → `../examples/examples.py`
6. **Tests** → `../tests/tests.py`

---

## 🎯 Document Recommendations by Background

### Python Beginners
1. QUICKSTART.md - Start here!
2. ../examples/examples.py - See it work
3. CHEATSHEET.md - Quick reference
4. README.md - Details

### Python Experienced
1. QUICKSTART.md - Overview
2. README.md - Full reference
3. FRAMEWORK.md - Deep dive
4. ../argchain/ - Source code

### Library Developers
1. FRAMEWORK.md - Architecture
2. ../argchain/ - Implementation
3. ../tests/tests.py - Test coverage
4. STATUS.md - Project status

---

## 📋 Version Information

- **Version**: 0.1.0
- **Status**: Production Ready
- **Python**: 3.10+
- **Created**: April 17, 2026
- **Author**: Laszlo Varga

---

## 🎉 Ready to Start?

Choose your path above and start learning!

- **Impatient?** → Run `python -m examples.examples`
- **Curious?** → Read `QUICKSTART.md`
- **Technical?** → Read `README.md`
- **Building?** → Read `CHEATSHEET.md`

---

**Happy piping! 🚀**

For questions, refer to the appropriate documentation above.
All answers are in these documents!
