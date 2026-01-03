# Contributing to Geode-Engine

Thank you for your interest in contributing to Geode-Engine! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

---

## Getting Started

### Issues

- Check existing issues before creating a new one
- Use issue templates when available
- Provide clear reproduction steps for bugs

### Feature Requests

- Explain the use case
- Consider backwards compatibility
- Link to relevant documentation

---

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Geode-Engine.git
cd Geode-Engine

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest mypy

# Run tests
python run_tests.py
```

---

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for public functions

```python
def calculate_hormone_effect(hormone: str, delta: float) -> float:
    """
    Calculate the effect of a hormone change.
    
    Args:
        hormone: Name of the hormone
        delta: Change amount
        
    Returns:
        Clamped hormone value
    """
    ...
```

### Commit Messages

Use conventional commits:

```
feat: add new sensory cortex module
fix: resolve memory leak in dream engine
docs: update architecture diagram
test: add unit tests for metabolism
```

### Testing

- Write tests for new features
- Maintain > 80% coverage for core modules
- Use mocks for external dependencies

---

## Pull Request Process

1. **Fork & Branch**: Create a feature branch from `main`
2. **Develop**: Make your changes with tests
3. **Test**: Run `python run_tests.py`
4. **Lint**: Check with `mypy src/`
5. **PR**: Open a pull request with clear description

### PR Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Code follows style guidelines

---

## 🙏 Thank You!

Every contribution helps make Geode-Engine better!
