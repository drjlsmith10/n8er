# Contributing to Project Automata

Thank you for your interest in contributing to Project Automata! 🎉

We welcome contributions from everyone. This document provides guidelines for contributing to the project.

---

## 🌟 Ways to Contribute

### 1. **Report Bugs** 🐛
Found a bug? Please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages or logs

### 2. **Suggest Features** 💡
Have an idea? Open a feature request with:
- Problem you're trying to solve
- Proposed solution
- Why it would benefit users
- Any implementation ideas

### 3. **Improve Documentation** 📚
Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples
- Improve getting started guides
- Translate documentation

### 4. **Contribute Code** 💻
Submit pull requests for:
- Bug fixes
- New features
- Performance improvements
- Code quality improvements

### 5. **Share Workflow Patterns** 🔄
Add community-learned workflow patterns:
- Real-world n8n workflows
- Error solutions you've discovered
- Node usage tips
- Best practices

### 6. **Help Others** 🤝
Support the community by:
- Answering questions in issues
- Helping debug problems
- Sharing your use cases
- Writing tutorials or blog posts

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- git
- Basic knowledge of n8n (helpful but not required)

### Setup Development Environment

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/n8er.git
cd n8er/automata-n8n

# 3. Add upstream remote
git remote add upstream https://github.com/drjlsmith10/n8er.git

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# 6. Run tests to verify setup
pytest tests/ -v
```

### Keep Your Fork Updated

```bash
# Fetch latest changes from upstream
git fetch upstream

# Merge upstream changes into your main branch
git checkout main
git merge upstream/main

# Push updates to your fork
git push origin main
```

---

## 📝 Development Workflow

### 1. Create a Branch

```bash
# Create a new branch for your work
git checkout -b feature/my-new-feature

# Or for bug fixes
git checkout -b fix/issue-123
```

**Branch naming conventions:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions/improvements

### 2. Make Your Changes

**Code Style:**
- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small
- Add inline comments for complex logic

**Example:**
```python
def generate_workflow(prompt: str, validate: bool = True) -> Dict:
    """
    Generate n8n workflow from natural language prompt.

    Args:
        prompt: Natural language description of workflow
        validate: Whether to validate generated workflow

    Returns:
        Dictionary containing workflow JSON

    Raises:
        ValueError: If prompt is empty or invalid
    """
    # Implementation here
    pass
```

### 3. Write Tests

**All new code must include tests:**

```python
# tests/test_my_feature.py
import pytest
from skills.my_feature import my_function

def test_my_function_basic():
    """Test basic functionality"""
    result = my_function("test input")
    assert result == "expected output"

def test_my_function_edge_case():
    """Test edge case handling"""
    with pytest.raises(ValueError):
        my_function("")
```

**Run tests:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_my_feature.py -v

# Run with coverage
pytest tests/ --cov=skills --cov=agents --cov-report=html
```

### 4. Commit Your Changes

**Write clear commit messages:**

```bash
# Format: <type>: <description>
git commit -m "feat: Add workflow optimization engine"
git commit -m "fix: Resolve circular dependency detection bug"
git commit -m "docs: Update installation instructions"
git commit -m "test: Add tests for NL parser"
```

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/improvements
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Good commit messages:**
✅ `feat: Add simulation engine for workflow testing`
✅ `fix: Handle empty node lists in parser (closes #123)`
✅ `docs: Add deployment guide for Docker`

**Bad commit messages:**
❌ `update`
❌ `fix bug`
❌ `changes`

### 5. Run Quality Checks

```bash
# Format code
black .

# Check code style
flake8 .

# Type checking
mypy skills/ agents/

# Run all tests
pytest tests/ -v

# Check test coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### 6. Push to Your Fork

```bash
# Push your branch to your fork
git push origin feature/my-new-feature
```

### 7. Create Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill in the PR template
4. Link related issues (e.g., "Closes #123")
5. Wait for review

---

## 🎯 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Code follows style guidelines (`black .` and `flake8 .`)
- [ ] Documentation updated (if applicable)
- [ ] Changelog updated (if applicable)
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Should Include

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2

## Testing
How did you test this?

## Screenshots (if applicable)
Before/after screenshots

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer review** (1-3 days typically)
3. **Feedback** may be provided
4. **Iteration** if changes requested
5. **Merge** when approved

---

## 🧪 Testing Guidelines

### Test Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Aim for >80% code coverage
- Tests should be fast (<1 second each)
- Tests should be isolated and repeatable

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange - Set up test data
    input_data = {...}

    # Act - Execute the code
    result = function_to_test(input_data)

    # Assert - Verify results
    assert result == expected_value
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_schema_validation.py

# Specific test
pytest tests/test_schema_validation.py::test_valid_workflow

# With coverage
pytest --cov=skills --cov-report=html

# Fast tests only
pytest -m "not slow"

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

---

## 📚 Documentation Guidelines

### Docstring Format

Use Google-style docstrings:

```python
def parse_workflow(prompt: str, strict: bool = True) -> ParsedIntent:
    """
    Parse natural language prompt into workflow intent.

    Args:
        prompt: Natural language description of desired workflow
        strict: Whether to use strict parsing mode

    Returns:
        ParsedIntent object containing extracted information

    Raises:
        ValueError: If prompt is empty or invalid

    Example:
        >>> intent = parse_workflow("When webhook arrives, save to DB")
        >>> print(intent.trigger_type)
        'webhook'
    """
```

### Documentation Files

- **README.md** - Overview, quick start, main features
- **QUICKSTART.md** - 5-minute getting started
- **docs/DEPLOYMENT.md** - Deployment instructions
- **docs/architecture.md** - System architecture
- **Code comments** - Inline explanations for complex logic

---

## 🎨 Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

```python
# Line length: 100 characters max
# Indentation: 4 spaces (no tabs)
# Quotes: Double quotes for strings
# Naming:
#   - Classes: PascalCase
#   - Functions: snake_case
#   - Constants: UPPER_SNAKE_CASE
#   - Private: _leading_underscore

# Good
class WorkflowParser:
    """Parse workflow descriptions."""

    def parse_prompt(self, prompt: str) -> ParsedIntent:
        """Parse natural language prompt."""
        return ParsedIntent(...)

# Use type hints
def generate_workflow(
    prompt: str,
    validate: bool = True,
    simulate: bool = False
) -> Dict[str, Any]:
    """Generate workflow with options."""
    pass

# Use f-strings
message = f"Generated {count} workflows"

# Use list comprehensions for simple transformations
active_nodes = [n for n in nodes if n.enabled]

# Use descriptive variable names
user_prompt = "..."  # Good
up = "..."          # Bad
```

### Import Order

```python
# 1. Standard library
import os
import sys
from typing import Dict, List

# 2. Third-party
import pytest
from dotenv import load_dotenv

# 3. Local
from skills.knowledge_base import KnowledgeBase
from agents import BaseAgent
```

---

## 🐛 Reporting Bugs

### Before Reporting

1. **Search existing issues** - Your bug may already be reported
2. **Try latest version** - Bug might be fixed in main branch
3. **Minimal reproduction** - Simplify to smallest reproducing case

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Install version X
2. Run command Y
3. See error Z

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.0]
- Project Automata version: [e.g., 2.0.0]

**Error Messages**
```
Paste full error message here
```

**Additional Context**
Any other relevant information
```

---

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Problem**
What problem does this solve?

**Proposed Solution**
Describe your proposed solution

**Alternatives Considered**
Other solutions you've thought about

**Use Cases**
How would this be used?

**Additional Context**
Mock-ups, examples, etc.
```

---

## 🔒 Security Issues

**Do NOT report security vulnerabilities in public issues.**

Instead:
1. Email security concerns to: [your-security-email]
2. Include "SECURITY" in subject line
3. Provide detailed description
4. We'll respond within 48 hours

See [SECURITY.md](SECURITY.md) for details.

---

## 🏆 Recognition

Contributors are recognized in:
- **GitHub Contributors** page
- **Release notes** for significant contributions
- **README.md** (top contributors)

---

## 📜 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

**Summary:**
- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

---

## 💬 Getting Help

**Need help contributing?**

- 💬 **GitHub Discussions** - Ask questions
- 📧 **Email** - [maintainer email]
- 🐛 **Issues** - Report bugs
- 📖 **Documentation** - Read the docs

---

## 📅 Release Process

Releases follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0) - Breaking changes
- **Minor** (0.X.0) - New features, backwards compatible
- **Patch** (0.0.X) - Bug fixes

**Release schedule:**
- Patch releases: As needed
- Minor releases: Monthly
- Major releases: When necessary

---

## 🎓 Learning Resources

**New to open source?**
- [First Contributions](https://github.com/firstcontributions/first-contributions)
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)

**New to n8n?**
- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)

**New to Python?**
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/)

---

## 🙏 Thank You!

Every contribution helps make Project Automata better. Whether you're:
- Fixing a typo
- Reporting a bug
- Adding a feature
- Helping others

**You're making a difference. Thank you!** ❤️

---

**Questions?** Open a discussion on GitHub or reach out to maintainers.

**Happy contributing!** 🚀
